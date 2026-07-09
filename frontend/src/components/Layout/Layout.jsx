import React from 'react';

const Layout = ({ leftPanel, rightPanel }) => {
  return (
    <div className="app-container">
      <div className="left-panel-container">
        {leftPanel}
      </div>
      <div className="right-panel-container">
        {rightPanel}
      </div>
    </div>
  );
};

export default Layout;
