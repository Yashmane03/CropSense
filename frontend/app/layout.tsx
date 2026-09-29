import type { Metadata } from 'next';
import './globals.css';
import Navbar from '@/components/Navbar';

export const metadata: Metadata = {
  title: 'CropSense - Crop Health Diagnostics',
  description: 'Context-aware crop health assessment platform.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className="bg-slate-50 text-slate-800 antialiased min-h-screen flex flex-col font-sans" suppressHydrationWarning>
        <Navbar />
        <main className="flex-1 max-w-6xl w-full mx-auto px-4 sm:px-6 py-6">
          {children}
        </main>
        <footer className="border-t border-slate-200 py-4 text-center text-xs text-slate-500 bg-white">
          <p>© CropSense Diagnostics</p>
        </footer>
      </body>
    </html>
  );
}
