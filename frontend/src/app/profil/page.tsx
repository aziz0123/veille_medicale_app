// frontend/src/app/profil/page.tsx
'use client';

import { useEffect, useState, useRef } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { getUser, apiCall } from '@/lib/auth';
import { 
  User, 
  Briefcase, 
  GraduationCap, 
  Award, 
  Target,
  MapPin,
  Calendar,
  Edit,
  Plus,
  Trash2,
  Save,
  X,
  Mail,
  Camera,
  Loader,
  Building,
  CheckCircle,
  XCircle,
  Upload,
  AlertCircle,
  Check
} from 'lucide-react';

interface Experience {
  id: number;
  titre: string;
  entreprise: string;
  lieu?: string;
  date_debut: string;
  date_fin?: string;
  description?: string;
  en_cours: boolean;
}

interface Formation {
  id: number;
  diplome: string;
  etablissement: string;
  domaine?: string;
  date_debut: string;
  date_fin?: string;
  description?: string;
}

interface Competence {
  id: number;
  nom: string;
  niveau?: number;
  categorie?: string;
}

interface Objectif {
  id: number;
  titre: string;
  description?: string;
  actif: boolean;
}

interface Photo {
  id: number;
  filename: string;
  file_path: string;
  uploaded_at: string;
}

interface UserProfile {
  id: number;
  email: string;
  nom: string;
  prenom: string;
  specialite: string;
  institution?: string;
  orcid_id?: string;
  experiences: Experience[];
  formations: Formation[];
  competences: Competence[];
  objectifs: Objectif[];
  photo?: Photo;
}

