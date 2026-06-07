import React, { useState } from 'react';
import { GlassCard } from '../components/GlassCard';
import type { Command } from '../types';
import { 
  Sparkles, 
  Terminal, 
  Settings, 
  Database, 
  Cpu, 
  CheckCircle,
  Hash,
  ArrowRight,
  ChevronRight,
  Eye,
  CheckCircle2
} from 'lucide-react';

interface NLPAnalysisProps {
  selectedCommand: Command | null;
}

export const NLPAnalysis: React.FC<NLPAnalysisProps> = ({ selectedCommand }) => {
  const [activeStep, setActiveStep] = useState<number>(1);
  const [activeTab, setActiveTab] = useState<'pipeline' | 'diagnostics'>('pipeline');

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

  // Get NLTK Pipeline steps with clean client-side fallback if not present
  const getPipelineSteps = (cmd: Command) => {
    if (cmd.nlp_pipeline_steps && cmd.nlp_pipeline_steps.length === 7) {
      return cmd.nlp_pipeline_steps;
    }
    
    // Fallback parser generator
    const text = cmd.original_text;
    const lang = cmd.language;
    const intent = cmd.intent;
    const entities = cmd.entities;
    const semantic = cmd.semantic_parse;
    const context = cmd.context_resolution;
    
    const sentences = [text];
    const tokens = text.match(/\w+|[^\w\s]/g) || [];
    
    const stopWords = ["a", "an", "the", "and", "or", "but", "is", "are", "to", "for", "on", "of", "with", "in", "it", "them", "at"];
    const filteredTokens = tokens.filter(t => !stopWords.includes(t.toLowerCase()));
    const removedStopwords = tokens.filter(t => stopWords.includes(t.toLowerCase()));
    
    const posTags = tokens.map(t => {
      let tag = "NN";
      let desc = "Noun, singular";
      const tl = t.toLowerCase();
      if (["create", "generate", "write", "send", "find", "search", "backup", "compress", "compose"].includes(tl)) {
        tag = "VB";
        desc = "Verb, base form";
      } else if (["email", "pdf", "file", "document", "report", "basics", "nlp", "farming"].includes(tl)) {
        tag = "NN";
        desc = "Noun, singular";
      } else if (tl.includes("@") || tl.includes(".")) {
        tag = "NNP";
        desc = "Proper noun, singular";
      } else if (stopWords.includes(tl)) {
        tag = "IN";
        desc = "Preposition / Conjunction";
      } else {
        tag = "UNK";
        desc = "Unknown / Other";
      }
      return { token: t, tag, description: desc };
    });
    
    const lemmas = tokens.map(t => {
      let lemma = t.toLowerCase();
      if (lemma.endsWith("ing")) lemma = lemma.slice(0, -3);
      else if (lemma.endsWith("ed")) lemma = lemma.slice(0, -2);
      else if (lemma.endsWith("s") && !lemma.endsWith("ss")) lemma = lemma.slice(0, -1);
      return { token: t, lemma };
    });
    
    return [
      {
        step: 1,
        name: "Sentence Segmentation",
        description: "Splitting raw input text into individual sentence units.",
        inputs: { text },
        outputs: { sentences }
      },
      {
        step: 2,
        name: "Word Tokenization",
        description: "Splitting sentence text into individual lexical tokens.",
        inputs: { sentences },
        outputs: { tokens }
      },
      {
        step: 3,
        name: "Stopwords Filtering",
        description: "Removing common grammatical words that lack semantic content.",
        inputs: { tokens, language: lang },
        outputs: { filtered_tokens: filteredTokens, removed_stopwords: removedStopwords }
      },
      {
        step: 4,
        name: "Part-of-Speech Tagging",
        description: "Labeling word tokens with grammatical categories (nouns, verbs, etc.).",
        inputs: { tokens },
        outputs: { pos_tags: posTags }
      },
      {
        step: 5,
        name: "Lemmatization & Normalization",
        description: "Reducing inflected words to their dictionary root/base form.",
        inputs: { pos_tags: posTags.map(p => ({ token: p.token, tag: p.tag })) },
        outputs: { lemmas }
      },
      {
        step: 6,
        name: "Named Entity Recognition & Intent Identification",
        description: "Identifying custom named entities (recipient names, emails, URLs, files) and mapping the target intent.",
        inputs: { text, lemmas: lemmas.map(l => l.lemma) },
        outputs: { detected_intent: intent, confidence_score: cmd.intent_confidence, extracted_entities: entities }
      },
      {
        step: 7,
        name: "Semantic Action Mapping & Logic Synthesis",
        description: "Synthesizing dependencies into a formal logic model and mapping actor, action, object, and instrument.",
        inputs: { intent, entities },
        outputs: { logical_form: semantic.logical_form, semantic_relations: semantic.semantic_relations, context }
      }
    ];
  };

  const pipelineSteps = getPipelineSteps(selectedCommand);
  const currentStepData = pipelineSteps[activeStep - 1];

  const entities = selectedCommand.entities;
  const semantic = selectedCommand.semantic_parse;
  const context = selectedCommand.context_resolution;

  // POS colors for step 4
  const getPosBadgeColor = (tag: string) => {
    if (tag.startsWith("VB")) return "bg-rose-500/10 text-rose-500 border border-rose-500/20";
    if (tag.startsWith("NN")) return "bg-violet-500/10 text-violet-500 border border-violet-500/20";
    if (tag.startsWith("JJ")) return "bg-amber-500/10 text-amber-500 border border-amber-500/20";
    if (tag.startsWith("PR") || tag === "PRP") return "bg-blue-500/10 text-blue-500 border border-blue-500/20";
    if (tag === "IN" || tag === "TO") return "bg-emerald-500/10 text-emerald-500 border border-emerald-500/20";
    return "bg-slate-500/10 text-slate-500 border border-slate-500/20";
  };

  return (
    <div className="space-y-6">
      {/* Target input summary */}
      <GlassCard glow="violet">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <span className="text-[10px] text-violet-500 uppercase font-bold tracking-wider">Analyzed Instruction</span>
            <h3 className="text-lg font-bold text-slate-800 dark:text-white mt-1 italic">
              "{selectedCommand.original_text}"
            </h3>
          </div>
          {/* Switch tabs */}
          <div className="flex bg-slate-100 dark:bg-white/5 p-1 rounded-xl border border-slate-200/50 dark:border-white/5 self-start md:self-center">
            <button
              onClick={() => setActiveTab('pipeline')}
              className={`px-4 py-1.5 rounded-lg text-xs font-bold transition-all ${
                activeTab === 'pipeline'
                  ? 'bg-violet-600 text-white shadow-lg shadow-violet-600/35'
                  : 'text-slate-400 hover:text-slate-800 dark:hover:text-slate-200'
              }`}
            >
              NLTK Live Pipeline
            </button>
            <button
              onClick={() => setActiveTab('diagnostics')}
              className={`px-4 py-1.5 rounded-lg text-xs font-bold transition-all ${
                activeTab === 'diagnostics'
                  ? 'bg-violet-600 text-white shadow-lg shadow-violet-600/35'
                  : 'text-slate-400 hover:text-slate-800 dark:hover:text-slate-200'
              }`}
            >
              Diagnostics Dashboard
            </button>
          </div>
        </div>
      </GlassCard>

      {activeTab === 'pipeline' ? (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
          {/* LEFT: 7 Steps Navigation */}
          <div className="lg:col-span-4 space-y-3">
            <span className="text-[10px] text-slate-400 uppercase font-bold tracking-wider px-2">Pipeline Stepper</span>
            <div className="space-y-2">
              {pipelineSteps.map((step) => {
                const isActive = step.step === activeStep;
                const isCompleted = step.step < activeStep;
                return (
                  <button
                    key={step.step}
                    onClick={() => setActiveStep(step.step)}
                    className={`w-full text-left p-3.5 rounded-2xl border transition-all flex items-center justify-between group relative overflow-hidden ${
                      isActive
                        ? 'bg-gradient-to-r from-violet-600/20 to-indigo-600/20 border-violet-500 shadow-md shadow-violet-600/5'
                        : 'bg-slate-100/10 dark:bg-white/5 border-slate-200/50 dark:border-white/5 hover:border-violet-500/30'
                    }`}
                  >
                    {/* Active highlight line */}
                    {isActive && (
                      <div className="absolute left-0 top-0 bottom-0 w-1 bg-violet-500 rounded-r-md" />
                    )}

                    <div className="flex items-center gap-3">
                      <div className={`w-7 h-7 rounded-xl flex items-center justify-center font-bold text-xs transition-all ${
                        isActive 
                          ? 'bg-violet-600 text-white shadow-md shadow-violet-600/35 scale-105' 
                          : isCompleted
                            ? 'bg-emerald-500/20 text-emerald-500 border border-emerald-500/20'
                            : 'bg-slate-200/50 text-slate-500 dark:bg-white/5 dark:text-slate-400'
                      }`}>
                        {isCompleted ? <CheckCircle2 className="w-4 h-4" /> : step.step}
                      </div>
                      <div>
                        <h5 className={`text-xs font-bold leading-tight ${isActive ? 'text-violet-600 dark:text-violet-400' : 'text-slate-700 dark:text-slate-200'}`}>
                          {step.name}
                        </h5>
                        <p className="text-[9px] text-slate-400 mt-0.5 truncate max-w-[190px]">
                          {step.description}
                        </p>
                      </div>
                    </div>
                    <ChevronRight className={`w-4 h-4 text-slate-400 group-hover:translate-x-1 transition-transform ${isActive ? 'text-violet-500' : ''}`} />
                  </button>
                );
              })}
            </div>
          </div>

          {/* RIGHT: Live Visualizer Pane */}
          <div className="lg:col-span-8">
            <GlassCard glow="indigo" className="min-h-[460px] flex flex-col justify-between">
              {/* Header */}
              <div className="pb-4 border-b border-slate-200/50 dark:border-white/5">
                <div className="flex items-center justify-between">
                  <span className="text-[9px] bg-indigo-500/10 text-indigo-500 dark:text-indigo-400 px-2 py-0.5 rounded-md font-bold uppercase tracking-wider">
                    Pipeline Step {currentStepData.step} of 7
                  </span>
                  <div className="flex items-center gap-1.5 text-xs text-slate-400">
                    <Eye className="w-3.5 h-3.5" />
                    <span>Live Output</span>
                  </div>
                </div>
                <h3 className="text-md font-extrabold text-slate-800 dark:text-white mt-1.5">
                  {currentStepData.name}
                </h3>
                <p className="text-xs text-slate-400 mt-0.5">
                  {currentStepData.description}
                </p>
              </div>

              {/* Step Visualization Area */}
              <div className="flex-1 py-6 overflow-y-auto max-h-[340px]">
                {/* STEP 1: SENTENCE SEGMENTATION */}
                {currentStepData.step === 1 && (
                  <div className="space-y-4">
                    <div className="p-4 rounded-2xl bg-slate-900 border border-slate-800 font-mono text-sm leading-relaxed text-[#00ffcc]">
                      <span className="text-slate-500 text-[10px] select-none block mb-1">{"// RAW INPUT STRING"}</span>
                      {currentStepData.inputs.text}
                    </div>
                    <div className="space-y-2">
                      <span className="text-[10px] text-slate-400 uppercase font-bold tracking-wider">Segmented Sentences ({currentStepData.outputs.sentences.length})</span>
                      {currentStepData.outputs.sentences.map((sent: string, i: number) => (
                        <div key={i} className="p-3.5 rounded-xl border border-violet-500/20 bg-violet-600/5 text-xs font-medium text-slate-700 dark:text-slate-200 flex items-center gap-3">
                          <span className="w-5 h-5 rounded-md bg-violet-500/20 text-violet-500 flex items-center justify-center font-bold text-[10px]">
                            {i+1}
                          </span>
                          <span>{sent}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* STEP 2: WORD TOKENIZATION */}
                {currentStepData.step === 2 && (
                  <div className="space-y-5">
                    <div className="p-3.5 rounded-xl bg-slate-100/30 dark:bg-white/5 border border-slate-200/50 dark:border-white/5 text-xs text-slate-400">
                      <span className="font-bold text-slate-700 dark:text-slate-200 block mb-1">Inputs (Sentences)</span>
                      {currentStepData.inputs.sentences.join(" ")}
                    </div>
                    <div className="space-y-2">
                      <span className="text-[10px] text-slate-400 uppercase font-bold tracking-wider">Extracted Tokens ({currentStepData.outputs.tokens.length})</span>
                      <div className="flex flex-wrap gap-1.5 p-4 rounded-2xl bg-slate-900 border border-slate-800">
                        {currentStepData.outputs.tokens.map((tok: string, idx: number) => (
                          <span 
                            key={idx} 
                            className="px-2.5 py-1 rounded-lg font-mono text-xs font-bold bg-violet-950 text-violet-400 border border-violet-800/35 hover:scale-105 transition-all shadow-sm"
                          >
                            {tok}
                          </span>
                        ))}
                      </div>
                    </div>
                  </div>
                )}

                {/* STEP 3: STOPWORDS FILTERING */}
                {currentStepData.step === 3 && (
                  <div className="space-y-5">
                    <div className="grid grid-cols-2 gap-4 text-xs">
                      <div className="p-4 rounded-xl border border-slate-200/30">
                        <span className="text-[10px] text-slate-400 font-bold block uppercase">Detected Language</span>
                        <span className="font-semibold text-slate-700 dark:text-slate-200 mt-1 block">{currentStepData.inputs.language}</span>
                      </div>
                      <div className="p-4 rounded-xl border border-slate-200/30">
                        <span className="text-[10px] text-slate-400 font-bold block uppercase">Filtered Content Tokens</span>
                        <span className="font-semibold text-emerald-500 mt-1 block">{currentStepData.outputs.filtered_tokens.length} / {currentStepData.inputs.tokens.length}</span>
                      </div>
                    </div>

                    <div className="space-y-3">
                      <span className="text-[10px] text-slate-400 uppercase font-bold tracking-wider">Filtered Pipeline Output</span>
                      <div className="p-4 rounded-2xl bg-slate-100/10 dark:bg-white/5 border border-slate-200/50 dark:border-white/5 space-y-3.5">
                        {/* Highlights */}
                        <div className="flex flex-wrap gap-1.5">
                          {currentStepData.inputs.tokens.map((tok: string, idx: number) => {
                            const isStopword = currentStepData.outputs.removed_stopwords.some((s: string) => s.toLowerCase() === tok.toLowerCase());
                            return (
                              <span 
                                key={idx} 
                                className={`px-2 py-0.5 rounded font-mono text-xs ${
                                  isStopword 
                                    ? 'bg-rose-500/10 text-rose-400/60 line-through border border-rose-500/10' 
                                    : 'bg-emerald-500/15 text-emerald-400 font-bold border border-emerald-500/25'
                                }`}
                              >
                                {tok}
                              </span>
                            );
                          })}
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {/* STEP 4: PART-OF-SPEECH TAGGING */}
                {currentStepData.step === 4 && (
                  <div className="space-y-4">
                    <span className="text-[10px] text-slate-400 uppercase font-bold tracking-wider block">Grammatical Tagging View</span>
                    <div className="flex flex-wrap gap-2.5 p-4 rounded-2xl bg-slate-100/10 dark:bg-white/5 border border-slate-200/50 dark:border-white/5">
                      {currentStepData.outputs.pos_tags.map((tagObj: any, idx: number) => (
                        <div 
                          key={idx} 
                          className="flex flex-col items-center bg-slate-200/50 dark:bg-white/5 p-2 rounded-xl border border-slate-200/30 min-w-[65px] hover:scale-105 transition-all cursor-help"
                          title={tagObj.description}
                        >
                          <span className="font-bold text-slate-700 dark:text-slate-200 text-xs">{tagObj.token}</span>
                          <span className={`text-[8px] font-extrabold px-1.5 py-0.2 rounded-md mt-1.5 ${getPosBadgeColor(tagObj.tag)}`}>
                            {tagObj.tag}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* STEP 5: LEMMATIZATION */}
                {currentStepData.step === 5 && (
                  <div className="space-y-4">
                    <span className="text-[10px] text-slate-400 uppercase font-bold tracking-wider block">Words Reductions to Lemmas</span>
                    <div className="border border-slate-200/50 dark:border-white/5 rounded-2xl overflow-hidden bg-slate-100/10 dark:bg-white/5">
                      <table className="w-full text-left text-xs border-collapse">
                        <thead>
                          <tr className="bg-slate-200/50 dark:bg-white/5 border-b border-slate-200/50 dark:border-white/5">
                            <th className="p-3 font-bold text-slate-400">Original Token</th>
                            <th className="p-3 font-bold text-slate-400">Arrow</th>
                            <th className="p-3 font-bold text-slate-400">Resolved Lemma</th>
                          </tr>
                        </thead>
                        <tbody>
                          {currentStepData.outputs.lemmas.map((item: any, idx: number) => (
                            <tr key={idx} className="border-b border-slate-200/10 last:border-b-0 hover:bg-slate-200/20 dark:hover:bg-white/2 cursor-default">
                              <td className="p-3 font-semibold text-slate-700 dark:text-slate-300">{item.token}</td>
                              <td className="p-3 text-violet-500 font-bold"><ArrowRight className="w-4 h-4" /></td>
                              <td className="p-3 font-mono font-bold text-indigo-500 dark:text-indigo-400">{item.lemma}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                )}

                {/* STEP 6: ENTITY & INTENT MATCHING */}
                {currentStepData.step === 6 && (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <GlassCard>
                      <span className="text-[9px] uppercase font-bold text-slate-400">Intent Resolved</span>
                      <div className="flex justify-between items-center mt-2 p-3 rounded-xl border border-violet-500/20 bg-violet-600/5">
                        <span className="font-mono text-xs font-bold text-violet-600 dark:text-violet-400">
                          {currentStepData.outputs.detected_intent}
                        </span>
                        <span className="text-xs font-extrabold text-slate-600 dark:text-slate-200">
                          {Math.round(currentStepData.outputs.confidence_score * 100)}%
                        </span>
                      </div>
                    </GlassCard>

                    <GlassCard>
                      <span className="text-[9px] uppercase font-bold text-slate-400">NER Mappings</span>
                      <div className="space-y-2 mt-2">
                        {Object.keys(currentStepData.outputs.extracted_entities).map((key) => {
                          if (key === 'keywords') return null;
                          const val = currentStepData.outputs.extracted_entities[key];
                          if (!val) return null;
                          return (
                            <div key={key} className="flex justify-between items-center text-[11px] p-2 bg-slate-200/30 dark:bg-white/5 border border-slate-200/20 rounded-lg">
                              <span className="text-slate-400 capitalize font-medium">{key.replace('_', ' ')}</span>
                              <span className="font-bold text-slate-800 dark:text-white truncate max-w-[130px]">{String(val)}</span>
                            </div>
                          );
                        })}
                      </div>
                    </GlassCard>
                  </div>
                )}

                {/* STEP 7: SEMANTIC ACTION RESOLUTION */}
                {currentStepData.step === 7 && (
                  <div className="space-y-4">
                    <div>
                      <span className="text-[10px] text-slate-400 uppercase font-bold tracking-wider block mb-1">Functional Logical Form</span>
                      <pre className="p-3.5 rounded-xl bg-slate-900 text-[#00ffcc] font-mono text-xs border border-slate-800 overflow-x-auto">
                        {currentStepData.outputs.logical_form}
                      </pre>
                    </div>

                    <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-xs">
                      {Object.keys(currentStepData.outputs.semantic_relations).map((key) => (
                        <div key={key} className="p-2.5 rounded-xl border border-slate-200/30 bg-slate-100/10 dark:bg-white/5">
                          <span className="text-[9px] text-slate-400 font-bold block uppercase">{key}</span>
                          <span className="font-semibold text-slate-700 dark:text-slate-200 mt-1 block truncate">
                            {currentStepData.outputs.semantic_relations[key]}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              {/* Navigation buttons */}
              <div className="pt-4 border-t border-slate-200/50 dark:border-white/5 flex items-center justify-between">
                <button
                  onClick={() => setActiveStep(prev => Math.max(prev - 1, 1))}
                  disabled={activeStep === 1}
                  className="px-4 py-2 text-xs font-bold rounded-xl border border-slate-200 dark:border-white/5 text-slate-700 dark:text-slate-200 hover:bg-slate-200/35 dark:hover:bg-white/5 disabled:opacity-30 disabled:pointer-events-none transition-all"
                >
                  Previous
                </button>
                <div className="flex items-center gap-1.5">
                  {[1, 2, 3, 4, 5, 6, 7].map((num) => (
                    <button
                      key={num}
                      onClick={() => setActiveStep(num)}
                      className={`w-2 h-2 rounded-full transition-all ${
                        num === activeStep ? 'bg-violet-600 w-4' : 'bg-slate-300 dark:bg-white/10'
                      }`}
                    />
                  ))}
                </div>
                <button
                  onClick={() => setActiveStep(prev => Math.min(prev + 1, 7))}
                  disabled={activeStep === 7}
                  className="px-4 py-2 text-xs font-bold rounded-xl bg-violet-600 text-white hover:bg-violet-500 disabled:opacity-30 disabled:pointer-events-none transition-all"
                >
                  Next
                </button>
              </div>
            </GlassCard>
          </div>
        </div>
      ) : (
        /* Original Diagnostics summaries */
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
      )}

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
              className="p-4 rounded-2xl border border-slate-200/50 dark:border-white/5 bg-slate-100/10 dark:bg-white/5 space-y-2.5 relative overflow-hidden font-sans"
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
