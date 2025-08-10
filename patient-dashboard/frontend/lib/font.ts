// Last Updated: 2025-08-09T20:12:00-06:00
import {
  // Geist fonts not available in Next.js 14
  // Geist,
  // Geist_Mono,
  Instrument_Sans,
  Inter,
  Mulish,
  Noto_Sans_Mono,
  Source_Sans_3,
  Source_Code_Pro
} from 'next/font/google';

import { cn } from '@/lib/utils';

// Use Source Sans as alternative to Geist
const fontSans = Source_Sans_3({
  subsets: ['latin'],
  variable: '--font-sans'
});

// Use Source Code Pro as alternative to Geist Mono
const fontMono = Source_Code_Pro({
  subsets: ['latin'],
  variable: '--font-mono'
});

const fontInstrument = Instrument_Sans({
  subsets: ['latin'],
  variable: '--font-instrument'
});

const fontNotoMono = Noto_Sans_Mono({
  subsets: ['latin'],
  variable: '--font-noto-mono'
});

const fontMullish = Mulish({
  subsets: ['latin'],
  variable: '--font-mullish'
});

const fontInter = Inter({
  subsets: ['latin'],
  variable: '--font-inter'
});

export const fontVariables = cn(
  fontSans.variable,
  fontMono.variable,
  fontInstrument.variable,
  fontNotoMono.variable,
  fontMullish.variable,
  fontInter.variable
);
