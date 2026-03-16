// src/lib/api.ts
import { apiCall } from './auth';

export interface Article {
  _id: string;
  title: string;
  source: string;
  specialite?: string;
  type_etude?: string;
  publication_date?: string;
  authors?: string[];
  abstract?: string;
  pmid?: string;
  doi?: string;
  resume_structure?: {
    resume_court: string;
    population: string;
    intervention: string;
    resultats: string;
    conclusion: string;
  };
  // Nouveaux champs pour le suivi utilisateur
  viewed_by?: string[];        // IDs des utilisateurs qui ont consulté
  saved_by?: string[];         // IDs des utilisateurs qui ont sauvegardé
  scraped_by?: string;         // Utilisateur qui a lancé le scraping
  scraped_at?: string;         // Date du scraping
}

export interface StatsResponse {
  total_articles: number;
  distribution_specialites: Array<{ _id: string; count: number }>;
  distribution_sources: Array<{ _id: string; count: number }>;
  distribution_types_etude: Array<{ _id: string; count: number }>;
  articles_recents: Article[];
}

// Récupérer le feed personnalisé de l'utilisateur
export const getPersonalizedFeed = async (limit: number = 20) => {
  return apiCall(`/api/feed?limit=${limit}`);
};

// Récupérer les articles (avec filtres)
export const getArticles = async (params?: {
  specialite?: string;
  type_etude?: string;
  source?: string;
  limit?: number;
  skip?: number;
}) => {
  const queryString = new URLSearchParams(params as any).toString();
  return apiCall(`/api/articles?${queryString}`);
};

// Récupérer un article par son ID (marque comme vu)
export const getArticleById = async (id: string) => {
  return apiCall(`/api/articles/${id}`);
};

// Récupérer les statistiques
export const getStats = async () => {
  return apiCall('/api/stats');
};

// Rechercher des articles dans la base
export const searchArticles = async (query: string, limit?: number) => {
  return apiCall(`/api/search?q=${query}&limit=${limit || 20}`);
};

// Lancer un scraping dynamique (génère des résumés IA)
export const scrapeArticles = async (query: string, source?: string, maxResults?: number) => {
  return apiCall(`/api/scrape?q=${query}&source=${source || 'all'}&max_results=${maxResults || 10}`, {
    method: 'POST'
  });
};

// Sauvegarder un article dans "Mes articles"
export const saveArticle = async (articleId: string) => {
  return apiCall(`/api/articles/${articleId}/save`, { method: 'POST' });
};

// Retirer un article des sauvegardes
export const unsaveArticle = async (articleId: string) => {
  return apiCall(`/api/articles/${articleId}/unsave`, { method: 'POST' });
};

// Récupérer les articles sauvegardés par l'utilisateur
export const getSavedArticles = async () => {
  return apiCall('/api/user/saved-articles');
};

// Récupérer l'historique des scrapings de l'utilisateur
export const getUserScrapingHistory = async () => {
  return apiCall('/api/user/scraping-history');
};

// Récupérer les spécialités disponibles
export const getSpecialites = async () => {
  return apiCall('/api/specialites');
};

// Récupérer les sources disponibles
export const getSources = async () => {
  return apiCall('/api/sources');
};