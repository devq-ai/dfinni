// Last Updated: 2025-08-09T20:12:00-06:00
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
  const publishableKey = process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY;
  const signInUrl = process.env.NEXT_PUBLIC_CLERK_SIGN_IN_URL;
  const signUpUrl = process.env.NEXT_PUBLIC_CLERK_SIGN_UP_URL;
  const afterSignInUrl = process.env.NEXT_PUBLIC_CLERK_AFTER_SIGN_IN_URL;
  const afterSignUpUrl = process.env.NEXT_PUBLIC_CLERK_AFTER_SIGN_UP_URL;
  
  return (
    <ClerkProvider 
      publishableKey={publishableKey}
      signInUrl={signInUrl}
      signUpUrl={signUpUrl}
      signInFallbackRedirectUrl={afterSignInUrl}
      signUpFallbackRedirectUrl={afterSignUpUrl}
    >
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