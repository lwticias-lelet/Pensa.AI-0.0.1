// ==========================================
// src/components/MessageComponents.js
// ==========================================
import React from 'react';
import '../styles/MessageComponents.css';

// Componente de Mensagem Individual
export const Message = ({ message }) => {
  return (
    <div className={`message ${message.sender}`}>
      <div 
        className="message-content"
        dangerouslySetInnerHTML={{
          __html: message.text.replace(/\n/g, '<br>')
        }}
      />
    </div>
  );
};

// Componente Indicador de Digitação
export const TypingIndicator = () => {
  return (
    <div className="message ai">
      <div className="typing-indicator">
        Pensando...
        <div className="typing-dots">
          <div className="typing-dot"></div>
          <div className="typing-dot"></div>
          <div className="typing-dot"></div>
        </div>
      </div>
    </div>
  );
};

// Componente Área de Mensagens
export const MessagesArea = ({ messages, isTyping, messagesAreaRef }) => {
  return (
    <div className="messages-area" ref={messagesAreaRef}>
      {messages.map((message, index) => (
        <Message key={index} message={message} />
      ))}
      {isTyping && <TypingIndicator />}
    </div>
  );
};
