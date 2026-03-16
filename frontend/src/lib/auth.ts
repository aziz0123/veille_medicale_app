// src/lib/auth.ts
import { jwtDecode } from "jwt-decode";

const API_URL = process.env.NEXT_PUBLIC_API_URL || '';

export interface User {
  id: number;
  email: string;
  nom: string;
  prenom: string;
  specialite: string;
  institution?: string;
  orcid_id?: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface RegisterData {
  email: string;
  nom: string;
  prenom: string;
  specialite: string;
  institution?: string;
  orcid_id?: string;
  password: string;
}

// Fonction utilitaire pour vérifier si on est côté client
const isClient = () => typeof window !== 'undefined';

// Stocker le token et l'utilisateur
export const setAuthData = (data: LoginResponse) => {
  if (isClient()) {
    localStorage.setItem('token', data.access_token);
    localStorage.setItem('user', JSON.stringify(data.user));
  }
};

// Récupérer le token
export const getToken = (): string | null => {
  if (!isClient()) return null;
  return localStorage.getItem('token');
};

// Récupérer l'utilisateur connecté
export const getUser = (): User | null => {
  if (!isClient()) return null;
  
  const userStr = localStorage.getItem('user');
  if (!userStr) return null;
  
  try {
    return JSON.parse(userStr);
  } catch {
    return null;
  }
};

// Vérifier si l'utilisateur est connecté
export const isAuthenticated = (): boolean => {
  if (!isClient()) return false;
  
  const token = getToken();
  if (!token) return false;
  
  try {
    const decoded: any = jwtDecode(token);
    const currentTime = Date.now() / 1000;
    return decoded.exp > currentTime;
  } catch {
    return false;
  }
};

// Déconnexion
export const logout = () => {
  if (isClient()) {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    window.location.href = '/login';
  }
};

// Inscription
export const register = async (data: RegisterData): Promise<LoginResponse> => {
  const response = await fetch(`${API_URL}/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Erreur lors de l\'inscription');
  }
  
  const result = await response.json();
  setAuthData(result);
  return result;
};

// Connexion
export const login = async (email: string, password: string): Promise<LoginResponse> => {
  const formData = new URLSearchParams();
  formData.append('username', email);
  formData.append('password', password);
  
  const response = await fetch(`${API_URL}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: formData
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Email ou mot de passe incorrect');
  }
  
  const result = await response.json();
  setAuthData(result);
  return result;
};

// Fonction pour appeler l'API avec le token
export const apiCall = async (url: string, options: RequestInit = {}) => {
  const token = getToken();
  
  const headers = {
    'Content-Type': 'application/json',
    ...(token && { 'Authorization': `Bearer ${token}` }),
    ...options.headers
  };
  
  const response = await fetch(`${API_URL}${url}`, { ...options, headers });
  
  if (response.status === 401) {
    // Token expiré ou invalide
    if (isClient()) {
      logout();
    }
    throw new Error('Session expirée, veuillez vous reconnecter');
  }
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Erreur API');
  }
  
  return response.json();
};