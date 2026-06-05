import React, { useState, useEffect } from 'react';
import { Mic, MicOff, Languages } from 'lucide-react';

interface VoiceInputProps {
  onTranscript: (text: string) => void;
  isLoading?: boolean;
}

type LangOption = 'en-US' | 'hi-IN' | 'kn-IN';

export const VoiceInput: React.FC<VoiceInputProps> = ({ onTranscript, isLoading }) => {
  const [isListening, setIsListening] = useState(false);
  const [lang, setLang] = useState<LangOption>('en-US');
  const [recognition, setRecognition] = useState<any>(null);
  const [showSimPresets, setShowSimPresets] = useState(false);

  // Predefined Multilingual simulated commands for testing
  const presets = {
    'en-US': [
      "Send quarterly strategic updates to Priya Sharma",
      "Search documents regarding cloud security audit compliance rules",
      "Check website https://news.ycombinator.com and backup titles to report.json"
    ],
    'hi-IN': [
      "ईमेल भेजें रमेश कुमार को विषय प्रोजेक्ट रिपोर्ट",
      "क्लाउड सुरक्षा ऑडिट दस्तावेज़ खोजें",
      "फ़ोल्डर बैकअप करें"
    ],
    'kn-IN': [
      "ಆರ್ಕೈವ್ ಫೈಲ್ ಬ್ಯಾಕಪ್ ಮಾಡಿ",
      "ರಮೇಶ್ ಕುಮಾರ್ ಗೆ ಇಮೇಲ್ ಕಳುಹಿಸಿ",
      "ವೆಬ್ ಸೈಟ್ ಬ್ರೌಸ್ ಮಾಡಿ"
    ]
  };

  useEffect(() => {
    // Check if webkitSpeechRecognition is available
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (SpeechRecognition) {
      const rec = new SpeechRecognition();
      rec.continuous = false;
      rec.interimResults = false;
      
      rec.onstart = () => {
        setIsListening(true);
      };
      
      rec.onend = () => {
        setIsListening(false);
      };

      rec.onerror = (event: any) => {
        console.error("Speech Recognition Error", event);
        setIsListening(false);
      };

      rec.onresult = (event: any) => {
        const transcript = event.results[0][0].transcript;
        if (transcript) {
          onTranscript(transcript);
        }
      };

      setRecognition(rec);
    }
  }, [onTranscript]);

  useEffect(() => {
    if (recognition) {
      recognition.lang = lang;
    }
  }, [lang, recognition]);

  const toggleListening = () => {
    if (!recognition) {
      // Fallback: Open presets list if speech recognition not supported in browser
      setShowSimPresets(!showSimPresets);
      return;
    }

    if (isListening) {
      recognition.stop();
    } else {
      try {
        recognition.start();
      } catch (err) {
        console.error("Failed to start speech recognition", err);
        // Fallback popup
        setShowSimPresets(true);
      }
    }
  };

  const handlePresetSelect = (preset: string) => {
    onTranscript(preset);
    setShowSimPresets(false);
  };

  return (
    <div className="relative">
      <div className="flex items-center gap-2">
        {/* Language selector */}
        <div className="relative">
          <select
            value={lang}
            onChange={(e) => setLang(e.target.value as LangOption)}
            className="appearance-none bg-slate-100 dark:bg-white/5 border border-slate-200/50 dark:border-white/5 rounded-xl py-2 pl-3 pr-8 text-xs font-semibold text-slate-600 dark:text-slate-300 focus:outline-none focus:border-violet-500 cursor-pointer"
          >
            <option value="en-US">English (US)</option>
            <option value="hi-IN">हिन्दी (India)</option>
            <option value="kn-IN">ಕನ್ನಡ (India)</option>
          </select>
          <Languages className="w-3.5 h-3.5 absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 pointer-events-none" />
        </div>

        {/* Mic Toggle Button */}
        <button
          type="button"
          onClick={toggleListening}
          disabled={isLoading}
          className={`p-2.5 rounded-xl border flex items-center justify-center transition-all ${
            isListening
              ? 'bg-red-500/20 text-red-500 border-red-500/30 animate-pulse'
              : 'bg-slate-100 dark:bg-white/5 border-slate-200/50 dark:border-white/5 text-slate-500 dark:text-slate-300 hover:bg-slate-200/50 dark:hover:bg-white/10'
          }`}
          title={recognition ? "Start Speech Input" : "Open Multilingual Simulated Presets"}
        >
          {isListening ? <MicOff className="w-4 h-4" /> : <Mic className="w-4 h-4" />}
        </button>

        {/* Manual Simulation trigger */}
        <button
          type="button"
          onClick={() => setShowSimPresets(!showSimPresets)}
          className="text-xs text-violet-500 hover:text-violet-600 dark:hover:text-violet-400 font-semibold underline"
        >
          Simulate Preset
        </button>
      </div>

      {/* Preset simulation dropdown */}
      {showSimPresets && (
        <div className="absolute right-0 top-12 z-50 w-72 rounded-xl border border-slate-200 dark:border-white/10 bg-white dark:bg-[#111327] p-3 shadow-xl animate-in fade-in slide-in-from-top-2 duration-150">
          <div className="flex items-center justify-between mb-2 pb-1.5 border-b border-slate-100 dark:border-white/5">
            <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">Simulate Speech In</span>
            <span className="text-xs bg-violet-500/10 text-violet-500 px-2 py-0.5 rounded-md font-semibold">
              {lang === 'en-US' ? 'English' : lang === 'hi-IN' ? 'Hindi' : 'Kannada'}
            </span>
          </div>
          <div className="space-y-1.5">
            {presets[lang].map((preset, idx) => (
              <button
                key={idx}
                type="button"
                onClick={() => handlePresetSelect(preset)}
                className="w-full text-left p-2 text-xs text-slate-600 dark:text-slate-300 hover:bg-violet-500/10 hover:text-violet-600 dark:hover:text-violet-400 rounded-lg transition-colors border border-transparent hover:border-violet-500/20"
              >
                "{preset}"
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
