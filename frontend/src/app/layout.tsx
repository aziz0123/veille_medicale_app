// frontend/src/app/layout.tsx
import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import AuthGuard from "@/components/auth/AuthGuard";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Veille Médicale IA",
  description: "Plateforme intelligente de curation et veille scientifique médicale personnalisée",
  keywords: ["médecine", "veille scientifique", "IA", "articles médicaux", "recherche"],
  authors: [{ name: "Équipe Veille Médicale" }],
  openGraph: {
    title: "Veille Médicale IA",
    description: "Plateforme intelligente de curation et veille scientifique médicale personnalisée",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="fr">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased bg-gradient-to-br from-blue-50 to-indigo-100`}
      >
        <AuthGuard>
          <main className="min-h-screen">
            {children}
          </main>
        </AuthGuard>
      </body>
    </html>
  );
}