from app.curation_service import CurationService

def main():
    print("🚀 Test du service de curation automatique")
    print("=" * 50)

    service = CurationService()  # Utilise la config par défaut

    # Récupérer des articles
    print("\n📡 Phase 1: Récupération des articles...")
    articles = service.search_all_sources(query="cancer immunotherapy", max_per_source=5)

    # Sauvegarde dans MongoDB
    print("\n💾 Phase 2: Sauvegarde dans MongoDB...")
    service.save_articles(articles)

    # Vérification des articles à traiter
    print("\n⏳ Phase 3: Articles à classifier...")
    to_process = service.get_articles_to_process()
    print(f"📊 {len(to_process)} articles en attente de classification IA")

    if to_process:
        example = to_process[0]
        print("\n📄 Exemple d'article:")
        print(f"Titre: {example.get('title', 'N/A')}")
        print(f"Source: {example.get('source', 'N/A')}")
        print(f"Résumé: {example.get('abstract', '')[:200]}...")

        print("\n🔍 Test de connexion MongoDB:")
        print(f"Base de données: {service.db.name}")
        print(f"Collections: {service.db.list_collection_names()}")
        print(f"Nombre d'articles: {service.articles_collection.count_documents({})}")

if __name__ == "__main__":
    main()
