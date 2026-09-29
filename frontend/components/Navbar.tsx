'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';

export default function Navbar() {
  const pathname = usePathname();

  return (
    <header className="bg-white border-b border-slate-200">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 h-14 flex items-center justify-between">
        {/* Brand */}
        <Link href="/" className="flex items-center space-x-2 font-bold text-slate-900 text-lg tracking-tight">
          <span className="w-3 h-3 rounded-full bg-emerald-700 inline-block" />
          <span>CropSense</span>
        </Link>

        {/* Navigation */}
        <nav className="flex items-center space-x-6 text-sm">
          <Link
            href="/"
            className={`font-medium transition-colors ${
              pathname === '/' ? 'text-emerald-800 font-semibold' : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            New Assessment
          </Link>
          <Link
            href="/history"
            className={`font-medium transition-colors ${
              pathname === '/history' ? 'text-emerald-800 font-semibold' : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            History
          </Link>
        </nav>
      </div>
    </header>
  );
}
