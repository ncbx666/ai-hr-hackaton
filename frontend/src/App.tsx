import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import './App.css';

// HR Pages
import HRDashboard from './pages/hr/HRDashboard';
import CreateInterview from './pages/hr/CreateInterview';
import ViewResults from './pages/hr/ViewResults';
import ViewRequirements from './pages/hr/ViewRequirements';

// Candidate Pages
import Welcome from './pages/candidate/Welcome';
import Registration from './pages/candidate/Registration';
import Waiting from './pages/candidate/Waiting';
import Interview from './pages/candidate/Interview';
import Completion from './pages/candidate/Completion';

function App() {
  return (
    <Router>
      <div className="App">
        <Routes>
          {/* Главная страница - редирект на HR панель */}
          <Route path="/" element={<Navigate to="/hr/dashboard" replace />} />
          
          {/* HR Routes */}
          <Route path="/hr/dashboard" element={<HRDashboard />} />
          <Route path="/hr/create" element={<CreateInterview />} />
          <Route path="/hr/results" element={<ViewResults />} />
          <Route path="/hr/requirements/:id" element={<ViewRequirements />} />
          
          {/* Candidate Routes */}
          <Route path="/candidate/:sessionId/welcome" element={<Welcome />} />
          <Route path="/candidate/:sessionId/registration" element={<Registration />} />
          <Route path="/candidate/:sessionId/waiting" element={<Waiting />} />
          <Route path="/candidate/:sessionId/interview" element={<Interview />} />
          <Route path="/candidate/:sessionId/completion" element={<Completion />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
