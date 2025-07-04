
// ==========================================
// src/components/ChatHeader.js
// ==========================================
import React from 'react';
import '../styles/ChatHeader.css';

const ChatHeader = ({ onToggleSidebar, sidebarVisible, onNewChat }) => {
  return (
    <div className="chat-header">
      <div className="chat-header-left">
        <button 
          className="sidebar-toggle-btn" 
          onClick={onToggleSidebar}
          title={sidebarVisible ? 'Esconder histórico' : 'Mostrar histórico'}
        >
          {sidebarVisible ? '◀' : '▶'}
        </button>
        <div className="chat-info">
          <div className="chat-title">🤖 Pensa.AI</div>
        </div>
      </div>
      
      <button className="new-chat-header-btn" onClick={onNewChat} title="Nova conversa">
        ✨ Nova Conversa
      </button>
    </div>
  );
};

export default ChatHeader;