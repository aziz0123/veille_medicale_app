// frontend/src/components/NetworkGraph.tsx
'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { apiCall } from '@/lib/auth';
import { Loader, Users, Link2, User } from 'lucide-react';

interface Node {
  id: number;
  name: string;
  institution: string;
  is_center: boolean;
}

interface Link {
  source: number;
  target: number;
  weight: number;
}

interface GraphData {
  nodes: Node[];
  links: Link[];
}

export default function NetworkGraph() {
  const [graphData, setGraphData] = useState<GraphData>({ nodes: [], links: [] });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchGraphData();
  }, []);

  const fetchGraphData = async () => {
    try {
      const data = await apiCall('/api/network/graph');
      const formattedData = {
        nodes: data.nodes || [],
        links: data.edges ? data.edges.map((edge: any) => ({
          source: edge.source,
          target: edge.target,
          weight: edge.weight
        })) : []
      };
      setGraphData(formattedData);
    } catch (error) {
      console.error('Erreur chargement graphe:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader className="animate-spin text-blue-600" size={32} />
      </div>
    );
  }

  if (graphData.nodes.length === 0) {
    return (
      <div className="bg-gray-50 rounded-lg h-64 flex items-center justify-center text-gray-500">
        <p>Aucune donnée de réseau disponible. Liez votre compte ORCID pour voir votre réseau.</p>
      </div>
    );
  }

  const centerNode = graphData.nodes.find(n => n.is_center);
  const otherNodes = graphData.nodes.filter(n => !n.is_center);

  return (
    <div className="space-y-6">
      {/* Statistiques du réseau */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-blue-50 rounded-lg p-4">
          <div className="flex items-center gap-3">
            <div className="bg-blue-100 p-2 rounded-full">
              <Users size={20} className="text-blue-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">Total collaborateurs</p>
              <p className="text-2xl font-bold text-blue-600">{graphData.nodes.length - 1}</p>
            </div>
          </div>
        </div>
        
        <div className="bg-green-50 rounded-lg p-4">
          <div className="flex items-center gap-3">
            <div className="bg-green-100 p-2 rounded-full">
              <Link2 size={20} className="text-green-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">Connexions</p>
              <p className="text-2xl font-bold text-green-600">{graphData.links.length}</p>
            </div>
          </div>
        </div>
        
        <div className="bg-purple-50 rounded-lg p-4">
          <div className="flex items-center gap-3">
            <div className="bg-purple-100 p-2 rounded-full">
              <Users size={20} className="text-purple-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">Institutions</p>
              <p className="text-2xl font-bold text-purple-600">
                {new Set(graphData.nodes.map(n => n.institution)).size}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Carte du chercheur principal */}
      {centerNode && (
        <div className="bg-gradient-to-r from-blue-500 to-indigo-600 rounded-lg p-6 text-white">
          <div className="flex items-center gap-4">
            <div className="bg-white/20 p-3 rounded-full">
              <User size={32} />
            </div>
            <div>
              <p className="text-sm opacity-90">Chercheur principal</p>
              <h3 className="text-2xl font-bold">{centerNode.name}</h3>
              <p className="text-sm opacity-90 mt-1">{centerNode.institution}</p>
            </div>
          </div>
        </div>
      )}

      {/* Liste des collaborateurs */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
          <Users size={20} className="text-blue-600" />
          Vos collaborateurs ({otherNodes.length})
        </h3>
        
        {otherNodes.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {otherNodes.map((node) => {
              const collaborationCount = graphData.links.filter(
                l => (l.source === node.id || l.target === node.id)
              ).length;
              
              return (
                <Link
                  key={node.id}
                  href={`/network/${node.id}`}
                  className="flex items-start gap-4 p-4 border rounded-lg hover:bg-gray-50 transition-colors group"
                >
                  <div className="bg-green-100 p-3 rounded-full group-hover:bg-green-200">
                    <User size={20} className="text-green-600" />
                  </div>
                  <div className="flex-1">
                    <p className="font-semibold text-gray-800 mb-1">{node.name}</p>
                    <p className="text-sm text-gray-500 mb-2">{node.institution}</p>
                    <p className="text-xs text-gray-400">
                      {collaborationCount} collaboration(s)
                    </p>
                  </div>
                </Link>
              );
            })}
          </div>
        ) : (
          <p className="text-gray-500 text-center py-4">
            Aucun collaborateur trouvé. Importez vos publications pour découvrir votre réseau.
          </p>
        )}
      </div>
    </div>
  );
}