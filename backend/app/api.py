from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from typing import Optional, List
from datetime import datetime
import uvicorn

# Créer l'application FastAPI
app = FastAPI(
    title="Veille Médicale API",
    description="API pour la plateforme de veille scientifique médicale",
    version="1.0.0"
)

# Configuration CORS pour permettre au frontend de communiquer
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # URL du frontend Next.js
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Connexion MongoDB (port 27018 comme configuré)
client = MongoClient("mongodb://admin:admin@localhost:27018/")
db = client["veille"]
articles_collection = db["articles"]

@app.get("/")
async def root():
    return {
        "message": "🚀 API Veille Médicale",
        "version": "1.0.0",
        "endpoints": [
            "/articles",
            "/articles/{id}",
            "/stats",
            "/search"
        ]
    }

@app.get("/articles")
async def get_articles(
    specialite: Optional[str] = Query(None, description="Filtrer par spécialité"),
    type_etude: Optional[str] = Query(None, description="Filtrer par type d'étude"),
    source: Optional[str] = Query(None, description="Filtrer par source (PubMed, EuropePMC, etc.)"),
    limit: int = Query(20, description="Nombre maximum de résultats"),
    skip: int = Query(0, description="Nombre de résultats à sauter (pagination)")
):
    """
    Récupère la liste des articles avec filtres optionnels
    """
    # Construire le filtre
    filter_query = {}
    if specialite:
        filter_query["specialite"] = specialite
    if type_etude:
        filter_query["type_etude"] = type_etude
    if source:
        filter_query["source"] = source
    
    # Récupérer les articles
    articles = list(articles_collection.find(
        filter_query,
        {
            "_id": 1,
            "title": 1,
            "source": 1,
            "specialite": 1,
            "type_etude": 1,
            "publication_date": 1,
            "authors": 1,
            "resume_structure.resume_court": 1
        }
    ).skip(skip).limit(limit))
    
    # Convertir ObjectId en string
    for article in articles:
        article["_id"] = str(article["_id"])
    
    return {
        "total": len(articles),
        "skip": skip,
        "limit": limit,
        "articles": articles
    }

@app.get("/articles/{article_id}")
async def get_article(article_id: str):
    """
    Récupère un article complet par son ID
    """
    from bson.objectid import ObjectId
    
    try:
        article = articles_collection.find_one({"_id": ObjectId(article_id)})
    except:
        raise HTTPException(status_code=400, detail="ID d'article invalide")
    
    if not article:
        raise HTTPException(status_code=404, detail="Article non trouvé")
    
    # Convertir ObjectId en string
    article["_id"] = str(article["_id"])
    
    return article

@app.get("/stats")
async def get_stats():
    """
    Statistiques sur les articles
    """
    # Nombre total d'articles
    total = articles_collection.count_documents({})
    
    # Distribution par spécialité
    specialites = list(articles_collection.aggregate([
        {"$group": {"_id": "$specialite", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]))
    
    # Distribution par source
    sources = list(articles_collection.aggregate([
        {"$group": {"_id": "$source", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]))
    
    # Distribution par type d'étude
    types_etude = list(articles_collection.aggregate([
        {"$group": {"_id": "$type_etude", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]))
    
    # Articles récents
    recents = list(articles_collection.find(
        {},
        {"title": 1, "publication_date": 1, "_id": 1}
    ).sort("publication_date", -1).limit(5))
    
    for article in recents:
        article["_id"] = str(article["_id"])
    
    return {
        "total_articles": total,
        "distribution_specialites": specialites,
        "distribution_sources": sources,
        "distribution_types_etude": types_etude,
        "articles_recents": recents
    }

@app.get("/search")
async def search_articles(
    q: str = Query(..., description="Termes de recherche"),
    limit: int = Query(20, description="Nombre maximum de résultats")
):
    """
    Recherche full-text dans les articles
    """
    # Recherche textuelle simple
    articles = list(articles_collection.find(
        {
            "$or": [
                {"title": {"$regex": q, "$options": "i"}},
                {"abstract": {"$regex": q, "$options": "i"}},
                {"authors": {"$regex": q, "$options": "i"}}
            ]
        },
        {
            "_id": 1,
            "title": 1,
            "source": 1,
            "specialite": 1,
            "publication_date": 1,
            "authors": 1,
            "resume_structure.resume_court": 1
        }
    ).limit(limit))
    
    # Convertir ObjectId en string
    for article in articles:
        article["_id"] = str(article["_id"])
    
    return {
        "query": q,
        "total": len(articles),
        "articles": articles
    }

@app.get("/specialites")
async def get_specialites():
    """
    Liste toutes les spécialités disponibles
    """
    specialites = articles_collection.distinct("specialite")
    return {"specialites": [s for s in specialites if s]}

@app.get("/sources")
async def get_sources():
    """
    Liste toutes les sources disponibles
    """
    sources = articles_collection.distinct("source")
    return {"sources": [s for s in sources if s]}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)