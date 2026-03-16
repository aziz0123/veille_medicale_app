from pymongo import MongoClient

try:
    # Connexion à MongoDB Docker (port 27018)
    client = MongoClient("mongodb://admin:admin@localhost:27018/")
    db = client["veille"]

    # Liste des collections
    collections = db.list_collection_names()
    print("✅ Connexion MongoDB réussie !")
    print(f"Collections existantes: {collections}")

    # Test création d'un index
    test_collection = db["test"]
    test_collection.create_index("test", unique=True)
    print("✅ Création d'index réussie !")

except Exception as e:
    print(f"❌ Erreur: {e}")
