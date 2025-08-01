import { type Metadata } from 'next'
import { Inter, Space_Mono } from 'next/font/google'
import {
  ClerkProvider,
  SignInButton,
  SignUpButton,
  SignedIn,
  SignedOut,
  UserButton,
} from '@clerk/nextjs'
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
  title: 'PFINNI Patient Dashboard',
  description: 'Healthcare patient management system',
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <ClerkProvider>
      <html lang="en" className="dark">
        <body className={`${inter.variable} ${spaceMono.variable}`}>
          <header className="flex justify-end items-center p-4 gap-4 h-16 bg-cyber-carbon-black border-b border-cyber-gray">
            <SignedOut>
              <SignInButton mode="modal">
                <button className="text-cyber-white hover:text-cyber-electric-cyan transition-colors">
                  Sign In
                </button>
              </SignInButton>
              <SignUpButton mode="modal">
                <button className="bg-cyber-electric-cyan text-cyber-void-black rounded-full font-medium text-sm px-5 py-2 hover:bg-cyber-matrix-green transition-colors">
                  Sign Up
                </button>
              </SignUpButton>
            </SignedOut>
            <SignedIn>
              <UserButton 
                appearance={{
                  elements: {
                    avatarBox: "w-10 h-10",
                  }
                }}
              />
            </SignedIn>
          </header>
          {children}
        </body>
      </html>
    </ClerkProvider>
  )
}