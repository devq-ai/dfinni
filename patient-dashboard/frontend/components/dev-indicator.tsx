// Created: 2025-08-05T22:35:00-06:00
'use client';

export function DevIndicator() {
  const isDevelopment = process.env.NODE_ENV === 'development';
  const environment = process.env.NEXT_PUBLIC_ENV || process.env.NODE_ENV;
  
  if (!isDevelopment) return null;
  
  return (
    <div className="fixed bottom-4 left-4 z-50">
      <div className="bg-yellow-500 text-black px-3 py-1 rounded-full text-xs font-bold shadow-lg flex items-center gap-2">
        <div className="w-2 h-2 bg-black rounded-full animate-pulse" />
        DEV MODE
        <span className="text-xs opacity-75">({environment})</span>
      </div>
    </div>
  );
}