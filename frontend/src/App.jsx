import React, { useState } from 'react';
import { Upload, FileText, CheckCircle, AlertCircle, BookOpen } from 'lucide-react';

export default function PensaAIPDFDemo() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState('');
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState('');
  const [loading, setLoading] = useState(false);

  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    if (file && file.type === 'application/pdf') {
      setSelectedFile(file);
      setUploadStatus('');
    } else {
      setUploadStatus('error: Apenas arquivos PDF são aceitos');
    }
  };

  const uploadPDF = async () => {
    if (!selectedFile) return;

    setUploading(true);
    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      const response = await fetch('http://127.0.0.1:8000/upload', {
        method: 'POST',
        body: formData
      });

      if (response.ok) {
        setUploadStatus('success: PDF indexado com sucesso! O Pensa.AI agora pode usar esse conteúdo.');
        setSelectedFile(null);
      } else {
        setUploadStatus('error: Erro no upload');
      }
    } catch (error) {
      setUploadStatus('error: Erro de conexão');
    }
    setUploading(false);
  };

  const askQuestion = async () => {
    if (!question.trim()) return;

    setLoading(true);
    try {
      const response = await fetch('http://127.0.0.1:8000/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ question })
      });

      if (response.ok) {
        const data = await response.json();
        setAnswer(data.answer);
      } else {
        setAnswer('Erro ao processar pergunta');
      }
    } catch (error) {
      setAnswer('Erro de conexão');
    }
    setLoading(false);
  };

  return (
    <div className="max-w-4xl mx-auto p-6 bg-gradient-to-br from-blue-50 to-indigo-100 min-h-screen">
      <div className="text-center mb-8">
        <h1 className="text-4xl font-bold text-indigo-800 mb-2">
          🎓 Pensa.AI - Demo PDF Upload
        </h1>
        <p className="text-gray-600">
          Carregue PDFs educacionais e faça perguntas baseadas no conteúdo
        </p>
      </div>

      {/* Upload Section */}
      <div className="bg-white rounded-xl shadow-lg p-6 mb-6">
        <h2 className="text-2xl font-semibold text-gray-800 mb-4 flex items-center">
          <Upload className="mr-2" /> Upload de Material Educacional
        </h2>
        
        <div className="border-2 border-dashed border-indigo-300 rounded-lg p-8 text-center">
          <input
            type="file"
            accept=".pdf"
            onChange={handleFileSelect}
            className="hidden"
            id="pdf-upload"
          />
          <label
            htmlFor="pdf-upload"
            className="cursor-pointer flex flex-col items-center"
          >
            <FileText className="w-12 h-12 text-indigo-400 mb-2" />
            <span className="text-lg text-gray-600">
              Clique para selecionar um PDF
            </span>
            <span className="text-sm text-gray-400 mt-1">
              Livros, apostilas, exercícios, etc.
            </span>
          </label>
        </div>

        {selectedFile && (
          <div className="mt-4 p-4 bg-indigo-50 rounded-lg">
            <p className="text-sm text-gray-700">
              <strong>Arquivo selecionado:</strong> {selectedFile.name}
            </p>
            <button
              onClick={uploadPDF}
              disabled={uploading}
              className="mt-2 bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700 disabled:opacity-50"
            >
              {uploading ? 'Processando...' : 'Carregar e Indexar'}
            </button>
          </div>
        )}

        {uploadStatus && (
          <div className={`mt-4 p-4 rounded-lg flex items-center ${
            uploadStatus.startsWith('success') 
              ? 'bg-green-50 text-green-700' 
              : 'bg-red-50 text-red-700'
          }`}>
            {uploadStatus.startsWith('success') ? (
              <CheckCircle className="mr-2" />
            ) : (
              <AlertCircle className="mr-2" />
            )}
            {uploadStatus.replace('success: ', '').replace('error: ', '')}
          </div>
        )}
      </div>

      {/* Chat Section */}
      <div className="bg-white rounded-xl shadow-lg p-6">
        <h2 className="text-2xl font-semibold text-gray-800 mb-4 flex items-center">
          <BookOpen className="mr-2" /> Pergunte ao Pensa.AI
        </h2>
        
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Sua pergunta educacional:
            </label>
            <textarea
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="Ex: Como resolver equações do segundo grau? Explique o teorema de Pitágoras..."
              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              rows="3"
            />
          </div>
          
          <button
            onClick={askQuestion}
            disabled={loading || !question.trim()}
            className="bg-green-600 text-white px-6 py-3 rounded-lg hover:bg-green-700 disabled:opacity-50 font-medium"
          >
            {loading ? 'Pensando...' : '🤔 Perguntar ao Tutor'}
          </button>
        </div>

        {answer && (
          <div className="mt-6 p-4 bg-gray-50 rounded-lg">
            <h3 className="font-semibold text-gray-800 mb-2">
              📚 Resposta do Pensa.AI:
            </h3>
            <div className="whitespace-pre-wrap text-gray-700 leading-relaxed">
              {answer}
            </div>
          </div>
        )}
      </div>

      {/* Examples */}
      <div className="mt-6 bg-white rounded-xl shadow-lg p-6">
        <h3 className="text-lg font-semibold text-gray-800 mb-3">
          💡 Exemplos de PDFs que Funcionam Bem:
        </h3>
        <div className="grid md:grid-cols-2 gap-4">
          <div className="p-3 bg-blue-50 rounded-lg">
            <h4 className="font-medium text-blue-800">📖 Livros Didáticos</h4>
            <p className="text-sm text-blue-600">Matemática, Física, Química, Biologia</p>
          </div>
          <div className="p-3 bg-green-50 rounded-lg">
            <h4 className="font-medium text-green-800">📝 Apostilas</h4>
            <p className="text-sm text-green-600">Material de cursos e aulas</p>
          </div>
          <div className="p-3 bg-purple-50 rounded-lg">
            <h4 className="font-medium text-purple-800">🧮 Exercícios</h4>
            <p className="text-sm text-purple-600">Listas de problemas resolvidos</p>
          </div>
          <div className="p-3 bg-orange-50 rounded-lg">
            <h4 className="font-medium text-orange-800">📊 Resumos</h4>
            <p className="text-sm text-orange-600">Fórmulas e conceitos organizados</p>
          </div>
        </div>
      </div>
    </div>
  );
}