'use client';

import React, { useState, useEffect, useRef } from 'react';
import { Person, AvailableQuestion, AskedQuestion } from '@/types/game';
import { MessageSquare, Send, Sparkles, UserCheck, HelpCircle } from 'lucide-react';

interface ChatbotPanelProps {
  selectedPerson: Person | null;
  questionsLeft: number;
  availableQuestions: AvailableQuestion[];
  askedQuestions: AskedQuestion[];
  onAskQuestion: (personId: string, questionKey?: string, customText?: string) => void;
  isLoading: boolean;
}

export const ChatbotPanel: React.FC<ChatbotPanelProps> = ({
  selectedPerson,
  questionsLeft,
  availableQuestions,
  askedQuestions,
  onAskQuestion,
  isLoading,
}) => {
  const [activeCategory, setActiveCategory] = useState<'BASIC' | 'GOSSIP' | 'RELATIONSHIP' | 'DEDUCTION'>('BASIC');
  const [customInput, setCustomInput] = useState('');
  const chatEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll chat to bottom when new messages arrive
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [askedQuestions, selectedPerson]);

  const filteredQuestions = availableQuestions.filter(
    (q) => (q as any).category === activeCategory
  );

  const handleCustomSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedPerson || !customInput.trim() || questionsLeft <= 0 || isLoading) return;
    onAskQuestion(selectedPerson.id, undefined, customInput.trim());
    setCustomInput('');
  };

  return (
    <div className="bg-slate-900/95 border border-slate-800 rounded-2xl shadow-2xl backdrop-blur-xl flex flex-col h-full overflow-hidden">
      
      {/* 1. Header: Interrogation Target */}
      <div className="bg-gradient-to-r from-slate-900 via-amber-950/40 to-slate-900 p-3.5 border-b border-slate-800 flex items-center justify-between">
        {selectedPerson ? (
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-amber-500/20 border border-amber-500/50 flex items-center justify-center text-amber-400 font-black text-sm">
              {selectedPerson.gender}
            </div>
            <div>
              <div className="flex items-center gap-1.5 flex-wrap">
                <span className="text-[10px] font-extrabold uppercase tracking-wider text-amber-400 bg-amber-500/10 px-1.5 py-0.5 rounded border border-amber-500/30">
                  INTERROGATING
                </span>
                <span className="text-[10px] text-slate-400 font-mono">Gen {selectedPerson.generation}</span>
                {selectedPerson.communication_frequency && (
                  <span className="text-[9px] font-mono text-cyan-300 bg-cyan-950/60 px-1.5 py-0.5 rounded border border-cyan-800/40" title="Communication Frequency">
                    Comm: {selectedPerson.communication_frequency}
                  </span>
                )}
                {selectedPerson.secret_keeping && (
                  <span className="text-[9px] font-mono text-indigo-300 bg-indigo-950/60 px-1.5 py-0.5 rounded border border-indigo-800/40" title="Secret Keeping Tendency">
                    Secret: {selectedPerson.secret_keeping}
                  </span>
                )}
              </div>
              <h2 className="font-extrabold text-base text-slate-100 leading-tight">
                {selectedPerson.name}
              </h2>
            </div>
          </div>
        ) : (
          <div className="flex items-center gap-2 text-slate-400 text-xs font-semibold">
            <UserCheck className="w-4 h-4 text-slate-500" />
            <span>Select a family member on the graph to start interrogation</span>
          </div>
        )}

        {/* Question Counter */}
        <div className="flex items-center gap-1.5 px-3 py-1 rounded-xl bg-cyan-950/60 border border-cyan-500/40 text-cyan-300 shadow-md">
          <HelpCircle className="w-4 h-4 text-cyan-400" />
          <span className="text-[11px] font-bold">LEFT:</span>
          <span className="text-sm font-black font-mono text-cyan-200">{questionsLeft}</span>
        </div>
      </div>

      {/* 2. Chat Message Thread Area */}
      <div className="flex-1 p-4 overflow-y-auto space-y-4 bg-slate-950/60">
        {!selectedPerson ? (
          <div className="h-full flex flex-col items-center justify-center text-center p-6 text-slate-500 space-y-2">
            <MessageSquare className="w-10 h-10 text-slate-700 animate-pulse" />
            <p className="text-xs max-w-xs font-medium text-slate-400">
              Click any node in the family tree on the left to begin an interrogation session.
            </p>
          </div>
        ) : (
          <>
            {/* Initial Greeting */}
            <div className="space-y-2">
              <div className="flex items-start gap-2.5 max-w-[85%]">
                <div className="w-7 h-7 rounded-lg bg-amber-500/20 border border-amber-500/40 text-amber-400 flex items-center justify-center text-xs font-bold shrink-0">
                  DET
                </div>
                <div className="bg-slate-800/80 border border-slate-700 text-slate-200 text-xs p-3 rounded-2xl rounded-tl-none space-y-1">
                  <div className="font-bold text-[10px] text-amber-400 uppercase">Detective</div>
                  <p>I have a few questions for you regarding the recent family rumor.</p>
                </div>
              </div>

              <div className="flex items-start gap-2.5 max-w-[85%] ml-auto flex-row-reverse">
                <div className="w-7 h-7 rounded-lg bg-emerald-500/20 border border-emerald-500/40 text-emerald-400 flex items-center justify-center text-xs font-bold shrink-0">
                  {selectedPerson.gender}
                </div>
                <div className="bg-emerald-950/40 border border-emerald-500/30 text-slate-200 text-xs p-3 rounded-2xl rounded-tr-none space-y-1">
                  <div className="font-bold text-[10px] text-emerald-400 uppercase">{selectedPerson.name}</div>
                  <p>&ldquo;Fine... but make it quick. What do you want to ask?&rdquo;</p>
                </div>
              </div>
            </div>

            {/* Conversation Log for this session */}
            {askedQuestions.map((aq, idx) => (
              <div key={idx} className="space-y-2 pt-2 border-t border-slate-800/60">
                {/* Detective Question Bubble */}
                <div className="flex items-start gap-2.5 max-w-[85%]">
                  <div className="w-7 h-7 rounded-lg bg-amber-500/20 border border-amber-500/40 text-amber-400 flex items-center justify-center text-xs font-bold shrink-0">
                    DET
                  </div>
                  <div className="bg-slate-800/80 border border-slate-700 text-slate-200 text-xs p-3 rounded-2xl rounded-tl-none">
                    <p className="font-medium text-amber-300">&ldquo;{aq.question_text || aq.question_key}&rdquo;</p>
                  </div>
                </div>

                {/* Persona Response Bubble */}
                <div className="flex items-start gap-2.5 max-w-[85%] ml-auto flex-row-reverse">
                  <div className="w-7 h-7 rounded-lg bg-emerald-500/20 border border-emerald-500/40 text-emerald-400 flex items-center justify-center text-xs font-bold shrink-0">
                    {aq.person_name ? aq.person_name.charAt(0) : 'P'}
                  </div>
                  <div className="bg-emerald-950/40 border border-emerald-500/30 text-slate-100 text-xs p-3 rounded-2xl rounded-tr-none space-y-1">
                    <div className="font-bold text-[10px] text-emerald-400 uppercase">{aq.person_name}</div>
                    <p className="italic font-serif text-sm text-slate-200">
                      {aq.persona_dialogue || aq.answer_text}
                    </p>
                  </div>
                </div>

                {/* System Dead-End Commentary */}
                {aq.system_commentary && (
                  <div className="my-1.5 p-2.5 rounded-xl bg-slate-900 border border-slate-800 text-[11px] text-amber-400/90 font-medium flex items-center gap-2 shadow-inner">
                    <Sparkles className="w-3.5 h-3.5 text-amber-400 shrink-0" />
                    <span>{aq.system_commentary}</span>
                  </div>
                )}
              </div>
            ))}

            <div ref={chatEndRef} />
          </>
        )}
      </div>

      {/* 3. Category Selector & Quick Question Options */}
      {selectedPerson && (
        <div className="bg-slate-900 border-t border-slate-800 p-3 space-y-2.5">
          {/* Category Tabs */}
          <div className="flex items-center gap-1.5 overflow-x-auto pb-1">
            {[
              { id: 'BASIC', label: 'BASIC INFO' },
              { id: 'GOSSIP', label: 'GOSSIP' },
              { id: 'RELATIONSHIP', label: 'RELATIONSHIPS' },
              { id: 'DEDUCTION', label: 'DEDUCTION' },
            ].map((cat) => (
              <button
                key={cat.id}
                type="button"
                onClick={() => setActiveCategory(cat.id as any)}
                className={`px-3 py-1.5 rounded-xl text-[11px] font-bold tracking-wider uppercase transition-all whitespace-nowrap ${
                  activeCategory === cat.id
                    ? 'bg-amber-500/20 border border-amber-500/60 text-amber-300 ring-2 ring-amber-500/20'
                    : 'bg-slate-800/60 border border-slate-700/60 text-slate-400 hover:border-slate-600'
                }`}
              >
                {cat.label}
              </button>
            ))}
          </div>

          {/* Question Option Buttons */}
          <div className="grid grid-cols-1 gap-1.5 max-h-28 overflow-y-auto pr-1">
            {filteredQuestions.map((q) => {
              const isDisabled = questionsLeft <= 0 || isLoading;
              return (
                <button
                  key={q.key}
                  type="button"
                  disabled={isDisabled}
                  onClick={() => onAskQuestion(selectedPerson.id, q.key)}
                  className={`w-full p-2 rounded-xl border text-left text-xs font-semibold flex items-center justify-between transition-all ${
                    isDisabled
                      ? 'bg-slate-900/40 border-slate-800 text-slate-600 cursor-not-allowed opacity-60'
                      : 'bg-slate-800/60 border-slate-700/80 text-slate-200 hover:border-amber-400 hover:bg-slate-800 hover:text-amber-300'
                  }`}
                >
                  <span className="truncate">{q.text}</span>
                  <Send className="w-3.5 h-3.5 text-amber-400 shrink-0 ml-2" />
                </button>
              );
            })}
          </div>

          {/* 4. Interactive Chatbox Input */}
          <form onSubmit={handleCustomSubmit} className="flex items-center gap-2 pt-1">
            <input
              type="text"
              value={customInput}
              onChange={(e) => setCustomInput(e.target.value)}
              disabled={questionsLeft <= 0 || isLoading}
              placeholder={`Ask ${selectedPerson.name} a custom question...`}
              className="flex-1 px-3 py-2 bg-slate-950 border border-slate-700 rounded-xl text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-amber-400 disabled:opacity-50"
            />
            <button
              type="submit"
              disabled={!customInput.trim() || questionsLeft <= 0 || isLoading}
              className="p-2 rounded-xl bg-gradient-to-r from-amber-500 to-orange-500 text-slate-950 font-bold hover:brightness-110 disabled:opacity-40 transition-all"
            >
              <Send className="w-4 h-4" />
            </button>
          </form>
        </div>
      )}
    </div>
  );
};
