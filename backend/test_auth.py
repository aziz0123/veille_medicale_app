# backend/test_auth.py (version simplifiée)
from app.auth import get_password_hash, verify_password

# Test du hashage
password = "monMotDePasse123"
hashed = get_password_hash(password)
print(f"Mot de passe: {password}")
print(f"Hash: {hashed}")
print(f"Vérification: {verify_password(password, hashed)}")
print(f"Mauvais mot de passe: {verify_password('wrong', hashed)}")