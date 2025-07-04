// ==========================================
// src/components/MessageInput.js
// ==========================================
import React, { useState, useRef } from 'react';
import { uploadFile } from '../utils/aiUtils';
import '../styles/MessageInput.css';

const MessageInput = ({ 
  inputValue, 
  setInputValue, 
  onSendMessage, 
  isTyping, 
  inputRef,
  onFileSelect // Callback para quando arquivo é processado
}) => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState('');
  const fileInputRef = useRef(null);

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleInputChange = (e) => {
    setInputValue(e.target.value);
    e.target.style.height = 'auto';
    e.target.style.height = e.target.scrollHeight + 'px';
  };

  const handleFileSelect = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    // Validações do arquivo
    if (file.size > 5 * 1024 * 1024) {
      alert('Arquivo muito grande. Máximo 5MB.');
      return;
    }

    const allowedTypes = [
      'application/pdf',
      'text/plain',
      'application/msword', 
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    ];

    if (!allowedTypes.includes(file.type)) {
      alert('Tipo de arquivo não suportado. Use PDF, DOC, DOCX ou TXT.');
      return;
    }

    setSelectedFile(file);
    setUploadStatus('Pronto para enviar');
  };

  const removeFile = () => {
    setSelectedFile(null);
    setUploadStatus('');
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleSend = async () => {
    // Se há arquivo, fazer upload primeiro
    if (selectedFile && !isUploading) {
      await handleFileUpload();
    }
    
    // Enviar mensagem de texto (se houver)
    if (inputValue.trim()) {
      onSendMessage();
    }
  };

  const handleFileUpload = async () => {
    if (!selectedFile) return;

    setIsUploading(true);
    setUploadStatus('Enviando arquivo...');

    try {
      const result = await uploadFile(selectedFile);
      
      // Sucesso no upload
      setUploadStatus('Arquivo processado!');
      
      // Adiciona mensagem informando sobre o upload
      const uploadMessage = `📎 Arquivo enviado: **${selectedFile.name}**\n\n${result.message || 'Arquivo processado com sucesso!'}`;
      
      // Chama callback se fornecido
      if (onFileSelect) {
        onFileSelect(selectedFile, result);
      }

      // Remove arquivo após 2 segundos
      setTimeout(() => {
        removeFile();
      }, 2000);

    } catch (error) {
      console.error('Erro no upload:', error);
      setUploadStatus('Erro no upload');
      alert(`Erro ao enviar arquivo: ${error.message}`);
      
      // Remove status de erro após 3 segundos
      setTimeout(() => {
        setUploadStatus('');
      }, 3000);
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="input-area">
      <div className="input-container">
        {/* Indicador de arquivo selecionado */}
        {selectedFile && (
          <div className="file-indicator">
            📎 {selectedFile.name.length > 20 
              ? selectedFile.name.substring(0, 20) + '...' 
              : selectedFile.name}
            {uploadStatus && (
              <span className="upload-status"> - {uploadStatus}</span>
            )}
            {!isUploading && (
              <button 
                className="remove-file" 
                onClick={removeFile}
                title="Remover arquivo"
              >
                ×
              </button>
            )}
          </div>
        )}

        {/* Botão de adicionar arquivo */}
        <button
          className={`add-file-button ${isUploading ? 'uploading' : ''}`}
          onClick={handleFileSelect}
          disabled={isTyping || isUploading}
          title="Adicionar arquivo (PDF, DOC, TXT)"
        >
          {isUploading ? '⏳' : '+'}
        </button>

        {/* Input de arquivo oculto */}
        <input
          ref={fileInputRef}
          type="file"
          className="file-input"
          onChange={handleFileChange}
          accept=".pdf,.doc,.docx,.txt"
        />

        {/* Input de texto */}
        <textarea
          ref={inputRef}
          className="message-input"
          placeholder="Pergunte alguma coisa ou envie um arquivo"
          value={inputValue}
          onChange={handleInputChange}
          onKeyPress={handleKeyPress}
          rows="1"
          disabled={isTyping || isUploading}
        />

        {/* Botão de enviar */}
        <button
          className={`send-button ${isUploading ? 'uploading' : ''}`}
          onClick={handleSend}
          disabled={isTyping || isUploading || (!inputValue.trim() && !selectedFile)}
          title="Enviar mensagem"
        >
          {isUploading ? '⏳' : '➤'}
        </button>
      </div>
    </div>
  );
};

export default MessageInput;