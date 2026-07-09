import React, { useEffect, useRef, useState } from 'react';
import { useSelector } from 'react-redux';

const InteractionForm = () => {
  const { extracted_data } = useSelector((state) => state.interaction);
  const prevDataRef = useRef({});
  const [changedFields, setChangedFields] = useState({});

  // Form field update highlighting effect
  useEffect(() => {
    if (Object.keys(prevDataRef.current).length > 0) {
      const changed = {};
      Object.keys(extracted_data).forEach((key) => {
        const prevVal = prevDataRef.current[key];
        const curVal = extracted_data[key];
        if (JSON.stringify(prevVal) !== JSON.stringify(curVal)) {
          changed[key] = true;
        }
      });
      if (Object.keys(changed).length > 0) {
        setChangedFields(changed);
        const timer = setTimeout(() => setChangedFields({}), 2000);
        return () => clearTimeout(timer);
      }
    }
    prevDataRef.current = { ...extracted_data };
  }, [extracted_data]);

  // Helper to format sentiment classes
  const getSentimentBadgeClass = (sentiment) => {
    if (!sentiment) return 'sentiment-badge-empty';
    const s = sentiment.toLowerCase();
    if (s === 'positive') return 'sentiment-badge-positive';
    if (s === 'negative') return 'sentiment-badge-negative';
    return 'sentiment-badge-neutral';
  };

  return (
    <div className="interaction-form-card">
      <div className="form-header-container">
        <h2 className="form-title">Log HCP Interaction</h2>
        <span className="form-subtitle-badge">Read-Only View</span>
      </div>
      
      {/* 1. Core Interaction Details */}
      <div className="form-section">
        <h3 className="section-title">Interaction Details</h3>
        
        <div className="form-grid">
          <div className={`form-group ${changedFields.hcp_name ? 'highlight-animation' : ''}`}>
            <label className="form-label">HCP Name</label>
            <input
              type="text"
              className="form-input"
              placeholder="E.g., Dr. Smith"
              value={extracted_data.hcp_name || ''}
              readOnly
            />
          </div>
          
          <div className={`form-group ${changedFields.interaction_type ? 'highlight-animation' : ''}`}>
            <label className="form-label">Interaction Type</label>
            <div className="form-input-placeholder">
              {extracted_data.interaction_type || 'Meeting'}
            </div>
          </div>
        </div>

        <div className="form-grid" style={{ marginTop: '16px' }}>
          <div className={`form-group ${changedFields.date ? 'highlight-animation' : ''}`}>
            <label className="form-label">Date</label>
            <input
              type="text"
              className="form-input"
              placeholder="MM/DD/YYYY"
              value={extracted_data.date || ''}
              readOnly
            />
          </div>
          
          <div className={`form-group ${changedFields.time ? 'highlight-animation' : ''}`}>
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
      </div>

      {/* 2. Meeting Details */}
      <div className="form-section">
        <h3 className="section-title">Meeting Details</h3>
        
        <div className={`form-group ${changedFields.attendees ? 'highlight-animation' : ''}`}>
          <label className="form-label">Attendees</label>
          {extracted_data.attendees && extracted_data.attendees.length > 0 ? (
            <ul className="list-tags">
              {extracted_data.attendees.map((item, idx) => (
                <li key={idx} className="attendee-chip">{item}</li>
              ))}
            </ul>
          ) : (
            <div className="empty-field-placeholder">No attendees recorded.</div>
          )}
        </div>

        <div className={`form-group ${changedFields.topics_discussed ? 'highlight-animation' : ''}`} style={{ marginTop: '16px' }}>
          <label className="form-label">Topics Discussed</label>
          {extracted_data.topics_discussed && extracted_data.topics_discussed.length > 0 ? (
            <ul className="list-tags">
              {extracted_data.topics_discussed.map((item, idx) => (
                <li key={idx} className="topic-chip">{item}</li>
              ))}
            </ul>
          ) : (
            <div className="empty-field-placeholder">No topics discussed.</div>
          )}
        </div>
      </div>

      {/* 3. Materials Shared and Samples Distributed */}
      <div className="form-section">
        <h3 className="section-title">Materials & Samples</h3>
        
        <div className="form-grid">
          <div className={`materials-sub-section ${changedFields.materials_shared ? 'highlight-animation' : ''}`}>
            <div className="materials-header">
              <span className="sub-section-title">Materials Shared</span>
            </div>
            {extracted_data.materials_shared && extracted_data.materials_shared.length > 0 ? (
              <ul className="materials-chips-list">
                {extracted_data.materials_shared.map((m, idx) => (
                  <li key={idx} className="material-chip">{m}</li>
                ))}
              </ul>
            ) : (
              <div className="empty-field-placeholder">No materials shared.</div>
            )}
          </div>

          <div className={`materials-sub-section ${changedFields.samples_distributed ? 'highlight-animation' : ''}`}>
            <div className="materials-header">
              <span className="sub-section-title">Samples Distributed</span>
            </div>
            {extracted_data.samples_distributed && extracted_data.samples_distributed.length > 0 ? (
              <ul className="materials-chips-list">
                {extracted_data.samples_distributed.map((s, idx) => (
                  <li key={idx} className="sample-chip">{s}</li>
                ))}
              </ul>
            ) : (
              <div className="empty-field-placeholder">No samples distributed.</div>
            )}
          </div>
        </div>
      </div>

      {/* 4. Sentiment and Outcomes */}
      <div className="form-section">
        <h3 className="section-title">Sentiment & Outcomes</h3>
        
        <div className="form-grid">
          <div className={`form-group ${changedFields.sentiment ? 'highlight-animation' : ''}`}>
            <label className="form-label">HCP Sentiment</label>
            <div style={{ marginTop: '4px' }}>
              <span className={`sentiment-badge ${getSentimentBadgeClass(extracted_data.sentiment)}`}>
                {extracted_data.sentiment || 'None'}
              </span>
            </div>
          </div>
          
          <div className={`form-group ${changedFields.outcomes ? 'highlight-animation' : ''}`}>
            <label className="form-label">Outcomes</label>
            <input
              type="text"
              className="form-input"
              placeholder="Key outcomes..."
              value={extracted_data.outcomes || ''}
              readOnly
            />
          </div>
        </div>

        <div className={`form-group ${changedFields.follow_up_actions ? 'highlight-animation' : ''}`} style={{ marginTop: '16px' }}>
          <label className="form-label">Follow-up Actions</label>
          {extracted_data.follow_up_actions && extracted_data.follow_up_actions.length > 0 ? (
            <ul className="list-tags">
              {extracted_data.follow_up_actions.map((item, idx) => (
                <li key={idx} className="follow-up-chip">{item}</li>
              ))}
            </ul>
          ) : (
            <div className="empty-field-placeholder">No follow-up actions recorded.</div>
          )}
        </div>
      </div>
    </div>
  );
};

export default InteractionForm;
