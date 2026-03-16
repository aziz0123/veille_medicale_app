import requests
from datetime import datetime
import time

class EuropePMCClient:
    """
    Client pour Europe PMC API utilisant directement requests
    """
    
    def __init__(self):
        self.base_url = "https://www.ebi.ac.uk/europepmc/webservices/rest"
    
    def search_and_fetch(self, query, max_results=10):
        """
        Recherche et récupère les articles depuis Europe PMC
        """
        articles = []
        
        try:
            # URL de recherche
            url = f"{self.base_url}/search"
            params = {
                "query": query,
                "format": "json",
                "pageSize": max_results,
                "resultType": "core"
            }
            
            print(f"🌐 Appel API Europe PMC: {query}")
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                
                # Extraire les résultats
                if "resultList" in data and "result" in data["resultList"]:
                    for paper in data["resultList"]["result"]:
                        article = self._parse_paper(paper)
                        articles.append(article)
                    
                    print(f"🔍 Europe PMC: {len(articles)} articles trouvés")
            else:
                print(f"❌ Erreur Europe PMC: {response.status_code}")
            
            # Petit délai pour respecter les limites
            time.sleep(0.5)
            
        except Exception as e:
            print(f"❌ Erreur Europe PMC: {e}")
        
        return articles
    
    def _parse_paper(self, paper):
        """
        Convertit un résultat Europe PMC en format standardisé
        """
        return {
            "source": "EuropePMC",
            "pmid": paper.get("pmid", ""),
            "pmcid": paper.get("pmcid", ""),
            "doi": paper.get("doi", ""),
            "title": paper.get("title", ""),
            "abstract": paper.get("abstractText", ""),
            "authors": paper.get("authorString", "").split(", ") if paper.get("authorString") else [],
            "journal": paper.get("journalTitle", ""),
            "publication_date": paper.get("pubYear", ""),
            "cited_by": paper.get("citedByCount", 0),
            "date_import": datetime.utcnow()
        }