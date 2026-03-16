# backend/app/models.py
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

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
    
    def __repr__(self):
        return f"<User {self.email}>"

class Author(Base):
    __tablename__ = "authors"
    
    id = Column(Integer, primary_key=True, index=True)
    orcid_id = Column(String, unique=True, index=True, nullable=True)
    nom = Column(String, nullable=False)
    prenom = Column(String, nullable=False)
    institution = Column(String, nullable=True)
    email = Column(String, nullable=True)
    research_fields = Column(String, nullable=True)  # JSON string
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
    article_id = Column(String)  # MongoDB _id de l'article
    article_title = Column(String)
    article_doi = Column(String)
    publication_date = Column(DateTime)
    is_corresponding = Column(Boolean, default=False)
    # Ajoutez ces classes à votre models.py existant

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
    niveau = Column(Integer, nullable=True)  # 1-5
    categorie = Column(String, nullable=True)  # Technique, Linguistique, etc.
    
    user = relationship("User", back_populates="competences")

class ObjectifCarriere(Base):
    __tablename__ = "objectifs_carriere"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    titre = Column(String, nullable=False)
    description = Column(String, nullable=True)
    actif = Column(Boolean, default=True)
    
    user = relationship("User", back_populates="objectifs")

# Ajoutez ces relations à la classe User existante
User.experiences = relationship("Experience", back_populates="user", cascade="all, delete-orphan")
User.formations = relationship("Formation", back_populates="user", cascade="all, delete-orphan")
User.competences = relationship("Competence", back_populates="user", cascade="all, delete-orphan")
User.objectifs = relationship("ObjectifCarriere", back_populates="user", cascade="all, delete-orphan")  

class PhotoProfil(Base):
    __tablename__ = "photos_profil"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), unique=True)
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="photo")

# Ajoutez cette relation à la classe User
User.photo = relationship("PhotoProfil", back_populates="user", uselist=False, cascade="all, delete-orphan")