export default function ProfilPage() {
  const router = useRouter();
  const [user, setUser] = useState<any>(null);
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [uploadingPhoto, setUploadingPhoto] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [uploadSuccess, setUploadSuccess] = useState(false);
  const [editing, setEditing] = useState<string | null>(null);
  const [formData, setFormData] = useState<any>({});
  const [showModal, setShowModal] = useState(false);
  const [modalType, setModalType] = useState<'experience' | 'formation' | 'competence' | 'objectif'>('experience');
  const [modalError, setModalError] = useState<string | null>(null);
  const [modalLoading, setModalLoading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    const currentUser = getUser();
    if (!currentUser) {
      router.push('/login');
      return;
    }
    setUser(currentUser);
    fetchProfile();
  }, []);

  const fetchProfile = async () => {
    setLoading(true);
    try {
      const data = await apiCall('/api/profil/complet');
      setProfile(data);
    } catch (error) {
      console.error('Erreur chargement profil:', error);
    } finally {
      setLoading(false);
    }
  };

  const handlePhotoUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    // Validation du fichier
    if (!file.type.startsWith('image/')) {
      setUploadError('Le fichier doit être une image');
      setTimeout(() => setUploadError(null), 3000);
      return;
    }

    if (file.size > 5 * 1024 * 1024) {
      setUploadError('L\'image ne doit pas dépasser 5 Mo');
      setTimeout(() => setUploadError(null), 3000);
      return;
    }

    setUploadingPhoto(true);
    setUploadError(null);
    setUploadSuccess(false);
    
    const formData = new FormData();
    formData.append('file', file);

    try {
      const token = localStorage.getItem('token');
      if (!token) {
        throw new Error('Non authentifié');
      }

      const response = await fetch('http://localhost:8000/api/profil/photo/upload', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: formData
      });

      const data = await response.json();

      if (response.ok) {
        setUploadSuccess(true);
        setTimeout(() => setUploadSuccess(false), 3000);
        await fetchProfile();
      } else {
        setUploadError(data.detail || 'Erreur lors de l\'upload');
      }
    } catch (error) {
      console.error('Erreur upload photo:', error);
      setUploadError('Erreur de connexion au serveur');
    } finally {
      setUploadingPhoto(false);
      // Reset l'input file
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  const handlePhotoDelete = async () => {
    if (!confirm('Voulez-vous vraiment supprimer votre photo de profil ?')) return;
    
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:8000/api/profil/photo', {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        await fetchProfile();
      } else {
        const data = await response.json();
        alert(data.detail || 'Erreur lors de la suppression');
      }
    } catch (error) {
      console.error('Erreur suppression photo:', error);
      alert('Erreur de connexion au serveur');
    }
  };

  const openAddModal = (type: 'experience' | 'formation' | 'competence' | 'objectif') => {
    setModalType(type);
    setFormData({});
    setModalError(null);
    setShowModal(true);
  };

  const handleAdd = async () => {
    setModalError(null);
    setModalLoading(true);

    try {
      let endpoint = '';
      let bodyData = { ...formData };

      // Validation
      if (modalType === 'experience') {
        if (!formData.titre || !formData.entreprise || !formData.date_debut) {
          throw new Error('Veuillez remplir tous les champs obligatoires');
        }
      } else if (modalType === 'formation') {
        if (!formData.diplome || !formData.etablissement || !formData.date_debut) {
          throw new Error('Veuillez remplir tous les champs obligatoires');
        }
      } else if (modalType === 'competence') {
        if (!formData.nom) {
          throw new Error('Veuillez entrer le nom de la compétence');
        }
      } else if (modalType === 'objectif') {
        if (!formData.titre) {
          throw new Error('Veuillez entrer le titre de l\'objectif');
        }
      }

      // Formater les dates
      if (modalType === 'experience' || modalType === 'formation') {
        if (formData.date_debut) {
          bodyData.date_debut = new Date(formData.date_debut).toISOString();
        }
        if (formData.date_fin && !formData.en_cours) {
          bodyData.date_fin = new Date(formData.date_fin).toISOString();
        }
        if (formData.en_cours) {
          bodyData.date_fin = null;
        }
      }

      switch (modalType) {
        case 'experience':
          endpoint = '/api/profil/experiences';
          break;
        case 'formation':
          endpoint = '/api/profil/formations';
          break;
        case 'competence':
          endpoint = '/api/profil/competences';
          break;
        case 'objectif':
          endpoint = '/api/profil/objectifs';
          break;
      }

      await apiCall(endpoint, {
        method: 'POST',
        body: JSON.stringify(bodyData)
      });

      await fetchProfile();
      setShowModal(false);
      setFormData({});
    } catch (error: any) {
      console.error(`Erreur ajout ${modalType}:`, error);
      setModalError(error.message || `Erreur lors de l'ajout`);
    } finally {
      setModalLoading(false);
    }
  };

  const handleDelete = async (type: string, id: number) => {
    if (!confirm('Voulez-vous vraiment supprimer cet élément ?')) return;
    try {
      await apiCall(`/api/profil/${type}/${id}`, { method: 'DELETE' });
      await fetchProfile();
    } catch (error) {
      console.error(`Erreur suppression ${type}:`, error);
      alert(`Erreur lors de la suppression`);
    }
  };

  const formatDate = (dateString?: string) => {
    if (!dateString) return 'Présent';
    try {
      return new Date(dateString).toLocaleDateString('fr-FR', { 
        year: 'numeric', 
        month: 'long' 
      });
    } catch {
      return dateString;
    }
  };

