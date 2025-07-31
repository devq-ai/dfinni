import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { ChatInterface } from './chat-interface'
import { useAIStore } from '@/stores/ai-store'

// Mock dependencies
vi.mock('@/stores/ai-store', () => ({
  useAIStore: vi.fn(),
}))

vi.mock('@/lib/logfire', () => ({
  logger: {
    componentMount: vi.fn(),
    componentUnmount: vi.fn(),
    userAction: vi.fn(),
    error: vi.fn(),
  },
}))

vi.mock('date-fns', () => ({
  formatDistanceToNow: vi.fn(() => '2 minutes ago'),
}))

describe('ChatInterface', () => {
  const mockSendMessage = vi.fn()
  const mockClearMessages = vi.fn()
  
  const defaultMessages = [
    {
      id: '1',
      role: 'user' as const,
      content: 'Hello AI',
      timestamp: new Date().toISOString(),
    },
    {
      id: '2',
      role: 'assistant' as const,
      content: 'Hello! How can I help you today?',
      timestamp: new Date().toISOString(),
    },
  ]

  beforeEach(() => {
    vi.clearAllMocks()
    vi.mocked(useAIStore).mockReturnValue({
      messages: [],
      isTyping: false,
      sendMessage: mockSendMessage,
      clearMessages: mockClearMessages,
      insights: [],
      isLoadingInsights: false,
      addMessage: vi.fn(),
      setTyping: vi.fn(),
      fetchInsights: vi.fn(),
      addInsight: vi.fn(),
      clearInsights: vi.fn(),
    })
  })

  it('renders empty state when no messages', () => {
    render(<ChatInterface />)
    
    expect(screen.getByText('AI Assistant')).toBeInTheDocument()
    expect(screen.getByText('Start a conversation to get AI-powered insights')).toBeInTheDocument()
  })

  it('renders messages when available', () => {
    vi.mocked(useAIStore).mockReturnValue({
      messages: defaultMessages,
      isTyping: false,
      sendMessage: mockSendMessage,
      clearMessages: mockClearMessages,
      insights: [],
      isLoadingInsights: false,
      addMessage: vi.fn(),
      setTyping: vi.fn(),
      fetchInsights: vi.fn(),
      addInsight: vi.fn(),
      clearInsights: vi.fn(),
    })

    render(<ChatInterface />)
    
    expect(screen.getByText('Hello AI')).toBeInTheDocument()
    expect(screen.getByText('Hello! How can I help you today?')).toBeInTheDocument()
    expect(screen.getByText('You')).toBeInTheDocument()
    expect(screen.getByText('AI Assistant')).toBeInTheDocument()
  })

  it('shows typing indicator when AI is typing', () => {
    vi.mocked(useAIStore).mockReturnValue({
      messages: defaultMessages,
      isTyping: true,
      sendMessage: mockSendMessage,
      clearMessages: mockClearMessages,
      insights: [],
      isLoadingInsights: false,
      addMessage: vi.fn(),
      setTyping: vi.fn(),
      fetchInsights: vi.fn(),
      addInsight: vi.fn(),
      clearInsights: vi.fn(),
    })

    render(<ChatInterface />)
    
    expect(screen.getByText('Thinking')).toBeInTheDocument()
  })

  it('sends message on form submit', async () => {
    mockSendMessage.mockResolvedValue(undefined)
    
    render(<ChatInterface />)
    
    const input = screen.getByPlaceholderText('Ask me about patient insights...')
    const sendButton = screen.getByRole('button', { name: '' })
    
    fireEvent.change(input, { target: { value: 'Test message' } })
    fireEvent.click(sendButton)
    
    await waitFor(() => {
      expect(mockSendMessage).toHaveBeenCalledWith('Test message')
    })
    
    // Input should be cleared
    expect(input).toHaveValue('')
  })

  it('prevents empty message submission', () => {
    render(<ChatInterface />)
    
    const sendButton = screen.getByRole('button', { name: '' })
    
    fireEvent.click(sendButton)
    
    expect(mockSendMessage).not.toHaveBeenCalled()
  })

  it('handles enter key to send message', async () => {
    mockSendMessage.mockResolvedValue(undefined)
    
    render(<ChatInterface />)
    
    const input = screen.getByPlaceholderText('Ask me about patient insights...')
    
    fireEvent.change(input, { target: { value: 'Test message' } })
    fireEvent.keyDown(input, { key: 'Enter', code: 'Enter' })
    fireEvent.submit(input.closest('form')!)
    
    await waitFor(() => {
      expect(mockSendMessage).toHaveBeenCalledWith('Test message')
    })
  })

  it('shows clear button when messages exist', () => {
    vi.mocked(useAIStore).mockReturnValue({
      messages: defaultMessages,
      isTyping: false,
      sendMessage: mockSendMessage,
      clearMessages: mockClearMessages,
      insights: [],
      isLoadingInsights: false,
      addMessage: vi.fn(),
      setTyping: vi.fn(),
      fetchInsights: vi.fn(),
      addInsight: vi.fn(),
      clearInsights: vi.fn(),
    })

    render(<ChatInterface />)
    
    const clearButton = screen.getByText('Clear Chat')
    expect(clearButton).toBeInTheDocument()
    
    fireEvent.click(clearButton)
    expect(mockClearMessages).toHaveBeenCalled()
  })

  it('disables input while loading', async () => {
    mockSendMessage.mockImplementation(() => new Promise(resolve => setTimeout(resolve, 100)))
    
    render(<ChatInterface />)
    
    const input = screen.getByPlaceholderText('Ask me about patient insights...')
    const sendButton = screen.getByRole('button', { name: '' })
    
    fireEvent.change(input, { target: { value: 'Test message' } })
    fireEvent.click(sendButton)
    
    expect(input).toBeDisabled()
    
    await waitFor(() => {
      expect(input).not.toBeDisabled()
    })
  })

  it('calls custom onSendMessage handler', async () => {
    const customHandler = vi.fn()
    mockSendMessage.mockResolvedValue(undefined)
    
    render(<ChatInterface onSendMessage={customHandler} />)
    
    const input = screen.getByPlaceholderText('Ask me about patient insights...')
    
    fireEvent.change(input, { target: { value: 'Test message' } })
    fireEvent.submit(input.closest('form')!)
    
    await waitFor(() => {
      expect(customHandler).toHaveBeenCalledWith('Test message')
      expect(mockSendMessage).toHaveBeenCalledWith('Test message')
    })
  })

  it('handles send error gracefully', async () => {
    const error = new Error('Network error')
    mockSendMessage.mockRejectedValue(error)
    
    render(<ChatInterface />)
    
    const input = screen.getByPlaceholderText('Ask me about patient insights...')
    
    fireEvent.change(input, { target: { value: 'Test message' } })
    fireEvent.submit(input.closest('form')!)
    
    await waitFor(() => {
      expect(mockSendMessage).toHaveBeenCalled()
    })
    
    // Input should still be enabled after error
    expect(input).not.toBeDisabled()
  })

  it('uses custom placeholder text', () => {
    render(<ChatInterface placeholder="Custom placeholder..." />)
    
    expect(screen.getByPlaceholderText('Custom placeholder...')).toBeInTheDocument()
  })

  it('applies custom className', () => {
    const { container } = render(<ChatInterface className="custom-class" />)
    
    expect(container.firstChild).toHaveClass('custom-class')
  })
})