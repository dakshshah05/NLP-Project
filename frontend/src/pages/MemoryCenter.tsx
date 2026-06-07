import React, { useEffect, useState } from 'react';
import { GlassCard } from '../components/GlassCard';
import type { Memory } from '../types';
import { 
  Database, 
  Search, 
  Plus, 
  User, 
  FileText, 
  Settings, 
  History, 
  Loader,
  Upload
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export const MemoryCenter: React.FC = () => {
  const { token } = useAuth();
  const [query, setQuery] = useState('');
  const [searchResults, setSearchResults] = useState<any[]>([]);
  const [searching, setSearching] = useState(false);
  const [allMemories, setAllMemories] = useState<Memory[]>([]);
  const [loading, setLoading] = useState(true);

  // Form State
  const [uploadMode, setUploadMode] = useState<'text' | 'file'>('text');
  const [category, setCategory] = useState('documents');
  const [content, setContent] = useState('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const fetchAllMemories = async () => {
    try {
      const backendUrl = import.meta.env.VITE_BACKEND_URL || 'http://127.0.0.1:8000';
      const res = await fetch(`${backendUrl}/api/memory/list`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      if (res.ok) {
        const data = await res.json();
        setAllMemories(data);
      }
    } catch (err) {
      console.error('Failed to load memories list', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (token) fetchAllMemories();
  }, [token]);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) {
      setSearchResults([]);
      return;
    }
    setSearching(true);

    try {
      const backendUrl = import.meta.env.VITE_BACKEND_URL || 'http://127.0.0.1:8000';
      const res = await fetch(`${backendUrl}/api/memory/search?query=${encodeURIComponent(query)}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      if (res.ok) {
        const data = await res.json();
        setSearchResults(data);
      }
    } catch (err) {
      console.error('Search error', err);
    } finally {
      setSearching(false);
    }
  };

  const handleInsertMemory = async (e: React.FormEvent) => {
    e.preventDefault();
    if (uploadMode === 'file') {
      await handleFileUpload();
      return;
    }

    if (!content.trim()) return;
    setSubmitting(true);

    try {
      const backendUrl = import.meta.env.VITE_BACKEND_URL || 'http://127.0.0.1:8000';
      const res = await fetch(`${backendUrl}/api/memory/add`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ category, content }),
      });

      if (res.ok) {
        setContent('');
        fetchAllMemories();
      }
    } catch (err) {
      console.error('Failed to inject memory', err);
    } finally {
      setSubmitting(false);
    }
  };

  const handleFileUpload = async () => {
    if (!selectedFile) return;
    setSubmitting(true);

    try {
      const backendUrl = import.meta.env.VITE_BACKEND_URL || 'http://127.0.0.1:8000';
      const formData = new FormData();
      formData.append('file', selectedFile);

      const res = await fetch(`${backendUrl}/api/storage/upload`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: formData
      });

      if (res.ok) {
        setSelectedFile(null);
        // Reset file input element
        const fileInput = document.getElementById('cloudinary-file-input') as HTMLInputElement;
        if (fileInput) fileInput.value = '';
        fetchAllMemories();
      } else {
        const errData = await res.json();
        alert(errData.detail || 'Upload failed');
      }
    } catch (err) {
      console.error('Upload failed', err);
      alert('Cloudinary upload connection failed.');
    } finally {
      setSubmitting(false);
    }
  };

  const getCategoryIcon = (cat: string) => {
    switch (cat) {
      case 'contacts': return User;
      case 'documents': return FileText;
      case 'preferences': return Settings;
      default: return History;
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Section: Vector Search Simulation */}
      <GlassCard glow="violet">
        <h3 className="text-md font-bold mb-4 flex items-center gap-2 text-slate-800 dark:text-slate-200">
          <Database className="w-5 h-5 text-violet-500 animate-pulse" />
          Vector Embedding Semantic Search
        </h3>

        <form onSubmit={handleSearch} className="flex gap-2">
          <div className="relative flex-1">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search vector database semantics (e.g. 'Priya Sharma contact' or 'security guides')..."
              className="w-full pl-10 pr-4 py-2.5 rounded-xl glass-input text-xs focus:ring-2 focus:ring-violet-500/20 text-slate-700 dark:text-slate-200"
            />
            <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
          </div>
          <button
            type="submit"
            disabled={searching || !query.trim()}
            className="px-5 py-2.5 rounded-xl bg-violet-600 hover:bg-violet-700 text-white font-semibold text-xs transition-all flex items-center gap-1.5 shadow-md shadow-violet-500/10"
          >
            {searching ? <Loader className="w-3.5 h-3.5 animate-spin" /> : <Search className="w-3.5 h-3.5" />}
            Semantic Match
          </button>
        </form>

        {/* Search Results Display */}
        {searchResults.length > 0 && (
          <div className="mt-5 space-y-3 pt-4 border-t border-slate-200/50 dark:border-white/5 animate-in fade-in slide-in-from-top-2 duration-200">
            <span className="text-[10px] text-slate-400 uppercase font-bold tracking-wider block mb-2">
              Semantic Search Hits
            </span>
            {searchResults.map((result) => {
              const Icon = getCategoryIcon(result.category);
              return (
                <div key={result.id} className="p-3 bg-slate-100/30 dark:bg-white/5 border border-slate-200/50 dark:border-white/5 rounded-xl flex items-center justify-between gap-4">
                  <div className="flex items-center gap-3">
                    <div className="p-2 rounded-lg bg-violet-500/10 text-violet-500">
                      <Icon className="w-4 h-4" />
                    </div>
                    <div className="min-w-0">
                      <p className="text-xs text-slate-700 dark:text-slate-200 font-medium break-all whitespace-pre-wrap">
                        {result.content}
                      </p>
                      <span className="text-[9px] uppercase font-bold text-slate-400">{result.category}</span>
                    </div>
                  </div>
                  
                  {/* Similarity gauge */}
                  <div className="shrink-0 text-right">
                    <span className="text-[9px] text-slate-400 font-bold block uppercase">Cosine Distance</span>
                    <div className="flex items-center gap-2 mt-0.5">
                      <div className="w-16 bg-slate-200 dark:bg-white/5 h-1.5 rounded-full overflow-hidden">
                        <div 
                          className="bg-violet-600 h-full rounded-full" 
                          style={{ width: `${result.score * 100}%` }}
                        />
                      </div>
                      <span className="font-mono text-xs font-bold text-slate-700 dark:text-slate-200">
                        {result.score.toFixed(2)}
                      </span>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </GlassCard>

      {/* Bottom Splitter */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* Insert memory form */}
        <GlassCard className="lg:col-span-5 min-h-[380px] flex flex-col justify-between">
          <div className="border-b border-slate-100 dark:border-white/5 pb-3 mb-4 flex items-center justify-between">
            <h4 className="text-sm font-bold text-slate-800 dark:text-slate-200 flex items-center gap-1.5">
              <Plus className="w-4.5 h-4.5 text-violet-500" />
              Inject Vector Entry
            </h4>
            <div className="flex bg-slate-100 dark:bg-white/5 p-1 rounded-lg text-[10px] font-semibold">
              <button 
                type="button" 
                onClick={() => setUploadMode('text')}
                className={`px-2 py-1 rounded-md transition-all ${uploadMode === 'text' ? 'bg-violet-600 text-white' : 'text-slate-400'}`}
              >
                Text
              </button>
              <button 
                type="button" 
                onClick={() => setUploadMode('file')}
                className={`px-2 py-1 rounded-md transition-all ${uploadMode === 'file' ? 'bg-violet-600 text-white' : 'text-slate-400'}`}
              >
                Upload File
              </button>
            </div>
          </div>

          <form onSubmit={handleInsertMemory} className="space-y-4 flex-1 flex flex-col justify-between">
            {uploadMode === 'text' ? (
              <div className="space-y-4">
                <div>
                  <label className="text-[10px] text-slate-400 font-bold uppercase tracking-wider block mb-1.5">Category</label>
                  <select
                    value={category}
                    onChange={(e) => setCategory(e.target.value)}
                    className="w-full bg-slate-100 dark:bg-white/5 border border-slate-200/50 dark:border-white/5 rounded-xl py-2 px-3 text-xs font-semibold text-slate-600 dark:text-slate-300 focus:outline-none"
                  >
                    <option value="documents">Known Document</option>
                    <option value="contacts">Contact Information</option>
                    <option value="preferences">User Preference</option>
                    <option value="commands">Previous Directive</option>
                  </select>
                </div>

                <div>
                  <label className="text-[10px] text-slate-400 font-bold uppercase tracking-wider block mb-1.5">Memory Payload</label>
                  <textarea
                    value={content}
                    onChange={(e) => setContent(e.target.value)}
                    placeholder="Enter details of contact, preference settings, or document content to embed..."
                    className="w-full h-24 p-3 text-xs rounded-xl glass-input focus:ring-2 focus:ring-violet-500/20 text-slate-700 dark:text-slate-200"
                    disabled={submitting}
                  />
                </div>
              </div>
            ) : (
              <div className="space-y-4 flex-1 flex flex-col justify-center py-2">
                <div className="border-2 border-dashed border-slate-200/50 dark:border-white/5 rounded-2xl p-6 text-center hover:border-violet-500/30 transition-colors cursor-pointer relative">
                  <Upload className="w-8 h-8 text-violet-400 mx-auto mb-2.5" />
                  <span className="text-xs font-semibold text-slate-500 block mb-1">Select workspace file</span>
                  <span className="text-[10px] text-slate-400">PDF, DOCX, Image up to 10MB</span>
                  
                  <input
                    type="file"
                    id="cloudinary-file-input"
                    accept=".pdf,.docx,.doc,.png,.jpg,.jpeg,.webp,.txt"
                    onChange={(e) => setSelectedFile(e.target.files?.[0] || null)}
                    className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                    disabled={submitting}
                  />
                </div>
                {selectedFile && (
                  <p className="text-[10px] font-mono bg-violet-500/10 text-violet-500 border border-violet-500/20 p-2 rounded-xl truncate">
                    Ready to Upload: {selectedFile.name} ({(selectedFile.size / 1024).toFixed(1)} KB)
                  </p>
                )}
              </div>
            )}

            <button
              type="submit"
              disabled={submitting || (uploadMode === 'text' ? !content.trim() : !selectedFile)}
              className="w-full py-2.5 rounded-xl bg-violet-600 hover:bg-violet-700 text-white font-semibold text-xs shadow-md transition-all flex items-center justify-center gap-1.5"
            >
              {submitting ? (
                <>
                  <Loader className="w-3.5 h-3.5 animate-spin" />
                  {uploadMode === 'text' ? 'Embedding...' : 'Uploading Asset...'}
                </>
              ) : (
                <>
                  {uploadMode === 'text' ? <Plus className="w-3.5 h-3.5" /> : <Upload className="w-3.5 h-3.5" />}
                  {uploadMode === 'text' ? 'Upsert Vector Embedding' : 'Upload and Index File'}
                </>
              )}
            </button>
          </form>
        </GlassCard>

        {/* Existing memory items layout */}
        <GlassCard className="lg:col-span-7 h-[360px] flex flex-col">
          <h4 className="text-sm font-bold text-slate-800 dark:text-slate-200 mb-4">
            Active Workspace Knowledge
          </h4>

          <div className="flex-1 overflow-y-auto space-y-3 pr-1">
            {loading ? (
              <div className="text-center py-12"><Loader className="w-6 h-6 animate-spin text-slate-400 mx-auto" /></div>
            ) : allMemories.length === 0 ? (
              <div className="text-center text-xs text-slate-400 py-12">No memory items indexed.</div>
            ) : (
              allMemories.map((item) => {
                const Icon = getCategoryIcon(item.category);
                return (
                  <div key={item.id} className="p-3 rounded-xl border border-slate-200/50 dark:border-white/5 bg-slate-100/10 dark:bg-white/5 flex items-start gap-3">
                    <div className="p-2 rounded-lg bg-violet-500/10 text-violet-500 shrink-0 mt-0.5">
                      <Icon className="w-3.5 h-3.5" />
                    </div>
                    <div className="min-w-0">
                      <p className="text-xs text-slate-700 dark:text-slate-200 font-medium break-all whitespace-pre-wrap">
                        {item.content}
                      </p>
                      <div className="flex items-center gap-2 mt-1.5">
                        <span className="text-[8px] uppercase font-extrabold text-violet-500 bg-violet-500/10 px-1.5 py-0.5 rounded">
                          {item.category}
                        </span>
                        <span className="text-[8px] text-slate-400 font-mono">{item.id}</span>
                      </div>
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </GlassCard>

      </div>
    </div>
  );
};
