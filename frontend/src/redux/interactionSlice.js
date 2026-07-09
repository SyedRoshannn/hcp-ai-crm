import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  extracted_data: {
    hcp_name: '',
    interaction_type: 'Meeting',
    date: '',
    time: '',
    attendees: [],
    topics_discussed: '',
    materials_shared: [],
    samples_distributed: [],
    sentiment: '',
    outcomes: '',
    follow_up_actions: []
  },
  interaction_id: null,
  loading: false,
  error: null,
  chat_history: [
    {
      sender: 'ai',
      text: "Log interaction details here (e.g., 'Met Dr. Smith, discussed Prodo-X efficacy, positive sentiment, shared brochure') or ask for help."
    }
  ]
};

const interactionSlice = createSlice({
  name: 'interaction',
  initialState,
  reducers: {
    updateExtractedData: (state, action) => {
      state.extracted_data = { ...state.extracted_data, ...action.payload };
    },
    setInteractionId: (state, action) => {
      state.interaction_id = action.payload;
    },
    addChatMessage: (state, action) => {
      state.chat_history.push(action.payload);
    },
    setLoading: (state, action) => {
      state.loading = action.payload;
    },
    setError: (state, action) => {
      state.error = action.payload;
    },
    resetState: (state) => {
      state.extracted_data = initialState.extracted_data;
      state.chat_history = initialState.chat_history;
      state.interaction_id = null;
      state.error = null;
      state.loading = false;
    }
  }
});

export const { updateExtractedData, setInteractionId, addChatMessage, setLoading, setError, resetState } = interactionSlice.actions;
export default interactionSlice.reducer;
