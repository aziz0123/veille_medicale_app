// frontend/src/app/network/page.tsx
'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { getUser, apiCall } from '@/lib/auth';
import NetworkGraph from '@/components/NetworkGraph';
import { 
  Users, 
  UserPlus, 
  Share2, 
  ArrowLeft, 
  Loader, 
  Github,
  Mail,
  Building2,
  Award,
  BookOpen,
  ExternalLink,
  Search,
  Filter,
  Edit
} from 'lucide-react';

export default function NetworkPage() {
  const router = useRouter();
  const [user, setUser] = useState<any>(null);
  const [orcidLinked, setOrcidLinked] = useState(false);
  const [suggestions, setSuggestions] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [orcidId, setOrcidId] = useState('');
  const [activeTab, setActiveTab] = useState('network');
  const [importing, setImporting] = useState(false);
  const [importMessage, setImportMessage] = useState('');
  const [showOrcidForm, setShowOrcidForm] = useState(false); // Nouvel état

  useEffect(() => {
    const currentUser = getUser();
    setUser(currentUser);
    if (currentUser?.orcid_id) {
      setOrcidLinked(true);
    }
    fetchNetworkData();
  }, []);

  const fetchNetworkData = async () => {
    try {
      const data = await apiCall('/api/network/suggestions');
      setSuggestions(data.suggestions || []);
    } catch (error) {
      console.error('Erreur réseau:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleLinkOrcid = async () => {
    if (!orcidId.trim()) return;
    
    try {
      const result = await apiCall(`/api/orcid/link?orcid_id=${orcidId}`, { method: 'POST' });
      setOrcidLinked(true);
      setUser({ ...user, orcid_id: orcidId });
      localStorage.setItem('user', JSON.stringify({ ...user, orcid_id: orcidId }));
      setShowOrcidForm(false); // Cacher le formulaire après liaison
      fetchNetworkData();
    } catch (error) {
      console.error('Erreur liaison ORCID:', error);
    }
  };

  const handleImportPublications = async () => {
    setImporting(true);
    setImportMessage('');
    
    try {
      const result = await apiCall('/api/orcid/import-publications', { method: 'POST' });
      setImportMessage(`✅ ${result.message}`);
      fetchNetworkData();
    } catch (error: any) {
      setImportMessage(`❌ Erreur: ${error.message}`);
    } finally {
      setImporting(false);
    }
  };

  const handleDisconnectOrcid = () => {
    // Optionnel : Appeler une API pour déconnecter l'ORCID
    setUser({ ...user, orcid_id: null });
    localStorage.setItem('user', JSON.stringify({ ...user, orcid_id: null }));
    setOrcidLinked(false);
    setShowOrcidForm(true);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Navigation */}
      <nav className="bg-white shadow-lg sticky top-0 z-50">
        <div className="container mx-auto px-4">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-4">
              <Link href="/dashboard" className="text-gray-600 hover:text-gray-900">
                <ArrowLeft size={24} />
              </Link>
              <h1 className="text-2xl font-bold text-gray-800 flex items-center gap-2">
                <Users className="text-blue-600" />
                Réseau de collaboration
              </h1>
            </div>

            {/* Tabs */}
            <div className="flex gap-2">
              <button
                onClick={() => setActiveTab('network')}
                className={`px-4 py-2 rounded-lg transition-colors ${
                  activeTab === 'network'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                Mon réseau
              </button>
              <button
                onClick={() => setActiveTab('suggestions')}
                className={`px-4 py-2 rounded-lg transition-colors ${
                  activeTab === 'suggestions'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                Suggestions
              </button>
            </div>
          </div>
        </div>
      </nav>

      <div className="container mx-auto px-4 py-8">
        {/* Formulaire ORCID - affiché si pas d'ORCID ou si on clique sur "Changer" */}
        {(!user?.orcid_id && !orcidLinked) || showOrcidForm ? (
          // Section liaison ORCID
          <div className="max-w-2xl mx-auto mb-8">
            <div className="bg-white rounded-2xl shadow-xl p-8">
              <div className="text-center mb-8">
                <div className="bg-blue-100 w-20 h-20 rounded-full flex items-center justify-center mx-auto mb-4">
                  <Github size={40} className="text-blue-600" />
                </div>
                <h2 className="text-2xl font-bold text-gray-800 mb-2">
                  Connectez votre ORCID
                </h2>
                <p className="text-gray-600">
                  Liez votre identifiant ORCID pour découvrir votre réseau de collaborateurs et recevoir des suggestions personnalisées.
                </p>
              </div>

              <div className="flex gap-4">
                <input
                  type="text"
                  value={orcidId}
                  onChange={(e) => setOrcidId(e.target.value)}
                  placeholder="0000-0001-2345-6789"
                  className="flex-1 px-4 py-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <button
                  onClick={handleLinkOrcid}
                  className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg flex items-center gap-2 font-medium transition-colors"
                >
                  <UserPlus size={20} />
                  Lier ORCID
                </button>
              </div>

              {showOrcidForm && (
                <button
                  onClick={() => setShowOrcidForm(false)}
                  className="mt-4 text-sm text-gray-500 hover:text-gray-700"
                >
                  Annuler
                </button>
              )}

              <p className="text-xs text-gray-500 mt-4 text-center">
                Vous n'avez pas d'ORCID ?{' '}
                <a
                  href="https://orcid.org/register"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-600 hover:underline inline-flex items-center gap-1"
                >
                  Créez-en un gratuitement
                  <ExternalLink size={12} />
                </a>
              </p>
            </div>
          </div>
        ) : null}

        {user?.orcid_id && orcidLinked && !showOrcidForm && (
          <>
            {activeTab === 'network' && (
              // Vue réseau
              <div className="space-y-6">
                {/* Barre d'actions ORCID avec bouton pour changer */}
                <div className="bg-white rounded-lg shadow-lg p-4 flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <Award className="text-green-600" size={24} />
                    <div>
                      <p className="text-sm text-gray-600">ORCID connecté</p>
                      <p className="text-sm font-mono text-gray-800">{user.orcid_id}</p>
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <button
                      onClick={() => setShowOrcidForm(true)}
                      className="bg-gray-100 hover:bg-gray-200 text-gray-700 px-3 py-2 rounded-lg flex items-center gap-1 text-sm transition-colors"
                    >
                      <Edit size={14} />
                      Changer
                    </button>
                    <button
                      onClick={handleImportPublications}
                      disabled={importing}
                      className="bg-green-600 hover:bg-green-700 disabled:bg-green-300 text-white px-4 py-2 rounded-lg flex items-center gap-2 text-sm transition-colors"
                    >
                      {importing ? (
                        <Loader size={16} className="animate-spin" />
                      ) : (
                        <BookOpen size={16} />
                      )}
                      Importer mes publications
                    </button>
                  </div>
                </div>

                {importMessage && (
                  <div className={`p-4 rounded-lg ${
                    importMessage.startsWith('✅') ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'
                  }`}>
                    {importMessage}
                  </div>
                )}

                {/* Informations utilisateur */}
                <div className="bg-white rounded-lg shadow-lg p-6">
                  <div className="flex items-start justify-between">
                    <div>
                      <h2 className="text-xl font-bold text-gray-800 mb-2">
                        Votre réseau de collaborateurs
                      </h2>
                      <p className="text-gray-600">
                        Explorez les connexions entre vous et vos co-auteurs. 
                        Plus la connexion est épaisse, plus vous avez collaboré.
                      </p>
                    </div>
                    <Link
                      href={`/network/${user?.id}`}
                      className="bg-blue-100 hover:bg-blue-200 text-blue-700 px-4 py-2 rounded-lg transition-colors"
                    >
                      Voir mon profil
                    </Link>
                  </div>
                </div>

                {/* Graphe de collaboration */}
                <div className="bg-white rounded-lg shadow-lg p-6">
                  <NetworkGraph />
                </div>
              </div>
            )}

            {activeTab === 'suggestions' && (
              // Suggestions de collaboration
              <div className="space-y-6">
                <div className="bg-white rounded-lg shadow-lg p-6">
                  <h2 className="text-xl font-bold text-gray-800 mb-4 flex items-center gap-2">
                    <UserPlus className="text-green-600" />
                    Suggestions de collaboration
                  </h2>
                  
                  {suggestions.length > 0 ? (
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {suggestions.map((suggestion, idx) => (
                        <Link
                          key={idx}
                          href={`/network/${suggestion.author_id}`}
                          className="block border rounded-lg p-5 hover:shadow-lg transition-shadow bg-white"
                        >
                          <div className="flex items-start justify-between mb-3">
                            <div>
                              <h3 className="font-semibold text-gray-800 text-lg">
                                {suggestion.name}
                              </h3>
                              <p className="text-sm text-gray-600 flex items-center gap-1 mt-1">
                                <Building2 size={14} />
                                {suggestion.institution || 'Institution non renseignée'}
                              </p>
                            </div>
                            <div className="bg-green-100 text-green-700 text-xs font-medium px-2 py-1 rounded-full">
                              Score: {suggestion.score}
                            </div>
                          </div>

                          {suggestion.orcid_id && (
                            <p className="text-xs text-gray-500 mb-3 flex items-center gap-1">
                              <Award size={12} />
                              ORCID: {suggestion.orcid_id}
                            </p>
                          )}

                          {suggestion.mutual_connections && suggestion.mutual_connections.length > 0 && (
                            <div className="mb-4">
                              <p className="text-xs text-gray-500 mb-1">Connaissances en commun :</p>
                              <div className="flex flex-wrap gap-1">
                                {suggestion.mutual_connections.map((conn: string, i: number) => (
                                  <span
                                    key={i}
                                    className="text-xs bg-gray-100 text-gray-700 px-2 py-1 rounded"
                                  >
                                    {conn}
                                  </span>
                                ))}
                              </div>
                            </div>
                          )}
                        </Link>
                      ))}
                    </div>
                  ) : (
                    <div className="text-center py-12">
                      <p className="text-gray-500 mb-4">
                        Aucune suggestion pour le moment.
                      </p>
                      <p className="text-sm text-gray-400">
                        Importez vos publications pour recevoir des suggestions personnalisées.
                      </p>
                    </div>
                  )}
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}