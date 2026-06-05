import React from 'react';
import { GlassCard } from '../components/GlassCard';
import type { Command } from '../types';
import { 
  Sparkles, 
  Terminal, 
  Settings, 
  Database, 
  Cpu, 
  CheckCircle,
  Hash
} from 'lucide-react';

interface NLPAnalysisProps {
  selectedCommand: Command | null;
}

export const NLPAnalysis: React.FC<NLPAnalysisProps> = ({ selectedCommand }) => {
  if (!selectedCommand) {
    return (
      <GlassCard className="text-center py-16">
        <Sparkles className="w-12 h-12 text-violet-400 mx-auto animate-pulse mb-3" />
        <h3 className="text-lg font-bold text-slate-700 dark:text-slate-200">No command selected for analysis</h3>
        <p className="text-xs text-slate-400 max-w-sm mx-auto mt-2">
          Head over to the AI Command Center, select or run a command, and then review the full structural breakdown here.
        </p>
      </GlassCard>
    );
  }

  const entities = selectedCommand.entities;
  const semantic = selectedCommand.semantic_parse;
  const context = selectedCommand.context_resolution;

  return (
    <div className="space-y-6">
      {/* Target input summary */}
      <GlassCard glow="violet">
        <span className="text-[10px] text-violet-500 uppercase font-bold tracking-wider">Analyzed Instruction</span>
        <h3 className="text-lg font-bold text-slate-800 dark:text-white mt-1 italic">
          "{selectedCommand.original_text}"
        </h3>
      </GlassCard>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left pane: Intent & Entities */}
        <div className="lg:col-span-6 space-y-6">
          {/* Intent */}
          <GlassCard>
            <h4 className="text-sm font-bold text-slate-800 dark:text-slate-200 mb-3 flex items-center gap-2">
              <Cpu className="w-4.5 h-4.5 text-violet-500" />
              Intent Classification
            </h4>
            <div className="flex items-center justify-between border border-slate-200/50 dark:border-white/5 p-4 rounded-2xl bg-slate-100/10 dark:bg-white/5">
              <div>
                <span className="text-[10px] text-slate-400 uppercase font-bold">Classified Label</span>
                <p className="font-mono text-sm font-bold text-violet-500 mt-0.5">{selectedCommand.intent}</p>
              </div>
              <div className="text-right">
                <span className="text-[10px] text-slate-400 uppercase font-bold">Confidence Score</span>
                <p className="text-md font-extrabold text-slate-700 dark:text-slate-200 mt-0.5">
                  {Math.round(selectedCommand.intent_confidence * 100)}%
                </p>
              </div>
            </div>

            {/* Confidence progress bar */}
            <div className="w-full bg-slate-200 dark:bg-white/5 h-2 rounded-full mt-4 overflow-hidden">
              <div 
                className="bg-violet-600 h-full rounded-full transition-all duration-500" 
                style={{ width: `${selectedCommand.intent_confidence * 100}%` }}
              />
            </div>
          </GlassCard>

          {/* Entity Tagging visualization */}
          <GlassCard>
            <h4 className="text-sm font-bold text-slate-800 dark:text-slate-200 mb-3 flex items-center gap-2">
              <Hash className="w-4.5 h-4.5 text-emerald-500" />
              Named Entity Recognition (NER)
            </h4>
            
            <div className="space-y-3">
              {Object.keys(entities).map((key) => {
                if (key === 'keywords') return null;
                const val = entities[key];
                
                // Color badges matching type
                let colorClass = 'bg-slate-200/50 text-slate-600 dark:bg-white/5 dark:text-slate-300';
                if (val) {
                  if (key === 'recipient') colorClass = 'bg-emerald-500/10 text-emerald-500 border border-emerald-500/20';
                  else if (key === 'filename') colorClass = 'bg-violet-500/10 text-violet-500 border border-violet-500/20';
                  else if (key === 'url') colorClass = 'bg-blue-500/10 text-blue-500 border border-blue-500/20';
                  else if (key === 'date_time') colorClass = 'bg-amber-500/10 text-amber-500 border border-amber-500/20';
                  else if (key === 'subject') colorClass = 'bg-pink-500/10 text-pink-500 border border-pink-500/20';
                }

                return (
                  <div key={key} className="flex items-center justify-between p-2 rounded-xl bg-slate-100/10 dark:bg-white/5 border border-slate-200/20 text-xs">
                    <span className="font-semibold text-slate-400 capitalize">{key.replace('_', ' ')}</span>
                    <span className={`px-2 py-0.5 rounded font-medium ${colorClass}`}>
                      {val ? String(val) : 'None'}
                    </span>
                  </div>
                );
              })}
            </div>
          </GlassCard>
        </div>

        {/* Right pane: Semantic Parse & Reference Resolution */}
        <div className="lg:col-span-6 space-y-6">
          {/* Semantic Output */}
          <GlassCard>
            <h4 className="text-sm font-bold text-slate-800 dark:text-slate-200 mb-3 flex items-center gap-2">
              <Terminal className="w-4.5 h-4.5 text-blue-500" />
              Semantic Parsing & Logic
            </h4>
            <div className="space-y-3.5">
              <div>
                <span className="text-[10px] text-slate-400 uppercase font-bold tracking-wider">Logical Form Structure</span>
                <pre className="mt-1 p-3 rounded-xl bg-slate-900 text-[#00ffcc] font-mono text-[11px] overflow-x-auto">
                  {semantic.logical_form}
                </pre>
              </div>
              <div className="grid grid-cols-2 gap-3 text-xs">
                <div className="p-2.5 rounded-xl border border-slate-200/30">
                  <span className="text-[9px] text-slate-400 font-bold block uppercase">Actor</span>
                  <span className="font-semibold text-slate-700 dark:text-slate-200">{semantic.semantic_relations.actor}</span>
                </div>
                <div className="p-2.5 rounded-xl border border-slate-200/30">
                  <span className="text-[9px] text-slate-400 font-bold block uppercase">Action</span>
                  <span className="font-semibold text-slate-700 dark:text-slate-200">{semantic.semantic_relations.action}</span>
                </div>
                <div className="p-2.5 rounded-xl border border-slate-200/30">
                  <span className="text-[9px] text-slate-400 font-bold block uppercase">Object</span>
                  <span className="font-semibold text-slate-700 dark:text-slate-200 truncate block">{semantic.semantic_relations.object}</span>
                </div>
                <div className="p-2.5 rounded-xl border border-slate-200/30">
                  <span className="text-[9px] text-slate-400 font-bold block uppercase">Dependency Tree</span>
                  <span className="font-semibold text-emerald-500 flex items-center gap-1">
                    <CheckCircle className="w-3.5 h-3.5" />
                    Verified
                  </span>
                </div>
              </div>
            </div>
          </GlassCard>

          {/* Context resolution */}
          <GlassCard>
            <h4 className="text-sm font-bold text-slate-800 dark:text-slate-200 mb-3 flex items-center gap-2">
              <Database className="w-4.5 h-4.5 text-indigo-500" />
              Context Resolution & Preferences
            </h4>
            <div className="space-y-3.5">
              <div className="flex justify-between items-center text-xs pb-2 border-b border-slate-100 dark:border-white/5">
                <span className="text-slate-400 font-semibold">Active Agent Session</span>
                <span className="font-mono bg-indigo-500/10 text-indigo-500 px-2 py-0.5 rounded">
                  {context.active_session}
                </span>
              </div>
              <div>
                <span className="text-[10px] text-slate-400 uppercase font-bold tracking-wider block mb-1">Pronoun/Reference Matching</span>
                <div className="grid grid-cols-2 gap-2 text-xs">
                  <div className="p-2 bg-slate-100/50 dark:bg-white/5 rounded-xl">
                    <span className="text-slate-400 text-[10px] block">"it" resolved to:</span>
                    <span className="font-semibold text-slate-700 dark:text-slate-200">{context.resolved_references.it}</span>
                  </div>
                  <div className="p-2 bg-slate-100/50 dark:bg-white/5 rounded-xl">
                    <span className="text-slate-400 text-[10px] block">"them" resolved to:</span>
                    <span className="font-semibold text-slate-700 dark:text-slate-200 truncate block">{context.resolved_references.them}</span>
                  </div>
                </div>
              </div>
              <div className="flex justify-between items-center text-xs pt-1">
                <span className="text-slate-400 font-semibold">Language Preference</span>
                <span className="font-semibold text-slate-700 dark:text-slate-200">
                  {context.user_preferences.language_preference}
                </span>
              </div>
            </div>
          </GlassCard>
        </div>
      </div>

      {/* Task Decomposition listing */}
      <GlassCard>
        <h4 className="text-sm font-bold text-slate-800 dark:text-slate-200 mb-4 flex items-center gap-2">
          <Settings className="w-4.5 h-4.5 text-violet-500 animate-spin" />
          Task Decomposition Results (DAG Order)
        </h4>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {selectedCommand.task_decomposition.map((task, idx) => (
            <div 
              key={task.id} 
              className="p-4 rounded-2xl border border-slate-200/50 dark:border-white/5 bg-slate-100/10 dark:bg-white/5 space-y-2.5 relative overflow-hidden"
            >
              <div className="absolute top-0 right-0 w-12 h-12 bg-violet-600/5 rounded-bl-full flex items-center justify-center font-bold text-violet-500/20 text-lg">
                #{idx+1}
              </div>
              <div className="flex items-center gap-2">
                <span className="text-[10px] uppercase font-extrabold px-2 py-0.5 rounded bg-violet-600 text-white">
                  {task.type}
                </span>
                <span className="font-mono text-[10px] text-slate-400">{task.id}</span>
              </div>
              <h5 className="text-xs font-bold text-slate-800 dark:text-slate-200">
                {task.label}
              </h5>
              <div className="text-[10px] space-y-1 pt-1.5 border-t border-slate-200/50 dark:border-white/5">
                <div>
                  <span className="text-slate-400 font-medium">Inputs: </span>
                  <span className="font-mono text-slate-500 dark:text-slate-400">{JSON.stringify(task.inputs)}</span>
                </div>
                <div>
                  <span className="text-slate-400 font-medium">Outputs: </span>
                  <span className="font-mono text-slate-500 dark:text-slate-400">{JSON.stringify(task.outputs)}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </GlassCard>
    </div>
  );
};
