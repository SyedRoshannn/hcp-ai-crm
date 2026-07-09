import React, { useState } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { addChatMessage, updateExtractedData, setLoading, setError } from '../../redux/interactionSlice';
import api from '../../services/api';

const ChatPanel = () => {
  const { chat_history, loading } = useSelector((state) => state.interaction);
  const dispatch = useDispatch();
  const [inputText, setInputText] = useState('');

  const handleSend = async (e) => {
    e.preventDefault();
    const query = inputText.trim();
    if (!query || loading) return;

    // 1. Dispatch the user's message to Redux chat log
    dispatch(addChatMessage({
      sender: 'user',
      text: query
    }));

    setInputText('');
    dispatch(setLoading(true));
    dispatch(setError(null));

    try {
      // 2. Call POST /chat using Axios client
      const response = await api.post('/chat', { message: query });
      
      const { intent, selected_tool, extracted_data } = response.data;

      // 3. Update Redux store with the extracted data
      dispatch(updateExtractedData(extracted_data));

      // 4. Formulate a friendly AI response based on the output metadata
      const aiResponseText = `Successfully processed. Intent detected: "${intent}". Executed tool: "${selected_tool || 'none'}". Form details updated!`;
      dispatch(addChatMessage({
        sender: 'ai',
        text: aiResponseText
      }));

    } catch (err) {
      console.error(err);
      const errorMessage = err.response?.data?.detail || err.message || 'An error occurred during communication.';
      
      // 5. Update Redux with the error
      dispatch(setError(errorMessage));

      // 6. Append an error message bubble in the chat log
      dispatch(addChatMessage({
        sender: 'ai',
        text: `⚠️ Error: ${errorMessage}`
      }));
    } finally {
      dispatch(setLoading(false));
    }
  };

  return (
    <div className="chat-panel-container">
      <div className="chat-header">
        <div className="ai-assistant-avatar">🤖</div>
        <div>
          <h2 className="ai-title">AI Assistant</h2>
          <p className="ai-subtitle">Log Interaction details here via chat</p>
        </div>
      </div>

      <div className="chat-messages-container">
        {chat_history.map((msg, index) => (
          <div key={index} className={`chat-message-bubble ${msg.sender}-bubble`}>
            {msg.text}
          </div>
        ))}
        {loading && (
          <div className="chat-message-bubble ai-bubble loading-bubble">
            AI is thinking...
          </div>
        )}
      </div>

      <form className="chat-input-form" onSubmit={handleSend}>
        <textarea
          className="chat-textarea"
          placeholder={loading ? "AI is processing..." : "Describe Interaction..."}
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          disabled={loading}
          rows={2}
        />
        <button 
          className="chat-send-btn" 
          type="submit" 
          disabled={loading || !inputText.trim()}
        >
          ➔
        </button>
      </form>
    </div>
  );
};

export default ChatPanel;
