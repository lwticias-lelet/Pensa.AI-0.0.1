// frontend/src/config/api.js - CORRIGIR CONEXÃO

const API_CONFIG = {
  development: 'http://localhost:8000',
  production: 'https://pensa-ai-backend.onrender.com'
}

// Detectar ambiente CORRETAMENTE
const getBaseURL = () => {
  // Em desenvolvimento sempre usar localhost
  if (process.env.NODE_ENV === 'development' || window.location.hostname === 'localhost') {
    console.log('🔗 Ambiente: DESENVOLVIMENTO - Usando localhost:8000')
    return 'http://localhost:8000'
  }
  
  // Em produção usar Render
  console.log('🔗 Ambiente: PRODUÇÃO - Usando Render')
  return API_CONFIG.production
}

export const API_BASE_URL = getBaseURL()

// Teste de conectividade MELHORADO
export const testConnection = async () => {
  console.log('🔍 Testando conexão com:', API_BASE_URL)
  
  try {
    const response = await fetch(`${API_BASE_URL}/health`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
      mode: 'cors',
      // Timeout de 5 segundos
      signal: AbortSignal.timeout(5000)
    })
    
    console.log('📡 Status da resposta:', response.status)
    
    if (response.ok) {
      const data = await response.json()
      console.log('✅ Backend conectado:', data)
      return { success: true, data }
    } else {
      console.error('❌ Backend retornou erro:', response.status)
      return { success: false, error: `HTTP ${response.status}` }
    }
  } catch (error) {
    console.error('❌ Erro de conexão detalhado:', error)
    return { success: false, error: error.message }
  }
}

// API melhorada com debug detalhado
export const api = {
  // Chat com debug completo
  chat: async (question) => {
    console.log('📤 Enviando pergunta:', question.substring(0, 50) + '...')
    console.log('🔗 URL do chat:', `${API_BASE_URL}/chat`)
    
    try {
      const response = await fetch(`${API_BASE_URL}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        mode: 'cors',
        body: JSON.stringify({ question }),
        // Timeout de 30 segundos para chat
        signal: AbortSignal.timeout(30000)
      })
      
      console.log('📡 Resposta do chat:', response.status, response.statusText)
      
      if (!response.ok) {
        const errorText = await response.text()
        console.error('❌ Erro detalhado:', errorText)
        throw new Error(`Backend error: ${response.status} - ${errorText}`)
      }
      
      const data = await response.json()
      console.log('✅ Chat respondido com sucesso')
      return data
      
    } catch (error) {
      console.error('❌ Erro no chat:', error.name, error.message)
      throw error
    }
  },

  // Health check
  healthCheck: testConnection
}

// Log da configuração inicial
console.log(`
🚀 CONFIGURAÇÃO DA API
📍 Frontend URL: ${window.location.origin}
🔗 Backend URL: ${API_BASE_URL}
🌍 Ambiente: ${process.env.NODE_ENV}
`)

export default api