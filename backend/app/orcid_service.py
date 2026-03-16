# backend/app/orcid_service.py
import requests
from datetime import datetime
from typing import Optional, Dict, List

class ORCIDService:
    def __init__(self):
        self.base_url = "https://pub.orcid.org/v3.0"
        self.headers = {"Accept": "application/json"}
    
    def get_researcher_profile(self, orcid_id: str) -> Optional[Dict]:
        """Récupère le profil d'un chercheur"""
        try:
            response = requests.get(f"{self.base_url}/{orcid_id}", headers=self.headers)
            return response.json() if response.status_code == 200 else None
        except Exception as e:
            print(f"Erreur ORCID: {e}")
            return None
    
    def extract_author_info(self, profile: Dict) -> Dict:
        """Extrait les informations de l'auteur depuis le profil ORCID"""
        info = {
            "orcid_id": "",
            "nom": "",
            "prenom": "",
            "institution": "",
            "email": "",
            "research_fields": []
        }
        
        try:
            # Extraire l'ORCID
            info["orcid_id"] = profile.get("orcid", {}).get("path", "")
            
            # Extraire le nom
            person = profile.get("person", {})
            name = person.get("name", {})
            info["nom"] = name.get("family-name", {}).get("value", "")
            info["prenom"] = name.get("given-names", {}).get("value", "")
            
            # Extraire l'institution
            employments = person.get("employments", {}).get("employment-summary", [])
            if employments:
                org = employments[0].get("organization", {})
                info["institution"] = org.get("name", "")
            
            # Extraire les emails
            emails = person.get("emails", {}).get("email", [])
            if emails:
                info["email"] = emails[0].get("email", "")
            
            # Extraire les domaines de recherche
            keywords = person.get("keywords", {}).get("keyword", [])
            info["research_fields"] = [k.get("content", "") for k in keywords]
            
        except Exception as e:
            print(f"Erreur extraction: {e}")
        
        return info
    
    def get_publications(self, orcid_id: str) -> List[Dict]:
        """Récupère les publications d'un chercheur"""
        try:
            response = requests.get(f"{self.base_url}/{orcid_id}/works", headers=self.headers)
            if response.status_code != 200:
                return []
            
            data = response.json()
            publications = []
            for work in data.get("group", [])[:20]:
                summary = work.get("work-summary", [{}])[0]
                title = summary.get("title", {}).get("title", {}).get("value", "")
                pub_date = summary.get("publication-date", {})
                
                publications.append({
                    "title": title,
                    "year": pub_date.get("year", {}).get("value", ""),
                    "doi": self._extract_doi(summary)
                })
            return publications
        except Exception as e:
            print(f"Erreur publications: {e}")
            return []
    
    def _extract_doi(self, work_summary):
        """Extrait le DOI si présent"""
        for ext_id in work_summary.get("external-ids", {}).get("external-id", []):
            if ext_id.get("external-id-type") == "doi":
                return ext_id.get("external-id-value")
        return None