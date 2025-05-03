import { FiSend } from 'react-icons/fi'
import { useState } from 'react'

export default function MessageInput({ value, onChange, onSend, isLoading }) {
  const [isComposing, setIsComposing] = useState(false)

  const handleSubmit = (e) => {
    e.preventDefault()
    if (!isLoading && value.trim()) {
      onSend(value)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="border-t border-gray-200 bg-white">
      <div className="max-w-3xl mx-auto p-4">
        <div className="relative">
          <input
            type="text"
            value={value}
            onChange={(e) => onChange(e.target.value)}
            onCompositionStart={() => setIsComposing(true)}
            onCompositionEnd={() => setIsComposing(false)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !isComposing && !e.shiftKey) {
                handleSubmit(e)
              }
            }}
            placeholder="Type your message..."
            className="w-full p-3 pr-12 border border-gray-300 rounded-xl focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
            disabled={isLoading}
          />
          <button
            type="submit"
            disabled={isLoading || !value.trim()}
            className="absolute right-3 top-1/2 -translate-y-1/2 p-2 text-gray-500 hover:text-blue-600 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <FiSend className="h-5 w-5" />
          </button>
        </div>
      </div>
    </form>
  )
}