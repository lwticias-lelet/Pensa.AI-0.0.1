import { useState } from 'react';
import { getAIResponse } from '../utils/aiUtils';
import { 
  saveChatToHistory, 
  loadChatHistory, 
  clearChatHistory, 
  getInitialMessage 
} from '../utils/storageUtils';

// Hook customizado para lógica do chat
export const useChat = () => {
  const [messages, setMessages] = useState([]);
  const [currentChatId, setCurrentChatId] = useState(null);
  const [isTyping, setIsTyping] = useState(false);
  const [chatHistory, setChatHistory] = useState([]);

  // Carrega mensagem inicial
  const loadInitialMessage = () => {
    const initialMessage = getInitialMessage();
    setMessages([initialMessage]);
  };

  // Envia mensagem
  const sendMessage = async (message) => {
    if (!message.trim() || isTyping) return;

    // Adiciona mensagem do usuário
    const userMessage = {
      text: message,
      sender: 'user',
      timestamp: Date.now()
    };

    setMessages(prev => [...prev, userMessage]);
    setIsTyping(true);

    try {
      // Obter resposta da IA
      const response = await getAIResponse(message);
      
      const aiMessage = {
        text: response,
        sender: 'ai',
        timestamp: Date.now()
      };

      setMessages(prev => [...prev, aiMessage]);
      
      // Salva no histórico
      const newMessages = [...messages, userMessage, aiMessage];
      saveCurrentChat(newMessages);
    } catch (error) {
      const errorMessage = {
        text: '😅 Ops! Algo deu errado. Tente novamente.',
        sender: 'ai',
        timestamp: Date.now()
      };
      setMessages(prev => [...prev, errorMessage]);
      console.error('Erro ao obter resposta:', error);
    } finally {
      setIsTyping(false);
    }
  };

  // Salva chat atual
  const saveCurrentChat = (messagesToSave = messages) => {
    const newChatId = saveChatToHistory(currentChatId, messagesToSave);
    if (newChatId) {
      setCurrentChatId(newChatId);
      loadHistory();
    }
  };

  // Carrega histórico
  const loadHistory = () => {
    const history = loadChatHistory();
    setChatHistory(history);
  };

  // Carrega chat específico
  const loadChat = (chatData) => {
    setMessages([...chatData.messages]);
    setCurrentChatId(chatData.id);
    loadHistory();
  };

  // Novo chat
  const newChat = () => {
    setMessages([]);
    setCurrentChatId(null);
    loadInitialMessage();
    loadHistory();
  };

  // Limpa histórico
  const clearAllHistory = () => {
    if (window.confirm('Tem certeza que deseja limpar todo o histórico?')) {
      clearChatHistory();
      loadHistory();
      newChat();
    }
  };

  return {
    messages,
    currentChatId,
    isTyping,
    chatHistory,
    sendMessage,
    loadHistory,
    loadChat,
    newChat,
    clearAllHistory,
    loadInitialMessage
  };
};