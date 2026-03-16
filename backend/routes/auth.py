# backend/app/routes/auth.py
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import List

from app import models, schemas, auth
from app.database import SessionLocal, engine

# Créer les tables si elles n'existent pas
models.Base.metadata.create_all(bind=engine)

router = APIRouter(prefix="/auth", tags=["authentification"])

# Dépendance pour obtenir la session DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Route d'inscription
@router.post("/register", response_model=schemas.Token, status_code=status.HTTP_201_CREATED)
async def register(user_data: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Inscription d'un nouvel utilisateur
    """
    # Vérifier si l'email existe déjà
    existing_user = db.query(models.User).filter(models.User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Un compte avec cet email existe déjà"
        )
    
    # Vérifier si l'ORCID est déjà utilisé (si fourni)
    if user_data.orcid_id:
        existing_orcid = db.query(models.User).filter(models.User.orcid_id == user_data.orcid_id).first()
        if existing_orcid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cet ORCID est déjà associé à un compte"
            )
    
    # Hasher le mot de passe
    hashed_password = auth.get_password_hash(user_data.password)
    
    # Créer l'utilisateur
    new_user = models.User(
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
    
    # Créer le token JWT
    access_token_expires = timedelta(minutes=auth.settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": new_user.email, "specialite": new_user.specialite},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": new_user
    }

# Route de connexion
@router.post("/login", response_model=schemas.Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Connexion d'un utilisateur
    """
    # Chercher l'utilisateur par email
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    
    # Vérifier si l'utilisateur existe et le mot de passe est correct
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Compte désactivé"
        )
    
    # Mettre à jour la date de dernière connexion
    from datetime import datetime
    user.last_login = datetime.utcnow()
    db.commit()
    
    # Créer le token JWT
    access_token_expires = timedelta(minutes=auth.settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.email, "specialite": user.specialite},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }

# Route pour obtenir le profil de l'utilisateur connecté
@router.get("/me", response_model=schemas.UserResponse)
async def get_current_user(token: str = Depends(OAuth2PasswordBearer(tokenUrl="/auth/login")), db: Session = Depends(get_db)):
    """
    Récupère le profil de l'utilisateur connecté
    """
    payload = auth.decode_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide ou expiré",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    email = payload.get("sub")
    if not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Utilisateur non trouvé",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user