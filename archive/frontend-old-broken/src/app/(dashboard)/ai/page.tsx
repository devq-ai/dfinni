import { ChatInterface } from '@/components/ai/chat-interface'
import { InsightsDashboard } from '@/components/ai/insights-dashboard'

export default function AIPage() {
  return (
    <div className="container mx-auto py-6">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-zinc-100">AI Assistant</h1>
        <p className="text-sm text-zinc-400 mt-1">
          Get AI-powered insights and chat with our assistant
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Chat Interface */}
        <div className="h-[600px]">
          <ChatInterface />
        </div>

        {/* Insights Dashboard */}
        <div className="h-[600px] overflow-y-auto">
          <InsightsDashboard />
        </div>
      </div>
    </div>
  )
}