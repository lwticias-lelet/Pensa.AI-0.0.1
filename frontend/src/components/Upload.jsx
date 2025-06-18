import React, { useState } from 'react'

export default function Upload({ addMessage }) {
  const [file, setFile] = useState(null)
  const [loading, setLoading] = useState(false)

  const handleChange = (e) => {
    setFile(e.target.files[0])
  }

  const handleUpload = async () => {
    if (!file) {
      alert("Selecione um arquivo PDF")
      return
    }
    
    setLoading(true)
    const formData = new FormData()
    formData.append("file", file)
    
    try {
      const res = await fetch("http://localhost:8000/upload", {
        method: "POST",
        body: formData,
      })
      
      if (!res.ok) {
        throw new Error(`Erro ${res.status}: ${res.statusText}`)
      }
      
      const data = await res.json()
      addMessage("system", `✅ ${data.message}`)
      setFile(null)
      // Limpa o input file
      document.querySelector('input[type="file"]').value = ''
    } catch (e) {
      addMessage("system", `❌ Erro no upload: ${e.message}`)
      console.error("Erro:", e)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="border border-gray-200 p-6 rounded-lg shadow-sm bg-white">
      <h2 className="text-lg font-semibold mb-4 text-gray-800">📄 Upload de PDF</h2>
      
      <div className="space-y-4">
        <div>
          <input 
            type="file" 
            accept="application/pdf" 
            onChange={handleChange}
            className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
          />
        </div>
        
        {file && (
          <div className="text-sm text-gray-600">
            📎 Arquivo selecionado: {file.name}
          </div>
        )}
        
        <button
          className="w-full px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          onClick={handleUpload}
          disabled={loading || !file}
        >
          {loading ? "Enviando..." : "📤 Enviar PDF"}
        </button>
      </div>
    </div>
  )
}