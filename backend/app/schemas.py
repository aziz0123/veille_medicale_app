# backend/app/schemas.py
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    nom: str
    prenom: str
    specialite: str
    institution: Optional[str] = None
    orcid_id: Optional[str] = None

class UserCreate(UserBase):
    password: str = Field(..., min_length=6)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

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

class PhotoProfilBase(BaseModel):
    filename: str
    file_path: str

class PhotoProfilResponse(PhotoProfilBase):
    id: int
    user_id: int
    uploaded_at: datetime
    
    class Config:
        from_attributes = True

class ProfilCompletResponse(UserResponse):
    experiences: List[ExperienceResponse] = []
    formations: List[FormationResponse] = []
    competences: List[CompetenceResponse] = []
    objectifs: List[ObjectifCarriereResponse] = []
    photo: Optional[PhotoProfilResponse] = None