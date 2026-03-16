from pymongo import MongoClient
from transformers import pipeline
from datetime import datetime
import re

class SpecialiteClassifier:
    """
    Classifieur d'articles médicaux par spécialité
    """
    
    def __init__(self):
        print("🔄 Initialisation du classifieur...")
        
        # Définition des spécialités médicales en français
        self.specialites = [
            "oncologie", "cardiologie", "neurologie", "pédiatrie",
            "immunologie", "endocrinologie", "gastroentérologie", 
            "néphrologie", "pneumologie", "rhumatologie", "psychiatrie",
            "dermatologie", "ophtalmologie", "infectiologie", "hématologie"
        ]
        
        # Modèle de classification zero-shot (ne nécessite pas d'entraînement)
        print("🔄 Chargement du modèle IA (premier lancement peut être lent)...")
        self.classifier = pipeline(
            "zero-shot-classification",
            model="facebook/bart-large-mnli",
            device=-1  # Utiliser CPU
        )
        print("✅ Modèle chargé avec succès!")
    
    def classifier_article(self, article):
        """
        Classifie un article par spécialité médicale
        """
        # Combiner titre et résumé
        titre = article.get('title', '')
        abstract = article.get('abstract', '')
        texte = f"{titre} {abstract}"
        
        # Nettoyer et limiter
        texte = re.sub(r'\s+', ' ', texte).strip()
        texte = texte[:1024]  # Limiter la longueur
        
        if len(texte) < 50:
            return "non classifié", 0.0, "non déterminé"
        
        try:
            # Classification
            result = self.classifier(texte, self.specialites)
            
            # Meilleure spécialité
            meilleure_specialite = result['labels'][0]
            meilleur_score = result['scores'][0]
            
            # Détection du type d'étude
            type_etude = self.detecter_type_etude(texte)
            
            return meilleure_specialite, meilleur_score, type_etude
            
        except Exception as e:
            print(f"⚠️ Erreur classification: {e}")
            return "erreur", 0.0, "erreur"
    
    def detecter_type_etude(self, texte):
        """
        Détecte le type d'étude à partir du texte
        """
        texte_lower = texte.lower()
        
        types = {
            "essai randomisé contrôlé": ["rct", "randomized", "randomised", "randomly assigned", "essai randomisé"],
            "méta-analyse": ["meta-analysis", "meta analysis", "méta-analyse", "systematic review"],
            "étude de cohorte": ["cohort", "prospective", "longitudinal", "follow-up", "cohorte"],
            "étude de cas": ["case report", "case series", "cas clinique"],
            "revue": ["review article", "literature review", "revue de littérature"],
            "recommandations": ["guideline", "recommendation", "consensus", "recommandation"]
        }
        
        for type_etude, mots_cles in types.items():
            if any(mot in texte_lower for mot in mots_cles):
                return type_etude
        
        return "autre"

def main():
    print("🧠 CLASSIFICATION DES ARTICLES PAR SPÉCIALITÉ MÉDICALE")
    print("=" * 60)
    
    # Connexion à MongoDB (port 27018)
    print("\n🔌 Connexion à MongoDB...")
    client = MongoClient("mongodb://admin:admin@localhost:27018/")
    db = client["veille"]
    articles_collection = db["articles"]
    
    # Vérifier la connexion
    nb_articles = articles_collection.count_documents({})
    print(f"✅ Connecté à MongoDB. {nb_articles} articles trouvés")
    
    # Initialiser le classifieur
    print("\n🔄 Initialisation du classifieur IA...")
    classifier = SpecialiteClassifier()
    
    # Récupérer les articles non classifiés
    print("\n📊 Récupération des articles non classifiés...")
    articles_non_classifies = list(articles_collection.find({
        "specialite": {"$exists": False}
    }))
    
    print(f"📊 {len(articles_non_classifies)} articles à classifier")
    
    if not articles_non_classifies:
        print("✅ Tous les articles sont déjà classifiés !")
        return
    
    # Classifier les articles
    print("\n🔬 Classification en cours...")
    
    for i, article in enumerate(articles_non_classifies):
        print(f"\n--- Article {i+1}/{len(articles_non_classifies)} ---")
        print(f"Titre: {article.get('title', 'N/A')[:80]}...")
        
        # Classifier
        specialite, score, type_etude = classifier.classifier_article(article)
        
        # Mettre à jour dans MongoDB
        articles_collection.update_one(
            {"_id": article["_id"]},
            {"$set": {
                "specialite": specialite,
                "specialite_score": round(score, 3),
                "type_etude": type_etude,
                "date_classification": datetime.utcnow()
            }}
        )
        
        print(f"  ✅ Spécialité: {specialite} (score: {score:.3f})")
        print(f"  📋 Type d'étude: {type_etude}")
    
    # Statistiques finales
    print("\n" + "=" * 60)
    print("📈 RÉSULTATS DE LA CLASSIFICATION")
    
    # Compter par spécialité
    pipeline = [
        {"$match": {"specialite": {"$exists": True}}},
        {"$group": {"_id": "$specialite", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    
    print("\n📊 Distribution par spécialité:")
    for result in articles_collection.aggregate(pipeline):
        print(f"  {result['_id']}: {result['count']} articles")
    
    # Compter par type d'étude
    pipeline = [
        {"$match": {"type_etude": {"$exists": True}}},
        {"$group": {"_id": "$type_etude", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    
    print("\n📊 Distribution par type d'étude:")
    for result in articles_collection.aggregate(pipeline):
        print(f"  {result['_id']}: {result['count']} articles")
    
    total_classifies = articles_collection.count_documents({"specialite": {"$exists": True}})
    print(f"\n✅ Total: {total_classifies} articles classifiés avec succès")

if __name__ == "__main__":
    main()