const getPhotoUrl = (filename?: string) => {
  if (!filename) return '';
  return `http://localhost:8000/api/profil/photo/${filename}?t=${Date.now()}`;
};

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-lg text-gray-600">Chargement de votre profil...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-indigo-700 text-white">
        <div className="container mx-auto px-4 py-8">
          <div className="flex items-center justify-between">
            <div>
              <Link href="/dashboard" className="text-white/80 hover:text-white mb-2 inline-block">
                ← Retour au tableau de bord
              </Link>
              <h1 className="text-3xl font-bold flex items-center gap-2">
                <User size={32} />
                Mon profil professionnel
              </h1>
            </div>
          </div>
        </div>
      </div>

      <div className="container mx-auto px-4 py-8">
        {/* Messages de notification */}
        {uploadError && (
          <div className="mb-4 bg-red-50 border border-red-200 rounded-lg p-4 flex items-center gap-3">
            <AlertCircle className="text-red-500 flex-shrink-0" size={20} />
            <p className="text-red-700">{uploadError}</p>
          </div>
        )}
        
        {uploadSuccess && (
          <div className="mb-4 bg-green-50 border border-green-200 rounded-lg p-4 flex items-center gap-3">
            <Check className="text-green-500 flex-shrink-0" size={20} />
            <p className="text-green-700">Photo uploadée avec succès !</p>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Colonne gauche - Photo et infos personnelles */}
          <div className="lg:col-span-1 space-y-6">
            {/* Carte de profil avec photo */}
            <div className="bg-white rounded-lg shadow-lg p-6">
              <div className="flex flex-col items-center">
                <div className="relative group">
                  <div className="w-32 h-32 rounded-full overflow-hidden bg-gray-200 border-4 border-white shadow-lg">
                    {profile?.photo?.filename ? (
                         <img
                         src={getPhotoUrl(profile.photo.filename)}
                         alt="Photo de profil"
                         className="w-full h-full object-cover"
                         onError={(e) => {
                         console.error('Erreur chargement image:', profile.photo?.filename);
                         (e.target as HTMLImageElement).src = 'https://via.placeholder.com/128?text=Erreur';
                      }}
                         />
                        ) : (
                      <div className="w-full h-full flex items-center justify-center bg-blue-100">
                     <User size={48} className="text-blue-600" />
                     </div>
                        )}
                    </div>
                  <div className="absolute -bottom-2 -right-2 flex gap-2">
                    <button
                      onClick={() => fileInputRef.current?.click()}
                      disabled={uploadingPhoto}
                      className="bg-blue-600 text-white p-2 rounded-full hover:bg-blue-700 transition-colors disabled:bg-blue-300"
                      title="Changer la photo"
                    >
                      {uploadingPhoto ? (
                        <Loader size={16} className="animate-spin" />
                      ) : (
                        <Camera size={16} />
                      )}
                    </button>
                    
                    {profile?.photo?.filename && (
                            <button
                            onClick={handlePhotoDelete}
                             className="bg-red-600 text-white p-2 rounded-full hover:bg-red-700 transition-colors"
                             title="Supprimer la photo"
                            >
                     <Trash2 size={16} />
                    </button>
                        )}
                    </div>
                    
                    <input
                        type="file"
                        ref={fileInputRef}
                        onChange={handlePhotoUpload}
                        accept="image/*"
                        className="hidden"
                    />
                    </div>

                <h2 className="text-2xl font-bold text-gray-800 mt-4">
                  {profile?.prenom} {profile?.nom}
                </h2>
                <p className="text-gray-600">{profile?.specialite}</p>
                
                {profile?.institution && (
                  <p className="text-sm text-gray-500 flex items-center gap-1 mt-2">
                    <Building size={14} />
                    {profile.institution}
                  </p>
                )}
                
                <p className="text-sm text-gray-500 flex items-center gap-1 mt-1">
                  <Mail size={14} />
                  {profile?.email}
                </p>
                
                {profile?.orcid_id && (
                  <p className="text-sm text-gray-500 flex items-center gap-1 mt-1">
                    <Award size={14} />
                    ORCID: {profile.orcid_id}
                  </p>
                )}
              </div>

              {/* Objectifs de carrière */}
              <div className="mt-6 pt-6 border-t">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold text-gray-800 flex items-center gap-2">
                    <Target size={20} className="text-blue-600" />
                    Objectifs de carrière
                  </h3>
                  <button
                    onClick={() => openAddModal('objectif')}
                    className="text-blue-600 hover:text-blue-800"
                    title="Ajouter un objectif"
                  >
                    <Plus size={20} />
                  </button>
                </div>
                
                {profile?.objectifs && profile.objectifs.length > 0 ? (
                  <div className="space-y-2">
                    {profile.objectifs.map((obj) => (
                      <div key={obj.id} className="bg-blue-50 p-3 rounded-lg relative group">
                        <p className="font-medium text-gray-800 pr-8">{obj.titre}</p>
                        {obj.description && (
                          <p className="text-sm text-gray-600 mt-1">{obj.description}</p>
                        )}
                        <button
                          onClick={() => handleDelete('objectifs', obj.id)}
                          className="absolute top-2 right-2 text-red-500 hover:text-red-700 opacity-0 group-hover:opacity-100 transition-opacity"
                          title="Supprimer"
                        >
                          <Trash2 size={14} />
                        </button>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-gray-500 text-sm italic">
                    Aucun objectif défini. Cliquez sur + pour en ajouter.
                  </p>
                )}
              </div>

              {/* Compétences */}
              <div className="mt-6 pt-6 border-t">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold text-gray-800 flex items-center gap-2">
                    <Award size={20} className="text-blue-600" />
                    Compétences
                  </h3>
                  <button
                    onClick={() => openAddModal('competence')}
                    className="text-blue-600 hover:text-blue-800"
                    title="Ajouter une compétence"
                  >
                    <Plus size={20} />
                  </button>
                </div>
                
                {profile?.competences && profile.competences.length > 0 ? (
                  <div className="flex flex-wrap gap-2">
                    {profile.competences.map((comp) => (
                      <div key={comp.id} className="bg-gray-100 px-3 py-1 rounded-full flex items-center gap-2 group">
                        <span className="text-gray-700">{comp.nom}</span>
                        {comp.niveau && (
                          <span className="text-xs text-gray-500">({comp.niveau}/5)</span>
                        )}
                        <button
                          onClick={() => handleDelete('competences', comp.id)}
                          className="text-red-500 hover:text-red-700 opacity-0 group-hover:opacity-100 transition-opacity"
                          title="Supprimer"
                        >
                          <X size={14} />
                        </button>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-gray-500 text-sm italic">
                    Aucune compétence ajoutée.
                  </p>
                )}
              </div>
            </div>
          </div>

          {/* Colonne droite - Expériences et Formations */}
          <div className="lg:col-span-2 space-y-6">
            {/* Expériences */}
            <div className="bg-white rounded-lg shadow-lg p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-xl font-bold text-gray-800 flex items-center gap-2">
                  <Briefcase className="text-blue-600" />
                  Expérience professionnelle
                </h3>
                <button
                  onClick={() => openAddModal('experience')}
                  className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg flex items-center gap-2 text-sm transition-colors"
                >
                  <Plus size={18} />
                  Ajouter une expérience
                </button>
              </div>
              
              {profile?.experiences && profile.experiences.length > 0 ? (
                <div className="space-y-4">
                  {profile.experiences.map((exp) => (
                    <div key={exp.id} className="border-l-4 border-blue-500 pl-4 relative group">
                      <div className="flex justify-between">
                        <div className="flex-1">
                          <h4 className="font-semibold text-gray-800 text-lg">{exp.titre}</h4>
                          <p className="text-gray-700">{exp.entreprise}</p>
                          {exp.lieu && (
                            <p className="text-sm text-gray-500 flex items-center gap-1 mt-1">
                              <MapPin size={14} />
                              {exp.lieu}
                            </p>
                          )}
                          <p className="text-sm text-gray-500 flex items-center gap-1 mt-1">
                            <Calendar size={14} />
                            {formatDate(exp.date_debut)} - {exp.en_cours ? 'Présent' : formatDate(exp.date_fin)}
                          </p>
                          {exp.description && (
                            <p className="text-sm text-gray-600 mt-2 bg-gray-50 p-2 rounded">
                              {exp.description}
                            </p>
                          )}
                        </div>
                        <button
                          onClick={() => handleDelete('experiences', exp.id)}
                          className="text-red-500 hover:text-red-700 opacity-0 group-hover:opacity-100 transition-opacity ml-4"
                          title="Supprimer"
                        >
                          <Trash2 size={18} />
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-gray-500 text-center py-8 italic">
                  Aucune expérience professionnelle ajoutée.
                </p>
              )}
            </div>

            {/* Formations */}
            <div className="bg-white rounded-lg shadow-lg p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-xl font-bold text-gray-800 flex items-center gap-2">
                  <GraduationCap className="text-blue-600" />
                  Formation
                </h3>
                <button
                  onClick={() => openAddModal('formation')}
                  className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg flex items-center gap-2 text-sm transition-colors"
                >
                  <Plus size={18} />
                  Ajouter une formation
                </button>
              </div>
              
              {profile?.formations && profile.formations.length > 0 ? (
                <div className="space-y-4">
                  {profile.formations.map((formation) => (
                    <div key={formation.id} className="border-l-4 border-green-500 pl-4 relative group">
                      <div className="flex justify-between">
                        <div className="flex-1">
                          <h4 className="font-semibold text-gray-800 text-lg">{formation.diplome}</h4>
                          <p className="text-gray-700">{formation.etablissement}</p>
                          {formation.domaine && (
                            <p className="text-sm text-gray-600 mt-1">{formation.domaine}</p>
                          )}
                          <p className="text-sm text-gray-500 flex items-center gap-1 mt-1">
                            <Calendar size={14} />
                            {formatDate(formation.date_debut)} - {formatDate(formation.date_fin)}
                          </p>
                          {formation.description && (
                            <p className="text-sm text-gray-600 mt-2 bg-gray-50 p-2 rounded">
                              {formation.description}
                            </p>
                          )}
                        </div>
                        <button
                          onClick={() => handleDelete('formations', formation.id)}
                          className="text-red-500 hover:text-red-700 opacity-0 group-hover:opacity-100 transition-opacity ml-4"
                          title="Supprimer"
                        >
                          <Trash2 size={18} />
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-gray-500 text-center py-8 italic">
                  Aucune formation ajoutée.
                </p>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Modal d'ajout */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full p-6 max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-xl font-bold text-gray-800">
                {modalType === 'experience' && 'Ajouter une expérience'}
                {modalType === 'formation' && 'Ajouter une formation'}
                {modalType === 'competence' && 'Ajouter une compétence'}
                {modalType === 'objectif' && 'Ajouter un objectif'}
              </h3>
              <button
                onClick={() => setShowModal(false)}
                className="text-gray-500 hover:text-gray-700"
              >
                <X size={24} />
              </button>
            </div>

            {modalError && (
              <div className="mb-4 bg-red-50 border border-red-200 rounded-lg p-3 flex items-center gap-2">
                <AlertCircle className="text-red-500 flex-shrink-0" size={18} />
                <p className="text-red-700 text-sm">{modalError}</p>
              </div>
            )}

            <div className="space-y-4">
              {modalType === 'experience' && (
                <>
                  <input
                    type="text"
                    placeholder="Titre du poste *"
                    className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    value={formData.titre || ''}
                    onChange={(e) => setFormData({...formData, titre: e.target.value})}
                    required
                  />
                  <input
                    type="text"
                    placeholder="Entreprise *"
                    className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                    value={formData.entreprise || ''}
                    onChange={(e) => setFormData({...formData, entreprise: e.target.value})}
                    required
                  />
                  <input
                    type="text"
                    placeholder="Lieu"
                    className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                    value={formData.lieu || ''}
                    onChange={(e) => setFormData({...formData, lieu: e.target.value})}
                  />
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm text-gray-600 mb-1">Date début *</label>
                      <input
                        type="date"
                        className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                        value={formData.date_debut || ''}
                        onChange={(e) => setFormData({...formData, date_debut: e.target.value})}
                        required
                      />
                    </div>
                    <div>
                      <label className="block text-sm text-gray-600 mb-1">Date fin</label>
                      <input
                        type="date"
                        className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                        value={formData.date_fin || ''}
                        onChange={(e) => setFormData({...formData, date_fin: e.target.value})}
                        disabled={formData.en_cours}
                      />
                    </div>
                  </div>
                  <label className="flex items-center gap-2">
                    <input
                      type="checkbox"
                      checked={formData.en_cours || false}
                      onChange={(e) => setFormData({...formData, en_cours: e.target.checked, date_fin: null})}
                    />
                    <span className="text-sm text-gray-600">En cours</span>
                  </label>
                  <textarea
                    placeholder="Description"
                    rows={4}
                    className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                    value={formData.description || ''}
                    onChange={(e) => setFormData({...formData, description: e.target.value})}
                  />
                </>
              )}

              {modalType === 'formation' && (
                <>
                  <input
                    type="text"
                    placeholder="Diplôme *"
                    className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                    value={formData.diplome || ''}
                    onChange={(e) => setFormData({...formData, diplome: e.target.value})}
                    required
                  />
                  <input
                    type="text"
                    placeholder="Établissement *"
                    className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                    value={formData.etablissement || ''}
                    onChange={(e) => setFormData({...formData, etablissement: e.target.value})}
                    required
                  />
                  <input
                    type="text"
                    placeholder="Domaine"
                    className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                    value={formData.domaine || ''}
                    onChange={(e) => setFormData({...formData, domaine: e.target.value})}
                  />
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm text-gray-600 mb-1">Date début *</label>
                      <input
                        type="date"
                        className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                        value={formData.date_debut || ''}
                        onChange={(e) => setFormData({...formData, date_debut: e.target.value})}
                        required
                      />
                    </div>
                    <div>
                      <label className="block text-sm text-gray-600 mb-1">Date fin</label>
                      <input
                        type="date"
                        className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                        value={formData.date_fin || ''}
                        onChange={(e) => setFormData({...formData, date_fin: e.target.value})}
                      />
                    </div>
                  </div>
                </>
              )}

              {modalType === 'competence' && (
                <>
                  <input
                    type="text"
                    placeholder="Nom de la compétence *"
                    className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                    value={formData.nom || ''}
                    onChange={(e) => setFormData({...formData, nom: e.target.value})}
                    required
                  />
                  <div>
                    <label className="block text-sm text-gray-600 mb-1">Niveau (1-5)</label>
                    <select
                      className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                      value={formData.niveau || ''}
                      onChange={(e) => setFormData({...formData, niveau: parseInt(e.target.value)})}
                    >
                      <option value="">Sélectionnez un niveau</option>
                      <option value="1">1 - Débutant</option>
                      <option value="2">2 - Intermédiaire</option>
                      <option value="3">3 - Avancé</option>
                      <option value="4">4 - Expert</option>
                      <option value="5">5 - Senior</option>
                    </select>
                  </div>
                  <input
                    type="text"
                    placeholder="Catégorie (ex: Technique, Linguistique)"
                    className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                    value={formData.categorie || ''}
                    onChange={(e) => setFormData({...formData, categorie: e.target.value})}
                  />
                </>
              )}

              {modalType === 'objectif' && (
                <>
                  <input
                    type="text"
                    placeholder="Titre de l'objectif *"
                    className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                    value={formData.titre || ''}
                    onChange={(e) => setFormData({...formData, titre: e.target.value})}
                    required
                  />
                  <textarea
                    placeholder="Description"
                    rows={4}
                    className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                    value={formData.description || ''}
                    onChange={(e) => setFormData({...formData, description: e.target.value})}
                  />
                </>
              )}

              <div className="flex gap-3 pt-4">
                <button
                  onClick={handleAdd}
                  disabled={modalLoading}
                  className="flex-1 bg-blue-600 hover:bg-blue-700 text-white py-2 rounded-lg transition-colors font-medium disabled:bg-blue-300 flex items-center justify-center gap-2"
                >
                  {modalLoading ? (
                    <>
                      <Loader size={18} className="animate-spin" />
                      Ajout en cours...
                    </>
                  ) : (
                    'Ajouter'
                  )}
                </button>
                <button
                  onClick={() => setShowModal(false)}
                  className="flex-1 bg-gray-200 hover:bg-gray-300 text-gray-700 py-2 rounded-lg transition-colors font-medium"
                >
                  Annuler
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}