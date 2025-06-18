import React, { useState } from 'react'

export default function Chat({ chatHistory, addMessage }) {
  const [input, setInput] = useState("")
  const [loading, setLoading] = useState(false)

  const sendQuestion = async () => {
    if (!input.trim()) return
    addMessage("user", input)
    setLoading(true)
    try {
      const res = await fetch("http://localhost:8000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: input }),
      })
      const data = await res.json()
      if (data.error) {
        addMessage("system", `Erro: ${data.error}`)
      } else {
        addMessage("assistant", data.answer)
      }
    } catch (e) {
      addMessage("system", "Erro no servidor: " + e.message)
    }
    setLoading(false)
    setInput("")
  }

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      sendQuestion()
    }
  }

  return (
    <div className="flex flex-col gap-4 border p-4 rounded shadow-sm bg-white max-h-[600px] overflow-y-auto">
      <div className="flex-grow overflow-auto">
        {chatHistory.length === 0 && (
          <p className="text-gray-500">Envie uma pergunta para começar a conversa.</p>
        )}
        {chatHistory.map(({ role, text }, i) => (
          <div
            key={i}
            className={`mb-3 p-3 rounded ${
              role === "user"
                ? "bg-blue-100 text-blue-800 self-end max-w-[70%]"
                : role === "assistant"
                ? "bg-gray-100 text-gray-900 self-start max-w-[70%]"
                : "bg-yellow-100 text-yellow-800 self-center max-w-[80%]"
            }`}
          >
            <strong>{role === "user" ? "Você:" : role === "assistant" ? "Pensa.AI:" : "Sistema:"}</strong>
            <p>{text}</p>
          </div>
        ))}
      </div>
      <textarea
        className="border rounded p-2 w-full resize-none"
        rows={3}
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="Digite sua pergunta e pressione Enter"
        disabled={loading}
      />
      <button
        onClick={sendQuestion}
        disabled={loading || !input.trim()}
        className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 disabled:opacity-50"
      >
        {loading ? "Enviando..." : "Enviar"}
      </button>
    </div>
  )
}
