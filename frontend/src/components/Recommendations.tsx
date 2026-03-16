// frontend/src/components/Recommendations.tsx
'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { apiCall } from '@/lib/auth';
import { Sparkles, Calendar, User } from 'lucide-react';

interface Recommendation {
  _id: string;
  title: string;
  source: string;
  specialite: string;
  publication_date: string;
  authors?: string[];
  resume_structure?: {
    resume_court: string;
  };
}

export default function Recommendations() {
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
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
        <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
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
        {recommendations.map((article) => (
          <Link
            key={article._id}
            href={`/articles/${article._id}`}
            className="block p-4 bg-white rounded-lg border border-purple-100 hover:border-purple-300 transition-colors shadow-sm hover:shadow"
          >
            <div className="flex items-center gap-2 mb-2">
              <span className="bg-purple-100 text-purple-700 text-xs font-medium px-2 py-1 rounded">
                {article.source}
              </span>
              <span className="bg-green-100 text-green-700 text-xs font-medium px-2 py-1 rounded">
                {article.specialite}
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
                <Calendar size={12} />
                {article.publication_date}
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