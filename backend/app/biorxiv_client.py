import requests
from datetime import datetime, timedelta

class BioRxivClient:
    """
    Client pour bioRxiv API (prépublications)
    API: https://api.biorxiv.org/
    """
    
    def __init__(self):
        self.base_url = "https://api.biorxiv.org/"
    
    def get_recent(self, server="biorxiv", days_back=7, max_results=50):
        """
        Récupère les articles récents de bioRxiv ou medRxiv
        - server: "biorxiv" ou "medrxiv"
        - days_back: nombre de jours en arrière
        """
        # Date de début
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        # Format: YYYY-MM-DD
        start_str = start_date.strftime("%Y-%m-%d")
        end_str = end_date.strftime("%Y-%m-%d")
        
        # API endpoint: https://api.biorxiv.org/details/{server}/{start}/{end}/{cursor}
        url = f"{self.base_url}details/{server}/{start_str}/{end_str}/0"
        
        articles = []
        try:
            response = requests.get(url)
            data = response.json()
            
            if data["messages"][0]["status"] == "ok":
                collection = data["collection"]
                
                for item in collection[:max_results]:
                    article = self._parse_item(item, server)
                    articles.append(article)
                
                print(f"🔍 {server}: {len(articles)} articles récents trouvés")
            
        except Exception as e:
            print(f"❌ Erreur {server}: {e}")
        
        return articles
    
    def _parse_item(self, item, server):
        """
        Parse un élément bioRxiv/medRxiv
        """
        return {
            "source": server,
            "doi": item.get("doi", ""),
            "title": item.get("title", ""),
            "abstract": item.get("abstract", ""),
            "authors": item.get("authors", "").split("; "),
            "category": item.get("category", ""),
            "publication_date": item.get("date", ""),
            "version": item.get("version", ""),
            "link_pdf": f"https://www.{server}.org/content/{item.get('doi')}.pdf",
            "date_import": datetime.utcnow()
        }