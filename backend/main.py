from fastapi import FastAPI, HTTPException, Query, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, ForeignKey, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from datetime import datetime, timedelta
from pymongo import MongoClient
from bson import ObjectId
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field
from jose import JWTError, jwt
import bcrypt
import uvicorn

# ============================================
# CONFIGURATION
# ============================================
SECRET_KEY = "votre-cle-secrete-tres-longue-et-securisee-a-changer-en-production-123456789"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# ============================================
# CONFIGURATION SQLITE
# ============================================
SQLALCHEMY_DATABASE_URL = "sqlite:///./veille.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

print("✅ SQLite configuré avec succès")

# ============================================
# MODÈLES SQLALCHEMY (SQLite)
# ============================================

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    nom = Column(String, nullable=False)
    prenom = Column(String, nullable=False)
    specialite = Column(String, nullable=False)
    institution = Column(String, nullable=True)
    orcid_id = Column(String, unique=True, nullable=True)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    date_inscription = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)

class Author(Base):
    __tablename__ = "authors"
    
    id = Column(Integer, primary_key=True, index=True)
    orcid_id = Column(String, unique=True, index=True, nullable=True)
    nom = Column(String, nullable=False)
    prenom = Column(String, nullable=False)
    institution = Column(String, nullable=True)
    email = Column(String, nullable=True)
    research_fields = Column(String, nullable=True)
    total_citations = Column(Integer, default=0)
    h_index = Column(Integer, default=0)
    last_sync = Column(DateTime, nullable=True)

class Collaboration(Base):
    __tablename__ = "collaborations"
    
    id = Column(Integer, primary_key=True, index=True)
    author1_id = Column(Integer, ForeignKey('authors.id'))
    author2_id = Column(Integer, ForeignKey('authors.id'))
    co_author_count = Column(Integer, default=1)
    first_collaboration = Column(DateTime, default=datetime.utcnow)
    last_collaboration = Column(DateTime, default=datetime.utcnow)
    strength = Column(Float, default=1.0)

class AuthorArticle(Base):
    __tablename__ = "author_articles"
    
    id = Column(Integer, primary_key=True, index=True)
    author_id = Column(Integer, ForeignKey('authors.id'))
    article_id = Column(String)
    article_title = Column(String)
    article_doi = Column(String)
    publication_date = Column(DateTime)
    is_corresponding = Column(Boolean, default=False)

# ============================================
# NOUVEAUX MODÈLES POUR LE PROFIL
# ============================================

class Experience(Base):
    __tablename__ = "experiences"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    titre = Column(String, nullable=False)
    entreprise = Column(String, nullable=False)
    lieu = Column(String, nullable=True)
    date_debut = Column(DateTime, nullable=False)
    date_fin = Column(DateTime, nullable=True)
    description = Column(String, nullable=True)
    en_cours = Column(Boolean, default=False)
    
    user = relationship("User", back_populates="experiences")

class Formation(Base):
    __tablename__ = "formations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    diplome = Column(String, nullable=False)
    etablissement = Column(String, nullable=False)
    domaine = Column(String, nullable=True)
    date_debut = Column(DateTime, nullable=False)
    date_fin = Column(DateTime, nullable=True)
    description = Column(String, nullable=True)
    
    user = relationship("User", back_populates="formations")

class Competence(Base):
    __tablename__ = "competences"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    nom = Column(String, nullable=False)
    niveau = Column(Integer, nullable=True)
    categorie = Column(String, nullable=True)
    
    user = relationship("User", back_populates="competences")

class ObjectifCarriere(Base):
    __tablename__ = "objectifs_carriere"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    titre = Column(String, nullable=False)
    description = Column(String, nullable=True)
    actif = Column(Boolean, default=True)
    
    user = relationship("User", back_populates="objectifs")

# Ajout des relations à User
User.experiences = relationship("Experience", back_populates="user", cascade="all, delete-orphan")
User.formations = relationship("Formation", back_populates="user", cascade="all, delete-orphan")
User.competences = relationship("Competence", back_populates="user", cascade="all, delete-orphan")
User.objectifs = relationship("ObjectifCarriere", back_populates="user", cascade="all, delete-orphan")

# ============================================
# CRÉATION DES TABLES SQLITE
# ============================================
print("🔄 Création des tables SQLite...")
Base.metadata.create_all(bind=engine)
print("✅ Tables SQLite créées avec succès")

# ============================================
# SCHÉMAS PYDANTIC
# ============================================

