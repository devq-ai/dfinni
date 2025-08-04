'use client';

import { useEffect } from 'react';

export function useServiceWorker() {
  useEffect(() => {
    if (typeof window !== 'undefined' && 'serviceWorker' in navigator) {
      // Only register in production
      if (process.env.NODE_ENV === 'production') {
        window.addEventListener('load', () => {
          navigator.serviceWorker
            .register('/sw.js')
            .then((registration) => {
              console.log('SW registered: ', registration);
              
              // Check for updates periodically
              setInterval(() => {
                registration.update();
              }, 60 * 60 * 1000); // Check every hour
              
              // Handle updates
              registration.addEventListener('updatefound', () => {
                const newWorker = registration.installing;
                if (newWorker) {
                  newWorker.addEventListener('statechange', () => {
                    if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
                      // New content is available
                      if (window.confirm('New version available! Reload to update?')) {
                        window.location.reload();
                      }
                    }
                  });
                }
              });
            })
            .catch((registrationError) => {
              console.log('SW registration failed: ', registrationError);
            });
        });
      }
    }
  }, []);
}