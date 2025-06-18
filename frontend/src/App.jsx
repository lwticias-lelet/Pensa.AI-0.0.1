import React, { useState } from 'react'
import Chat from './components/Chat'
import Upload from './components/Upload'

export default function App() {
  const [chatHistory, setChatHistory] = useState([])

  const addMessage = (role, text) => {
    setChatHistory(prev => [...prev, { role, text }])
  }

  return (
    <div className="flex flex-col gap-8">
      <h1 className="text-3xl font-bold text-center">Pensa.AI Chatbot Educacional</h1>
      <Upload addMessage={addMessage} />
      <Chat chatHistory={chatHistory} addMessage={addMessage} />
    </div>
  )
}
