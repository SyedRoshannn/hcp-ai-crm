import React, { useState, useRef, useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { addChatMessage, updateExtractedData, setInteractionId, setMemory, setLoading, setError } from '../../redux/interactionSlice';
import api from '../../services/api';

const MicIcon = ({ className }) => (
  <svg 
    xmlns="http://www.w3.org/2000/svg" 
    viewBox="0 0 24 24" 
    fill="none" 
    stroke="currentColor" 
    strokeWidth="2" 
    strokeLinecap="round" 
    strokeLinejoin="round" 
    className={className}
    style={{ width: '18px', height: '18px' }}
  >
    <path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z" />
    <path d="M19 10v1a7 7 0 0 1-14 0v-1" />
    <line x1="12" x2="12" y1="19" y2="22" />
  </svg>
);

const SendIcon = () => (
  <svg 
    xmlns="http://www.w3.org/2000/svg" 
    viewBox="0 0 24 24" 
    fill="none" 
    stroke="currentColor" 
    strokeWidth="2" 
    strokeLinecap="round" 
    strokeLinejoin="round"
    style={{ width: '18px', height: '18px' }}
  >
    <line x1="22" x2="11" y1="2" y2="13" />
    <polygon points="22 2 15 22 11 13 2 9 22 2" />
  </svg>
);

const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
const isSupported = !!SpeechRecognition;

const ChatPanel = () => {
  const { chat_history, loading, extracted_data, interaction_id, last_intent, last_tool, last_response } = useSelector((state) => state.interaction);
  const dispatch = useDispatch();
  const [inputText, setInputText] = useState('');
  const [isListening, setIsListening] = useState(false);
  const [recognitionError, setRecognitionError] = useState('');
  
  const messagesEndRef = useRef(null);
  const textareaRef = useRef(null);
  const recognitionRef = useRef(null);
  const transcriptRef = useRef('');

  // Auto scroll chat to the bottom on new message
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chat_history, loading]);

  // Initialize Speech Recognition on Mount
  useEffect(() => {
    if (isSupported) {
      const rec = new SpeechRecognition();
      rec.lang = 'en-US';
      rec.continuous = false;
      rec.interimResults = true;

      rec.onstart = () => {
        setIsListening(true);
        setRecognitionError('');
      };

      rec.onresult = (event) => {
        const transcript = Array.from(event.results)
          .map(result => result[0])
          .map(result => result.transcript)
          .join('');
        
        transcriptRef.current = transcript;
        setInputText(transcript);
      };

      rec.onerror = (event) => {
        console.error('Speech recognition error:', event.error);
        setIsListening(false);
        if (event.error === 'not-allowed') {
          setRecognitionError('Microphone access denied.');
        } else if (event.error === 'no-speech') {
          setRecognitionError('No speech detected.');
        } else {
          setRecognitionError(`Speech recognition error: ${event.error}`);
        }
      };

      rec.onend = () => {
        setIsListening(false);
        const finalQuery = transcriptRef.current.trim();
        if (finalQuery) {
          handleSend(null, finalQuery);
          transcriptRef.current = '';
        }
        // Auto-focus textarea after recording
        textareaRef.current?.focus();
      };

      recognitionRef.current = rec;
    }

    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.abort();
      }
    };
  }, []);

  const toggleListening = () => {
    if (!isSupported || loading) return;

    if (isListening) {
      recognitionRef.current?.stop();
    } else {
      setInputText('');
      transcriptRef.current = '';
      setRecognitionError('');
      try {
        recognitionRef.current?.start();
      } catch (err) {
        console.error(err);
      }
    }
  };

  const handleSend = async (e, textOverride = '') => {
    if (e) e.preventDefault();
    const query = (textOverride || inputText).trim();
    if (!query || loading) return;

    // 1. Dispatch the user's message to Redux chat log
    dispatch(addChatMessage({
      sender: 'user',
      text: query
    }));

    setInputText('');
    dispatch(setLoading(true));
    dispatch(setError(null));
    setRecognitionError('');

    try {
      // 2. Call POST /chat passing state variables including memory tracking
      const response = await api.post('/chat', { 
        message: query,
        extracted_data: extracted_data,
        interaction_id: interaction_id,
        last_intent: last_intent,
        last_tool: last_tool,
        last_response: last_response
      });
      
      const { 
        intent, 
        selected_tool, 
        extracted_data: new_extracted_data, 
        response: ai_response, 
        interaction_id: new_interaction_id,
        last_intent: new_last_intent,
        last_tool: new_last_tool,
        last_response: new_last_response
      } = response.data;

      // 3. Update Redux store
      dispatch(updateExtractedData(new_extracted_data));
      if (new_interaction_id !== undefined) {
        dispatch(setInteractionId(new_interaction_id));
      }
      dispatch(setMemory({
        last_intent: new_last_intent,
        last_tool: new_last_tool,
        last_response: new_last_response
      }));

      // 4. Determine AI message response text (prefer backend-generated responses)
      let aiResponseText = ai_response;
      if (!aiResponseText) {
        aiResponseText = `✅ Interaction details parsed successfully.\n\n`;
        aiResponseText += `I extracted the following details:\n`;
        
        if (new_extracted_data.hcp_name) aiResponseText += `• **Doctor**: ${new_extracted_data.hcp_name}\n`;
        if (new_extracted_data.interaction_type) aiResponseText += `• **Interaction**: ${new_extracted_data.interaction_type}\n`;
        if (new_extracted_data.date) aiResponseText += `• **Date**: ${new_extracted_data.date}\n`;
        if (new_extracted_data.time) aiResponseText += `• **Time**: ${new_extracted_data.time}\n`;
        
        if (new_extracted_data.attendees && new_extracted_data.attendees.length > 0) {
          aiResponseText += `• **Attendees**: ${new_extracted_data.attendees.join(', ')}\n`;
        }
        if (new_extracted_data.topics_discussed && new_extracted_data.topics_discussed.length > 0) {
          aiResponseText += `• **Topics**: ${new_extracted_data.topics_discussed.join(', ')}\n`;
        }
        if (new_extracted_data.materials_shared && new_extracted_data.materials_shared.length > 0) {
          aiResponseText += `• **Materials Shared**: ${new_extracted_data.materials_shared.join(', ')}\n`;
        }
        if (new_extracted_data.samples_distributed && new_extracted_data.samples_distributed.length > 0) {
          aiResponseText += `• **Samples Distributed**: ${new_extracted_data.samples_distributed.join(', ')}\n`;
        }
        if (new_extracted_data.sentiment) aiResponseText += `• **Sentiment**: ${new_extracted_data.sentiment}\n`;
        if (new_extracted_data.outcomes) aiResponseText += `• **Outcomes**: ${new_extracted_data.outcomes}\n`;
        if (new_extracted_data.follow_up_actions && new_extracted_data.follow_up_actions.length > 0) {
          aiResponseText += `• **Follow-up Actions**: ${new_extracted_data.follow_up_actions.join(', ')}\n`;
        }

        aiResponseText += `\nYour interaction form has been updated automatically.\n\n`;
        aiResponseText += `Would you like to add a follow-up action or make any edits?`;
      }

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

      {recognitionError && (
        <div className="chat-speech-error">
          ⚠️ {recognitionError}
        </div>
      )}

      <form className="chat-input-form" onSubmit={(e) => handleSend(e)}>
        <textarea
          ref={textareaRef}
          className="chat-textarea"
          placeholder={
            isListening 
              ? "Listening..." 
              : loading 
                ? "AI is processing..." 
                : "Describe Interaction..."
          }
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          disabled={loading || isListening}
          rows={2}
        />
        <div className="chat-controls">
          <button
            type="button"
            className={`chat-mic-btn ${isListening ? 'listening' : ''} ${!isSupported ? 'unsupported' : ''}`}
            onClick={toggleListening}
            disabled={loading || !isSupported}
            title={!isSupported ? "Speech recognition is not supported in this browser." : isListening ? "Stop listening" : "Start voice input"}
            aria-label="Toggle voice input"
          >
            <MicIcon className={isListening ? "pulse-icon" : ""} />
          </button>
          <button 
            className="chat-send-btn" 
            type="submit" 
            disabled={loading || isListening || !inputText.trim()}
            aria-label="Send message"
          >
            <SendIcon />
          </button>
        </div>
      </form>
    </div>
  );
};

export default ChatPanel;
