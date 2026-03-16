from pymongo import MongoClient
from datetime import datetime
from .pubmed_client import PubMedClient
from .europepmc_client import EuropePMCClient
from .biorxiv_client import BioRxivClient

class CurationService:
    """
    Service unifié pour la curation automatique des articles
    """
    
    def __init__(self, mongo_uri="mongodb://admin:admin@localhost:27018/", mongo_db="veille"):
        """
        Initialise le service de curation
        Args:
            mongo_uri: URI de connexion MongoDB (par défaut port 27018 avec auth)
            mongo_db: Nom de la base de données
        """
        # Connexion MongoDB avec le bon port et authentification
        print(f"🔌 Connexion à MongoDB: {mongo_uri}")
        self.client = MongoClient(mongo_uri)
        self.db = self.client[mongo_db]
        self.articles_collection = self.db["articles"]
        
        # Créer un index unique sur DOI pour éviter les doublons
        try:
            self.articles_collection.create_index("doi", unique=True, sparse=True)
            print("✅ Index créé sur DOI")
        except Exception as e:
            print(f"⚠️ Index可能存在 déjà: {e}")
        
        # Initialiser les clients API avec les vrais scrapers
        self.pubmed = PubMedClient(email="azizkhaled73@gmail.com")
        self.europepmc = EuropePMCClient()
        self.biorxiv = BioRxivClient()
        
        print("✅ Service de curation initialisé")
    
    def search_all_sources(self, query="cancer", max_per_source=20):
        """
        Recherche dans toutes les sources scientifiques
        """
        all_articles = []
        
        # 1. PubMed
        print(f"\n📡 Récupération depuis PubMed pour '{query}'...")
        pmids = self.pubmed.search(query, max_results=max_per_source)
        if pmids:
            pubmed_articles = self.pubmed.fetch_details(pmids)
            all_articles.extend(pubmed_articles)
            print(f"   → {len(pubmed_articles)} articles PubMed récupérés")
        else:
            print("   → Aucun article PubMed trouvé")
        
        # 2. Europe PMC
        print(f"\n📡 Récupération depuis Europe PMC pour '{query}'...")
        epmc_articles = self.europepmc.search_and_fetch(query, max_results=max_per_source)
        if epmc_articles:
            all_articles.extend(epmc_articles)
            print(f"   → {len(epmc_articles)} articles Europe PMC récupérés")
        else:
            print("   → Aucun article Europe PMC trouvé")
        
        # 3. bioRxiv
        print("\n📡 Récupération depuis bioRxiv...")
        try:
            biorxiv_articles = self.biorxiv.get_recent(server="biorxiv", days_back=30)
            if biorxiv_articles:
                biorxiv_selected = biorxiv_articles[:max_per_source]
                all_articles.extend(biorxiv_selected)
                print(f"   → {len(biorxiv_selected)} articles bioRxiv récupérés")
            else:
                print("   → Aucun article bioRxiv trouvé")
        except Exception as e:
            print(f"   → Erreur bioRxiv: {e}")
        
        # 4. medRxiv
        print("\n📡 Récupération depuis medRxiv...")
        try:
            medrxiv_articles = self.biorxiv.get_recent(server="medrxiv", days_back=30)
            if medrxiv_articles:
                medrxiv_selected = medrxiv_articles[:max_per_source]
                all_articles.extend(medrxiv_selected)
                print(f"   → {len(medrxiv_selected)} articles medRxiv récupérés")
            else:
                print("   → Aucun article medRxiv trouvé")
        except Exception as e:
            print(f"   → Erreur medRxiv: {e}")
        
        print(f"\n✅ Total: {len(all_articles)} articles récupérés")
        return all_articles
    
    def save_articles(self, articles):
        """
        Sauvegarde les articles dans MongoDB (évite les doublons)
        """
        saved_count = 0
        total_articles = len(articles)
        
        print(f"\n💾 Sauvegarde de {total_articles} articles dans MongoDB...")
        
        for i, article in enumerate(articles, 1):
            try:
                # Vérifier si l'article existe déjà
                existing = None
                
                # Chercher par DOI d'abord (si disponible)
                if article.get("doi") and article["doi"]:
                    existing = self.articles_collection.find_one({"doi": article["doi"]})
                
                # Si pas de DOI ou pas trouvé, chercher par titre
                if not existing and article.get("title") and article["title"]:
                    existing = self.articles_collection.find_one({"title": article["title"]})
                
                # Si l'article n'existe pas, l'insérer
                if not existing:
                    # Ajouter la date de sauvegarde
                    article["date_saved"] = datetime.utcnow()
                    
                    result = self.articles_collection.insert_one(article)
                    if result.inserted_id:
                        saved_count += 1
                        print(f"  ✅ [{i}/{total_articles}] Nouvel article: {article.get('title', 'N/A')[:60]}...")
                else:
                    print(f"  ⏩ [{i}/{total_articles}] Déjà existant: {article.get('title', 'N/A')[:60]}...")
                
            except Exception as e:
                print(f"  ⚠️ [{i}/{total_articles}] Erreur: {e}")
        
        print(f"\n💾 Résultat: {saved_count} nouveaux articles sauvegardés sur {total_articles}")
        return saved_count
    
    def get_articles_to_process(self, limit=100):
        """
        Récupère les articles qui n'ont pas encore été traités (sans classification)
        """
        try:
            articles = list(self.articles_collection.find({
                "specialite": {"$exists": False}
            }).limit(limit))
            print(f"📊 {len(articles)} articles en attente de classification IA")
            return articles
        except Exception as e:
            print(f"⚠️ Erreur lors de la récupération des articles: {e}")
            return []
    
    def update_article_classification(self, article_id, specialite, type_etude):
        """
        Met à jour un article avec sa classification
        """
        from bson.objectid import ObjectId
        
        try:
            result = self.articles_collection.update_one(
                {"_id": ObjectId(article_id)},
                {"$set": {
                    "specialite": specialite,
                    "type_etude": type_etude,
                    "date_classification": datetime.utcnow()
                }}
            )
            
            if result.modified_count > 0:
                print(f"✅ Article {article_id} classifié: {specialite} - {type_etude}")
            else:
                print(f"⚠️ Article {article_id} non trouvé ou non modifié")
            
            return result.modified_count
        except Exception as e:
            print(f"⚠️ Erreur lors de la mise à jour: {e}")
            return 0
    
    def get_statistics(self):
        """
        Retourne des statistiques sur les articles dans la base
        """
        try:
            total = self.articles_collection.count_documents({})
            with_classification = self.articles_collection.count_documents({
                "specialite": {"$exists": True}
            })
            without_classification = self.articles_collection.count_documents({
                "specialite": {"$exists": False}
            })
            
            stats = {
                "total": total,
                "avec_classification": with_classification,
                "sans_classification": without_classification,
                "sources": {}
            }
            
            # Compter par source
            pipeline = [
                {"$group": {"_id": "$source", "count": {"$sum": 1}}}
            ]
            
            for result in self.articles_collection.aggregate(pipeline):
                stats["sources"][result["_id"]] = result["count"]
            
            return stats
        except Exception as e:
            print(f"⚠️ Erreur lors des statistiques: {e}")
            return {"total": 0, "avec_classification": 0, "sans_classification": 0, "sources": {}}