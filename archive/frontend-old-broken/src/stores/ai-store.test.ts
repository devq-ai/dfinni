import { describe, it, expect, vi, beforeEach } from 'vitest'
import { useAIStore } from './ai-store'

// Mock fetch
global.fetch = vi.fn()

// Mock logger
vi.mock('@/lib/logfire', () => ({
  logger: {
    userAction: vi.fn(),
    error: vi.fn(),
  },
}))

describe('AI Store', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    // Reset store state
    useAIStore.setState({
      messages: [],
      isTyping: false,
      insights: [],
      isLoadingInsights: false,
    })
  })

  describe('Chat functionality', () => {
    it('sends message and receives response', async () => {
      const mockResponse = { response: 'AI response message' }
      vi.mocked(fetch).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      } as Response)

      const { sendMessage, messages } = useAIStore.getState()
      
      await sendMessage('Test message')

      const updatedState = useAIStore.getState()
      
      // Should have user message and AI response
      expect(updatedState.messages).toHaveLength(2)
      expect(updatedState.messages[0]).toMatchObject({
        role: 'user',
        content: 'Test message',
      })
      expect(updatedState.messages[1]).toMatchObject({
        role: 'assistant',
        content: 'AI response message',
      })
      expect(updatedState.isTyping).toBe(false)
    })

    it('handles send message error', async () => {
      vi.mocked(fetch).mockRejectedValueOnce(new Error('Network error'))

      const { sendMessage } = useAIStore.getState()
      
      await sendMessage('Test message')

      const { messages } = useAIStore.getState()
      
      // Should have user message and error message
      expect(messages).toHaveLength(2)
      expect(messages[1]).toMatchObject({
        role: 'assistant',
        content: 'I apologize, but I encountered an error processing your request. Please try again.',
      })
    })

    it('sets typing state during message send', async () => {
      let typingStateChecked = false
      
      vi.mocked(fetch).mockImplementation(() => {
        // Check typing state while fetch is pending
        const { isTyping } = useAIStore.getState()
        expect(isTyping).toBe(true)
        typingStateChecked = true
        
        return Promise.resolve({
          ok: true,
          json: async () => ({ response: 'AI response' }),
        } as Response)
      })

      const { sendMessage } = useAIStore.getState()
      
      await sendMessage('Test message')
      
      expect(typingStateChecked).toBe(true)
      expect(useAIStore.getState().isTyping).toBe(false)
    })

    it('adds message to store', () => {
      const { addMessage, messages } = useAIStore.getState()
      
      const testMessage = {
        id: '1',
        role: 'user' as const,
        content: 'Test',
        timestamp: new Date().toISOString(),
      }
      
      addMessage(testMessage)
      
      const { messages: updatedMessages } = useAIStore.getState()
      expect(updatedMessages).toHaveLength(1)
      expect(updatedMessages[0]).toBe(testMessage)
    })

    it('clears messages', () => {
      // Add some messages first
      useAIStore.setState({
        messages: [
          {
            id: '1',
            role: 'user',
            content: 'Test',
            timestamp: new Date().toISOString(),
          },
        ],
      })

      const { clearMessages } = useAIStore.getState()
      clearMessages()
      
      expect(useAIStore.getState().messages).toHaveLength(0)
    })

    it('includes message context in API call', async () => {
      // Add existing messages
      const existingMessages = Array.from({ length: 15 }, (_, i) => ({
        id: String(i),
        role: i % 2 === 0 ? 'user' as const : 'assistant' as const,
        content: `Message ${i}`,
        timestamp: new Date().toISOString(),
      }))
      
      useAIStore.setState({ messages: existingMessages })

      vi.mocked(fetch).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ response: 'AI response' }),
      } as Response)

      const { sendMessage } = useAIStore.getState()
      await sendMessage('New message')

      expect(fetch).toHaveBeenCalledWith('/api/ai/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: 'New message',
          context: {
            messages: existingMessages.slice(-10), // Should only include last 10
          },
        }),
      })
    })
  })

  describe('Insights functionality', () => {
    it('fetches insights successfully', async () => {
      const mockInsights = [
        {
          id: '1',
          type: 'trend',
          title: 'Test Insight',
          description: 'Test description',
          severity: 'medium',
          createdAt: new Date().toISOString(),
        },
      ]

      vi.mocked(fetch).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ insights: mockInsights }),
      } as Response)

      const { fetchInsights } = useAIStore.getState()
      await fetchInsights()

      const { insights, isLoadingInsights } = useAIStore.getState()
      expect(insights).toEqual(mockInsights)
      expect(isLoadingInsights).toBe(false)
    })

    it('handles fetch insights error', async () => {
      vi.mocked(fetch).mockRejectedValueOnce(new Error('Network error'))

      const { fetchInsights } = useAIStore.getState()
      await fetchInsights()

      const { insights, isLoadingInsights } = useAIStore.getState()
      expect(insights).toHaveLength(0)
      expect(isLoadingInsights).toBe(false)
    })

    it('sets loading state during insights fetch', async () => {
      let loadingStateChecked = false
      
      vi.mocked(fetch).mockImplementation(() => {
        // Check loading state while fetch is pending
        const { isLoadingInsights } = useAIStore.getState()
        expect(isLoadingInsights).toBe(true)
        loadingStateChecked = true
        
        return Promise.resolve({
          ok: true,
          json: async () => ({ insights: [] }),
        } as Response)
      })

      const { fetchInsights } = useAIStore.getState()
      await fetchInsights()
      
      expect(loadingStateChecked).toBe(true)
      expect(useAIStore.getState().isLoadingInsights).toBe(false)
    })

    it('adds insight to store', () => {
      const { addInsight, insights } = useAIStore.getState()
      
      const testInsight = {
        id: '1',
        type: 'trend' as const,
        title: 'Test Insight',
        description: 'Test',
        severity: 'low' as const,
        createdAt: new Date().toISOString(),
      }
      
      addInsight(testInsight)
      
      const { insights: updatedInsights } = useAIStore.getState()
      expect(updatedInsights).toHaveLength(1)
      expect(updatedInsights[0]).toBe(testInsight)
    })

    it('adds new insights at the beginning', () => {
      // Add existing insight
      const existingInsight = {
        id: '1',
        type: 'trend' as const,
        title: 'Existing',
        description: 'Existing insight',
        severity: 'low' as const,
        createdAt: new Date().toISOString(),
      }
      
      useAIStore.setState({ insights: [existingInsight] })

      const { addInsight } = useAIStore.getState()
      
      const newInsight = {
        id: '2',
        type: 'anomaly' as const,
        title: 'New',
        description: 'New insight',
        severity: 'high' as const,
        createdAt: new Date().toISOString(),
      }
      
      addInsight(newInsight)
      
      const { insights } = useAIStore.getState()
      expect(insights).toHaveLength(2)
      expect(insights[0]).toBe(newInsight)
      expect(insights[1]).toBe(existingInsight)
    })

    it('clears insights', () => {
      // Add some insights first
      useAIStore.setState({
        insights: [
          {
            id: '1',
            type: 'trend',
            title: 'Test',
            description: 'Test',
            severity: 'low',
            createdAt: new Date().toISOString(),
          },
        ],
      })

      const { clearInsights } = useAIStore.getState()
      clearInsights()
      
      expect(useAIStore.getState().insights).toHaveLength(0)
    })
  })

  describe('Logging', () => {
    it('logs user actions', async () => {
      const { logger } = require('@/lib/logfire')
      
      const { sendMessage, clearMessages, fetchInsights, clearInsights } = useAIStore.getState()
      
      // Mock successful responses
      vi.mocked(fetch).mockResolvedValue({
        ok: true,
        json: async () => ({ response: 'AI response', insights: [] }),
      } as Response)
      
      await sendMessage('Test')
      clearMessages()
      await fetchInsights()
      clearInsights()
      
      expect(logger.userAction).toHaveBeenCalledWith('ai_send_message', expect.any(Object))
      expect(logger.userAction).toHaveBeenCalledWith('ai_clear_messages')
      expect(logger.userAction).toHaveBeenCalledWith('ai_fetch_insights')
      expect(logger.userAction).toHaveBeenCalledWith('ai_clear_insights')
    })

    it('logs errors', async () => {
      const { logger } = require('@/lib/logfire')
      
      vi.mocked(fetch).mockRejectedValue(new Error('Test error'))
      
      const { sendMessage, fetchInsights } = useAIStore.getState()
      
      await sendMessage('Test')
      await fetchInsights()
      
      expect(logger.error).toHaveBeenCalledTimes(2)
    })
  })
})