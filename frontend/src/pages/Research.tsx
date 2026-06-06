import React, { useEffect, useState } from 'react';
import { GlassCard } from '../components/GlassCard';
import { BookOpen, AlertTriangle, Layers, Award, ShieldAlert } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import type { AnalyticsResponse } from '../types';

export const Research: React.FC = () => {
  const { token } = useAuth();
  const [data, setData] = useState<AnalyticsResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAnalytics = async () => {
      try {
        const backendUrl = import.meta.env.VITE_BACKEND_URL || 'http://127.0.0.1:8000';
        const res = await fetch(`${backendUrl}/api/dashboard/analytics`, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
        if (res.ok) {
          const result = await res.json();
          setData(result);
        }
      } catch (err) {
        console.error('Failed to fetch analytics for research page', err);
      } finally {
        setLoading(false);
      }
    };

    if (token) {
      fetchAnalytics();
    } else {
      setLoading(false);
    }
  }, [token]);

  return (
    <div className="space-y-6 max-w-5xl">
      
      {/* Overview Intro */}
      <GlassCard glow="violet">
        <h3 className="text-lg font-bold text-slate-800 dark:text-white flex items-center gap-2">
          <BookOpen className="w-5.5 h-5.5 text-violet-500" />
          AURA AI: Scientific and Architectural Blueprint
        </h3>
        <p className="text-xs text-slate-400 mt-1.5 leading-relaxed">
          Autonomous NLP-based Agent frameworks address the translation gap between human intent and system-level API executions. 
          Below, we document the technical gaps, methodologies, and architectures governing AURA AI's engine.
        </p>
      </GlassCard>

      {/* Grid: Gaps & Problem Statement */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        
        {/* Problem Statement */}
        <GlassCard className="flex flex-col justify-between">
          <div>
            <h4 className="text-sm font-bold text-slate-800 dark:text-slate-200 mb-2.5 flex items-center gap-1.5">
              <ShieldAlert className="w-4.5 h-4.5 text-red-500 animate-pulse" />
              Problem Statement
            </h4>
            <p className="text-xs text-slate-500 dark:text-slate-300 leading-relaxed">
              Standard task automation tools (e.g., Zapier, IFTTT) require manual configuration of static, rule-based triggers and actions. 
              They lack the cognitive flexibility to comprehend context-rich, multi-lingual, or ambiguous user commands. 
              Conversely, raw Large Language Models (LLMs) excel at conversation but cannot safely trigger orchestrations 
              across local filesystems, secure emails, or network sockets without structure.
            </p>
          </div>
        </GlassCard>

        {/* Research Gaps */}
        <GlassCard className="flex flex-col justify-between">
          <div>
            <h4 className="text-sm font-bold text-slate-800 dark:text-slate-200 mb-2.5 flex items-center gap-1.5">
              <AlertTriangle className="w-4.5 h-4.5 text-amber-500" />
              Identified Research Gaps
            </h4>
            <ul className="text-xs text-slate-500 dark:text-slate-300 space-y-2 list-disc pl-4">
              <li>
                <strong>Context Resolution Stalls:</strong> Existing tools struggle to resolve references like "it" or "them" to correct entities across multi-turn sessions.
              </li>
              <li>
                <strong>Multilingual Fragility:</strong> Lack of unified grammatical representation structures for Indic scripts (Hindi, Kannada) alongside English in workflow generation.
              </li>
              <li>
                <strong>Unpredictable DAG Topologies:</strong> Generating non-deterministic graphs that result in broken logic pipelines when executing compound tasks.
              </li>
            </ul>
          </div>
        </GlassCard>
      </div>

      {/* Architectural breakdown */}
      <GlassCard>
        <h4 className="text-sm font-bold text-slate-800 dark:text-slate-200 mb-4 flex items-center gap-1.5">
          <Layers className="w-4.5 h-4.5 text-blue-500" />
          Proposed Methodology & Pipeline
        </h4>
        
        <div className="space-y-4 text-xs text-slate-500 dark:text-slate-300">
          <p className="leading-relaxed">
            AURA AI implements a **Layered Cognitive Pipeline** that translates raw natural language signals into secure system execution blocks:
          </p>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 font-mono text-[10px] text-slate-700 dark:text-slate-200">
            <div className="p-3 bg-slate-100/30 dark:bg-white/5 border border-slate-200/50 dark:border-white/5 rounded-2xl">
              <span className="text-violet-500 font-bold block mb-1">1. NLP Parser Layer</span>
              - Language Auto-Detection
              - Intent Classification (BERT)
              - Entity Extraction (spaCy NER)
              - Dependency Parsing (Logic)
            </div>
            <div className="p-3 bg-slate-100/30 dark:bg-white/5 border border-slate-200/50 dark:border-white/5 rounded-2xl">
              <span className="text-emerald-500 font-bold block mb-1">2. Planner Agent Layer</span>
              - Context Reference Resolution
              - Task Graph (DAG) Compiling
              - Inputs/Outputs Variable Binding
              - Path Optimization Checks
            </div>
            <div className="p-3 bg-slate-100/30 dark:bg-white/5 border border-slate-200/50 dark:border-white/5 rounded-2xl">
              <span className="text-blue-500 font-bold block mb-1">3. Execution Layer</span>
              - Async Micro-Agent Spawning
              - Relational Database Logs
              - Error Mitigation Rules
              - Vector Memory Storage
            </div>
          </div>
        </div>
      </GlassCard>

      {/* Expected Outcomes */}
      <GlassCard>
        <h4 className="text-sm font-bold text-slate-800 dark:text-slate-200 mb-3.5 flex items-center gap-1.5">
          <Award className="w-4.5 h-4.5 text-emerald-500" />
          Expected Outcomes & Benchmarks
        </h4>
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4 text-center">
          <div className="p-4 bg-slate-100/10 dark:bg-white/5 rounded-2xl border border-slate-200/20">
            <span className="text-2xl font-extrabold text-violet-500 block">
              {loading || !data ? '95%+' : `${data.intent_accuracy}%`}
            </span>
            <span className="text-[10px] text-slate-400 font-semibold block mt-1">Intent Classification Accuracy</span>
          </div>
          <div className="p-4 bg-slate-100/10 dark:bg-white/5 rounded-2xl border border-slate-200/20">
            <span className="text-2xl font-extrabold text-emerald-500 block">
              {loading || !data ? '<4s' : `${data.mean_execution_speed}s`}
            </span>
            <span className="text-[10px] text-slate-400 font-semibold block mt-1">Mean Pipeline Setup Latency</span>
          </div>
          <div className="p-4 bg-slate-100/10 dark:bg-white/5 rounded-2xl border border-slate-200/20">
            <span className="text-2xl font-extrabold text-blue-500 block">
              {loading || !data ? '98%+' : `${data.ner_f1}%`}
            </span>
            <span className="text-[10px] text-slate-400 font-semibold block mt-1">Semantic Memory Recall F1</span>
          </div>
          <div className="p-4 bg-slate-100/10 dark:bg-white/5 rounded-2xl border border-slate-200/20">
            <span className="text-2xl font-extrabold text-indigo-500 block">100%</span>
            <span className="text-[10px] text-slate-400 font-semibold block mt-1">Determinism in DAG Compilation</span>
          </div>
        </div>
      </GlassCard>
    </div>
  );
};
