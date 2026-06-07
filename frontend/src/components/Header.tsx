import React, { useState, useEffect, useRef } from 'react';
import { useTheme } from '../context/ThemeContext';
import { 
  Sun, 
  Moon, 
  Bell, 
  Menu, 
  X, 
  Cpu, 
  Trash2, 
  Check, 
  AlertCircle, 
  CheckCircle2, 
  Info, 
  AlertTriangle 
} from 'lucide-react';

interface HeaderProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
}

interface AuraNotification {
  id: string;
  title: string;
  message: string;
  type: 'success' | 'error' | 'info' | 'warning';
  timestamp: string;
  read: boolean;
}

export const Header: React.FC<HeaderProps> = ({ activeTab, setActiveTab }) => {
  const { theme, toggleTheme } = useTheme();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [notificationsOpen, setNotificationsOpen] = useState(false);
  const [notifications, setNotifications] = useState<AuraNotification[]>([]);
  const [backendStatus, setBackendStatus] = useState<'checking' | 'online' | 'offline'>('checking');
  
  const notificationsRef = useRef<HTMLDivElement>(null);

  // Check Backend Status
  useEffect(() => {
    const checkHealth = async () => {
      try {
        const backendUrl = import.meta.env.VITE_BACKEND_URL || 'http://127.0.0.1:8000';
        const res = await fetch(`${backendUrl}/health`);
        if (res.ok) {
          setBackendStatus('online');
        } else {
          setBackendStatus('offline');
        }
      } catch (err) {
        setBackendStatus('offline');
      }
    };
    checkHealth();
    const interval = setInterval(checkHealth, 8000);
    return () => clearInterval(interval);
  }, []);

  // Load Notifications
  useEffect(() => {
    const saved = localStorage.getItem('aura-notifications');
    if (saved) {
      try {
        setNotifications(JSON.parse(saved));
      } catch (e) {
        console.error(e);
      }
    } else {
      // Seed initial welcoming notifications
      const initial: AuraNotification[] = [
        {
          id: 'welcome',
          title: 'System Initialized',
          message: 'Welcome to the AURA AI Cockpit. All micro-agents idle and ready.',
          type: 'success',
          timestamp: new Date().toISOString(),
          read: false
        }
      ];
      setNotifications(initial);
      localStorage.setItem('aura-notifications', JSON.stringify(initial));
    }

    // Event Listener for notifications
    const handleNewNotification = (e: Event) => {
      const customEvent = e as CustomEvent<Omit<AuraNotification, 'read'>>;
      if (customEvent.detail) {
        const newNotif: AuraNotification = {
          ...customEvent.detail,
          read: false
        };
        setNotifications((prev) => {
          // Avoid duplicate IDs
          if (prev.some((n) => n.id === newNotif.id)) return prev;
          const updated = [newNotif, ...prev].slice(0, 20); // Keep last 20
          localStorage.setItem('aura-notifications', JSON.stringify(updated));
          return updated;
        });
        
        // Play notification audio alert (soft synth blip)
        try {
          const context = new (window.AudioContext || (window as any).webkitAudioContext)();
          const osc = context.createOscillator();
          const gain = context.createGain();
          osc.connect(gain);
          gain.connect(context.destination);
          osc.type = 'sine';
          osc.frequency.setValueAtTime(587.33, context.currentTime); // D5 note
          osc.frequency.setValueAtTime(880, context.currentTime + 0.08); // A5 note
          gain.gain.setValueAtTime(0.04, context.currentTime);
          gain.gain.exponentialRampToValueAtTime(0.0001, context.currentTime + 0.25);
          osc.start();
          osc.stop(context.currentTime + 0.25);
        } catch (audioErr) {
          // AudioContext blocked by user interaction gesture, ignore safely
        }
      }
    };

    window.addEventListener('aura-notification', handleNewNotification);
    return () => {
      window.removeEventListener('aura-notification', handleNewNotification);
    };
  }, []);

  // Click Outside to Close
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (notificationsRef.current && !notificationsRef.current.contains(event.target as Node)) {
        setNotificationsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const unreadCount = notifications.filter((n) => !n.read).length;

  const markAllAsRead = () => {
    const updated = notifications.map((n) => ({ ...n, read: true }));
    setNotifications(updated);
    localStorage.setItem('aura-notifications', JSON.stringify(updated));
  };

  const markAsRead = (id: string) => {
    const updated = notifications.map((n) => (n.id === id ? { ...n, read: true } : n));
    setNotifications(updated);
    localStorage.setItem('aura-notifications', JSON.stringify(updated));
  };

  const clearAllNotifications = () => {
    setNotifications([]);
    localStorage.setItem('aura-notifications', JSON.stringify([]));
  };

  const formatTitle = (tab: string) => {
    return tab
      .split('-')
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  };

  const getNotificationIcon = (type: string) => {
    switch (type) {
      case 'success':
        return <CheckCircle2 className="w-4 h-4 text-emerald-500" />;
      case 'error':
        return <AlertCircle className="w-4 h-4 text-red-500" />;
      case 'warning':
        return <AlertTriangle className="w-4 h-4 text-amber-500" />;
      default:
        return <Info className="w-4 h-4 text-blue-500" />;
    }
  };

  const getNotificationColor = (type: string, read: boolean) => {
    if (read) return 'border-slate-200/40 dark:border-white/5 opacity-70';
    switch (type) {
      case 'success':
        return 'border-emerald-500/30 bg-emerald-500/5';
      case 'error':
        return 'border-red-500/30 bg-red-500/5';
      case 'warning':
        return 'border-amber-500/30 bg-amber-500/5';
      default:
        return 'border-blue-500/30 bg-blue-500/5';
    }
  };

  const menuItems = [
    { id: 'dashboard', label: 'Dashboard' },
    { id: 'command-center', label: 'AI Command Center' },
    { id: 'nlp-analysis', label: 'NLP Analysis' },
    { id: 'workflow-builder', label: 'Workflow Builder' },
    { id: 'agent-control', label: 'Agent Control Center' },
    { id: 'execution-monitor', label: 'Execution Monitor' },
    { id: 'memory-center', label: 'Memory Center' },
    { id: 'analytics', label: 'Analytics Dashboard' },
    { id: 'research', label: 'Research Page' },
  ];

  return (
    <>
      <header className="h-20 border-b border-slate-200/50 dark:border-white/5 glass-panel fixed top-0 right-0 left-0 lg:left-72 z-10 flex items-center justify-between px-6 transition-all duration-300">
        {/* Left: Mobile Menu Trigger & Page Title */}
        <div className="flex items-center gap-4">
          <button
            onClick={() => setMobileMenuOpen(true)}
            className="lg:hidden p-2 rounded-xl text-slate-500 hover:bg-slate-100 dark:hover:bg-white/5 transition-all"
          >
            <Menu className="w-6 h-6" />
          </button>
          
          <h2 className="text-xl font-bold tracking-tight text-slate-800 dark:text-white">
            {formatTitle(activeTab)}
          </h2>
        </div>

        {/* Right: Actions */}
        <div className="flex items-center gap-3">
          {/* Dynamic Backend Status Badge */}
          {backendStatus === 'online' && (
            <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-xs text-emerald-600 dark:text-emerald-400 font-medium">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-ping" />
              Backend Connected
            </div>
          )}
          {backendStatus === 'offline' && (
            <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-full bg-red-500/10 border border-red-500/20 text-xs text-red-600 dark:text-red-400 font-medium">
              <span className="w-1.5 h-1.5 rounded-full bg-red-500 animate-pulse" />
              Backend Offline
            </div>
          )}
          {backendStatus === 'checking' && (
            <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-full bg-amber-500/10 border border-amber-500/20 text-xs text-amber-600 dark:text-amber-400 font-medium">
              <span className="w-1.5 h-1.5 rounded-full bg-amber-500 animate-pulse" />
              Checking Link...
            </div>
          )}

          {/* Theme Toggle Button */}
          <button
            onClick={toggleTheme}
            className="p-2.5 rounded-xl border border-slate-200/50 dark:border-white/5 text-slate-500 hover:bg-slate-200/50 dark:hover:bg-white/5 transition-all"
            title="Toggle theme"
          >
            {theme === 'dark' ? <Sun className="w-5 h-5 text-amber-400" /> : <Moon className="w-5 h-5 text-indigo-600" />}
          </button>

          {/* Notification Button & Dropdown Wrapper */}
          <div className="relative" ref={notificationsRef}>
            <button
              onClick={() => setNotificationsOpen(!notificationsOpen)}
              className={`p-2.5 rounded-xl border border-slate-200/50 dark:border-white/5 text-slate-500 hover:bg-slate-200/50 dark:hover:bg-white/5 transition-all relative ${
                notificationsOpen ? 'bg-slate-200/50 dark:bg-white/5' : ''
              }`}
              title="Notifications"
            >
              <Bell className="w-5 h-5" />
              {unreadCount > 0 && (
                <span className="absolute top-1 right-1 w-5 h-5 bg-violet-600 text-white text-[9px] font-bold rounded-full flex items-center justify-center ring-2 ring-white dark:ring-[#07080e] animate-bounce">
                  {unreadCount}
                </span>
              )}
            </button>

            {/* Premium Glassmorphism Notifications Dropdown */}
            {notificationsOpen && (
              <div className="absolute right-0 mt-3 w-80 sm:w-96 glass-card border border-slate-200/70 dark:border-white/5 rounded-2xl p-4 shadow-2xl z-50 animate-in fade-in slide-in-from-top-3 duration-200">
                <div className="flex items-center justify-between pb-2.5 border-b border-slate-200/50 dark:border-white/5 mb-3">
                  <div className="flex items-center gap-1.5">
                    <span className="font-bold text-xs text-slate-800 dark:text-slate-100">Telemetry Feed</span>
                    {unreadCount > 0 && (
                      <span className="text-[10px] bg-violet-500/10 text-violet-500 font-extrabold px-1.5 py-0.5 rounded-md">
                        {unreadCount} New
                      </span>
                    )}
                  </div>
                  <div className="flex gap-2">
                    {unreadCount > 0 && (
                      <button
                        onClick={markAllAsRead}
                        className="text-[10px] font-semibold text-violet-600 hover:text-violet-700 dark:text-violet-400 dark:hover:text-violet-300 transition-colors flex items-center gap-0.5"
                      >
                        <Check className="w-3 h-3" /> Mark Read
                      </button>
                    )}
                    {notifications.length > 0 && (
                      <button
                        onClick={clearAllNotifications}
                        className="text-[10px] font-semibold text-red-500 hover:text-red-600 transition-colors flex items-center gap-0.5"
                      >
                        <Trash2 className="w-3 h-3" /> Clear
                      </button>
                    )}
                  </div>
                </div>

                {/* Notifications Scroll List */}
                <div className="max-h-72 overflow-y-auto space-y-2 pr-1">
                  {notifications.length === 0 ? (
                    <div className="text-center py-10 text-slate-400 text-xs italic">
                      Zero notifications in workspace logs.
                    </div>
                  ) : (
                    notifications.map((notif) => (
                      <div
                        key={notif.id}
                        onClick={() => markAsRead(notif.id)}
                        className={`p-3 rounded-xl border text-xs cursor-pointer transition-all hover:translate-x-0.5 flex gap-2.5 items-start ${getNotificationColor(
                          notif.type,
                          notif.read
                        )}`}
                      >
                        <div className="shrink-0 mt-0.5">{getNotificationIcon(notif.type)}</div>
                        <div className="flex-1 min-w-0">
                          <div className="flex justify-between items-center mb-0.5">
                            <span className="font-bold text-slate-700 dark:text-slate-200 truncate pr-2">
                              {notif.title}
                            </span>
                            <span className="text-[9px] text-slate-400 shrink-0">
                              {new Date(notif.timestamp).toLocaleTimeString([], {
                                hour: '2-digit',
                                minute: '2-digit'
                              })}
                            </span>
                          </div>
                          <p className="text-[11px] text-slate-500 dark:text-slate-400 leading-normal">
                            {notif.message}
                          </p>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      </header>

      {/* Mobile Sidebar overlay */}
      {mobileMenuOpen && (
        <div className="fixed inset-0 z-50 lg:hidden flex">
          <div className="fixed inset-0 bg-slate-900/60 backdrop-blur-sm" onClick={() => setMobileMenuOpen(false)} />
          
          <div className="w-72 bg-slate-50 dark:bg-[#0f101d] h-full relative z-10 flex flex-col p-6 shadow-2xl animate-in slide-in-from-left duration-250 border-r border-slate-200/50 dark:border-white/5">
            <div className="flex items-center justify-between mb-8">
              <div className="flex items-center gap-3">
                <Cpu className="w-6 h-6 text-violet-500 animate-pulse-slow" />
                <span className="font-bold text-lg text-slate-800 dark:text-white">AURA AI</span>
              </div>
              <button
                onClick={() => setMobileMenuOpen(false)}
                className="p-1 rounded-lg hover:bg-slate-200 dark:hover:bg-white/10"
              >
                <X className="w-6 h-6 text-slate-400" />
              </button>
            </div>

            <nav className="flex-1 space-y-1 overflow-y-auto">
              {menuItems.map((item) => (
                <button
                  key={item.id}
                  onClick={() => {
                    setActiveTab(item.id);
                    setMobileMenuOpen(false);
                  }}
                  className={`w-full text-left px-4 py-3 rounded-xl text-sm font-medium transition-all ${
                    activeTab === item.id
                      ? 'bg-violet-600 text-white shadow-md'
                      : 'text-slate-600 dark:text-slate-300 hover:bg-slate-200/50 dark:hover:bg-white/5'
                  }`}
                >
                  {item.label}
                </button>
              ))}
            </nav>
          </div>
        </div>
      )}
    </>
  );
};
