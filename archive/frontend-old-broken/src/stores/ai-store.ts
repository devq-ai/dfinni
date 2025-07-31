import { create } from 'zustand'
import { devtools } from 'zustand/middleware'
import { logger } from '@/lib/logfire'
import type { ChatMessage } from '@/components/ai/chat-interface'

interface AIState {
  // Chat state
  messages: ChatMessage[]
  isTyping: boolean
  
  // Insights state
  insights: AIInsight[]
  isLoadingInsights: boolean
  
  // Actions
  sendMessage: (content: string) => Promise<void>
  addMessage: (message: ChatMessage) => void
  clearMessages: () => void
  setTyping: (isTyping: boolean) => void
  
  // Insights actions
  fetchInsights: () => Promise<void>
  addInsight: (insight: AIInsight) => void
  clearInsights: () => void
}

export interface AIInsight {
  id: string
  type: 'trend' | 'anomaly' | 'prediction' | 'recommendation'
  title: string
  description: string
  severity: 'low' | 'medium' | 'high'
  patientId?: string
  createdAt: string
  data?: any
}

export const useAIStore = create<AIState>()(
  devtools(
    (set, get) => ({
      // Initial state
      messages: [],
      isTyping: false,
      insights: [],
      isLoadingInsights: false,

      // Chat actions
      sendMessage: async (content: string) => {
        logger.userAction('ai_send_message', { contentLength: content.length })
        
        // Add user message
        const userMessage: ChatMessage = {
          id: Date.now().toString(),
          role: 'user',
          content,
          timestamp: new Date().toISOString(),
        }
        
        get().addMessage(userMessage)
        set({ isTyping: true })

        try {
          // Simulate API call to AI service
          const response = await fetch('/api/ai/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
              message: content,
              context: {
                messages: get().messages.slice(-10), // Last 10 messages for context
              }
            }),
          })

          if (!response.ok) {
            throw new Error('Failed to get AI response')
          }

          const data = await response.json()
          
          // Add AI response
          const aiMessage: ChatMessage = {
            id: Date.now().toString(),
            role: 'assistant',
            content: data.response,
            timestamp: new Date().toISOString(),
          }
          
          get().addMessage(aiMessage)
          logger.userAction('ai_response_received', { 
            responseLength: data.response.length 
          })
        } catch (error) {
          logger.error('AI chat error', error)
          
          // Add error message
          const errorMessage: ChatMessage = {
            id: Date.now().toString(),
            role: 'assistant',
            content: 'I apologize, but I encountered an error processing your request. Please try again.',
            timestamp: new Date().toISOString(),
          }
          
          get().addMessage(errorMessage)
        } finally {
          set({ isTyping: false })
        }
      },

      addMessage: (message: ChatMessage) => {
        set((state) => ({
          messages: [...state.messages, message]
        }))
      },

      clearMessages: () => {
        logger.userAction('ai_clear_messages')
        set({ messages: [] })
      },

      setTyping: (isTyping: boolean) => {
        set({ isTyping })
      },

      // Insights actions
      fetchInsights: async () => {
        logger.userAction('ai_fetch_insights')
        set({ isLoadingInsights: true })

        try {
          const response = await fetch('/api/ai/insights')
          
          if (!response.ok) {
            throw new Error('Failed to fetch insights')
          }

          const data = await response.json()
          
          set({ 
            insights: data.insights,
            isLoadingInsights: false 
          })
          
          logger.userAction('ai_insights_fetched', { 
            count: data.insights.length 
          })
        } catch (error) {
          logger.error('Failed to fetch AI insights', error)
          set({ isLoadingInsights: false })
        }
      },

      addInsight: (insight: AIInsight) => {
        set((state) => ({
          insights: [insight, ...state.insights]
        }))
      },

      clearInsights: () => {
        logger.userAction('ai_clear_insights')
        set({ insights: [] })
      },
    }),
    {
      name: 'ai-store',
    }
  )
)