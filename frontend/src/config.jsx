// Configuração inteligente que detecta o IP da rede automaticamente

export const API_CONFIG = {
  BASE_URLS: [],
  CURRENT_URL: null
}

// Função para obter o IP da máquina atual
function getCurrentIP() {
  // Pega o hostname da URL atual (ex: 172.29.213.100)
  const hostname = window.location.hostname
  
  // Se estiver rodando em IP da rede, usa o mesmo IP
  if (hostname !== 'localhost' && hostname !== '127.0.0.1') {
    return hostname
  }
  
  return null
}

// Função para gerar URLs possíveis
function generatePossibleURLs() {
  const currentIP = getCurrentIP()
  const urls = []
  
  // URLs baseadas no IP atual do frontend
  if (currentIP) {
    urls.push(`http://${currentIP}:8000`)
  }
  
  // URLs padrão
  urls.push('http://localhost:8000')
  urls.push('http://127.0.0.1:8000')
  
  // Se estiver rodando em rede, tenta outros IPs comuns
  if (currentIP && currentIP.startsWith('172.')) {
    // Tenta diferentes portas na mesma rede
    const baseIP = currentIP.substring(0, currentIP.lastIndexOf('.'))
    for (let i = 1; i <= 10; i++) {
      urls.push(`http://${baseIP}.${i}:8000`)
    }
  }
  
  return [...new Set(urls)] // Remove duplicatas
}

// Função para testar conectividade
export async function testConnection(url) {
  try {
    console.log(`🔍 Testando: ${url}`)
    const response = await fetch(`${url}/health`, {
      method: 'GET',
      signal: AbortSignal.timeout(3000)
    })
    
    if (response.ok) {
      console.log(`✅ Sucesso: ${url}`)
      return true
    }
  } catch (error) {
    console.log(`❌ Falhou: ${url} - ${error.message}`)
  }
  
  return false
}

// Função para encontrar URL que funciona
export async function findWorkingURL() {
  console.log('🌐 Detectando configuração de rede...')
  console.log(`Frontend rodando em: ${window.location.href}`)
  
  const possibleURLs = generatePossibleURLs()
  API_CONFIG.BASE_URLS = possibleURLs
  
  console.log('🔍 URLs a testar:', possibleURLs)
  
  for (const url of possibleURLs) {
    if (await testConnection(url)) {
      console.log(`✅ Backend encontrado: ${url}`)
      API_CONFIG.CURRENT_URL = url
      return url
    }
  }
  
  console.log('❌ Nenhum backend encontrado')
  return null
}

// Função para fazer requisições com fallback automático
export async function apiRequest(endpoint, options = {}) {
  // Se não temos URL, tentar encontrar uma
  if (!API_CONFIG.CURRENT_URL) {
    await findWorkingURL()
  }
  
  // Tentar com URL atual
  if (API_CONFIG.CURRENT_URL) {
    try {
      const response = await fetch(`${API_CONFIG.CURRENT_URL}${endpoint}`, {
        ...options,
        signal: AbortSignal.timeout(15000)
      })
      
      if (response.ok) {
        return response
      }
    } catch (error) {
      console.log(`❌ Falha na requisição para ${API_CONFIG.CURRENT_URL}`)
    }
  }
  
  // Se falhou, tentar encontrar nova URL
  const workingURL = await findWorkingURL()
  if (workingURL) {
    return fetch(`${workingURL}${endpoint}`, {
      ...options,
      signal: AbortSignal.timeout(15000)
    })
  }
  
  throw new Error(`
❌ Não foi possível conectar ao servidor!

🔧 POSSÍVEIS SOLUÇÕES:
1. Certifique-se que o backend está rodando
2. Execute: python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
3. Verifique se a porta 8000 está liberada no firewall

🌐 Frontend: ${window.location.hostname}
📋 URLs testadas: ${API_CONFIG.BASE_URLS.join(', ')}
  `)
}

// Função para obter status da conexão
export function getConnectionInfo() {
  return {
    frontendURL: window.location.href,
    backendURL: API_CONFIG.CURRENT_URL,
    testedURLs: API_CONFIG.BASE_URLS
  }
}