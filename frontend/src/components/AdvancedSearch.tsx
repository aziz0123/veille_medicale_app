'use client';

import { useState } from 'react';
import { scrapeArticles } from '@/lib/api';
import { Search, Loader, Database, AlertCircle } from 'lucide-react';

interface AdvancedSearchProps {
  onScrapeComplete: () => void;
}

export default function AdvancedSearch({ onScrapeComplete }: AdvancedSearchProps) {
  const [query, setQuery] = useState('');
  const [source, setSource] = useState('all');
  const [maxResults, setMaxResults] = useState(10);
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSearch = async () => {
    if (!query.trim()) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const data = await scrapeArticles(query, source, maxResults);
      setResults(data);
      
      // Rafraîchir la liste des articles après le scraping
      if (data.saved_new > 0) {
        onScrapeComplete();
      }
    } catch (err) {
      setError('Erreur lors de la recherche');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
      <h2 className="text-xl font-bold text-gray-800 mb-4 flex items-center gap-2">
        <Database size={24} className="text-blue-600" />
        Recherche dynamique sur les sources scientifiques
      </h2>
      
      <div className="space-y-4">
        {/* Barre de recherche */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Termes de recherche
          </label>
          <div className="flex gap-2">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Ex: cancer immunotherapy, diabetes, COVID-19..."
              className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
            />
            <button
              onClick={handleSearch}
              disabled={loading || !query.trim()}
              className="bg-blue-600 hover:bg-blue-700 disabled:bg-blue-300 text-white px-6 py-2 rounded-lg flex items-center gap-2 transition-colors"
            >
              {loading ? (
                <Loader size={20} className="animate-spin" />
              ) : (
                <Search size={20} />
              )}
              Rechercher
            </button>
          </div>
        </div>
        
        {/* Options avancées */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Source
            </label>
            <select
              value={source}
              onChange={(e) => setSource(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
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
              value={maxResults}
              onChange={(e) => setMaxResults(Number(e.target.value))}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value={5}>5 articles</option>
              <option value={10}>10 articles</option>
              <option value={20}>20 articles</option>
              <option value={50}>50 articles</option>
            </select>
          </div>
        </div>
        
        {/* Résultats */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-start gap-3">
            <AlertCircle className="text-red-500 flex-shrink-0 mt-0.5" size={20} />
            <p className="text-red-700">{error}</p>
          </div>
        )}
        
        {results && (
          <div className="bg-green-50 border border-green-200 rounded-lg p-4">
            <p className="text-green-800 font-medium">
              ✅ Recherche terminée !
            </p>
            <p className="text-green-700 text-sm mt-1">
              {results.total_found} articles trouvés, {results.saved_new} nouveaux ajoutés à la base.
            </p>
            {results.articles && results.articles.length > 0 && (
              <div className="mt-3">
                <p className="text-sm font-medium text-green-800 mb-2">Aperçu des nouveaux articles :</p>
                <ul className="space-y-2">
                  {results.articles.map((article: any, idx: number) => (
                    <li key={idx} className="text-sm text-green-700 bg-white p-2 rounded">
                      {article.title}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}