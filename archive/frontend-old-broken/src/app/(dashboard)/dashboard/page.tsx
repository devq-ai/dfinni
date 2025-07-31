'use client'

export default function MinimalDashboardPage() {
  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold text-zinc-100 mb-4">Dashboard (Minimal)</h1>
      
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-6">
          <h3 className="text-zinc-400 text-sm">Total Patients</h3>
          <p className="text-2xl font-bold text-zinc-100 mt-2">156</p>
        </div>
        
        <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-6">
          <h3 className="text-zinc-400 text-sm">Active Patients</h3>
          <p className="text-2xl font-bold text-zinc-100 mt-2">112</p>
        </div>
        
        <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-6">
          <h3 className="text-zinc-400 text-sm">New This Month</h3>
          <p className="text-2xl font-bold text-zinc-100 mt-2">18</p>
        </div>
        
        <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-6">
          <h3 className="text-zinc-400 text-sm">High Risk</h3>
          <p className="text-2xl font-bold text-zinc-100 mt-2">14</p>
        </div>
      </div>
      
      <div className="mt-8 bg-zinc-900 border border-zinc-800 rounded-lg p-6">
        <h2 className="text-xl font-bold text-zinc-100 mb-4">System Status</h2>
        <p className="text-zinc-400">Dashboard is running in minimal mode to diagnose issues.</p>
      </div>
    </div>
  )
}