class UserBase(BaseModel):
    email: EmailStr
    nom: str
    prenom: str
    specialite: str
    institution: Optional[str] = None
    orcid_id: Optional[str] = None

class UserCreate(UserBase):
    password: str = Field(..., min_length=6)

class UserResponse(UserBase):
    id: int
    is_active: bool
    date_inscription: datetime
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

class TokenData(BaseModel):
    email: Optional[str] = None
    specialite: Optional[str] = None

class AuthorResponse(BaseModel):
    id: int
    nom: str
    prenom: str
    institution: Optional[str] = None
    orcid_id: Optional[str] = None
    email: Optional[str] = None
    research_fields: Optional[str] = None
    total_citations: int
    h_index: int
    
    class Config:
        from_attributes = True

class CollaborationSuggestion(BaseModel):
    author_id: int
    name: str
    institution: Optional[str] = None
    orcid_id: Optional[str] = None
    score: float
    mutual_connections: List[str] = []

# ============================================
# NOUVEAUX SCHÉMAS POUR LE PROFIL
# ============================================

class ExperienceBase(BaseModel):
    titre: str
    entreprise: str
    lieu: Optional[str] = None
    date_debut: datetime
    date_fin: Optional[datetime] = None
    description: Optional[str] = None
    en_cours: bool = False

class ExperienceCreate(ExperienceBase):
    pass

class ExperienceResponse(ExperienceBase):
    id: int
    user_id: int
    
    class Config:
        from_attributes = True

class FormationBase(BaseModel):
    diplome: str
    etablissement: str
    domaine: Optional[str] = None
    date_debut: datetime
    date_fin: Optional[datetime] = None
    description: Optional[str] = None

class FormationCreate(FormationBase):
    pass

class FormationResponse(FormationBase):
    id: int
    user_id: int
    
    class Config:
        from_attributes = True

class CompetenceBase(BaseModel):
    nom: str
    niveau: Optional[int] = None
    categorie: Optional[str] = None

class CompetenceCreate(CompetenceBase):
    pass

class CompetenceResponse(CompetenceBase):
    id: int
    user_id: int
    
    class Config:
        from_attributes = True

class ObjectifCarriereBase(BaseModel):
    titre: str
    description: Optional[str] = None
    actif: bool = True

class ObjectifCarriereCreate(ObjectifCarriereBase):
    pass

class ObjectifCarriereResponse(ObjectifCarriereBase):
    id: int
    user_id: int
    
    class Config:
        from_attributes = True

class ProfilCompletResponse(UserResponse):
    experiences: List[ExperienceResponse] = []
    formations: List[FormationResponse] = []
    competences: List[CompetenceResponse] = []
    objectifs: List[ObjectifCarriereResponse] = []

# ============================================
# FONCTIONS D'AUTHENTIFICATION
# ============================================

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        plain_password.encode('utf-8'), 
        hashed_password.encode('utf-8')
    )

