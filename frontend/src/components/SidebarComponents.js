// ==========================================
// src/components/SidebarComponents.js
// ==========================================
import React from 'react';
import '../styles/SidebarComponents.css';

// Componente Item do Histórico
export const HistoryItem = ({ chat, isActive, onClick }) => {
  const formatDate = (timestamp) => {
    return new Date(timestamp).toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <div
      className={`history-item ${isActive ? 'active' : ''}`}
      onClick={onClick}
    >
      <div>{chat.title}</div>
      <div className="history-meta">{formatDate(chat.timestamp)}</div>
    </div>
  );
};

// Botão Toggle do Sidebar
export const SidebarToggle = ({ isVisible, onToggle }) => {
  return (
    <button 
      className="sidebar-toggle" 
      onClick={onToggle}
      title={isVisible ? 'Esconder histórico' : 'Mostrar histórico'}
    >
      {isVisible ? '◀' : '▶'}
    </button>
  );
};

// Componente Overlay para Mobile
export const SidebarOverlay = ({ isVisible, onClose }) => {
  if (!isVisible) return null;
  
  return (
    <div 
      className="sidebar-overlay visible" 
      onClick={onClose}
      aria-label="Fechar menu"
    />
  );
};

// Componente Sidebar do Histórico
export const Sidebar = ({ 
  chatHistory, 
  currentChatId, 
  onLoadChat, 
  onClearHistory, 
  onNewChat,
  isVisible,
  onToggleSidebar // Nova prop para fechar o sidebar
}) => {
  return (
    <>
      <div className={`sidebar ${isVisible ? 'visible' : 'hidden'}`}>
        <div className="sidebar-header">
          <div className="sidebar-header-content">
            <span>💬</span>
            <span className="sidebar-title">Histórico</span>
          </div>
          <button className="new-chat-btn" onClick={onNewChat} title="Nova conversa">
            ✨ Nova
          </button>
        </div>
        
        <div className="history-list">
          {chatHistory.length === 0 ? (
            <div className="no-history">
              Nenhuma conversa ainda
            </div>
          ) : (
            chatHistory.map(chat => (
              <HistoryItem
                key={chat.id}
                chat={chat}
                isActive={chat.id === currentChatId}
                onClick={() => onLoadChat(chat)}
              />
            ))
          )}
        </div>
        
        <button className="clear-history" onClick={onClearHistory}>
          🗑️ Limpar Histórico
        </button>
      </div>
      
      {/* Overlay para fechar sidebar em mobile */}
      <SidebarOverlay 
        isVisible={isVisible} 
        onClose={onToggleSidebar} 
      />
    </>
  );
};