// frontend/src/components/auth/AuthGuard.tsx
'use client';

import { useEffect } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import { isAuthenticated } from '@/lib/auth';

export default function AuthGuard({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  
  // Pages publiques (pas besoin d'être connecté)
  const publicPages = ['/login', '/register'];
  
  useEffect(() => {
    const auth = isAuthenticated();
    const isPublicPage = publicPages.includes(pathname);
    
    if (!auth && !isPublicPage) {
      // Rediriger vers login si non authentifié sur page protégée
      router.push('/login');
    } else if (auth && isPublicPage) {
      // Rediriger vers dashboard si déjà connecté sur login/register
      router.push('/dashboard');
    }
  }, [pathname, router]);
  
  return <>{children}</>;
}