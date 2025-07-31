// Updated: 2025-07-31T12:42:00-06:00
'use client'

import { useState, useEffect, useRef } from 'react'
import { useAuth } from '@/contexts/auth-context'
import { useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card'

export default function LoginPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const { login } = useAuth()
  const router = useRouter()
  
  const cardRef = useRef<HTMLDivElement>(null)
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 })
  const [isHovered, setIsHovered] = useState(false)

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (!cardRef.current || !isHovered) return
      
      const rect = cardRef.current.getBoundingClientRect()
      const x = (e.clientX - rect.left) / rect.width
      const y = (e.clientY - rect.top) / rect.height
      
      setMousePosition({ x, y })
    }

    window.addEventListener('mousemove', handleMouseMove)
    return () => window.removeEventListener('mousemove', handleMouseMove)
  }, [isHovered])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    
    try {
      await login(email, password)
    } catch (error) {
      console.error('Login failed:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const rotateX = isHovered ? (mousePosition.y - 0.5) * 45 : 0
  const rotateY = isHovered ? (mousePosition.x - 0.5) * -45 : 0

  return (
    <div className="min-h-screen flex items-center justify-center relative overflow-hidden bg-gradient-to-br from-gray-900 via-black to-gray-900">
      {/* Animated background particles */}
      <div className="absolute inset-0 overflow-hidden">
        {[...Array(100)].map((_, i) => (
          <div
            key={i}
            className="absolute w-2 h-2 bg-blue-500/50 rounded-full animate-float"
            style={{
              left: `${Math.random() * 100}%`,
              animationDelay: `${Math.random() * 10}s`,
              animationDuration: `${5 + Math.random() * 10}s`
            }}
          />
        ))}
      </div>
      
      {/* 3D Login Card */}
      <div className="z-20 perspective-1000">
        <div
          ref={cardRef}
          className="relative transform-gpu transition-transform duration-100 ease-out"
          style={{
            transform: `rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateZ(100px)`,
            transformStyle: 'preserve-3d'
          }}
          onMouseEnter={() => setIsHovered(true)}
          onMouseLeave={() => {
            setIsHovered(false)
            setMousePosition({ x: 0.5, y: 0.5 })
          }}
        >
          <Card className="w-full max-w-md mx-4 bg-black/50 backdrop-blur-xl border-gray-800 shadow-2xl relative overflow-hidden">
            {/* Glow effect */}
            <div className="absolute -inset-1 bg-gradient-to-r from-blue-500 to-purple-500 rounded-lg blur opacity-30 animate-pulse" />
            
            <div className="relative bg-black/50 rounded-lg">
              <CardHeader className="space-y-1">
                <CardTitle className="text-2xl font-bold text-center text-white">
                  Sign in to PFINNI
                </CardTitle>
                <CardDescription className="text-center text-gray-400">
                  Healthcare Patient Management System
                </CardDescription>
              </CardHeader>
              <CardContent>
                <form onSubmit={handleSubmit} className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="email" className="text-gray-200">Email address</Label>
                    <Input
                      id="email"
                      type="email"
                      placeholder="demo@example.com"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      required
                      autoComplete="email"
                      className="bg-gray-900/50 border-gray-700 text-white placeholder:text-gray-500 focus:border-blue-500 transition-all focus:scale-110 focus:shadow-lg focus:shadow-blue-500/50"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="password" className="text-gray-200">Password</Label>
                    <Input
                      id="password"
                      type="password"
                      placeholder="••••••••"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      required
                      autoComplete="current-password"
                      className="bg-gray-900/50 border-gray-700 text-white placeholder:text-gray-500 focus:border-blue-500 transition-all focus:scale-110 focus:shadow-lg focus:shadow-blue-500/50"
                    />
                  </div>
                  <Button
                    type="submit"
                    className="w-full bg-gradient-to-r from-blue-500 to-purple-500 hover:from-blue-600 hover:to-purple-600 text-white font-semibold transform transition-all hover:scale-110 active:scale-90"
                    disabled={isLoading}
                  >
                    {isLoading ? (
                      <span className="flex items-center gap-2">
                        <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                        Signing in...
                      </span>
                    ) : (
                      'Sign in'
                    )}
                  </Button>
                </form>
              </CardContent>
              <CardFooter className="flex flex-col space-y-4">
                <div className="text-center text-xs text-gray-500">
                  <p>© 2025 PFINNI Healthcare Systems</p>
                </div>
              </CardFooter>
            </div>
          </Card>
        </div>
      </div>
      
      {/* Additional visual effects */}
      <div className="absolute bottom-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-blue-500 to-transparent animate-pulse" />
      <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-purple-500 to-transparent animate-pulse" />
      
      <style jsx>{`
        @keyframes float {
          0% {
            transform: translateY(0) translateX(0);
            opacity: 0;
          }
          10% {
            opacity: 1;
          }
          90% {
            opacity: 1;
          }
          100% {
            transform: translateY(-120vh) translateX(200px) scale(2);
            opacity: 0;
          }
        }
        
        .animate-float {
          animation: float linear infinite;
        }
        
        .perspective-1000 {
          perspective: 1000px;
        }
      `}</style>
    </div>
  )
}