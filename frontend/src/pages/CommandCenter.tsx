import React, { useEffect, useState } from 'react';
import { GlassCard } from '../components/GlassCard';
import { VoiceInput } from '../components/VoiceInput';
import { Send, History, Sparkles, ArrowRight, Brain } from 'lucide-react';
import type { Command } from '../types';
import { useAuth } from '../context/AuthContext';

interface CommandCenterProps {
  onCommandProcessed: (command: Command) => void;
  setActiveTab: (tab: string) => void;
}

export const CommandCenter: React.FC<CommandCenterProps> = ({ 
  onCommandProcessed, 
  setActiveTab 
}) => {
  const { token } = useAuth();
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [history, setHistory] = useState<Command[]>([]);
  const [latestResponse, setLatestResponse] = useState<Command | null>(null);

  const fetchHistory = async () => {
    try {
      const backendUrl = import.meta.env.VITE_BACKEND_URL || 'http://127.0.0.1:8000';
      const res = await fetch(`${backendUrl}/api/command/history`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      if (res.ok) {
        const data = await res.json();
        setHistory(data);
      }
    } catch (err) {
      console.error('Failed to load command history', err);
    }
  };

  useEffect(() => {
    if (token) fetchHistory();
  }, [token]);

  const handleVoiceTranscript = (text: string) => {
    setInputText(text);
  };

  const handleExecute = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputText.trim()) return;

    setIsLoading(true);
    setError('');

    try {
      const backendUrl = import.meta.env.VITE_BACKEND_URL || 'http://127.0.0.1:8000';
      const res = await fetch(`${backendUrl}/api/command/process`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ text: inputText }),
      });

      if (!res.ok) {
        throw new Error('API server returned an error');
      }

      const commandResult: Command = await res.json();
      setLatestResponse(commandResult);
      onCommandProcessed(commandResult);
      setInputText('');
      
      // Refresh history panel
      fetchHistory();
    } catch (err) {
      setError('Could not process command. Make sure the FastAPI backend is running.');
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* Left Column: Command Console Input */}
        <div className="lg:col-span-8 space-y-6">
          <GlassCard glow="violet">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-md font-bold flex items-center gap-2 text-slate-800 dark:text-slate-200">
                <Brain className="w-5 h-5 text-violet-500" />
                Autonomous Directive Console
              </h3>
              <VoiceInput onTranscript={handleVoiceTranscript} isLoading={isLoading} />
            </div>

            <form onSubmit={handleExecute} className="space-y-4">
              <div className="relative">
                <textarea
                  value={inputText}
                  onChange={(e) => setInputText(e.target.value)}
                  placeholder="Enter a natural language instructions (e.g. 'Send quarterly strategic report to Priya Sharma' or 'आर्ಕೈವ್ ಫೈಲ್ ಬ್ಯಾಕಪ್ ಮಾಡಿ')..."
                  className="w-full h-32 p-4 text-sm rounded-2xl glass-input pr-12 focus:ring-2 focus:ring-violet-500/20 text-slate-700 dark:text-slate-200"
                  disabled={isLoading}
                />
                <button
                  type="submit"
                  disabled={isLoading || !inputText.trim()}
                  className="absolute right-3.5 bottom-3.5 p-2.5 rounded-xl bg-violet-600 hover:bg-violet-700 text-white shadow-md transition-all disabled:opacity-40"
                >
                  <Send className="w-4 h-4" />
                </button>
              </div>

              {error && (
                <p className="text-xs font-semibold text-red-500">
                  {error}
                </p>
              )}
            </form>
          </GlassCard>

          {/* AI Response Section */}
          {latestResponse && (
            <GlassCard className="animate-in fade-in slide-in-from-bottom-3 duration-250 border-violet-500/20">
              <div className="flex items-center justify-between border-b border-slate-200/50 dark:border-white/5 pb-3 mb-3">
                <h4 className="text-sm font-bold flex items-center gap-2 text-violet-500">
                  <Sparkles className="w-4 h-4" />
                  NLP Parsing Successful
                </h4>
                <div className="text-[10px] uppercase font-bold text-slate-400 bg-slate-100 dark:bg-white/5 px-2 py-0.5 rounded">
                  Language: {latestResponse.language}
                </div>
              </div>

              <div className="space-y-3">
                <div>
                  <span className="text-[10px] text-slate-400 uppercase font-bold tracking-wider">Detected Intent</span>
                  <div className="text-sm font-semibold text-slate-800 dark:text-slate-200 flex items-center gap-2 mt-0.5">
                    <span className="px-2 py-0.5 bg-violet-500/10 text-violet-500 rounded border border-violet-500/20 font-mono text-xs">
                      {latestResponse.intent}
                    </span>
                    <span className="text-xs text-slate-400">
                      (Confidence: {Math.round(latestResponse.intent_confidence * 100)}%)
                    </span>
                  </div>
                </div>

                <div>
                  <span className="text-[10px] text-slate-400 uppercase font-bold tracking-wider">Subtask Breakdown</span>
                  <div className="mt-1.5 space-y-1">
                    {latestResponse.task_decomposition.map((task, index) => (
                      <div key={task.id} className="text-xs text-slate-600 dark:text-slate-300 flex items-center gap-2">
                        <span className="w-4 h-4 rounded-full bg-slate-200/50 dark:bg-white/5 border border-slate-300/30 text-[9px] flex items-center justify-center font-bold text-slate-500">
                          {index + 1}
                        </span>
                        <span>{task.label}</span>
                        <span className="text-[9px] uppercase font-bold text-violet-500 bg-violet-500/10 px-1 rounded">
                          {task.type}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="pt-2 border-t border-slate-200/50 dark:border-white/5 flex gap-3">
                  <button
                    onClick={() => setActiveTab('nlp-analysis')}
                    className="text-xs font-semibold text-slate-500 dark:text-slate-400 hover:text-violet-500 dark:hover:text-violet-400 flex items-center gap-1"
                  >
                    View NLP Analysis Details <ArrowRight className="w-3.5 h-3.5" />
                  </button>
                  <button
                    onClick={() => setActiveTab('workflow-builder')}
                    className="text-xs font-semibold text-violet-500 hover:text-violet-600 dark:hover:text-violet-400 flex items-center gap-1"
                  >
                    Construct Workflow <ArrowRight className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
            </GlassCard>
          )}
        </div>

        {/* Right Column: Historical Commands */}
        <div className="lg:col-span-4">
          <GlassCard className="flex flex-col h-[480px]">
            <h3 className="text-md font-bold mb-4 flex items-center gap-2 text-slate-800 dark:text-slate-200">
              <History className="w-5 h-5 text-slate-400" />
              Command History
            </h3>

            <div className="flex-1 overflow-y-auto space-y-3.5 pr-1">
              {history.length === 0 ? (
                <div className="text-center text-xs text-slate-400 py-16">
                  No command history found.
                </div>
              ) : (
                history.map((cmd) => (
                  <button
                    key={cmd.id}
                    onClick={() => {
                      setLatestResponse(cmd);
                      onCommandProcessed(cmd);
                    }}
                    className="w-full text-left p-3 rounded-xl border border-slate-200/50 dark:border-white/5 bg-slate-100/10 dark:bg-white/5 hover:border-violet-500/30 hover:bg-violet-500/5 transition-all group"
                  >
                    <p className="text-xs text-slate-700 dark:text-slate-200 font-medium line-clamp-2">
                      "{cmd.original_text}"
                    </p>
                    <div className="flex items-center justify-between mt-2.5">
                      <span className="text-[9px] font-mono text-violet-500 bg-violet-500/10 px-1.5 py-0.5 rounded font-bold uppercase">
                        {cmd.intent}
                      </span>
                      <span className="text-[9px] text-slate-400">
                        {new Date(cmd.created_at).toLocaleDateString()}
                      </span>
                    </div>
                  </button>
                ))
              )}
            </div>
          </GlassCard>
        </div>
      </div>
    </div>
  );
};
