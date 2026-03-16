from app.curation_service import CurationService
from pymongo import MongoClient

# ⚠️ IMPORTANT: Utiliser le port 27018 car c'est celui mappé dans Docker
MONGO_URI = "mongodb://admin:admin@localhost:27018/"
MONGO_DB = "veille"

print(f"🔌 Connexion à MongoDB: {MONGO_URI}")

# Test de connexion directe avec pymongo
try:
    client = MongoClient(MONGO_URI)
    client.admin.command('ping')
    print("✅ Connexion MongoDB réussie !")
    
    # Liste les bases de données
    dbs = client.list_database_names()
    print(f"📊 Bases de données: {dbs}")
    
except Exception as e:
    print(f"❌ Erreur de connexion: {e}")
    exit(1)

# Maintenant, on doit modifier CurationService pour utiliser cette URI
# Pour l'instant, on va utiliser directement pymongo
db = client[MONGO_DB]
articles_collection = db["articles"]

# Récupérer les articles via le service existant
print("\n📡 Récupération des articles...")
service = CurationService()  # Utilise la config par défaut (mais ne sauvegarde pas)
articles = service.search_all_sources(query="cancer immunotherapy", max_per_source=5)

# Sauvegarde forcée avec la bonne connexion
print("\n💾 Sauvegarde forcée...")
saved = 0
for article in articles:
    try:
        # Vérifier si l'article existe déjà
        existing = None
        if article.get("doi"):
            existing = articles_collection.find_one({"doi": article["doi"]})
        
        if not existing:
            result = articles_collection.insert_one(article)
            if result.inserted_id:
                saved += 1
                print(f"✅ Article {saved} sauvegardé: {article.get('title', 'N/A')[:50]}...")
        else:
            print(f"⏩ Article déjà existant: {article.get('title', 'N/A')[:50]}...")
            
    except Exception as e:
        print(f"⚠️ Erreur: {e}")

print(f"\n💾 Total: {saved} articles sauvegardés")

# Vérification finale
print(f"\n📊 Nombre total d'articles dans la base: {articles_collection.count_documents({})}")