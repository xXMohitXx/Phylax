import React from 'react';
import { Sidebar } from '@/components/sidebar';
import { Footer } from '@/components/Footer';

export default function DocsLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="flex w-full mx-auto max-w-[1450px]">
      <Sidebar />
      <div className="flex-1 min-w-0 flex flex-col min-h-[calc(100vh-4rem)] bg-porcelain">
        <main className="flex-1 w-full mx-auto max-w-4xl px-6 py-12 md:px-10 lg:px-12 prose prose-slate prose-a:text-lime-cream hover:prose-a:text-lime-cream/80 prose-headings:text-coffee-bean prose-p:text-coffee-bean/80 prose-li:text-coffee-bean/80 prose-code:text-coffee-bean prose-code:bg-beige prose-code:px-1.5 prose-code:rounded-md prose-pre:bg-code-bg prose-pre:border prose-pre:border-black/20 prose-strong:text-coffee-bean">
          {children}
        </main>
        <Footer />
      </div>
    </div>
  );
}