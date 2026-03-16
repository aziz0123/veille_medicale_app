# backend/app/recommendation_service.py
from pymongo import MongoClient
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from collections import Counter, defaultdict
import random
import numpy as np

class RecommendationService:
    def __init__(self, mongo_uri="mongodb://admin:admin@localhost:27018/"):
        self.client = MongoClient(mongo_uri)
        self.db = self.client["veille"]
        self.articles = self.db["articles"]
        self.user_actions = self.db["user_actions"]  # Pour tracker les interactions
    
    def get_personalized_feed(self, user_id, user_specialite, viewed_articles=None, limit=20):
        """
        Feed personnalisé style LinkedIn avec :
        - 60% articles de la spécialité
        - 20% articles populaires (collaborative)
        - 20% articles divers (découverte)
        """
        # Récupérer l'historique de l'utilisateur
        user_history = list(self.user_actions.find({"user_id": user_id}))
        viewed_ids = [a["article_id"] for a in user_history if a["action"] == "view"]
        
        # 1. CONTENT-BASED : articles de la même spécialité (60%)
        content_based = list(self.articles.find(
            {
                "specialite": {"$regex": user_specialite, "$options": "i"},
                "_id": {"$nin": [ObjectId(v) for v in viewed_ids[-50:]]}  # Exclure les 50 derniers vus
            },
            {
                "title": 1,
                "source": 1,
                "specialite": 1,
                "type_etude": 1,
                "publication_date": 1,
                "authors": 1,
                "resume_structure.resume_court": 1,
                "view_count": 1,
                "saved_count": 1
            }
        ).sort("publication_date", -1).limit(50))
        
        # 2. COLLABORATIVE : articles populaires (20%)
        popular = list(self.articles.find(
            {
                "specialite": {"$regex": user_specialite, "$options": "i"},
                "_id": {"$nin": [ObjectId(v) for v in viewed_ids[-20:]]}
            },
            {
                "title": 1,
                "source": 1,
                "specialite": 1,
                "type_etude": 1,
                "publication_date": 1,
                "authors": 1,
                "resume_structure.resume_court": 1,
                "view_count": 1,
                "saved_count": 1
            }
        ).sort([("view_count", -1), ("saved_count", -1)]).limit(30))
        
        # 3. DIVERS : articles d'autres spécialités pour la découverte (20%)
        other_specialites = list(self.articles.find(
            {
                "specialite": {"$not": {"$regex": user_specialite, "$options": "i"}},
                "_id": {"$nin": [ObjectId(v) for v in viewed_ids[-10:]]}
            },
            {
                "title": 1,
                "source": 1,
                "specialite": 1,
                "type_etude": 1,
                "publication_date": 1,
                "authors": 1,
                "resume_structure.resume_court": 1
            }
        ).sort("publication_date", -1).limit(20))
        
        # Fusionner et mélanger
        all_articles = content_based + popular + other_specialites
        random.shuffle(all_articles)
        
        # Convertir ObjectId en string
        for article in all_articles[:limit]:
            article["_id"] = str(article["_id"])
            article["type"] = self._determine_article_type(article)
        
        return all_articles[:limit]
    
    def get_career_feed(self, user_id, user_specialite, user_institution=None, limit=20):
        """
        Feed carrière style LinkedIn avec :
        - Opportunités de collaboration
        - Articles de leaders d'opinion
        - Appels à papers
        - Événements scientifiques
        """
        feed_items = []
        
        # 1. Suggestions de collaboration (co-auteurs potentiels)
        collab_suggestions = self._get_collaboration_suggestions(user_specialite, limit=5)
        feed_items.extend(collab_suggestions)
        
        # 2. Articles de leaders d'opinion (auteurs avec beaucoup de vues)
        opinion_leaders = self._get_opinion_leaders_articles(user_specialite, limit=5)
        feed_items.extend(opinion_leaders)
        
        # 3. Appels à papers (simulés pour l'instant)
        call_for_papers = self._get_call_for_papers(user_specialite, limit=5)
        feed_items.extend(call_for_papers)
        
        # 4. Événements scientifiques (simulés)
        events = self._get_scientific_events(user_specialite, limit=5)
        feed_items.extend(events)
        
        # Mélanger et limiter
        random.shuffle(feed_items)
        
        for item in feed_items:
            if "_id" in item:
                item["_id"] = str(item["_id"])
        
        return feed_items[:limit]
    
    def _get_collaboration_suggestions(self, specialite, limit=5):
        """Suggère des collaborateurs potentiels"""
        suggestions = []
        
        # Trouver les auteurs les plus actifs dans la spécialité
        pipeline = [
            {"$match": {"specialite": {"$regex": specialite, "$options": "i"}}},
            {"$unwind": "$authors"},
            {"$group": {"_id": "$authors", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": limit}
        ]
        
        top_authors = list(self.articles.aggregate(pipeline))
        
        for author in top_authors:
            suggestions.append({
                "type": "collaboration",
                "title": f"Collaborer avec {author['_id']}",
                "description": f"{author['count']} publications dans votre domaine",
                "author": author['_id'],
                "publications_count": author['count'],
                "timestamp": datetime.utcnow().isoformat(),
                "action_text": "Contacter",
                "action_link": "/network"
            })
        
        return suggestions
    
    def _get_opinion_leaders_articles(self, specialite, limit=5):
        """Récupère les articles des auteurs les plus influents"""
        leaders = []
        
        pipeline = [
            {"$match": {"specialite": {"$regex": specialite, "$options": "i"}}},
            {"$sort": {"view_count": -1, "saved_count": -1}},
            {"$limit": limit}
        ]
        
        articles = list(self.articles.aggregate(pipeline))
        
        for article in articles:
            leaders.append({
                "type": "opinion_leader",
                "title": article.get("title", ""),
                "description": article.get("resume_structure", {}).get("resume_court", ""),
                "source": article.get("source", ""),
                "authors": article.get("authors", [])[:2],
                "publication_date": article.get("publication_date", ""),
                "timestamp": datetime.utcnow().isoformat(),
                "action_text": "Lire",
                "action_link": f"/articles/{article['_id']}"
            })
        
        return leaders
    
    def _get_call_for_papers(self, specialite, limit=5):
        """Simule des appels à papers (à connecter avec des vraies sources plus tard)"""
        calls = [
            {
                "type": "call_for_papers",
                "title": f"Appel à communications - Journal of {specialite.capitalize()}",
                "description": "Soumettez vos recherches avant le 30 juin 2026",
                "deadline": "2026-06-30",
                "journal": f"Journal of {specialite.capitalize()}",
                "timestamp": datetime.utcnow().isoformat(),
                "action_text": "Soumettre",
                "action_link": "#"
            },
            {
                "type": "call_for_papers",
                "title": f"Congrès International de {specialite.capitalize()} 2026",
                "description": "Appel à communications ouvert jusqu'au 15 juillet",
                "deadline": "2026-07-15",
                "conference": f"International Conference on {specialite.capitalize()}",
                "timestamp": datetime.utcnow().isoformat(),
                "action_text": "Proposer",
                "action_link": "#"
            }
        ]
        return calls[:limit]
    
    def _get_scientific_events(self, specialite, limit=5):
        """Simule des événements scientifiques"""
        events = [
            {
                "type": "event",
                "title": f"Webinaire : Les dernières avancées en {specialite}",
                "description": "Présentation par les experts internationaux",
                "date": "2026-04-15",
                "time": "14:00 UTC",
                "speakers": ["Dr. Martin", "Pr. Bernard"],
                "timestamp": datetime.utcnow().isoformat(),
                "action_text": "S'inscrire",
                "action_link": "#"
            },
            {
                "type": "event",
                "title": f"Formation : Méta-analyses en {specialite}",
                "description": "Atelier pratique de 2 jours",
                "date": "2026-05-10",
                "location": "Paris / Distanciel",
                "timestamp": datetime.utcnow().isoformat(),
                "action_text": "Voir détails",
                "action_link": "#"
            }
        ]
        return events[:limit]
    
    def _determine_article_type(self, article):
        """Détermine le type d'article pour le feed"""
        if article.get("type_etude") == "essai randomisé contrôlé":
            return "clinical_trial"
        elif article.get("type_etude") == "méta-analyse":
            return "meta_analysis"
        elif article.get("view_count", 0) > 100:
            return "trending"
        else:
            return "regular"
    
    def track_user_action(self, user_id, article_id, action):
        """Track les actions utilisateur pour améliorer les recommandations"""
        self.user_actions.update_one(
            {"user_id": user_id, "article_id": article_id},
            {"$set": {
                "action": action,
                "timestamp": datetime.utcnow()
            }},
            upsert=True
        )