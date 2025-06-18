import React, { useState } from 'react'

export default function Upload({ addMessage }) {
  const [file, setFile] = useState(null)
  const [loading, setLoading] = useState(false)

  const handleChange = (e) => {
    setFile(e.target.files[0])
  }

  const handleUpload = async () => {
    if (!file) return alert("Selecione um arquivo PDF")
    setLoading(true)
    const formData = new FormData()
    formData.append("file", file)
    try {
      const res = await fetch("http://localhost:8000/upload", {
        method: "POST",
        body: formData,
      })
      const data = await res.json()
      if (data.error) {
        alert(data.error)
      } else {
        addMessage("system", `Arquivo ${data.filename} enviado com sucesso!`)
      }
    } catch (e) {
      alert("Erro no upload: " + e.message)
    }
    setLoading(false)
  }

  return (
    <div className="border p-4 rounded shadow-sm bg-gray-50">
      <label className="block mb-2 font-semibold">Upload de PDF:</label>
      <input type="file" accept="application/pdf" onChange={handleChange} />
      <button
        className="mt-2 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        onClick={handleUpload}
        disabled={loading}
      >
        {loading ? "Enviando..." : "Enviar"}
      </button>
    </div>
  )
}
