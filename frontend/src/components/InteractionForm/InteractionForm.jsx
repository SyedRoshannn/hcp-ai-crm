import React from 'react';
import { useSelector } from 'react-redux';

const InteractionForm = () => {
  const { extracted_data } = useSelector((state) => state.interaction);

  return (
    <div className="interaction-form-card">
      <div className="form-header-container">
        <h2 className="form-title">Log HCP Interaction</h2>
      </div>
      
      {/* 1. Core Interaction Details */}
      <div className="form-section">
        <h3 className="section-title">Interaction Details</h3>
        
        <div className="form-grid">
          <div className="form-group">
            <label className="form-label">HCP Name</label>
            <input
              type="text"
              className="form-input"
              placeholder="Search or select HCP..."
              value={extracted_data.hcp_name || ''}
              readOnly
            />
          </div>
          
          <div className="form-group">
            <label className="form-label">Interaction Type</label>
            <select
              className="form-select"
              value={extracted_data.interaction_type || 'Meeting'}
              disabled
            >
              <option value="Meeting">Meeting</option>
              <option value="Call">Call</option>
              <option value="Email">Email</option>
              <option value="Seminar">Seminar</option>
              <option value="Presentation">Presentation</option>
            </select>
          </div>
        </div>

        <div className="form-grid">
          <div className="form-group">
            <label className="form-label">Date</label>
            <input
              type="text"
              className="form-input"
              placeholder="MM/DD/YYYY"
              value={extracted_data.date || ''}
              readOnly
            />
          </div>
          
          <div className="form-group">
            <label className="form-label">Time</label>
            <input
              type="text"
              className="form-input"
              placeholder="HH:MM AM/PM"
              value={extracted_data.time || ''}
              readOnly
            />
          </div>
        </div>

        <div className="form-group">
          <label className="form-label">Attendees</label>
          {extracted_data.attendees && extracted_data.attendees.length > 0 ? (
            <ul className="list-tags">
              {extracted_data.attendees.map((item, idx) => (
                <li key={idx}>{item}</li>
              ))}
            </ul>
          ) : (
            <input
              type="text"
              className="form-input"
              placeholder="No attendees added..."
              value=""
              readOnly
            />
          )}
        </div>

        <div className="form-group">
          <label className="form-label">Topics Discussed</label>
          {extracted_data.topics_discussed && extracted_data.topics_discussed.length > 0 ? (
            <ul className="list-tags">
              {extracted_data.topics_discussed.map((item, idx) => (
                <li key={idx} style={{ backgroundColor: '#f0fdf4', color: '#166534', borderColor: '#bbf7d0' }}>{item}</li>
              ))}
            </ul>
          ) : (
            <input
              type="text"
              className="form-input"
              placeholder="No topics added..."
              value=""
              readOnly
            />
          )}
        </div>

        <div className="voice-note-btn-container">
          <button className="voice-note-btn" type="button" disabled>
            <span className="mic-icon">🎙️</span> Summarize from Voice Note (Requires Consent)
          </button>
        </div>
      </div>

      {/* 2. Sentiment and Outcomes */}
      <div className="form-section">
        <h3 className="section-title">Sentiment & Outcomes</h3>
        
        <div className="form-grid">
          <div className="form-group">
            <label className="form-label">HCP Sentiment</label>
            <input
              type="text"
              className="form-input"
              placeholder="E.g., Positive, Neutral, Negative"
              value={extracted_data.sentiment || ''}
              readOnly
              style={{
                fontWeight: 'bold',
                color: extracted_data.sentiment?.toLowerCase() === 'positive' ? '#166534' : 
                       extracted_data.sentiment?.toLowerCase() === 'negative' ? '#991b1b' : '#1e293b'
              }}
            />
          </div>
          
          <div className="form-group">
            <label className="form-label">Outcomes</label>
            <input
              type="text"
              className="form-input"
              placeholder="Key outcome or agreements..."
              value={extracted_data.outcomes || ''}
              readOnly
            />
          </div>
        </div>

        <div className="form-group">
          <label className="form-label">Follow-up Actions</label>
          {extracted_data.follow_up_actions && extracted_data.follow_up_actions.length > 0 ? (
            <ul className="list-tags">
              {extracted_data.follow_up_actions.map((item, idx) => (
                <li key={idx} style={{ backgroundColor: '#fff7ed', color: '#c2410c', borderColor: '#ffedd5' }}>{item}</li>
              ))}
            </ul>
          ) : (
            <input
              type="text"
              className="form-input"
              placeholder="No follow-up actions recorded..."
              value=""
              readOnly
            />
          )}
        </div>
      </div>

      {/* 3. Materials and Samples */}
      <div className="form-section">
        <h3 className="section-title">Materials Shared & Samples Distributed</h3>
        
        <div className="form-grid">
          <div className="materials-sub-section">
            <div className="materials-header">
              <span className="sub-section-title">Materials Shared</span>
              <button className="search-add-btn" type="button" disabled>
                🔍 Search/Add
              </button>
            </div>
            
            <div className="materials-list-empty">
              {extracted_data.materials_shared && extracted_data.materials_shared.length > 0 ? (
                <ul className="materials-list">
                  {extracted_data.materials_shared.map((m, idx) => (
                    <li key={idx}>{m}</li>
                  ))}
                </ul>
              ) : (
                <span className="empty-text">No materials added.</span>
              )}
            </div>
          </div>

          <div className="materials-sub-section">
            <div className="materials-header">
              <span className="sub-section-title">Samples Distributed</span>
              <button className="search-add-btn" type="button" disabled>
                🔍 Search/Add
              </button>
            </div>
            
            <div className="materials-list-empty">
              {extracted_data.samples_distributed && extracted_data.samples_distributed.length > 0 ? (
                <ul className="materials-list">
                  {extracted_data.samples_distributed.map((s, idx) => (
                    <li key={idx}>{s}</li>
                  ))}
                </ul>
              ) : (
                <span className="empty-text">No samples distributed.</span>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default InteractionForm;
