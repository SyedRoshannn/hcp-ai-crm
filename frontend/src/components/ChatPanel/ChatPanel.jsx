import React, { useState, useRef, useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { addChatMessage, updateExtractedData, setLoading, setError } from '../../redux/interactionSlice';
import api from '../../services/api';

const ChatPanel = () => {
  const { chat_history, loading } = useSelector((state) => state.interaction);
  const dispatch = useDispatch();
  const [inputText, setInputText] = useState('');
  const messagesEndRef = useRef(null);

  // Auto scroll chat to the bottom on new message
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chat_history, loading]);

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

      // 4. Formulate a natural conversational response
      let aiResponseText = `✅ Interaction details parsed successfully.\n\n`;
      aiResponseText += `I extracted the following details:\n`;
      
      if (extracted_data.hcp_name) aiResponseText += `• **Doctor**: ${extracted_data.hcp_name}\n`;
      if (extracted_data.interaction_type) aiResponseText += `• **Interaction**: ${extracted_data.interaction_type}\n`;
      if (extracted_data.date) aiResponseText += `• **Date**: ${extracted_data.date}\n`;
      if (extracted_data.time) aiResponseText += `• **Time**: ${extracted_data.time}\n`;
      
      if (extracted_data.attendees && extracted_data.attendees.length > 0) {
        aiResponseText += `• **Attendees**: ${extracted_data.attendees.join(', ')}\n`;
      }
      if (extracted_data.topics_discussed && extracted_data.topics_discussed.length > 0) {
        aiResponseText += `• **Topics**: ${extracted_data.topics_discussed.join(', ')}\n`;
      }
      if (extracted_data.materials_shared && extracted_data.materials_shared.length > 0) {
        aiResponseText += `• **Materials Shared**: ${extracted_data.materials_shared.join(', ')}\n`;
      }
      if (extracted_data.samples_distributed && extracted_data.samples_distributed.length > 0) {
        aiResponseText += `• **Samples Distributed**: ${extracted_data.samples_distributed.join(', ')}\n`;
      }
      if (extracted_data.sentiment) aiResponseText += `• **Sentiment**: ${extracted_data.sentiment}\n`;
      if (extracted_data.outcomes) aiResponseText += `• **Outcomes**: ${extracted_data.outcomes}\n`;
      if (extracted_data.follow_up_actions && extracted_data.follow_up_actions.length > 0) {
        aiResponseText += `• **Follow-up Actions**: ${extracted_data.follow_up_actions.join(', ')}\n`;
      }

      aiResponseText += `\nYour interaction form has been updated automatically.\n\n`;
      aiResponseText += `Would you like to add a follow-up action or make any edits?`;

      dispatch(addChatMessage({
        sender: 'ai',
        text: aiResponseText
      }));

    } catch (err) {
      console.error(err);
      const errorMessage = err.response?.data?.detail || err.message || 'An error occurred during communication.';
      
      // Update Redux with the error
      dispatch(setError(errorMessage));

      // Append an error message bubble in the chat log
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
          <div className="chat-message-bubble ai-bubble">
            <div className="typing-indicator">
              <div className="typing-dot"></div>
              <div className="typing-dot"></div>
              <div className="typing-dot"></div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
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
