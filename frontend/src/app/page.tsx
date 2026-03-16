// src/app/page.tsx
'use client';

import { useEffect, useState } from 'react';
import { getStats, StatsResponse } from '@/lib/api';
import Link from 'next/link';
import { 
  BarChart3, 
  BookOpen, 
  Database, 
  FileText, 
  TrendingUp,
  ArrowRight 
} from 'lucide-react';

export default function Home() {
  const [stats, setStats] = useState<StatsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const data = await getStats();
        setStats(data);
      } catch (err) {
        setError('Erreur de chargement des statistiques');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-lg text-gray-600">Chargement de vos articles médicaux...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="bg-white p-8 rounded-lg shadow-lg text-center">
          <p className="text-red-500 text-xl mb-4">❌ {error}</p>
          <p className="text-gray-600">Vérifie que le backend tourne sur http://localhost:8000</p>
        </div>
      </div>
    );
  }

  const colors = [
    'bg-blue-500', 'bg-green-500', 'bg-purple-500', 
    'bg-pink-500', 'bg-yellow-500', 'bg-indigo-500'
  ];

  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Hero Section */}
      <div className="bg-gradient-to-r from-blue-600 to-indigo-700 text-white">
        <div className="container mx-auto px-4 py-16">
          <h1 className="text-5xl font-bold mb-4 flex items-center gap-3">
            <BookOpen size={48} />
            Veille Médicale IA
          </h1>
          <p className="text-xl opacity-90 max-w-2xl">
            Plateforme intelligente de curation et veille scientifique médicale
          </p>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="container mx-auto px-4 py-12">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
          <div className="bg-white rounded-lg shadow-lg p-6 transform hover:scale-105 transition-transform">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-500 text-sm">Total Articles</p>
                <p className="text-3xl font-bold text-gray-800">{stats?.total_articles || 0}</p>
              </div>
              <div className="bg-blue-100 p-3 rounded-full">
                <Database className="text-blue-600" size={24} />
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-lg p-6 transform hover:scale-105 transition-transform">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-500 text-sm">Sources</p>
                <p className="text-3xl font-bold text-gray-800">{stats?.distribution_sources.length || 0}</p>
              </div>
              <div className="bg-green-100 p-3 rounded-full">
                <FileText className="text-green-600" size={24} />
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-lg p-6 transform hover:scale-105 transition-transform">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-500 text-sm">Spécialités</p>
                <p className="text-3xl font-bold text-gray-800">{stats?.distribution_specialites.length || 0}</p>
              </div>
              <div className="bg-purple-100 p-3 rounded-full">
                <BarChart3 className="text-purple-600" size={24} />
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-lg p-6 transform hover:scale-105 transition-transform">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-500 text-sm">Types d'étude</p>
                <p className="text-3xl font-bold text-gray-800">{stats?.distribution_types_etude.length || 0}</p>
              </div>
              <div className="bg-pink-100 p-3 rounded-full">
                <TrendingUp className="text-pink-600" size={24} />
              </div>
            </div>
          </div>
        </div>

        {/* Distribution par spécialité */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-12">
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-xl font-bold mb-4 text-gray-800">📊 Distribution par Spécialité</h2>
            <div className="space-y-3">
              {stats?.distribution_specialites.map((item, index) => (
                <div key={item._id} className="flex items-center">
                  <span className="w-32 text-gray-600">{item._id || 'Non classifié'}</span>
                  <div className="flex-1 mx-4">
                    <div className="bg-gray-200 rounded-full h-4 overflow-hidden">
                      <div 
                        className={`${colors[index % colors.length]} h-full rounded-full`}
                        style={{ width: `${(item.count / stats.total_articles) * 100}%` }}
                      ></div>
                    </div>
                  </div>
                  <span className="text-sm font-semibold text-gray-700">{item.count}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Distribution par source */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-xl font-bold mb-4 text-gray-800">📚 Distribution par Source</h2>
            <div className="space-y-3">
              {stats?.distribution_sources.map((item, index) => (
                <div key={item._id} className="flex items-center">
                  <span className="w-32 text-gray-600">{item._id || 'Inconnue'}</span>
                  <div className="flex-1 mx-4">
                    <div className="bg-gray-200 rounded-full h-4 overflow-hidden">
                      <div 
                        className={`${colors[index % colors.length]} h-full rounded-full`}
                        style={{ width: `${(item.count / stats.total_articles) * 100}%` }}
                      ></div>
                    </div>
                  </div>
                  <span className="text-sm font-semibold text-gray-700">{item.count}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Articles récents */}
        <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
          <h2 className="text-xl font-bold mb-4 text-gray-800">🆕 Articles Récents</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {stats?.articles_recents.map((article) => (
              <Link 
                href={`/articles/${article._id}`} 
                key={article._id}
                className="block p-4 border rounded-lg hover:shadow-md transition-shadow hover:border-blue-300"
              >
                <h3 className="font-semibold text-gray-800 mb-2 line-clamp-2">{article.title}</h3>
                <div className="flex items-center gap-2 text-sm text-gray-500">
                  <span className="bg-blue-100 text-blue-700 px-2 py-1 rounded">
                    {article.source}
                  </span>
                  {article.specialite && (
                    <span className="bg-green-100 text-green-700 px-2 py-1 rounded">
                      {article.specialite}
                    </span>
                  )}
                </div>
              </Link>
            ))}
          </div>
        </div>

        {/* Call to Action */}
        <div className="text-center">
          <Link 
            href="/articles"
            className="inline-flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-8 rounded-lg transition-colors shadow-lg"
          >
            Voir tous les articles
            <ArrowRight size={20} />
          </Link>
        </div>
      </div>
    </main>
  );
}