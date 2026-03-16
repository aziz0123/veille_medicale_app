// src/app/articles/[id]/page.tsx
'use client';

import { useEffect, useState } from 'react';
import { getArticleById, Article } from '@/lib/api';
import Link from 'next/link';
import { useParams } from 'next/navigation';
import { 
  ArrowLeft, 
  Calendar, 
  User, 
  BookOpen, 
  Tag, 
  FileText,
  Users,
  Pill,
  BarChart3,
  Award,
  ExternalLink
} from 'lucide-react';

export default function ArticleDetailPage() {
  const params = useParams();
  const articleId = params.id as string;
  
  const [article, setArticle] = useState<Article | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchArticle = async () => {
      try {
        setLoading(true);
        const data = await getArticleById(articleId);
        setArticle(data);
      } catch (err) {
        setError('Erreur lors du chargement de l\'article');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    if (articleId) {
      fetchArticle();
    }
  }, [articleId]);

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-lg text-gray-600">Chargement de l'article...</p>
        </div>
      </div>
    );
  }

  if (error || !article) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="bg-white p-8 rounded-lg shadow-lg text-center">
          <p className="text-red-500 text-xl mb-4">❌ {error || 'Article non trouvé'}</p>
          <Link href="/articles" className="text-blue-600 hover:underline flex items-center justify-center gap-2">
            <ArrowLeft size={16} />
            Retour à la liste
          </Link>
        </div>
      </div>
    );
  }

  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Navigation */}
      <div className="bg-white shadow-sm">
        <div className="container mx-auto px-4 py-4">
          <Link 
            href="/articles" 
            className="inline-flex items-center gap-2 text-gray-600 hover:text-blue-600 transition-colors"
          >
            <ArrowLeft size={20} />
            Retour à la liste des articles
          </Link>
        </div>
      </div>

      {/* Contenu principal */}
      <div className="container mx-auto px-4 py-8">
        <div className="bg-white rounded-lg shadow-lg overflow-hidden">
          {/* En-tête */}
          <div className="bg-gradient-to-r from-blue-600 to-indigo-700 text-white p-8">
            <div className="flex items-center gap-2 mb-4">
              <span className="bg-white/20 px-3 py-1 rounded-full text-sm">
                {article.source}
              </span>
              {article.specialite && (
                <span className="bg-green-500/30 px-3 py-1 rounded-full text-sm">
                  {article.specialite}
                </span>
              )}
              {article.type_etude && article.type_etude !== 'autre' && (
                <span className="bg-purple-500/30 px-3 py-1 rounded-full text-sm">
                  {article.type_etude}
                </span>
              )}
            </div>
            
            <h1 className="text-3xl font-bold mb-4">{article.title}</h1>
            
            <div className="flex flex-wrap gap-4 text-sm text-white/80">
              {article.publication_date && (
                <span className="flex items-center gap-1">
                  <Calendar size={16} />
                  {article.publication_date}
                </span>
              )}
              {article.authors && article.authors.length > 0 && (
                <span className="flex items-center gap-1">
                  <User size={16} />
                  {article.authors.join(', ')}
                </span>
              )}
            </div>
          </div>

          {/* Corps de l'article */}
          <div className="p-8">
            {/* Résumé structuré */}
            {article.resume_structure && (
              <div className="mb-8">
                <h2 className="text-xl font-bold text-gray-800 mb-4 flex items-center gap-2">
                  <FileText className="text-blue-600" />
                  Résumé structuré
                </h2>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {/* Population */}
                  {article.resume_structure.population && 
                   article.resume_structure.population !== 'Non spécifié' && (
                    <div className="bg-blue-50 rounded-lg p-4">
                      <div className="flex items-center gap-2 text-blue-700 mb-2">
                        <Users size={20} />
                        <span className="font-semibold">Population</span>
                      </div>
                      <p className="text-gray-700">{article.resume_structure.population}</p>
                    </div>
                  )}

                  {/* Intervention */}
                  {article.resume_structure.intervention && 
                   article.resume_structure.intervention !== 'Non spécifié' && (
                    <div className="bg-green-50 rounded-lg p-4">
                      <div className="flex items-center gap-2 text-green-700 mb-2">
                        <Pill size={20} />
                        <span className="font-semibold">Intervention</span>
                      </div>
                      <p className="text-gray-700">{article.resume_structure.intervention}</p>
                    </div>
                  )}

                  {/* Résultats */}
                  {article.resume_structure.resultats && 
                   article.resume_structure.resultats !== 'Non spécifié' && (
                    <div className="bg-purple-50 rounded-lg p-4">
                      <div className="flex items-center gap-2 text-purple-700 mb-2">
                        <BarChart3 size={20} />
                        <span className="font-semibold">Résultats</span>
                      </div>
                      <p className="text-gray-700">{article.resume_structure.resultats}</p>
                    </div>
                  )}

                  {/* Conclusion */}
                  {article.resume_structure.conclusion && 
                   article.resume_structure.conclusion !== 'Non spécifié' && (
                    <div className="bg-orange-50 rounded-lg p-4">
                      <div className="flex items-center gap-2 text-orange-700 mb-2">
                        <Award size={20} />
                        <span className="font-semibold">Conclusion</span>
                      </div>
                      <p className="text-gray-700">{article.resume_structure.conclusion}</p>
                    </div>
                  )}
                </div>

                {/* Résumé court */}
                {article.resume_structure.resume_court && (
                  <div className="mt-4 p-4 bg-gray-50 rounded-lg">
                    <p className="text-gray-700 italic">
                      "{article.resume_structure.resume_court}"
                    </p>
                  </div>
                )}
              </div>
            )}

            {/* Abstract original */}
            {article.abstract && (
              <div className="mb-8">
                <h2 className="text-xl font-bold text-gray-800 mb-4 flex items-center gap-2">
                  <BookOpen className="text-blue-600" />
                  Abstract original
                </h2>
                <div className="bg-gray-50 rounded-lg p-4">
                  <p className="text-gray-700 leading-relaxed">{article.abstract}</p>
                </div>
              </div>
            )}

            {/* Métadonnées supplémentaires */}
            <div className="border-t border-gray-200 pt-6">
              <h2 className="text-xl font-bold text-gray-800 mb-4 flex items-center gap-2">
                <Tag className="text-blue-600" />
                Informations complémentaires
              </h2>
              
              <dl className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {article.source && (
                  <>
                    <dt className="font-semibold text-gray-600">Source:</dt>
                    <dd className="text-gray-800">{article.source}</dd>
                  </>
                )}
                
                {article.publication_date && (
                  <>
                    <dt className="font-semibold text-gray-600">Date de publication:</dt>
                    <dd className="text-gray-800">{article.publication_date}</dd>
                  </>
                )}
                
                {article.specialite && (
                  <>
                    <dt className="font-semibold text-gray-600">Spécialité:</dt>
                    <dd className="text-gray-800">{article.specialite}</dd>
                  </>
                )}
                
                {article.type_etude && (
                  <>
                    <dt className="font-semibold text-gray-600">Type d'étude:</dt>
                    <dd className="text-gray-800">{article.type_etude}</dd>
                  </>
                )}
                
                {article.authors && article.authors.length > 0 && (
                  <>
                    <dt className="font-semibold text-gray-600">Auteurs:</dt>
                    <dd className="text-gray-800">{article.authors.join(', ')}</dd>
                  </>
                )}
              </dl>
            </div>

            {/* Liens externes */}
            <div className="border-t border-gray-200 mt-6 pt-6">
              <div className="flex gap-4">
                {article.doi && (
                  <a
                    href={`https://doi.org/${article.doi}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-2 text-blue-600 hover:text-blue-800"
                  >
                    <ExternalLink size={16} />
                    Voir sur DOI.org
                  </a>
                )}
                {article.pmid && (
                  <a
                    href={`https://pubmed.ncbi.nlm.nih.gov/${article.pmid}/`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-2 text-blue-600 hover:text-blue-800"
                  >
                    <ExternalLink size={16} />
                    Voir sur PubMed
                  </a>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}