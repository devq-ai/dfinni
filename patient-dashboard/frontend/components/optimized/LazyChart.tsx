import dynamic from 'next/dynamic';
import { Skeleton } from '@/components/ui/skeleton';

// Lazy load heavy chart component
export const LazyChart = dynamic(
  () => import('@/components/charts/PatientTrendsChart').then(mod => mod.PatientTrendsChart),
  {
    loading: () => (
      <div className="w-full h-[300px] p-4">
        <Skeleton className="w-full h-full" />
      </div>
    ),
    ssr: false, // Disable SSR for chart libraries
  }
);

// Lazy load with preload on hover
export const LazyChartWithPreload = dynamic(
  () => import('@/components/charts/PatientTrendsChart').then(mod => mod.PatientTrendsChart),
  {
    loading: () => (
      <div className="w-full h-[300px] p-4">
        <Skeleton className="w-full h-full" />
      </div>
    ),
    ssr: false,
    // Preload on hover
    onLoad: () => {
      import('@/components/charts/PatientTrendsChart');
    },
  }
);