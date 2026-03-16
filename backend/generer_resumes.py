from pymongo import MongoClient
from app.resume_generator import ResumeGenerator
from datetime import datetime
import time

def main():
    print("🧠 GÉNÉRATION DE RÉSUMÉS STRUCTURÉS")
    print("=" * 60)
    
    # Connexion à MongoDB
    print("\n🔌 Connexion à MongoDB...")
    client = MongoClient("mongodb://admin:admin@localhost:27018/")
    db = client["veille"]
    articles_collection = db["articles"]
    
    # Vérifier la connexion
    nb_articles = articles_collection.count_documents({})
    print(f"✅ Connecté. {nb_articles} articles trouvés")
    
    # Initialiser le générateur
    print("\n🔄 Initialisation du générateur de résumés...")
    generator = ResumeGenerator()
    
    # Récupérer les articles sans résumé structuré
    articles = list(articles_collection.find({
        "resume_structure": {"$exists": False}
    }))
    
    print(f"\n📊 {len(articles)} articles à traiter")
    
    if not articles:
        print("✅ Tous les articles ont déjà un résumé!")
        return
    
    # Générer les résumés
    print("\n📝 Génération des résumés en cours...")
    
    for i, article in enumerate(articles):
        print(f"\n--- Article {i+1}/{len(articles)} ---")
        print(f"Titre: {article.get('title', 'N/A')[:80]}...")
        
        # Générer le résumé structuré
        resume = generator.generer_resume_structure(article)
        
        # Mettre à jour dans MongoDB
        articles_collection.update_one(
            {"_id": article["_id"]},
            {"$set": {
                "resume_structure": resume,
                "date_resume": datetime.utcnow()
            }}
        )
        
        print(f"  ✅ Résumé généré!")
        print(f"  📄 Résumé court: {resume['resume_court'][:100]}...")
        print(f"  👥 Population: {resume['population']}")
        print(f"  💊 Intervention: {resume['intervention']}")
        print(f"  📊 Résultats: {resume['resultats']}")
        print(f"  🎯 Conclusion: {resume['conclusion']}")
        
        # Petit délai pour éviter de surcharger
        time.sleep(1)
    
    print("\n" + "=" * 60)
    print("✅ GÉNÉRATION TERMINÉE!")
    print(f"📊 {len(articles)} résumés générés avec succès")

if __name__ == "__main__":
    main()