// Gera título do chat
export const generateChatTitle = (messages) => {
  const firstMessage = messages.find(m => m.sender === 'user');
  if (!firstMessage) return 'Nova Conversa';

  let title = firstMessage.text.substring(0, 40);
  if (firstMessage.text.length > 40) title += '...';
  return title;
};

// Salva chat no localStorage
export const saveChatToHistory = (chatId, messages) => {
  if (messages.length < 2) return null;

  const chatData = {
    id: chatId || Date.now(),
    title: generateChatTitle(messages),
    messages: messages,
    timestamp: Date.now()
  };

  let history = JSON.parse(localStorage.getItem('chatHistory') || '[]');

  if (chatId) {
    history = history.filter(chat => chat.id !== chatId);
  }

  history.unshift(chatData);
  history = history.slice(0, 50); // Limita a 50 conversas

  localStorage.setItem('chatHistory', JSON.stringify(history));
  return chatData.id;
};

// Carrega histórico do localStorage
export const loadChatHistory = () => {
  return JSON.parse(localStorage.getItem('chatHistory') || '[]');
};

// Limpa todo o histórico
export const clearChatHistory = () => {
  localStorage.removeItem('chatHistory');
};

// Carrega mensagem inicial
export const getInitialMessage = () => {
  return {
    text: `🤖 Olá! Sou o Pensa.AI, seu assistente educacional.

💡 **Minha missão:** Te ajudar a aprender através do pensamento crítico, sem dar respostas prontas.

🎯 Digite sua dúvida ou tema de estudo para começarmos!`,
    sender: 'ai',
    timestamp: Date.now()
  };
};