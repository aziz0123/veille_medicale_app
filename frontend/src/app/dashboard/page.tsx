// src/app/dashboard/page.tsx
'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { getUser, logout, apiCall } from '@/lib/auth';
import { 
  LogOut, 
  BookOpen, 
  BarChart3, 
  Search, 
  User, 
  Bell, 
  Loader,
  Sparkles,
  TrendingUp,
  Clock,
  Star,
  Users,
  Award,
  Globe
} from 'lucide-react';

// Composant pour les recommandations
function Recommendations() {
  const [recommendations, setRecommendations] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchRecommendations = async () => {
      try {
        const data = await apiCall('/api/recommendations?limit=6');
        setRecommendations(data.recommendations || []);
      } catch (error) {
        console.error('Erreur recommandations:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchRecommendations();
  }, []);

  if (loading) {
    return (
      <div className="flex justify-center py-4">
        <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-purple-600"></div>
      </div>
    );
  }

  if (recommendations.length === 0) {
    return null;
  }

  return (
    <div className="bg-gradient-to-r from-purple-50 to-pink-50 rounded-lg shadow-lg p-6 mb-6 border-l-4 border-purple-500">
      <h2 className="text-xl font-bold text-gray-800 mb-4 flex items-center gap-2">
        <Sparkles className="text-purple-600" />
        Recommandé pour vous
      </h2>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {recommendations.map((article, index) => (
          <Link
            key={`${article._id}-${index}`}  // ← CORRECTION : ajout de l'index pour garantir l'unicité
            href={`/articles/${article._id}`}
            className="block p-4 bg-white rounded-lg border border-purple-100 hover:border-purple-300 transition-colors shadow-sm hover:shadow"
          >
            <div className="flex items-center gap-2 mb-2">
              <span className="bg-purple-100 text-purple-700 text-xs font-medium px-2 py-1 rounded">
                {article.source}
              </span>
              <span className="bg-green-100 text-green-700 text-xs font-medium px-2 py-1 rounded">
                {article.specialite || 'Général'}
              </span>
            </div>
            <h3 className="font-semibold text-gray-800 mb-2 line-clamp-2">
              {article.title}
            </h3>
            {article.resume_structure?.resume_court && (
              <p className="text-gray-600 text-sm mb-3 line-clamp-2">
                {article.resume_structure.resume_court}
              </p>
            )}
            <div className="flex items-center justify-between text-xs text-gray-500">
              <span className="flex items-center gap-1">
                <Clock size={12} />
                {article.publication_date || 'Date inconnue'}
              </span>
              {article.authors && article.authors.length > 0 && (
                <span className="flex items-center gap-1 truncate ml-2">
                  <User size={12} />
                  {article.authors[0].split(' ').pop()}
                  {article.authors.length > 1 && ' et al.'}
                </span>
              )}
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}

// Composant pour les articles récents
function RecentArticles() {
  const [recent, setRecent] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchRecent = async () => {
      try {
        const data = await apiCall('/api/articles?limit=5');
        setRecent(data.articles || []);
      } catch (error) {
        console.error('Erreur articles récents:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchRecent();
  }, []);

  if (loading) {
    return (
      <div className="flex justify-center py-4">
        <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (recent.length === 0) {
    return null;
  }

  return (
    <div className="bg-white rounded-lg shadow-lg p-6 mt-6">
      <h2 className="text-xl font-bold text-gray-800 mb-4 flex items-center gap-2">
        <TrendingUp className="text-blue-600" />
        Articles récents
      </h2>
      <div className="space-y-3">
        {recent.map((article, index) => (
          <Link
            key={`${article._id}-${index}`}  // ← CORRECTION : ajout de l'index pour garantir l'unicité
            href={`/articles/${article._id}`}
            className="block p-3 border rounded-lg hover:border-blue-300 transition-colors"
          >
            <div className="flex items-center gap-2 mb-1">
              <span className="bg-blue-100 text-blue-700 text-xs font-medium px-2 py-0.5 rounded">
                {article.source}
              </span>
              {article.specialite && (
                <span className="bg-green-100 text-green-700 text-xs font-medium px-2 py-0.5 rounded">
                  {article.specialite}
                </span>
              )}
            </div>
            <h3 className="font-medium text-gray-800 line-clamp-1">{article.title}</h3>
            <p className="text-xs text-gray-500 mt-1">{article.publication_date}</p>
          </Link>
        ))}
      </div>
    </div>
  );
}

export default function DashboardPage() {
  const router = useRouter();
  const [user, setUser] = useState<any>(null);
  const [feed, setFeed] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [mounted, setMounted] = useState(false);

  // S'assurer que le composant est monté côté client
  useEffect(() => {
    setMounted(true);
    const currentUser = getUser();
    setUser(currentUser);
    
    const fetchFeed = async () => {
      try {
        const data = await apiCall('/api/feed?limit=10');
        setFeed(data);
      } catch (error) {
        console.error('Erreur feed:', error);
      } finally {
        setLoading(false);
      }
    };

    if (currentUser) {
      fetchFeed();
    }
  }, []);

  const handleLogout = () => {
    logout();
  };

  // Ne rien rendre pendant le rendu serveur ou avant le montage
  if (!mounted) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-lg text-gray-600">Chargement...</p>
        </div>
      </div>
    );
  }

  if (!user) {
    return null; // Le AuthGuard va rediriger
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-lg text-gray-600">Chargement de votre dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Navbar */}
      <nav className="bg-white shadow-lg sticky top-0 z-50">
        <div className="container mx-auto px-4">
          <div className="flex justify-between items-center h-16">
            <Link href="/dashboard" className="flex items-center gap-2 hover:opacity-80 transition-opacity">
              <BookOpen className="text-blue-600" size={24} />
              <span className="font-bold text-xl text-gray-800">Veille Médicale</span>
            </Link>
            
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2 bg-blue-50 px-3 py-1.5 rounded-full">
                <User size={16} className="text-blue-600" />
                <span className="text-sm font-medium text-gray-700">
                  Dr. {user.prenom} {user.nom}
                </span>
              </div>
              <button
                onClick={handleLogout}
                className="flex items-center gap-2 text-gray-600 hover:text-red-600 transition-colors bg-gray-100 hover:bg-red-50 px-3 py-1.5 rounded-full"
                title="Déconnexion"
              >
                <LogOut size={18} />
                <span className="hidden sm:inline text-sm">Déconnexion</span>
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* Main content */}
      <div className="container mx-auto px-4 py-8">
        {/* En-tête de bienvenue */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-800">
            Bonjour, {user.prenom} 👋
          </h1>
          <p className="text-gray-600 mt-1">
            Spécialité: <span className="font-medium text-blue-600">{user.specialite}</span>
          </p>
          {user.orcid_id && (
            <p className="text-sm text-gray-500 mt-1 flex items-center gap-1">
              <Award size={14} className="text-green-600" />
              ORCID: {user.orcid_id}
            </p>
          )}
        </div>

        {/* Cartes d'actions rapides */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4 mb-8">
          <Link href="/articles" className="bg-white rounded-lg shadow-lg p-6 hover:shadow-xl transition-all hover:scale-105">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-500 text-sm">Explorer</p>
                <p className="text-2xl font-bold text-gray-800">Articles</p>
              </div>
              <div className="bg-blue-100 p-3 rounded-full">
                <BookOpen className="text-blue-600" size={24} />
              </div>
            </div>
          </Link>

          <Link href="/stats" className="bg-white rounded-lg shadow-lg p-6 hover:shadow-xl transition-all hover:scale-105">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-500 text-sm">Analyser</p>
                <p className="text-2xl font-bold text-gray-800">Statistiques</p>
              </div>
              <div className="bg-green-100 p-3 rounded-full">
                <BarChart3 className="text-green-600" size={24} />
              </div>
            </div>
          </Link>

          <Link href="/articles?search=true" className="bg-white rounded-lg shadow-lg p-6 hover:shadow-xl transition-all hover:scale-105">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-500 text-sm">Recherche</p>
                <p className="text-2xl font-bold text-gray-800">Dynamique</p>
              </div>
              <div className="bg-purple-100 p-3 rounded-full">
                <Search className="text-purple-600" size={24} />
              </div>
            </div>
          </Link>

          <Link href="/saved" className="bg-white rounded-lg shadow-lg p-6 hover:shadow-xl transition-all hover:scale-105">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-500 text-sm">Mes</p>
                <p className="text-2xl font-bold text-gray-800">Favoris</p>
              </div>
              <div className="bg-yellow-100 p-3 rounded-full">
                <Star className="text-yellow-600" size={24} />
              </div>
            </div>
          </Link>

          <Link href="/network" className="bg-white rounded-lg shadow-lg p-6 hover:shadow-xl transition-all hover:scale-105">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-500 text-sm">Mon</p>
                <p className="text-2xl font-bold text-gray-800">Réseau</p>
              </div>
              <div className="bg-indigo-100 p-3 rounded-full">
                <Users className="text-indigo-600" size={24} />
              </div>
            </div>
          </Link>
        </div>

        {/* Section des recommandations */}
        <Recommendations />

        {/* Grille à deux colonnes pour le feed et les articles récents */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Feed personnalisé - prend 2 colonnes sur grand écran */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-lg shadow-lg p-6 h-full">
              <h2 className="text-xl font-bold text-gray-800 mb-4 flex items-center gap-2">
                <Bell className="text-blue-600" />
                Votre feed personnalisé - {user.specialite}
              </h2>
              
              {feed?.articles?.length > 0 ? (
                <div className="space-y-4">
                  {feed.articles.map((article: any, index: number) => (
                    <Link
                      key={`${article._id}-${index}`}  // ← CORRECTION : ajout de l'index
                      href={`/articles/${article._id}`}
                      className="block p-4 border rounded-lg hover:border-blue-300 transition-colors hover:bg-blue-50/30"
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
                      <h3 className="font-semibold text-gray-800 mb-2">{article.title}</h3>
                      {article.resume_structure?.resume_court && (
                        <p className="text-gray-600 text-sm mb-2 line-clamp-2">
                          {article.resume_structure.resume_court}
                        </p>
                      )}
                      <div className="flex items-center gap-2 text-sm text-gray-500">
                        <span>{article.publication_date}</span>
                        {article.authors && article.authors.length > 0 && (
                          <>
                            <span>•</span>
                            <span>{article.authors[0].split(' ').pop()}
                              {article.authors.length > 1 && ' et al.'}
                            </span>
                          </>
                        )}
                      </div>
                    </Link>
                  ))}
                </div>
              ) : (
                <div className="text-center py-12">
                  <p className="text-gray-500 mb-4">
                    Aucun article trouvé pour votre spécialité.
                  </p>
                  <Link
                    href="/articles?search=true"
                    className="inline-flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors"
                  >
                    <Search size={18} />
                    Rechercher des articles
                  </Link>
                </div>
              )}
            </div>
          </div>

          {/* Articles récents - prend 1 colonne */}
          <div className="lg:col-span-1">
            <RecentArticles />
            
            {/* Lien rapide vers le réseau */}
            {!user.orcid_id && (
              <div className="bg-gradient-to-r from-indigo-50 to-purple-50 rounded-lg shadow-lg p-6 mt-6 border-l-4 border-indigo-500">
                <h3 className="font-semibold text-gray-800 mb-2 flex items-center gap-2">
                  <Globe className="text-indigo-600" size={20} />
                  Connectez votre ORCID
                </h3>
                <p className="text-sm text-gray-600 mb-4">
                  Liez votre compte ORCID pour découvrir votre réseau de collaborateurs.
                </p>
                <Link
                  href="/network"
                  className="inline-flex items-center gap-2 bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg text-sm transition-colors"
                >
                  <Users size={16} />
                  Configurer
                </Link>
              </div>
            )}
          </div>
        </div>

        {/* Footer */}
        <div className="mt-8 text-center text-sm text-gray-500">
          <p>© 2026 Veille Médicale - Plateforme de veille scientifique personnalisée</p>
        </div>
      </div>
    </div>
  );
}