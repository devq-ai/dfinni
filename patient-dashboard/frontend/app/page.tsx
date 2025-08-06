import Link from 'next/link'

export default function Home() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-[#0f0f0f]">
      <div className="text-center">
        <h1 className="text-3xl font-bold text-white mb-8">PFINNI Patient Dashboard</h1>
        <Link 
          href="/sign-in" 
          className="inline-block px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          Sign In
        </Link>
      </div>
    </div>
  )
}