def get_password_hash(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt

def decode_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Identifiants invalides",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = decode_token(token)
    if not payload:
        raise credentials_exception
    
    email = payload.get("sub")
    if not email:
        raise credentials_exception
    
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise credentials_exception
    
    return user

# ============================================
# CONFIGURATION MONGODB
# ============================================
try:
    client = MongoClient("mongodb://admin:admin@localhost:27018/")
    db = client["veille"]
    articles_collection = db["articles"]
    count = articles_collection.count_documents({})
    print(f"✅ MongoDB connecté sur le port 27018 - {count} articles trouvés")
except Exception as e:
    print(f"❌ Erreur MongoDB: {e}")

# ============================================
# CRÉATION DE L'APPLICATION FASTAPI
# ============================================
app = FastAPI(
    title="Veille Médicale - Backend Complet",
    description="API pour la plateforme de veille scientifique médicale",
    version="1.0.0"
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://teena-subcivilized-daniela.ngrok-free.dev",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================
# ROUTES D'AUTHENTIFICATION
# ============================================

@app.post("/auth/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    try:
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise HTTPException(400, "Un compte avec cet email existe déjà")
        
        if user_data.orcid_id:
            existing_orcid = db.query(User).filter(User.orcid_id == user_data.orcid_id).first()
            if existing_orcid:
                raise HTTPException(400, "Cet ORCID est déjà associé à un compte")
        
        hashed_password = get_password_hash(user_data.password)
        new_user = User(
            email=user_data.email,
            nom=user_data.nom,
            prenom=user_data.prenom,
            specialite=user_data.specialite,
            institution=user_data.institution,
            orcid_id=user_data.orcid_id,
            hashed_password=hashed_password,
            is_active=True
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        access_token = create_access_token(
            data={"sub": new_user.email, "specialite": new_user.specialite}
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": new_user
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")
        raise HTTPException(500, f"Erreur interne: {str(e)}")

@app.post("/auth/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    try:
        user = db.query(User).filter(User.email == form_data.username).first()
        
        if not user or not verify_password(form_data.password, user.hashed_password):
            raise HTTPException(401, "Email ou mot de passe incorrect")
        
        if not user.is_active:
            raise HTTPException(400, "Compte désactivé")
        
        user.last_login = datetime.utcnow()
        db.commit()
        
        access_token = create_access_token(
            data={"sub": user.email, "specialite": user.specialite}
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": user
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")
        raise HTTPException(500, f"Erreur interne: {str(e)}")

@app.get("/auth/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    return current_user

# ============================================
# ROUTES DE BASE
# ============================================

@app.get("/")
async def root():
    return {
        "message": "🚀 Backend Veille Medicale",
        "version": "1.0.0",
        "api_docs": "/docs"
    }

@app.get("/health")
async def health():
    try:
        articles_count = articles_collection.count_documents({})
        mongodb_status = "connected"
    except:
        articles_count = 0
        mongodb_status = "disconnected"
    
    return {
        "status": "OK",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "database": "sqlite",
            "mongodb": mongodb_status,
            "articles_count": articles_count
        }
    }

# ============================================
# ROUTES POUR LE FEED STYLE LINKEDIN (NOUVELLES)
# ============================================

@app.get("/api/feed/personalized")
async def get_feed_personalized(
    limit: int = Query(20, description="Nombre d'articles"),
    current_user: User = Depends(get_current_user)
):
    """
    Feed personnalisé d'articles
    """
    try:
        from app.recommendation_service import RecommendationService
        
        service = RecommendationService()
        feed = service.get_personalized_feed(
            user_id=current_user.id,
            user_specialite=current_user.specialite,
            limit=limit
        )
        
        return {
            "user": f"{current_user.prenom} {current_user.nom}",
            "specialite": current_user.specialite,
            "total": len(feed),
            "feed": feed
        }
    except Exception as e:
        print(f"❌ Erreur feed personalized: {e}")
        raise HTTPException(500, detail=str(e))

@app.get("/api/feed/career")
async def get_feed_career(
    limit: int = Query(20, description="Nombre d'éléments"),
    current_user: User = Depends(get_current_user)
):
    """
    Feed carrière avec opportunités professionnelles
    """
    try:
        from app.recommendation_service import RecommendationService
        
        service = RecommendationService()
        feed = service.get_career_feed(
            user_id=current_user.id,
            user_specialite=current_user.specialite,
            user_institution=current_user.institution,
            limit=limit
        )
        
        return {
            "user": f"{current_user.prenom} {current_user.nom}",
            "specialite": current_user.specialite,
            "total": len(feed),
            "feed": feed
        }
    except Exception as e:
        print(f"❌ Erreur feed career: {e}")
        raise HTTPException(500, detail=str(e))

@app.post("/api/feed/track/{article_id}/{action}")
async def track_action(
    article_id: str,
    action: str,
    current_user: User = Depends(get_current_user)
):
    """
    Track les actions utilisateur (view, save, share)
    """
    try:
        from app.recommendation_service import RecommendationService
        service = RecommendationService()
        service.track_user_action(
            user_id=current_user.id,
            article_id=article_id,
            action=action
        )
        return {"message": "Action trackée"}
    except Exception as e:
        raise HTTPException(500, detail=str(e))

# ============================================
# ROUTES POUR LE PROFIL COMPLET (NOUVELLES)
# ============================================

@app.get("/api/profil/complet", response_model=ProfilCompletResponse)
async def get_profil_complet(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Récupère le profil complet de l'utilisateur
    """
    user = db.query(User).filter(User.id == current_user.id).first()
    return user

# EXPÉRIENCES
@app.get("/api/profil/experiences", response_model=List[ExperienceResponse])
async def get_experiences(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    experiences = db.query(Experience).filter(
        Experience.user_id == current_user.id
    ).order_by(Experience.date_debut.desc()).all()
    return experiences

@app.post("/api/profil/experiences", response_model=ExperienceResponse)
async def create_experience(
    experience: ExperienceCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    new_exp = Experience(
        **experience.dict(),
        user_id=current_user.id
    )
    db.add(new_exp)
    db.commit()
    db.refresh(new_exp)
    return new_exp

@app.put("/api/profil/experiences/{exp_id}", response_model=ExperienceResponse)
async def update_experience(
    exp_id: int,
    experience: ExperienceCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    exp = db.query(Experience).filter(
        Experience.id == exp_id,
        Experience.user_id == current_user.id
    ).first()
    if not exp:
        raise HTTPException(404, "Expérience non trouvée")
    
    for key, value in experience.dict().items():
        setattr(exp, key, value)
    
    db.commit()
    db.refresh(exp)
    return exp

@app.delete("/api/profil/experiences/{exp_id}")
async def delete_experience(
    exp_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    exp = db.query(Experience).filter(
        Experience.id == exp_id,
        Experience.user_id == current_user.id
    ).first()
    if not exp:
        raise HTTPException(404, "Expérience non trouvée")
    
    db.delete(exp)
    db.commit()
    return {"message": "Expérience supprimée"}

# FORMATIONS
@app.get("/api/profil/formations", response_model=List[FormationResponse])
async def get_formations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    formations = db.query(Formation).filter(
        Formation.user_id == current_user.id
    ).order_by(Formation.date_debut.desc()).all()
    return formations

@app.post("/api/profil/formations", response_model=FormationResponse)
async def create_formation(
    formation: FormationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    new_formation = Formation(
        **formation.dict(),
        user_id=current_user.id
    )
    db.add(new_formation)
    db.commit()
    db.refresh(new_formation)
    return new_formation

# COMPÉTENCES
@app.get("/api/profil/competences", response_model=List[CompetenceResponse])
async def get_competences(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    competences = db.query(Competence).filter(
        Competence.user_id == current_user.id
    ).all()
    return competences

@app.post("/api/profil/competences", response_model=CompetenceResponse)
async def create_competence(
    competence: CompetenceCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    new_comp = Competence(
        **competence.dict(),
        user_id=current_user.id
    )
    db.add(new_comp)
    db.commit()
    db.refresh(new_comp)
    return new_comp

# OBJECTIFS
@app.get("/api/profil/objectifs", response_model=List[ObjectifCarriereResponse])
async def get_objectifs(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    objectifs = db.query(ObjectifCarriere).filter(
        ObjectifCarriere.user_id == current_user.id,
        ObjectifCarriere.actif == True
    ).all()
    return objectifs

@app.post("/api/profil/objectifs", response_model=ObjectifCarriereResponse)
async def create_objectif(
    objectif: ObjectifCarriereCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    new_obj = ObjectifCarriere(
        **objectif.dict(),
        user_id=current_user.id
    )
    db.add(new_obj)
    db.commit()
    db.refresh(new_obj)
    return new_obj

# ============================================
# ROUTES MONGODB POUR LES ARTICLES
# ============================================

@app.get("/api/articles")
async def get_articles(
    specialite: Optional[str] = Query(None),
    type_etude: Optional[str] = Query(None),
    source: Optional[str] = Query(None),
    limit: int = Query(20),
    skip: int = Query(0),
    current_user: User = Depends(get_current_user)
):
    try:
        filter_query = {}
        if specialite:
            filter_query["specialite"] = specialite
        if type_etude:
            filter_query["type_etude"] = type_etude
        if source:
            filter_query["source"] = source
        
        articles = list(articles_collection.find(
            filter_query,
            {
                "title": 1,
                "source": 1,
                "specialite": 1,
                "type_etude": 1,
                "publication_date": 1,
                "authors": 1,
                "resume_structure.resume_court": 1,
                "saved_by": 1
            }
        ).skip(skip).limit(limit))
        
        for article in articles:
            article["_id"] = str(article["_id"])
            article["is_saved"] = current_user.id in article.get("saved_by", [])
        
        return {
            "total": len(articles),
            "skip": skip,
            "limit": limit,
            "articles": articles
        }
    except Exception as e:
        raise HTTPException(500, detail=str(e))

@app.get("/api/articles/{article_id}")
async def get_article(
    article_id: str,
    current_user: User = Depends(get_current_user)
):
    try:
        article = articles_collection.find_one({"_id": ObjectId(article_id)})
        if not article:
            raise HTTPException(404, "Article non trouvé")
        
        articles_collection.update_one(
            {"_id": ObjectId(article_id)},
            {
                "$addToSet": {"viewed_by": current_user.id},
                "$inc": {"view_count": 1}
            }
        )
        
        article["_id"] = str(article["_id"])
        article["is_saved"] = current_user.id in article.get("saved_by", [])
        
        return article
    except Exception as e:
        raise HTTPException(400, detail=str(e))

@app.get("/api/stats")
async def get_stats(current_user: User = Depends(get_current_user)):
    try:
        total = articles_collection.count_documents({})
        
        specialites = list(articles_collection.aggregate([
            {"$group": {"_id": "$specialite", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]))
        
        return {
            "total_articles": total,
            "distribution_specialites": specialites
        }
    except Exception as e:
        raise HTTPException(500, detail=str(e))

@app.get("/api/search")
async def search_articles(
    q: str = Query(...),
    limit: int = Query(20),
    current_user: User = Depends(get_current_user)
):
    try:
        articles = list(articles_collection.find(
            {
                "$or": [
                    {"title": {"$regex": q, "$options": "i"}},
                    {"abstract": {"$regex": q, "$options": "i"}},
                    {"authors": {"$regex": q, "$options": "i"}}
                ]
            },
            {
                "title": 1,
                "source": 1,
                "specialite": 1,
                "publication_date": 1,
                "authors": 1,
                "resume_structure.resume_court": 1,
                "saved_by": 1
            }
        ).limit(limit))
        
        for article in articles:
            article["_id"] = str(article["_id"])
            article["is_saved"] = current_user.id in article.get("saved_by", [])
        
        return {
            "query": q,
            "total": len(articles),
            "articles": articles
        }
    except Exception as e:
        raise HTTPException(500, detail=str(e))

@app.post("/api/scrape")
async def scrape_articles(
    q: str = Query(...),
    source: str = Query("all"),
    max_results: int = Query(10),
    current_user: User = Depends(get_current_user)
):
    try:
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from app.curation_service import CurationService
        
        service = CurationService(mongo_uri="mongodb://admin:admin@localhost:27018/")
        
        articles = []
        if source == "all":
            articles = service.search_all_sources(query=q, max_per_source=max_results)
        elif source == "pubmed":
            pmids = service.pubmed.search(q, max_results=max_results)
            articles = service.pubmed.fetch_details(pmids) if pmids else []
        elif source == "europepmc":
            articles = service.europepmc.search_and_fetch(q, max_results=max_results)
        elif source == "biorxiv":
            articles = service.biorxiv.get_recent(server="biorxiv", days_back=30)
            articles = articles[:max_results]
        elif source == "medrxiv":
            articles = service.biorxiv.get_recent(server="medrxiv", days_back=30)
            articles = articles[:max_results]
        else:
            raise HTTPException(400, "Source invalide")
        
        for article in articles:
            article["scraped_by"] = current_user.id
            article["scraped_at"] = datetime.utcnow()
        
        saved_count = 0
        if articles:
            saved_count = service.save_articles(articles)
        
        apercu = []
        for article in articles[:5]:
            if article:
                apercu.append({
                    "title": article.get("title", ""),
                    "source": article.get("source", ""),
                    "doi": article.get("doi", ""),
                    "pmid": article.get("pmid", "")
                })
        
        return {
            "query": q,
            "source": source,
            "total_found": len(articles),
            "saved_new": saved_count,
            "articles_preview": apercu
        }
        
    except ImportError as e:
        raise HTTPException(500, detail=f"Erreur d'import: {str(e)}")
    except Exception as e:
        raise HTTPException(500, detail=str(e))

@app.get("/api/specialites")
async def get_specialites(current_user: User = Depends(get_current_user)):
    try:
        specialites = articles_collection.distinct("specialite")
        return {"specialites": [s for s in specialites if s]}
    except Exception as e:
        raise HTTPException(500, detail=str(e))

@app.get("/api/sources")
async def get_sources(current_user: User = Depends(get_current_user)):
    try:
        sources = articles_collection.distinct("source")
        return {"sources": [s for s in sources if s]}
    except Exception as e:
        raise HTTPException(500, detail=str(e))

@app.get("/api/feed")
async def get_personalized_feed(
    limit: int = Query(20),
    current_user: User = Depends(get_current_user)
):
    try:
        user_specialite = current_user.specialite.lower()
        
        if user_specialite in ["cardiologie", "cardio", "cardiovasculaire"]:
            filter_query = {
                "$or": [
                    {"specialite": {"$regex": "cardiologie|cardio|heart|cardiac", "$options": "i"}},
                    {"title": {"$regex": "heart|cardiac|myocardial|arrhythmia|ventricular", "$options": "i"}},
                    {"abstract": {"$regex": "heart|cardiac|myocardial|arrhythmia|ventricular", "$options": "i"}}
                ]
            }
        else:
            filter_query = {"specialite": {"$regex": user_specialite, "$options": "i"}}
        
        articles = list(articles_collection.find(
            filter_query,
            {
                "title": 1,
                "source": 1,
                "specialite": 1,
                "publication_date": 1,
                "authors": 1,
                "resume_structure.resume_court": 1
            }
        ).sort("publication_date", -1).limit(limit))
        
        for article in articles:
            article["_id"] = str(article["_id"])
        
        return {
            "specialite": current_user.specialite,
            "total": len(articles),
            "articles": articles
        }
    except Exception as e:
        print(f"❌ Erreur feed: {e}")
        raise HTTPException(500, detail=str(e))

@app.get("/api/recommendations")
async def get_recommendations(
    limit: int = Query(10),
    current_user: User = Depends(get_current_user)
):
    try:
        from app.recommendation_service import RecommendationService
        
        rec_service = RecommendationService()
        recommendations = rec_service.get_personalized_feed(
            user_id=current_user.id, 
            user_specialite=current_user.specialite,
            limit=limit
        )
        
        for article in recommendations:
            if "_id" in article:
                article["_id"] = str(article["_id"])
        
        return {
            "user_id": current_user.id,
            "specialite": current_user.specialite,
            "total": len(recommendations),
            "recommendations": recommendations
        }
    except Exception as e:
        print(f"❌ Erreur recommendations: {e}")
        raise HTTPException(500, detail=str(e))

# ============================================
# ROUTES POUR LE RÉSEAU DE COLLABORATION
# ============================================

@app.post("/api/orcid/link")
async def link_orcid_account(
    orcid_id: str = Query(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        from app.orcid_service import ORCIDService
        
        orcid_service = ORCIDService()
        profile = orcid_service.get_researcher_profile(orcid_id)
        
        if not profile:
            raise HTTPException(404, "Profil ORCID non trouvé")
        
        current_user.orcid_id = orcid_id
        db.commit()
        
        author_info = orcid_service.extract_author_info(profile)
        
        from app.models import Author
        existing_author = db.query(Author).filter(Author.orcid_id == orcid_id).first()
        if not existing_author:
            author = Author(
                orcid_id=orcid_id,
                nom=author_info['nom'],
                prenom=author_info['prenom'],
                institution=author_info['institution'],
                email=author_info['email'],
                research_fields=','.join(author_info['research_fields'])
            )
            db.add(author)
            db.commit()
        
        return {
            "message": "Compte ORCID lié avec succès",
            "author": author_info
        }
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        raise HTTPException(500, detail=str(e))

@app.post("/api/orcid/import-publications")
async def import_orcid_publications(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        if not current_user.orcid_id:
            raise HTTPException(400, "Aucun ORCID lié à ce compte")
        
        from app.orcid_service import ORCIDService
        from app.collaboration_service import CollaborationService
        from app.models import Author, AuthorArticle
        
        orcid_service = ORCIDService()
        publications = orcid_service.get_publications(current_user.orcid_id)
        
        author = db.query(Author).filter(Author.orcid_id == current_user.orcid_id).first()
        if not author:
            raise HTTPException(404, "Auteur non trouvé")
        
        saved_count = 0
        for pub in publications:
            if pub.get("doi"):
                existing = articles_collection.find_one({"doi": pub["doi"]})
                
                article_id = None
                if existing:
                    article_id = str(existing["_id"])
                else:
                    new_article = {
                        "title": pub["title"],
                        "doi": pub["doi"],
                        "source": "ORCID",
                        "authors": [f"{author.prenom} {author.nom}"],
                        "publication_date": str(pub.get("publication_date", {}).get("year", "")),
                        "imported_from_orcid": True,
                        "imported_by": current_user.id,
                        "date_import": datetime.utcnow()
                    }
                    result = articles_collection.insert_one(new_article)
                    article_id = str(result.inserted_id)
                
                if article_id:
                    existing_link = db.query(AuthorArticle).filter(
                        AuthorArticle.author_id == author.id,
                        AuthorArticle.article_doi == pub["doi"]
                    ).first()
                    
                    if not existing_link:
                        pub_date = None
                        if pub.get("publication_date", {}).get("year"):
                            try:
                                pub_date = datetime.strptime(pub["publication_date"]["year"], "%Y")
                            except:
                                pass
                        
                        author_article = AuthorArticle(
                            author_id=author.id,
                            article_id=article_id,
                            article_title=pub["title"],
                            article_doi=pub["doi"],
                            publication_date=pub_date,
                            is_corresponding=True
                        )
                        db.add(author_article)
                        saved_count += 1
        
        db.commit()
        
        collab_service = CollaborationService()
        collab_service.build_coauthor_graph(author.id, db, depth=3)
        
        return {
            "message": f"{saved_count} publications importées avec succès",
            "total": len(publications),
            "imported": saved_count
        }
        
    except Exception as e:
        raise HTTPException(500, detail=str(e))

@app.get("/api/network/suggestions")
async def get_collaboration_suggestions(
    limit: int = Query(5),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        from app.collaboration_service import CollaborationService
        from app.models import Author
        
        if not current_user.orcid_id:
            return {"suggestions": [], "message": "Liez d'abord votre compte ORCID"}
        
        author = db.query(Author).filter(Author.orcid_id == current_user.orcid_id).first()
        
        if not author:
            return {"suggestions": [], "message": "Auteur non trouvé"}
        
        collab_service = CollaborationService()
        suggestions = collab_service.suggest_collaborations(author.id, db, limit)
        
        return {"suggestions": suggestions}
        
    except Exception as e:
        print(f"❌ Erreur suggestions: {e}")
        return {"suggestions": [], "error": str(e)}

@app.get("/api/network/graph")
async def get_collaboration_graph(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        from app.collaboration_service import CollaborationService
        
        from app.models import Author
        author = db.query(Author).filter(Author.orcid_id == current_user.orcid_id).first()
        
        if not author:
            return {"nodes": [], "edges": []}
        
        collab_service = CollaborationService()
        graph = collab_service.get_collaboration_network(author.id, db)
        
        return graph
        
    except Exception as e:
        raise HTTPException(500, detail=str(e))

@app.get("/api/author/{author_id}", response_model=AuthorResponse)
async def get_author_profile(
    author_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        from app.models import Author
        author = db.query(Author).filter(Author.id == author_id).first()
        
        if not author:
            raise HTTPException(404, "Auteur non trouvé")
        
        return author
    except Exception as e:
        raise HTTPException(500, detail=str(e))

@app.get("/api/author/{author_id}/publications")
async def get_author_publications(
    author_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        from app.models import AuthorArticle
        
        publications = db.query(AuthorArticle).filter(
            AuthorArticle.author_id == author_id
        ).order_by(AuthorArticle.publication_date.desc()).all()
        
        return {
            "publications": [
                {
                    "title": pub.article_title,
                    "doi": pub.article_doi,
                    "publication_date": pub.publication_date.isoformat() if pub.publication_date else None
                }
                for pub in publications
            ]
        }
    except Exception as e:
        raise HTTPException(500, detail=str(e))

@app.get("/api/author/{author_id}/collaborators")
async def get_author_collaborators(
    author_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        from app.models import Collaboration, Author
        
        collaborations = db.query(Collaboration).filter(
            (Collaboration.author1_id == author_id) | (Collaboration.author2_id == author_id)
        ).all()
        
        collaborators = []
        for collab in collaborations:
            other_id = collab.author2_id if collab.author1_id == author_id else collab.author1_id
            other = db.query(Author).filter(Author.id == other_id).first()
            
            if other:
                collaborators.append({
                    "id": other.id,
                    "name": f"{other.prenom} {other.nom}",
                    "institution": other.institution,
                    "co_author_count": collab.co_author_count
                })
        
        return {"collaborators": collaborators}
    except Exception as e:
        raise HTTPException(500, detail=str(e))

# ============================================
# ROUTES POUR LA PHOTO DE PROFIL
# ============================================
import os
import shutil
from fastapi import UploadFile, File
from fastapi.responses import FileResponse
from pathlib import Path

# Configuration pour les uploads
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

@app.post("/api/profil/photo/upload")
async def upload_photo(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload une photo de profil
    """
    try:
        # Vérifier le type de fichier
        if not file.content_type.startswith("image/"):
            raise HTTPException(400, "Le fichier doit être une image")
        
        # Créer un nom de fichier unique
        file_extension = os.path.splitext(file.filename)[1]
        filename = f"user_{current_user.id}_{datetime.utcnow().timestamp()}{file_extension}"
        file_path = UPLOAD_DIR / filename
        
        # Sauvegarder le fichier
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Supprimer l'ancienne photo si elle existe
        from app.models import PhotoProfil
        old_photo = db.query(PhotoProfil).filter(
            PhotoProfil.user_id == current_user.id
        ).first()
        
        if old_photo:
            old_file_path = UPLOAD_DIR / old_photo.filename
            if old_file_path.exists():
                old_file_path.unlink()
            db.delete(old_photo)
            db.commit()
        
        # Créer la nouvelle entrée photo
        new_photo = PhotoProfil(
            user_id=current_user.id,
            filename=filename,
            file_path=str(file_path)
        )
        db.add(new_photo)
        db.commit()
        
        return {
            "message": "Photo uploadée avec succès",
            "filename": filename,
            "url": f"/api/profil/photo/{filename}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Erreur upload: {e}")
        raise HTTPException(500, detail=str(e))

@app.get("/api/profil/photo/{filename}")
async def get_photo(filename: str):
    """
    Récupère une photo de profil
    """
    file_path = UPLOAD_DIR / filename
    if not file_path.exists():
        raise HTTPException(404, "Photo non trouvée")
    
    return FileResponse(file_path)

@app.delete("/api/profil/photo")
async def delete_photo(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Supprime la photo de profil
    """
    from app.models import PhotoProfil
    
    photo = db.query(PhotoProfil).filter(
        PhotoProfil.user_id == current_user.id
    ).first()
    
    if not photo:
        raise HTTPException(404, "Aucune photo trouvée")
    
    file_path = UPLOAD_DIR / photo.filename
    if file_path.exists():
        file_path.unlink()
    
    db.delete(photo)
    db.commit()
    
    return {"message": "Photo supprimée avec succès"}

# ============================================
# ROUTES POUR LA PERSONNALISATION (SAUVEGARDE)
# ============================================

@app.post("/api/articles/{article_id}/save")
async def save_article(
    article_id: str,
    current_user: User = Depends(get_current_user)
):
    try:
        result = articles_collection.update_one(
            {"_id": ObjectId(article_id)},
            {"$addToSet": {"saved_by": current_user.id}}
        )
        
        if result.modified_count == 0 and result.matched_count == 0:
            raise HTTPException(404, "Article non trouvé")
        
        return {"message": "Article sauvegardé", "saved": True}
    except Exception as e:
        raise HTTPException(400, detail=str(e))

@app.post("/api/articles/{article_id}/unsave")
async def unsave_article(
    article_id: str,
    current_user: User = Depends(get_current_user)
):
    try:
        result = articles_collection.update_one(
            {"_id": ObjectId(article_id)},
            {"$pull": {"saved_by": current_user.id}}
        )
        
        if result.modified_count == 0 and result.matched_count == 0:
            raise HTTPException(404, "Article non trouvé")
        
        return {"message": "Article retiré des sauvegardes", "saved": False}
    except Exception as e:
        raise HTTPException(400, detail=str(e))

@app.get("/api/user/saved-articles")
async def get_saved_articles(
    current_user: User = Depends(get_current_user)
):
    try:
        articles = list(articles_collection.find(
            {"saved_by": current_user.id},
            {
                "title": 1,
                "source": 1,
                "specialite": 1,
                "type_etude": 1,
                "publication_date": 1,
                "authors": 1,
                "resume_structure.resume_court": 1
            }
        ).sort("publication_date", -1))
        
        for article in articles:
            article["_id"] = str(article["_id"])
            article["is_saved"] = True
        
        return {"articles": articles}
    except Exception as e:
        raise HTTPException(500, detail=str(e))

@app.get("/api/user/scraping-history")
async def get_scraping_history(
    current_user: User = Depends(get_current_user)
):
    try:
        articles = list(articles_collection.find(
            {"scraped_by": current_user.id},
            {
                "title": 1,
                "source": 1,
                "specialite": 1,
                "publication_date": 1,
                "scraped_at": 1
            }
        ).sort("scraped_at", -1).limit(50))
        
        for article in articles:
            article["_id"] = str(article["_id"])
        
        return {"history": articles}
    except Exception as e:
        raise HTTPException(500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)