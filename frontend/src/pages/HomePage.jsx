import React from 'react';
import Layout from '../components/Layout/Layout';
import InteractionForm from '../components/InteractionForm/InteractionForm';
import ChatPanel from '../components/ChatPanel/ChatPanel';

const HomePage = () => {
  return (
    <Layout
      leftPanel={<InteractionForm />}
      rightPanel={<ChatPanel />}
    />
  );
};

export default HomePage;
