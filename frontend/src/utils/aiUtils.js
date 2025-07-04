// Configuração da API
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Detecta matéria baseada na mensagem
export const detectSubject = (message) => {
  const subjects = {
    'matemática': ['função', 'equação', 'derivada', 'integral', 'álgebra', 'geometria', 'trigonometria', 'cálculo'],
    'física': ['força', 'energia', 'movimento', 'velocidade', 'aceleração', 'gravidade', 'onda', 'luz'],
    'química': ['átomo', 'molécula', 'reação', 'ligação', 'elemento', 'tabela periódica', 'ph', 'ácido'],
    'biologia': ['célula', 'dna', 'evolução', 'fotossíntese', 'respiração', 'reprodução', 'genética'],
    'história': ['guerra', 'revolução', 'império', 'século', 'civilização', 'cultura', 'brasil'],
    'geografia': ['clima', 'relevo', 'população', 'país', 'continente', 'oceano', 'cidade'],
    'português': ['verbo', 'substantivo', 'sintaxe', 'literatura', 'texto', 'gramática', 'redação'],
    'inglês': ['verb', 'noun', 'grammar', 'vocabulary', 'pronunciation', 'english']
  };

  const messageLower = message.toLowerCase();
  for (const [subject, keywords] of Object.entries(subjects)) {
    if (keywords.some(keyword => messageLower.includes(keyword))) {
      return subject;
    }
  }
  return 'geral';
};

// Emoji para cada matéria
export const getSubjectEmoji = (subject) => {
  const emojis = {
    'matemática': '📊',
    'física': '⚡',
    'química': '🧪',
    'biologia': '🌱',
    'história': '📚',
    'geografia': '🌍',
    'português': '📝',
    'inglês': '🇺🇸',
    'geral': '🤖'
  };
  return emojis[subject] || '🤖';
};

// Upload de arquivo para o backend
export const uploadFile = async (file) => {
  try {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${API_BASE_URL}/upload`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Erro no upload do arquivo');
    }

    const result = await response.json();
    return result;
  } catch (error) {
    console.error('Erro no upload:', error);
    throw error;
  }
};

// Verifica status do backend
export const checkBackendHealth = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/health`);
    if (response.ok) {
      return await response.json();
    }
    return null;
  } catch (error) {
    console.error('Backend não disponível:', error);
    return null;
  }
};

// Gera resposta da IA - INTEGRADO COM BACKEND
export const getAIResponse = async (message) => {
  try {
    // Primeiro tenta usar o backend
    const response = await fetch(`${API_BASE_URL}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        question: message
      }),
    });

    if (response.ok) {
      const data = await response.json();
      return data.answer;
    } else {
      console.warn('Backend indisponível, usando fallback');
      throw new Error('Backend error');
    }
  } catch (error) {
    console.error('Erro ao conectar com backend:', error);
    
    // Fallback para resposta local se backend falhar
    const subject = detectSubject(message);
    const emoji = getSubjectEmoji(subject);

    const fallbackResponses = [
      `${emoji} **[MODO OFFLINE]** Interessante! Me conte: o que você já sabe sobre esse assunto?`,
      `${emoji} **[MODO OFFLINE]** Ótima pergunta! Qual seria o primeiro passo para resolver isso?`,
      `${emoji} **[MODO OFFLINE]** Vamos pensar juntos. Como você aplicaria isso na prática?`,
      `${emoji} **[MODO OFFLINE]** Você está no caminho certo! Que tal conectar com algo que já conhece?`,
      `${emoji} **[MODO OFFLINE]** Excelente! Qual seria o próximo passo lógico aqui?`,
    ];

    // Simula delay mesmo no fallback
    await new Promise(resolve => setTimeout(resolve, 1000));

    let response = fallbackResponses[Math.floor(Math.random() * fallbackResponses.length)];
    
    response += '\n\n⚠️ **Nota**: O backend está indisponível. Conecte-se à internet e verifique se o servidor está rodando para funcionalidade completa.';

    return response;
  }
};