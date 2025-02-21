import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title:
    "COXCOX AI - Agente de Inteligencia Artificial para Telemarketing | Automatización de Ventas",
  description:
    "Moderniza tu equipo de telemarketing con nuestro agente de IA. Automatiza consultas, pedidos y soporte al cliente. Solución integral de atención al cliente 24/7 con inteligencia artificial avanzada.",
  keywords: [
    "telemarketing IA",
    "agente virtual",
    "automatización ventas",
    "inteligencia artificial",
    "atención al cliente",
    "COXCOX AI",
    "bot telemarketing",
    "servicio al cliente automatizado",
  ],
  authors: [{ name: "COXCOX AI" }],
  robots: {
    index: true,
    follow: true,
  },
  openGraph: {
    type: "website",
    url: "https://coxcoxai.com/",
    title:
      "COXCOX AI - Revoluciona tu Telemarketing con Inteligencia Artificial",
    description:
      "Transforma tu equipo de telemarketing con nuestro agente de IA. Gestión automática de consultas, pedidos y soporte al cliente 24/7.",
    images: [
      {
        url: "/coxcox-logo.webp",
        alt: "COXCOX AI Logo",
      },
    ],
  },
  twitter: {
    card: "summary_large_image",
    title: "COXCOX AI - Revoluciona tu Telemarketing con IA",
    description:
      "Transforma tu equipo de telemarketing con nuestro agente de IA. Gestión automática de consultas, pedidos y soporte al cliente 24/7.",
    images: [
      {
        url: "/coxcox-logo.webp",
        alt: "COXCOX AI Logo",
      },
    ],
  },
  alternates: {
    canonical: "https://coxcoxai.com/",
  },
  other: {
    "geo.region": "MX",
    "geo.position": "23.634501;-102.552784",
    "geo.placename": "México",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        {children}
      </body>
    </html>
  );
}
