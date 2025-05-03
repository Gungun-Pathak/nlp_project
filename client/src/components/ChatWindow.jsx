import { FiUser, FiMessageSquare } from 'react-icons/fi'

export default function ChatWindow({ messages, isLoading, chatEndRef }) {
  return (
    <div className="flex-1 overflow-y-auto p-4 space-y-4">
      {messages.map((message, index) => (
        <div
          key={index}
          className={`flex ${message.isUser ? 'justify-end' : 'justify-start'} gap-3`}
        >
          {!message.isUser && (
            <div className="mt-1.5">
              <FiMessageSquare className="h-5 w-5 text-gray-500" />
            </div>
          )}
          <div
            className={`max-w-3xl p-4 rounded-lg ${
              message.isUser
                ? 'bg-blue-500 text-white'
                : 'bg-white border border-gray-200'
            }`}
          >
            <div className="prose prose-sm">{message.text}</div>
          </div>
          {message.isUser && (
            <div className="mt-1.5">
              <FiUser className="h-5 w-5 text-gray-500" />
            </div>
          )}
        </div>
      ))}
      {isLoading && (
        <div className="flex justify-start gap-3">
          <div className="mt-1.5">
            <FiMessageSquare className="h-5 w-5 text-gray-500 animate-pulse" />
          </div>
          <div className="bg-white border border-gray-200 p-4 rounded-lg">
            <div className="flex space-x-2">
              <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
              <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-100"></div>
              <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-200"></div>
            </div>
          </div>
        </div>
      )}
      <div ref={chatEndRef} />
    </div>
  )
}