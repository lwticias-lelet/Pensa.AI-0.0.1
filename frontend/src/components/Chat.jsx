import React, { useState, useRef, useEffect } from 'react'

export default function Chat({ chatHistory, addMessage }) {
  const [input, setInput] = useState("")
  const [loading, setLoading] = useState(false)
  const messagesEndRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [chatHistory])

  const sendQuestion = async () => {
    if (!input.trim()) return
    
    const question = input.trim()
    addMessage("user", question)
    setInput("")
    setLoading(true)
    
    try {
      const res = await fetch("http://localhost:8000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question }),
      })
      
      if (!res.ok) {
        throw new Error(`Erro ${res.status}: ${res.statusText}`)
      }
      
      const data = await res.json()
      addMessage("assistant", data.answer)
    } catch (e) {
      addMessage("system", "Erro no servidor: " + e.message)
      console.error("Erro:", e)
    } finally {
      setLoading(false)
    }
  }

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      sendQuestion()
    }
  }

  return (
    <div className="flex flex-col gap-4 border border-gray-200 rounded-lg shadow-sm bg-white">
      {/* Área de mensagens */}
      <div className="flex-grow overflow-auto max-h-96 p-4 space-y-3">
        {chatHistory.length === 0 && (
          <div className="text-center text-gray-500 py-8">
            <p>👋 Olá! Sou o Pensa.AI</p>
            <p>Faça upload de um PDF e faça suas perguntas!</p>
          </div>
        )}
        
        {chatHistory.map(({ role, text }, i) => (
          <div
            key={i}
            className={`flex ${role === "user" ? "justify-end" : "justify-start"}`}
          >
            <div
              className={`max-w-[70%] p-3 rounded-lg ${
                role === "user"
                  ? "bg-blue-500 text-white rounded-br-sm"
                  : role === "assistant"
                  ? "bg-gray-100 text-gray-900 rounded-bl-sm"
                  : "bg-yellow-100 text-yellow-800 rounded-lg"
              }`}
            >
              <div className="text-xs mb-1 opacity-70">
                {role === "user" ? "Você" : role === "assistant" ? "Pensa.AI" : "Sistema"}
              </div>
              <p className="whitespace-pre-wrap">{text}</p>
            </div>
          </div>
        ))}
        
        {loading && (
          <div className="flex justify-start">
            <div className="bg-gray-100 p-3 rounded-lg rounded-bl-sm">
              <div className="flex items-center space-x-2">
                <div className="animate-pulse">🤔</div>
                <span>Pensando...</span>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>
      
      {/* Área de input */}
      <div className="border-t border-gray-200 p-4">
        <div className="flex gap-2">
          <textarea
            className="flex-1 border border-gray-300 rounded-lg p-3 resize-none focus:outline-none focus:ring-2 focus:ring-blue-500"
            rows={2}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Digite sua pergunta e pressione Enter..."
            disabled={loading}
          />
          <button
            onClick={sendQuestion}
            disabled={loading || !input.trim()}
            className="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {loading ? "..." : "Enviar"}
          </button>
        </div>
      </div>
    </div>
  )
}