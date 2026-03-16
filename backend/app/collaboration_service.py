# backend/app/collaboration_service.py
from pymongo import MongoClient
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Dict
import networkx as nx

class CollaborationService:
    def __init__(self, mongo_uri="mongodb://admin:admin@localhost:27018/"):
        self.client = MongoClient(mongo_uri)
        self.db = self.client["veille"]
        self.articles = self.db["articles"]
    
    def build_coauthor_graph(self, author_id: int, db: Session, depth: int = 2) -> nx.Graph:
        """Construit un graphe de co-auteurs"""
        G = nx.Graph()
    
        from app.models import AuthorArticle, Author
    
        # Récupérer les articles de l'auteur
        author_articles = db.query(AuthorArticle).filter(
        AuthorArticle.author_id == author_id
        ).all()
    
        # Ajouter le nœud principal
        G.add_node(author_id)
    
        # Si pas d'articles, retourner le graphe avec seulement l'auteur
        if not author_articles:
            return G
    
        for aa in author_articles:
            # Récupérer les co-auteurs
            coauthors = db.query(AuthorArticle).filter(
                AuthorArticle.article_id == aa.article_id,
                AuthorArticle.author_id != author_id
            ).all()
        
            for co in coauthors:
                if not G.has_node(co.author_id):
                    G.add_node(co.author_id)
            
                if G.has_edge(author_id, co.author_id):
                    G[author_id][co.author_id]['weight'] += 1
                else:
                    G.add_edge(author_id, co.author_id, weight=1)
    
        # Si depth > 1, on pourrait étendre le graphe (optionnel)
        return G
    
    def suggest_collaborations(self, author_id: int, db: Session, limit: int = 5) -> List[Dict]:
        """Suggère des collaborations"""
        try:
            G = self.build_coauthor_graph(author_id, db)
            
            # Si pas de nœud ou pas de voisins, retourner vide
            if not G.has_node(author_id) or G.degree(author_id) == 0:
                return []
            
            suggestions = []
            neighbors = list(G.neighbors(author_id))
            second_degree = set()
            
            for neighbor in neighbors:
                for n in G.neighbors(neighbor):
                    if n != author_id and n not in neighbors:
                        second_degree.add(n)
            
            from app.models import Author
            
            for potential_id in second_degree:
                potential = db.query(Author).filter(Author.id == potential_id).first()
                if potential:
                    score = 0
                    for neighbor in neighbors:
                        if G.has_edge(potential_id, neighbor):
                            score += G[potential_id][neighbor]['weight']
                    
                    # Connexions mutuelles
                    mutual = []
                    for neighbor in neighbors:
                        if G.has_edge(potential_id, neighbor):
                            neighbor_author = db.query(Author).filter(Author.id == neighbor).first()
                            if neighbor_author:
                                mutual.append(f"{neighbor_author.prenom} {neighbor_author.nom}")
                    
                    suggestions.append({
                        "author_id": potential.id,
                        "name": f"{potential.prenom} {potential.nom}",
                        "institution": potential.institution or "",
                        "orcid_id": potential.orcid_id,
                        "score": score,
                        "mutual_connections": mutual[:3]
                    })
            
            suggestions.sort(key=lambda x: x['score'], reverse=True)
            return suggestions[:limit]
            
        except Exception as e:
            print(f"Erreur suggestions: {e}")
            return []
    
    def get_collaboration_network(self, author_id: int, db: Session) -> Dict:
        """Récupère le réseau"""
        try:
            G = self.build_coauthor_graph(author_id, db)
            
            from app.models import Author
            
            nodes = []
            for node in G.nodes():
                author = db.query(Author).filter(Author.id == node).first()
                if author:
                    nodes.append({
                        "id": node,
                        "name": f"{author.prenom} {author.nom}",
                        "institution": author.institution or "",
                        "is_center": node == author_id,
                        "size": max(G.degree(node) * 2, 5) if G.degree(node) > 0 else 5
                    })
            
            edges = []
            for u, v, data in G.edges(data=True):
                edges.append({
                    "source": u,
                    "target": v,
                    "weight": data.get('weight', 1)
                })
            
            return {
                "nodes": nodes,
                "edges": edges
            }
            
        except Exception as e:
            print(f"Erreur réseau: {e}")
            return {"nodes": [], "edges": []}