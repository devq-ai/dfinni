'use client'

import { useState, useRef, useEffect } from 'react'
import { Send, Bot, User, Loader2 } from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { cn } from '@/lib/utils'
import { logger } from '@/lib/logfire'
import { useAIStore } from '@/stores/ai-store'
import { formatDistanceToNow } from 'date-fns'

export interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: string
  isTyping?: boolean
}

interface ChatInterfaceProps {
  className?: string
  placeholder?: string
  onSendMessage?: (message: string) => void
}

export function ChatInterface({ 
  className,
  placeholder = "Ask me about patient insights...",
  onSendMessage
}: ChatInterfaceProps) {
  const { messages, isTyping, sendMessage, clearMessages } = useAIStore()
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  // Log component mount
  useEffect(() => {
    logger.componentMount('ChatInterface')
    return () => {
      logger.componentUnmount('ChatInterface')
    }
  }, [])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!input.trim() || isLoading) return

    const userMessage = input.trim()
    setInput('')
    setIsLoading(true)

    logger.userAction('send_chat_message', { 
      messageLength: userMessage.length 
    })

    try {
      // Call custom handler if provided
      if (onSendMessage) {
        onSendMessage(userMessage)
      }
      
      // Send message via store
      await sendMessage(userMessage)
    } catch (error) {
      logger.error('Failed to send chat message', error)
    } finally {
      setIsLoading(false)
      inputRef.current?.focus()
    }
  }

  const renderMessage = (message: ChatMessage) => {
    const isUser = message.role === 'user'
    
    return (
      <div
        key={message.id}
        className={cn(
          "flex gap-3 p-4 rounded-lg",
          isUser ? "bg-zinc-800" : "bg-zinc-900"
        )}
      >
        <div className={cn(
          "flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center",
          isUser ? "bg-blue-500" : "bg-green-500"
        )}>
          {isUser ? (
            <User className="h-4 w-4 text-white" />
          ) : (
            <Bot className="h-4 w-4 text-white" />
          )}
        </div>
        
        <div className="flex-1 space-y-1">
          <div className="flex items-center gap-2">
            <span className="text-sm font-medium text-zinc-100">
              {isUser ? 'You' : 'AI Assistant'}
            </span>
            <span className="text-xs text-zinc-500">
              {formatDistanceToNow(new Date(message.timestamp), { 
                addSuffix: true 
              })}
            </span>
          </div>
          
          <div className="text-sm text-zinc-300">
            {message.isTyping ? (
              <div className="flex items-center gap-1">
                <span>Thinking</span>
                <Loader2 className="h-3 w-3 animate-spin" />
              </div>
            ) : (
              <p className="whitespace-pre-wrap">{message.content}</p>
            )}
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className={cn(
      "flex flex-col h-full bg-zinc-950 border border-zinc-800 rounded-lg",
      className
    )}>
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-zinc-800">
        <div className="flex items-center gap-2">
          <Bot className="h-5 w-5 text-green-500" />
          <h3 className="text-sm font-semibold text-zinc-100">
            AI Assistant
          </h3>
        </div>
        
        {messages.length > 0 && (
          <Button
            variant="ghost"
            size="sm"
            onClick={() => {
              clearMessages()
              logger.userAction('clear_chat_messages')
            }}
            className="text-xs"
          >
            Clear Chat
          </Button>
        )}
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 ? (
          <div className="text-center py-12">
            <Bot className="h-12 w-12 text-zinc-600 mx-auto mb-4" />
            <p className="text-sm text-zinc-500">
              Start a conversation to get AI-powered insights
            </p>
          </div>
        ) : (
          <>
            {messages.map(renderMessage)}
            {isTyping && renderMessage({
              id: 'typing',
              role: 'assistant',
              content: '',
              timestamp: new Date().toISOString(),
              isTyping: true
            })}
          </>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <form onSubmit={handleSubmit} className="p-4 border-t border-zinc-800">
        <div className="flex gap-2">
          <Input
            ref={inputRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder={placeholder}
            disabled={isLoading}
            className="flex-1"
            autoFocus
          />
          <Button
            type="submit"
            size="icon"
            disabled={!input.trim() || isLoading}
          >
            {isLoading ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Send className="h-4 w-4" />
            )}
          </Button>
        </div>
      </form>
    </div>
  )
}