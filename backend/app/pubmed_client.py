import requests
import xml.etree.ElementTree as ET
from datetime import datetime
import time

class PubMedClient:
    """
    Client pour récupérer des articles depuis PubMed via E-utilities API
    Documentation: https://eutils.ncbi.nlm.nih.gov/entrez/eutils/
    """
    
    def __init__(self, email="votre.email@example.com", api_key=None):
        """
        Initialise le client PubMed
        - email: OBLIGATOIRE pour utiliser NCBI (donne une priorité plus élevée)
        - api_key: optionnel mais recommandé pour plus de requêtes
        """
        self.base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
        self.email = email
        self.api_key = api_key
        self.headers = {"User-Agent": "VeilleMedicale/1.0"}
    
    def search(self, query, max_results=10, sort="relevance"):
        """
        Recherche des articles PubMed
        - query: termes de recherche (ex: "cancer immunotherapy")
        - max_results: nombre maximum de résultats
        - sort: "relevance" ou "pub_date"
        Retourne: liste d'IDs PubMed
        """
        params = {
            "db": "pubmed",
            "term": query,
            "retmax": max_results,
            "retmode": "json",
            "sort": sort,
            "email": self.email
        }
        
        if self.api_key:
            params["api_key"] = self.api_key
        
        url = self.base_url + "esearch.fcgi"
        response = requests.get(url, params=params, headers=self.headers)
        
        if response.status_code == 200:
            data = response.json()
            id_list = data["esearchresult"]["idlist"]
            print(f"🔍 PubMed: {len(id_list)} articles trouvés pour '{query}'")
            return id_list
        else:
            print(f"❌ Erreur PubMed search: {response.status_code}")
            return []
    
    def fetch_details(self, pmid_list):
        """
        Récupère les détails complets des articles par leurs IDs
        """
        if not pmid_list:
            return []
        
        # Convertir la liste en string séparé par des virgules
        ids = ",".join(pmid_list)
        
        params = {
            "db": "pubmed",
            "id": ids,
            "retmode": "xml",
            "email": self.email
        }
        
        if self.api_key:
            params["api_key"] = self.api_key
        
        url = self.base_url + "efetch.fcgi"
        response = requests.get(url, params=params, headers=self.headers)
        
        articles = []
        if response.status_code == 200:
            # Parser le XML
            root = ET.fromstring(response.content)
            
            for article in root.findall(".//PubmedArticle"):
                article_data = self._parse_article_xml(article)
                articles.append(article_data)
            
            print(f"📥 Détails récupérés pour {len(articles)} articles")
        else:
            print(f"❌ Erreur PubMed fetch: {response.status_code}")
        
        # Respecter la limite de requêtes (3 par seconde sans API key)
        time.sleep(0.34)
        
        return articles
    
    def _parse_article_xml(self, article_elem):
        """
        Parse un élément XML d'article PubMed
        """
        # Extraction du PMID
        pmid_elem = article_elem.find(".//PMID")
        pmid = pmid_elem.text if pmid_elem is not None else ""
        
        # Extraction du titre
        title_elem = article_elem.find(".//ArticleTitle")
        title = title_elem.text if title_elem is not None else ""
        
        # Extraction du résumé
        abstract_elems = article_elem.findall(".//AbstractText")
        abstract_parts = []
        for abs_elem in abstract_elems:
            if abs_elem.text:
                abstract_parts.append(abs_elem.text)
        abstract = " ".join(abstract_parts)
        
        # Extraction de la date de publication
        pub_date = self._extract_publication_date(article_elem)
        
        # Extraction des auteurs
        authors = []
        author_elems = article_elem.findall(".//Author")
        for author in author_elems:
            last = author.find("LastName")
            fore = author.find("ForeName")
            if last is not None and fore is not None:
                authors.append(f"{fore.text} {last.text}")
        
        # Extraction du journal
        journal_elem = article_elem.find(".//Title")
        journal = journal_elem.text if journal_elem is not None else ""
        
        # Extraction des mots-clés MeSH
        mesh_terms = []
        mesh_elems = article_elem.findall(".//MeshHeading/DescriptorName")
        for mesh in mesh_elems:
            if mesh.text:
                mesh_terms.append(mesh.text)
        
        return {
            "source": "PubMed",
            "pmid": pmid,
            "doi": self._extract_doi(article_elem),
            "title": title,
            "abstract": abstract,
            "authors": authors,
            "journal": journal,
            "publication_date": pub_date,
            "mesh_terms": mesh_terms,
            "date_import": datetime.utcnow(),
            "raw_xml": ET.tostring(article_elem, encoding='unicode')  # Sauvegarde brute
        }
    
    def _extract_publication_date(self, article_elem):
        """Extrait la date de publication"""
        pub_date_elem = article_elem.find(".//PubDate")
        if pub_date_elem is not None:
            year = pub_date_elem.find("Year")
            month = pub_date_elem.find("Month")
            day = pub_date_elem.find("Day")
            
            date_parts = []
            if year is not None:
                date_parts.append(year.text)
            if month is not None and month.text:
                # Convertir les mois en chiffres si nécessaire
                month_map = {
                    "Jan": "01", "Feb": "02", "Mar": "03", "Apr": "04",
                    "May": "05", "Jun": "06", "Jul": "07", "Aug": "08",
                    "Sep": "09", "Oct": "10", "Nov": "11", "Dec": "12"
                }
                month_text = month.text
                if month_text in month_map:
                    date_parts.append(month_map[month_text])
                else:
                    date_parts.append(month_text)
            if day is not None and day.text:
                date_parts.append(day.text)
            
            return "-".join(date_parts)
        return None
    
    def _extract_doi(self, article_elem):
        """Extrait le DOI si présent"""
        article_ids = article_elem.findall(".//ArticleId")
        for id_elem in article_ids:
            if id_elem.get("IdType") == "doi":
                return id_elem.text
        return None