// Updated: 2025-08-05T22:30:00-06:00
import { type Metadata } from 'next'
import { Inter, Space_Mono } from 'next/font/google'
import { ClerkProvider } from '@clerk/nextjs'
import { Toaster } from '@/components/ui/toaster'
import { DevIndicator } from '@/components/dev-indicator'
import './globals.css'

const inter = Inter({ 
  subsets: ['latin'],
  variable: '--font-inter',
  display: 'swap',
})

const spaceMono = Space_Mono({ 
  subsets: ['latin'],
  weight: ['400', '700'],
  variable: '--font-space-mono',
  display: 'swap',
})

export const metadata: Metadata = {
  title: 'pfinni - Patient Dashboard',
  description: 'Healthcare patient management system',
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <ClerkProvider publishableKey={process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY}>
      <html lang="en" className="dark">
        <body className={`${inter.variable} ${spaceMono.variable}`}>
          {children}
          <Toaster />
          <DevIndicator />
        </body>
      </html>
    </ClerkProvider>
  )
}