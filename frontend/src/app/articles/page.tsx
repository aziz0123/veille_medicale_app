// src/app/articles/page.tsx
'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { 
  getArticles, 
  getSpecialites, 
  getSources, 
  scrapeArticles,
  getPersonalizedFeed,
  saveArticle,
  unsaveArticle,
  Article,
} from '@/lib/api';
import { getUser, isAuthenticated, logout } from '@/lib/auth';
import { 
  Search, 
  Filter, 
  X, 
  Calendar, 
  User, 
  BookOpen, 
  Database, 
  Loader, 
  AlertCircle, 
  Globe,
  LogOut,
  Heart,
  Sparkles,
  TrendingUp
} from 'lucide-react';

export default function ArticlesPage() {
  const router = useRouter();
  const [currentUser, setCurrentUser] = useState<any>(null);
  const [mounted, setMounted] = useState(false);
  
  const [articles, setArticles] = useState<Article[]>([]);
  const [feed, setFeed] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // États pour les filtres
  const [selectedSpecialite, setSelectedSpecialite] = useState<string>('');
  const [selectedSource, setSelectedSource] = useState<string>('');
  const [searchQuery, setSearchQuery] = useState('');
  const [showFilters, setShowFilters] = useState(false);
  
  // Listes pour les filtres
  const [specialites, setSpecialites] = useState<string[]>([]);
  const [sources, setSources] = useState<string[]>([]);

  // États pour le scraping dynamique
  const [scrapeQuery, setScrapeQuery] = useState('');
  const [scrapeSource, setScrapeSource] = useState('all');
  const [scrapeMaxResults, setScrapeMaxResults] = useState(10);
  const [scraping, setScraping] = useState(false);
  const [scrapeResults, setScrapeResults] = useState<any>(null);
  const [scrapeError, setScrapeError] = useState<string | null>(null);
  const [showScrapePanel, setShowScrapePanel] = useState(false);

  // États pour les articles sauvegardés
  const [savedArticles, setSavedArticles] = useState<Set<string>>(new Set());

  // Pagination
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);
  const articlesPerPage = 20;

  // Initialisation côté client
  useEffect(() => {
    setMounted(true);
    setCurrentUser(getUser());
  }, []);

  // Rediriger si non authentifié
  useEffect(() => {
    if (mounted && !isAuthenticated()) {
      router.push('/login');
    }
  }, [mounted, router]);

  // Charger les données initiales
  useEffect(() => {
    if (!mounted || !currentUser) return;

    const fetchData = async () => {
      try {
        setLoading(true);
        setPage(1);
        
        // Construire les paramètres de filtre
        const params: any = { limit: articlesPerPage, skip: 0 };
        if (selectedSpecialite) params.specialite = selectedSpecialite;
        if (selectedSource) params.source = selectedSource;
        
        // Récupérer les articles
        const articlesData = await getArticles(params);
        setArticles(articlesData.articles || []);
        setHasMore(articlesData.articles.length === articlesPerPage);
        
        // Récupérer le feed personnalisé
        const feedData = await getPersonalizedFeed(10);
        setFeed(feedData);
        
        // Récupérer les listes pour les filtres
        const [specialitesData, sourcesData] = await Promise.all([
          getSpecialites(),
          getSources()
        ]);
        
        setSpecialites(specialitesData.specialites || []);
        setSources(sourcesData.sources || []);
        
      } catch (err) {
        setError('Erreur lors du chargement des articles');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [mounted, currentUser, selectedSpecialite, selectedSource]);

  // Charger plus d'articles (pagination)
  const loadMore = async () => {
    try {
      const params: any = { 
        limit: articlesPerPage, 
        skip: page * articlesPerPage 
      };
      if (selectedSpecialite) params.specialite = selectedSpecialite;
      if (selectedSource) params.source = selectedSource;
      
      const articlesData = await getArticles(params);
      if (articlesData.articles.length > 0) {
        setArticles(prev => [...prev, ...articlesData.articles]);
        setPage(prev => prev + 1);
        setHasMore(articlesData.articles.length === articlesPerPage);
      } else {
        setHasMore(false);
      }
    } catch (err) {
      console.error('Erreur chargement plus d\'articles:', err);
    }
  };

  // Fonction pour sauvegarder/retirer un article
  const toggleSaveArticle = async (articleId: string, event: React.MouseEvent) => {
    event.preventDefault();
    event.stopPropagation();
    
    try {
      if (savedArticles.has(articleId)) {
        await unsaveArticle(articleId);
        savedArticles.delete(articleId);
      } else {
        await saveArticle(articleId);
        savedArticles.add(articleId);
      }
      setSavedArticles(new Set(savedArticles));
    } catch (error) {
      console.error('Erreur lors de la sauvegarde:', error);
    }
  };

  // Fonction pour recharger les articles après scraping
  const refreshArticles = async () => {
    try {
      const params: any = { limit: articlesPerPage, skip: 0 };
      if (selectedSpecialite) params.specialite = selectedSpecialite;
      if (selectedSource) params.source = selectedSource;
      
      const articlesData = await getArticles(params);
      setArticles(articlesData.articles || []);
      setPage(1);
      setHasMore(articlesData.articles.length === articlesPerPage);
      
      // Recharger aussi le feed
      const feedData = await getPersonalizedFeed(10);
      setFeed(feedData);
    } catch (err) {
      console.error('Erreur lors du rafraîchissement:', err);
    }
  };

  // Fonction pour lancer le scraping
  const handleScrape = async () => {
    if (!scrapeQuery.trim()) return;
    
    setScraping(true);
    setScrapeError(null);
    setScrapeResults(null);
    
    try {
      console.log('🚀 Lancement scraping pour:', scrapeQuery);
      const result = await scrapeArticles(scrapeQuery, scrapeSource, scrapeMaxResults);
      console.log('✅ Résultat scraping:', result);
      setScrapeResults(result);
      
      // IMPORTANT: Rafraîchir les articles pour voir les nouveaux
      await refreshArticles();
      
    } catch (err: any) {
      console.error('❌ Erreur scraping:', err);
      let errorMessage = 'Erreur lors du scraping';
      
      if (err.response) {
        const status = err.response.status;
        const data = err.response.data;
        
        if (status === 422) {
          errorMessage = 'Paramètres de recherche invalides';
        } else if (data?.detail) {
          errorMessage = typeof data.detail === 'string' ? data.detail : JSON.stringify(data.detail);
        }
      } else if (err.request) {
        errorMessage = 'Le serveur ne répond pas';
      } else {
        errorMessage = err.message || errorMessage;
      }
      
      setScrapeError(errorMessage);
    } finally {
      setScraping(false);
    }
  };

  // Filtrer par recherche client-side
  const filteredArticles = articles.filter(article => {
    if (!searchQuery) return true;
    const query = searchQuery.toLowerCase();
    return (
      article.title?.toLowerCase().includes(query) ||
      article.abstract?.toLowerCase().includes(query) ||
      article.authors?.some(author => author.toLowerCase().includes(query))
    );
  });

  // Réinitialiser tous les filtres
  const resetFilters = () => {
    setSelectedSpecialite('');
    setSelectedSource('');
    setSearchQuery('');
  };

  // Déconnexion
  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    router.push('/login');
  };

  if (!mounted || !currentUser) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-lg text-gray-600">Chargement...</p>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-lg text-gray-600">Chargement de vos articles...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="bg-white p-8 rounded-lg shadow-lg text-center">
          <p className="text-red-500 text-xl mb-4">❌ {error}</p>
          <button
            onClick={handleLogout}
            className="text-blue-600 hover:underline"
          >
            Retour à la connexion
          </button>
        </div>
      </div>
    );
  }

  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* En-tête avec infos utilisateur */}
      <div className="bg-gradient-to-r from-blue-600 to-indigo-700 text-white sticky top-0 z-50 shadow-lg">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div>
              <Link href="/" className="text-white/80 hover:text-white mb-1 inline-block">
                ← Dashboard
              </Link>
              <h1 className="text-2xl font-bold flex items-center gap-2">
                <BookOpen size={28} />
                Articles médicaux
              </h1>
              <p className="text-white/80 text-sm">
                Dr. {currentUser.prenom} {currentUser.nom} - {currentUser.specialite}
              </p>
            </div>
            <div className="flex gap-2">
              <button
                onClick={() => setShowScrapePanel(!showScrapePanel)}
                className="bg-green-600 hover:bg-green-700 px-3 py-2 rounded-lg flex items-center gap-2 text-sm transition-colors"
              >
                <Globe size={18} />
                {showScrapePanel ? 'Masquer' : 'Recherche dynamique'}
              </button>
              <button
                onClick={() => setShowFilters(!showFilters)}
                className="bg-white/10 hover:bg-white/20 px-3 py-2 rounded-lg flex items-center gap-2 text-sm transition-colors"
              >
                <Filter size={18} />
                {showFilters ? 'Masquer' : 'Filtres'}
              </button>
              <button
                onClick={handleLogout}
                className="bg-red-600 hover:bg-red-700 px-3 py-2 rounded-lg flex items-center gap-2 text-sm transition-colors"
              >
                <LogOut size={18} />
                Déconnexion
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="container mx-auto px-4 py-6">
        {/* Section Résultats du scraping */}
        {scrapeResults && (
          <div className="bg-green-50 border-l-4 border-green-500 rounded-lg p-4 mb-6 animate-pulse">
            <div className="flex items-start gap-3">
              <div className="bg-green-500 rounded-full p-1">
                <TrendingUp className="text-white" size={16} />
              </div>
              <div>
                <p className="font-medium text-green-800">
                  ✅ {scrapeResults.saved_new} nouveaux articles ajoutés !
                </p>
                <p className="text-sm text-green-700 mt-1">
                  {scrapeResults.total_found} articles trouvés au total. 
                  Les nouveaux apparaissent ci-dessous.
                </p>
              </div>
              <button
                onClick={() => setScrapeResults(null)}
                className="ml-auto text-green-700 hover:text-green-900"
              >
                <X size={18} />
              </button>
            </div>
          </div>
        )}

        {/* Panneau de scraping dynamique */}
        {showScrapePanel && (
          <div className="bg-white rounded-lg shadow-lg p-6 mb-6 border-2 border-green-200">
            <h2 className="text-xl font-bold text-gray-800 mb-4 flex items-center gap-2">
              <Database size={24} className="text-green-600" />
              Rechercher de nouveaux articles
            </h2>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Termes de recherche
                </label>
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={scrapeQuery}
                    onChange={(e) => setScrapeQuery(e.target.value)}
                    placeholder="Ex: cardiology, heart failure, arrhythmia..."
                    className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
                    onKeyPress={(e) => e.key === 'Enter' && handleScrape()}
                  />
                  <button
                    onClick={handleScrape}
                    disabled={scraping || !scrapeQuery.trim()}
                    className="bg-green-600 hover:bg-green-700 disabled:bg-green-300 text-white px-6 py-2 rounded-lg flex items-center gap-2 transition-colors"
                  >
                    {scraping ? (
                      <Loader size={20} className="animate-spin" />
                    ) : (
                      <Search size={20} />
                    )}
                    Rechercher
                  </button>
                </div>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Source
                  </label>
                  <select
                    value={scrapeSource}
                    onChange={(e) => setScrapeSource(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
                  >
                    <option value="all">Toutes les sources</option>
                    <option value="pubmed">PubMed</option>
                    <option value="europepmc">Europe PMC</option>
                    <option value="biorxiv">bioRxiv</option>
                    <option value="medrxiv">medRxiv</option>
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Nombre de résultats
                  </label>
                  <select
                    value={scrapeMaxResults}
                    onChange={(e) => setScrapeMaxResults(Number(e.target.value))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
                  >
                    <option value={5}>5 articles</option>
                    <option value={10}>10 articles</option>
                    <option value={20}>20 articles</option>
                    <option value={50}>50 articles</option>
                  </select>
                </div>
              </div>
              
              {scrapeError && (
                <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-start gap-3">
                  <AlertCircle className="text-red-500 flex-shrink-0 mt-0.5" size={20} />
                  <p className="text-red-700">{scrapeError}</p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Feed personnalisé amélioré */}
        {feed && feed.articles && feed.articles.length > 0 && (
          <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg shadow-lg p-6 mb-6 border-l-4 border-blue-500">
            <h2 className="text-xl font-bold text-gray-800 mb-4 flex items-center gap-2">
              <Sparkles className="text-blue-600" />
              Recommandé pour vous - Spécialité: {currentUser.specialite}
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {feed.articles.slice(0, 4).map((article: Article) => (
                <Link
                  key={article._id}
                  href={`/articles/${article._id}`}
                  className="block p-4 bg-white rounded-lg border border-blue-100 hover:border-blue-300 transition-colors shadow-sm hover:shadow"
                >
                  <div className="flex items-center gap-2 mb-2">
                    <span className="bg-blue-100 text-blue-700 text-xs font-medium px-2 py-1 rounded">
                      {article.source}
                    </span>
                    {article.specialite && (
                      <span className="bg-green-100 text-green-700 text-xs font-medium px-2 py-1 rounded">
                        {article.specialite}
                      </span>
                    )}
                  </div>
                  <h3 className="font-semibold text-gray-800 mb-2 line-clamp-2">
                    {article.title}
                  </h3>
                  <p className="text-sm text-gray-500">
                    {article.publication_date}
                  </p>
                </Link>
              ))}
            </div>
          </div>
        )}

        {/* Barre de recherche */}
        <div className="mb-4">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
            <input
              type="text"
              placeholder="Rechercher dans les articles..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
        </div>

        {/* Filtres */}
        {showFilters && (
          <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-gray-800">Filtres</h2>
              <button
                onClick={resetFilters}
                className="text-sm text-gray-500 hover:text-gray-700 flex items-center gap-1"
              >
                <X size={16} />
                Réinitialiser
              </button>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Spécialité
                </label>
                <select
                  value={selectedSpecialite}
                  onChange={(e) => setSelectedSpecialite(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">Toutes les spécialités</option>
                  {specialites.map(s => (
                    <option key={s} value={s}>{s}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Source
                </label>
                <select
                  value={selectedSource}
                  onChange={(e) => setSelectedSource(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">Toutes les sources</option>
                  {sources.map(s => (
                    <option key={s} value={s}>{s}</option>
                  ))}
                </select>
              </div>
            </div>

            {(selectedSpecialite || selectedSource) && (
              <div className="mt-4 pt-4 border-t border-gray-200">
                <p className="text-sm text-gray-600">
                  Filtres actifs : 
                  {selectedSpecialite && (
                    <span className="ml-2 inline-flex items-center gap-1 bg-blue-100 text-blue-700 px-2 py-1 rounded">
                      {selectedSpecialite}
                      <button onClick={() => setSelectedSpecialite('')}>
                        <X size={14} />
                      </button>
                    </span>
                  )}
                  {selectedSource && (
                    <span className="ml-2 inline-flex items-center gap-1 bg-green-100 text-green-700 px-2 py-1 rounded">
                      {selectedSource}
                      <button onClick={() => setSelectedSource('')}>
                        <X size={14} />
                      </button>
                    </span>
                  )}
                </p>
              </div>
            )}
          </div>
        )}

        {/* Résultats */}
        <div className="mb-4 flex items-center justify-between">
          <p className="text-gray-600">
            {filteredArticles.length} article{filteredArticles.length > 1 ? 's' : ''} affiché{filteredArticles.length > 1 ? 's' : ''}
          </p>
          {selectedSpecialite !== currentUser.specialite && (
            <button
              onClick={() => setSelectedSpecialite(currentUser.specialite)}
              className="text-sm text-blue-600 hover:text-blue-800 flex items-center gap-1"
            >
              <Sparkles size={16} />
              Voir ma spécialité ({currentUser.specialite})
            </button>
          )}
        </div>

        {/* Grille d'articles */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredArticles.map((article) => (
            <div key={article._id} className="relative group">
              <Link
                href={`/articles/${article._id}`}
                className="block bg-white rounded-lg shadow-lg overflow-hidden hover:shadow-xl transition-shadow"
              >
                <div className="p-6">
                  <div className="flex items-center gap-2 mb-3">
                    <span className="bg-blue-100 text-blue-700 text-xs font-medium px-2 py-1 rounded">
                      {article.source}
                    </span>
                    {article.specialite && (
                      <span className={`text-xs font-medium px-2 py-1 rounded ${
                        article.specialite === currentUser?.specialite 
                          ? 'bg-green-200 text-green-800 font-bold border border-green-300' 
                          : 'bg-green-100 text-green-700'
                      }`}>
                        {article.specialite}
                        {article.specialite === currentUser?.specialite && ' ★'}
                      </span>
                    )}
                  </div>

                  <h3 className="font-semibold text-gray-800 mb-3 line-clamp-2 group-hover:text-blue-600 transition-colors">
                    {article.title}
                  </h3>

                  {article.resume_structure?.resume_court && (
                    <p className="text-gray-600 text-sm mb-4 line-clamp-3">
                      {article.resume_structure.resume_court}
                    </p>
                  )}

                  <div className="flex items-center justify-between text-sm text-gray-500">
                    {article.publication_date && (
                      <span className="flex items-center gap-1">
                        <Calendar size={14} />
                        {article.publication_date}
                      </span>
                    )}
                    {article.authors && article.authors.length > 0 && (
                      <span className="flex items-center gap-1 truncate ml-2">
                        <User size={14} />
                        {article.authors[0].split(' ').pop()}
                        {article.authors.length > 1 && ' et al.'}
                      </span>
                    )}
                  </div>
                </div>
              </Link>
              
              {/* Bouton de sauvegarde */}
              <button
                onClick={(e) => toggleSaveArticle(article._id, e)}
                className="absolute top-2 right-2 p-2 bg-white rounded-full shadow-md hover:shadow-lg transition-shadow opacity-0 group-hover:opacity-100"
              >
                <Heart 
                  className={savedArticles.has(article._id) ? "text-red-500 fill-current" : "text-gray-400 hover:text-red-500"} 
                  size={20} 
                />
              </button>
            </div>
          ))}
        </div>

        {/* Bouton Load More */}
        {hasMore && filteredArticles.length >= articlesPerPage && (
          <div className="text-center mt-8">
            <button
              onClick={loadMore}
              className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-medium transition-colors shadow-md hover:shadow-lg"
            >
              Charger plus d'articles
            </button>
          </div>
        )}

        {/* Message si aucun résultat */}
        {filteredArticles.length === 0 && (
          <div className="text-center py-12">
            <p className="text-gray-500 text-lg">Aucun article trouvé</p>
            <button
              onClick={resetFilters}
              className="mt-4 text-blue-600 hover:underline"
            >
              Réinitialiser les filtres
            </button>
          </div>
        )}
      </div>
    </main>
  );
}