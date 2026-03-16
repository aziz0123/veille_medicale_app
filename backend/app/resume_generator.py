from transformers import pipeline
import re
from datetime import datetime

class ResumeGenerator:
    """
    Générateur de résumés structurés pour articles médicaux
    """
    
    def __init__(self):
        print("🔄 Initialisation du générateur de résumés...")
        
        # Utiliser un modèle plus léger pour les résumés
        self.summarizer = pipeline(
            "summarization",
            model="facebook/bart-large-cnn",
            device=-1  # CPU
        )
        
        print("✅ Modèle de résumé chargé!")
    
    def generer_resume_structure(self, article):
        """
        Génère un résumé structuré de l'article
        """
        titre = article.get('title', '')
        abstract = article.get('abstract', '')
        
        # Combiner titre et résumé
        texte = f"Titre: {titre}\n\nRésumé: {abstract}"
        texte = texte[:1024]  # Limiter la longueur
        
        if len(texte) < 100:
            return {
                "resume_court": texte[:200],
                "population": "Non spécifié",
                "intervention": "Non spécifié",
                "resultats": "Non spécifié",
                "conclusion": "Non spécifié",
                "erreur": "Texte trop court"
            }
        
        try:
            # Générer un résumé court
            resume = self.summarizer(texte, max_length=150, min_length=50, do_sample=False)
            resume_court = resume[0]['summary_text']
            
            # Extraire les parties structurées (simplifié)
            population = self._extraire_population(texte)
            intervention = self._extraire_intervention(texte)
            resultats = self._extraire_resultats(texte)
            conclusion = self._extraire_conclusion(texte)
            
            return {
                "resume_court": resume_court,
                "population": population,
                "intervention": intervention,
                "resultats": resultats,
                "conclusion": conclusion,
                "date_generation": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            print(f"⚠️ Erreur génération résumé: {e}")
            return {
                "resume_court": abstract[:200] if abstract else "",
                "population": "Erreur",
                "intervention": "Erreur",
                "resultats": "Erreur",
                "conclusion": "Erreur",
                "erreur": str(e)
            }
    
    def _extraire_population(self, texte):
        """Extrait la population étudiée"""
        texte_lower = texte.lower()
        
        patterns = [
            r'(\d+)\s*(patients?|participants?|sujets?)',
            r'(adultes?|enfants?|personnes? âgées?)',
            r'(hommes?|femmes?|population)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, texte_lower)
            if match:
                return match.group(0)
        
        return "Non spécifié"
    
    def _extraire_intervention(self, texte):
        """Extrait l'intervention/traitement"""
        texte_lower = texte.lower()
        
        patterns = [
            r'(traitement|thérapie|intervention)\s*(par|avec)?\s*([a-z\s]+)',
            r'(administration|dose)\s*(de)?\s*([a-z\s]+)',
            r'(immunothérapie|chimiothérapie|radiothérapie)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, texte_lower)
            if match:
                return match.group(0)
        
        return "Non spécifié"
    
    def _extraire_resultats(self, texte):
        """Extrait les résultats principaux"""
        texte_lower = texte.lower()
        
        patterns = [
            r'(résultats?|conclusions?) (montrent?|indiquent?|suggèrent?) ([^.!?]+)',
            r'(amélioration|réduction|augmentation) ([^.!?]+)',
            r'(significatif|efficace) ([^.!?]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, texte_lower)
            if match:
                return match.group(0)
        
        return "Non spécifié"
    
    def _extraire_conclusion(self, texte):
        """Extrait la conclusion"""
        texte_lower = texte.lower()
        
        patterns = [
            r'(en conclusion|conclusion|finalement)[,.]?\s*([^.!?]+)',
            r'(ces résultats suggèrent|nos résultats indiquent) ([^.!?]+)',
            r'(cette étude démontre|cette étude montre) ([^.!?]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, texte_lower)
            if match:
                return match.group(0)
        
        # Si pas de conclusion explicite, prendre la dernière phrase
        phrases = re.split(r'[.!?]', texte)
        if len(phrases) > 1:
            return phrases[-2].strip()
        
        return "Non spécifié"