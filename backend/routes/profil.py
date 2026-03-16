# backend/app/routes/profil.py
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
import shutil
import os  
from pathlib import Path
from app import models, schemas
from app.auth import get_current_user
from app.database import get_db

router = APIRouter(prefix="/api/profil", tags=["profil"])

# ============================================
# PROFIL COMPLET
# ============================================

@router.get("/complet", response_model=schemas.ProfilCompletResponse)
async def get_profil_complet(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Récupère le profil complet de l'utilisateur
    """
    # Recharger l'utilisateur avec toutes ses relations
    user = db.query(models.User).filter(models.User.id == current_user.id).first()
    return user

# ============================================
# EXPÉRIENCES
# ============================================

@router.get("/experiences", response_model=List[schemas.ExperienceResponse])
async def get_experiences(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Récupère toutes les expériences de l'utilisateur"""
    experiences = db.query(models.Experience).filter(
        models.Experience.user_id == current_user.id
    ).order_by(models.Experience.date_debut.desc()).all()
    return experiences

@router.post("/experiences", response_model=schemas.ExperienceResponse)
async def create_experience(
    experience: schemas.ExperienceCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Ajoute une nouvelle expérience"""
    new_exp = models.Experience(
        **experience.dict(),
        user_id=current_user.id
    )
    db.add(new_exp)
    db.commit()
    db.refresh(new_exp)
    return new_exp

@router.put("/experiences/{exp_id}", response_model=schemas.ExperienceResponse)
async def update_experience(
    exp_id: int,
    experience: schemas.ExperienceCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Modifie une expérience"""
    exp = db.query(models.Experience).filter(
        models.Experience.id == exp_id,
        models.Experience.user_id == current_user.id
    ).first()
    if not exp:
        raise HTTPException(404, "Expérience non trouvée")
    
    for key, value in experience.dict().items():
        setattr(exp, key, value)
    
    db.commit()
    db.refresh(exp)
    return exp

@router.delete("/experiences/{exp_id}")
async def delete_experience(
    exp_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Supprime une expérience"""
    exp = db.query(models.Experience).filter(
        models.Experience.id == exp_id,
        models.Experience.user_id == current_user.id
    ).first()
    if not exp:
        raise HTTPException(404, "Expérience non trouvée")
    
    db.delete(exp)
    db.commit()
    return {"message": "Expérience supprimée"}

# ============================================
# FORMATIONS
# ============================================

@router.get("/formations", response_model=List[schemas.FormationResponse])
async def get_formations(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Récupère toutes les formations"""
    formations = db.query(models.Formation).filter(
        models.Formation.user_id == current_user.id
    ).order_by(models.Formation.date_debut.desc()).all()
    return formations

@router.post("/formations", response_model=schemas.FormationResponse)
async def create_formation(
    formation: schemas.FormationCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Ajoute une formation"""
    new_formation = models.Formation(
        **formation.dict(),
        user_id=current_user.id
    )
    db.add(new_formation)
    db.commit()
    db.refresh(new_formation)
    return new_formation

# ============================================
# COMPÉTENCES
# ============================================

@router.get("/competences", response_model=List[schemas.CompetenceResponse])
async def get_competences(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Récupère toutes les compétences"""
    competences = db.query(models.Competence).filter(
        models.Competence.user_id == current_user.id
    ).all()
    return competences

@router.post("/competences", response_model=schemas.CompetenceResponse)
async def create_competence(
    competence: schemas.CompetenceCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Ajoute une compétence"""
    new_comp = models.Competence(
        **competence.dict(),
        user_id=current_user.id
    )
    db.add(new_comp)
    db.commit()
    db.refresh(new_comp)
    return new_comp

# ============================================
# OBJECTIFS DE CARRIÈRE
# ============================================

@router.get("/objectifs", response_model=List[schemas.ObjectifCarriereResponse])
async def get_objectifs(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Récupère les objectifs de carrière"""
    objectifs = db.query(models.ObjectifCarriere).filter(
        models.ObjectifCarriere.user_id == current_user.id,
        models.ObjectifCarriere.actif == True
    ).all()
    return objectifs

@router.post("/objectifs", response_model=schemas.ObjectifCarriereResponse)
async def create_objectif(
    objectif: schemas.ObjectifCarriereCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Ajoute un objectif de carrière"""
    new_obj = models.ObjectifCarriere(
        **objectif.dict(),
        user_id=current_user.id
    )
    db.add(new_obj)
    db.commit()
    db.refresh(new_obj)
    return new_obj

# Configuration pour les uploads
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

@router.post("/photo/upload")
async def upload_photo(
    file: UploadFile = File(...),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload une photo de profil
    """
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
    old_photo = db.query(models.PhotoProfil).filter(
        models.PhotoProfil.user_id == current_user.id
    ).first()
    
    if old_photo:
        old_file_path = UPLOAD_DIR / old_photo.filename
        if old_file_path.exists():
            old_file_path.unlink()
        db.delete(old_photo)
        db.commit()
    
    # Créer la nouvelle entrée photo
    new_photo = models.PhotoProfil(
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

@router.get("/photo/{filename}")
async def get_photo(filename: str):
    """
    Récupère une photo de profil
    """
    file_path = UPLOAD_DIR / filename
    if not file_path.exists():
        raise HTTPException(404, "Photo non trouvée")
    
    from fastapi.responses import FileResponse
    return FileResponse(file_path)

@router.delete("/photo")
async def delete_photo(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Supprime la photo de profil
    """
    photo = db.query(models.PhotoProfil).filter(
        models.PhotoProfil.user_id == current_user.id
    ).first()
    
    if not photo:
        raise HTTPException(404, "Aucune photo trouvée")
    
    file_path = UPLOAD_DIR / photo.filename
    if file_path.exists():
        file_path.unlink()
    
    db.delete(photo)
    db.commit()
    
    return {"message": "Photo supprimée avec succès"}