import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';
import { Navbar } from '@/components/Navbar';
import { MouseFollower } from '@/components/mouse-follower';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'Phylax — CI for AI Behavior',
  description: 'Stop AI regressions before they reach production. Deterministic behavior enforcement for LLM systems.',
  icons: {
    icon: '/favicon.png',
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={`${inter.className} min-h-screen flex flex-col selection:bg-lime-cream/30`}>
        <MouseFollower />
        <Navbar />
        <main className="flex-1 flex flex-col">
          {children}
        </main>
      </body>
    </html>
  );
}