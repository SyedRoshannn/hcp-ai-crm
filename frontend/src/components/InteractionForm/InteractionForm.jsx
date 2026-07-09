import React from 'react';
import { useSelector } from 'react-redux';

const InteractionForm = () => {
  const { extracted_data } = useSelector((state) => state.interaction);

  return (
    <div className="interaction-form-card">
      <h2 className="form-title">Log HCP Interaction</h2>
      
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
          <input
            type="text"
            className="form-input"
            placeholder="Enter names or search..."
            value={extracted_data.attendees ? extracted_data.attendees.join(', ') : ''}
            readOnly
          />
        </div>

        <div className="form-group">
          <label className="form-label">Topics Discussed</label>
          <textarea
            className="form-textarea"
            placeholder="Enter key discussion points..."
            value={extracted_data.topics_discussed || ''}
            readOnly
            rows={4}
          />
        </div>

        <div className="voice-note-btn-container">
          <button className="voice-note-btn" type="button" disabled>
            <span className="mic-icon">🎙️</span> Summarize from Voice Note (Requires Consent)
          </button>
        </div>
      </div>

      <div className="form-section">
        <h3 className="section-title">Materials Shared / Samples Distributed</h3>
        
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
      </div>
    </div>
  );
};

export default InteractionForm;
