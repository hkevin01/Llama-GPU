import { useEffect, useState } from 'react';
import { Route, Routes, useLocation } from 'react-router-dom';
import './App.css';
import NotificationCenter from './components/Common/NotificationCenter';
import Header from './components/Layout/Header';
import Sidebar from './components/Layout/Sidebar';
import TaskModal from './components/Modals/TaskModal';
import Dashboard from './components/Pages/Dashboard';
import PlanComparison from './components/Pages/PlanComparison';
import ProgressTracker from './components/Pages/ProgressTracker';
import ProjectPlans from './components/Pages/ProjectPlans';
import Settings from './components/Pages/Settings';
import { ProjectProvider } from './context/ProjectContext';

function App() {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [loading, setLoading] = useState(true);
  const location = useLocation();

  // Simulate initial loading
  useEffect(() => {
    const timer = setTimeout(() => {
      setLoading(false);
    }, 1500);
    return () => clearTimeout(timer);
  }, []);

  // Page transition effect
  useEffect(() => {
    window.scrollTo(0, 0);
  }, [location]);

  if (loading) {
    return (
      <div className="loading-screen">
        <div className="loading-spinner">
          <div className="spinner"></div>
          <h2>Loading LLaMA GPU Project Tracker</h2>
          <p>Initializing dashboard components...</p>
        </div>
      </div>
    );
  }

  return (
    <ProjectProvider>
      <div className="app">
        <Sidebar
          collapsed={sidebarCollapsed}
          onToggle={() => setSidebarCollapsed(!sidebarCollapsed)}
        />

        <div className={`main-content ${sidebarCollapsed ? 'sidebar-collapsed' : ''}`}>
          <Header onSidebarToggle={() => setSidebarCollapsed(!sidebarCollapsed)} />

          <main className="page-content">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/plans" element={<ProjectPlans />} />
              <Route path="/progress" element={<ProgressTracker />} />
              <Route path="/comparison" element={<PlanComparison />} />
              <Route path="/settings" element={<Settings />} />
            </Routes>
          </main>
        </div>

        <TaskModal />
        <NotificationCenter />
      </div>
    </ProjectProvider>
  );
}

export default App;
