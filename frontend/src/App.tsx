import React, { useState } from 'react';
import { ThemeProvider } from './context/ThemeContext';
import { AuthProvider, useAuth } from './context/AuthContext';
import { Sidebar } from './components/Sidebar';
import { Header } from './components/Header';
import { Dashboard } from './pages/Dashboard';
import { CommandCenter } from './pages/CommandCenter';
import { NLPAnalysis } from './pages/NLPAnalysis';
import { WorkflowBuilder } from './pages/WorkflowBuilder';
import { AgentControl } from './pages/AgentControl';
import { ExecutionMonitor } from './pages/ExecutionMonitor';
import { MemoryCenter } from './pages/MemoryCenter';
import { Analytics } from './pages/Analytics';
import { Research } from './pages/Research';
import type { Command, Workflow } from './types';
import { LogIn, KeyRound, Globe } from 'lucide-react';

const AppContent: React.FC = () => {
  const { user, loading, loginWithGoogle } = useAuth();
  const [activeTab, setActiveTab] = useState('dashboard');
  const [selectedCommand, setSelectedCommand] = useState<Command | null>(null);
  const [activeWorkflow, setActiveWorkflow] = useState<Workflow | null>(null);

  const handleCommandProcessed = (command: Command) => {
    setSelectedCommand(command);
    setActiveWorkflow(null);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center">
        <div className="w-10 h-10 border-4 border-violet-500 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  if (!user) {
    return (
      <div className="min-h-screen bg-[#07080e] flex items-center justify-center relative overflow-hidden px-4">
        {/* Glow Effects */}
        <div className="absolute top-[20%] left-[30%] w-[400px] h-[400px] bg-violet-600/10 rounded-full blur-[100px] pointer-events-none" />
        <div className="absolute bottom-[20%] right-[30%] w-[400px] h-[400px] bg-indigo-600/10 rounded-full blur-[100px] pointer-events-none" />
        
        <div className="glass-card border border-white/5 bg-[#111327]/60 rounded-3xl p-8 max-w-md w-full text-center shadow-2xl backdrop-blur-xl relative z-10 animate-in fade-in slide-in-from-bottom-6 duration-300">
          <div className="w-14 h-14 bg-violet-600/20 text-violet-400 rounded-2xl flex items-center justify-center mx-auto mb-6 border border-violet-500/25">
            <KeyRound className="w-6 h-6 animate-pulse" />
          </div>
          <h2 className="text-2xl font-black bg-gradient-to-r from-violet-400 to-indigo-300 bg-clip-text text-transparent tracking-tight">
            AURA AI Cockpit
          </h2>
          <p className="text-slate-400 text-xs mt-2 mb-8 leading-relaxed">
            Welcome to the Autonomous NLP Workflow Agent dashboard. 
            Authenticate using your Firebase enterprise portal to continue.
          </p>

          <button
            onClick={loginWithGoogle}
            className="w-full flex items-center justify-center gap-3 py-3 rounded-xl bg-violet-600 hover:bg-violet-700 text-white font-semibold text-xs shadow-lg shadow-violet-500/20 transition-all active:scale-[0.98]"
          >
            <LogIn className="w-4 h-4" />
            Sign In with Google Cloud Auth
          </button>
          
          <div className="mt-8 pt-6 border-t border-white/5 flex items-center justify-center gap-1.5 text-[10px] text-slate-500">
            <Globe className="w-3.5 h-3.5" />
            Global Identity Services Protected
          </div>
        </div>
      </div>
    );
  }

  const renderActivePage = () => {
    switch (activeTab) {
      case 'dashboard':
        return <Dashboard />;
      case 'command-center':
        return (
          <CommandCenter 
            onCommandProcessed={handleCommandProcessed} 
            setActiveTab={setActiveTab} 
          />
        );
      case 'nlp-analysis':
        return <NLPAnalysis selectedCommand={selectedCommand} />;
      case 'workflow-builder':
        return (
          <WorkflowBuilder
            selectedCommand={selectedCommand}
            activeWorkflow={activeWorkflow}
            setActiveWorkflow={setActiveWorkflow}
            setActiveTab={setActiveTab}
          />
        );
      case 'agent-control':
        return <AgentControl />;
      case 'execution-monitor':
        return <ExecutionMonitor activeWorkflow={activeWorkflow} />;
      case 'memory-center':
        return <MemoryCenter />;
      case 'analytics':
        return <Analytics />;
      case 'research':
        return <Research />;
      default:
        return <Dashboard />;
    }
  };

  return (
    <div className="min-h-screen transition-colors duration-300 bg-slate-50 dark:bg-[#07080e] flex">
      {/* Sidebar Navigation */}
      <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />

      {/* Main Layout Area */}
      <div className="flex-1 flex flex-col min-w-0 lg:pl-72 relative min-h-screen">
        
        {/* Background ambient lighting glows */}
        <div className="absolute top-[-10%] left-[20%] w-[500px] h-[500px] bg-violet-600/10 dark:bg-violet-600/5 rounded-full blur-[120px] pointer-events-none" />
        <div className="absolute bottom-[-10%] right-[10%] w-[600px] h-[600px] bg-indigo-600/10 dark:bg-indigo-600/5 rounded-full blur-[120px] pointer-events-none" />

        {/* Global Toolbar Header */}
        <Header activeTab={activeTab} setActiveTab={setActiveTab} />

        {/* Page Content View */}
        <main className="flex-1 pt-28 px-6 pb-12 overflow-y-auto z-0 relative">
          <div className="max-w-[1400px] mx-auto animate-in fade-in-50 duration-300">
            {renderActivePage()}
          </div>
        </main>
      </div>
    </div>
  );
};

function App() {
  return (
    <AuthProvider>
      <ThemeProvider>
        <AppContent />
      </ThemeProvider>
    </AuthProvider>
  );
}

export default App;
