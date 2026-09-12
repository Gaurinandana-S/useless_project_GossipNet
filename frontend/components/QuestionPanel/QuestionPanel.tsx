'use client';

import React from 'react';
import { Person, AvailableQuestion, AskedQuestion } from '@/types/game';
import { HelpCircle, User, History, Send, ChevronRight } from 'lucide-react';

interface QuestionPanelProps {
  selectedPerson: Person | null;
  questionsLeft: number;
  availableQuestions: AvailableQuestion[];
  askedQuestions: AskedQuestion[];
  onAskQuestion: (personId: string, questionKey: string) => void;
  isLoading: boolean;
}

export const QuestionPanel: React.FC<QuestionPanelProps> = ({
  selectedPerson,
  questionsLeft,
  availableQuestions,
  askedQuestions,
  onAskQuestion,
  isLoading,
}) => {
  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-4 shadow-xl backdrop-blur-md flex flex-col h-full space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-slate-800 pb-3">
        <div className="flex items-center gap-2">
          <HelpCircle className="w-5 h-5 text-cyan-400" />
          <h2 className="font-extrabold text-sm text-slate-100 uppercase tracking-wider">
            INVESTIGATION PANEL
          </h2>
        </div>
        <span className="text-xs font-mono font-bold text-cyan-300 bg-cyan-950/60 border border-cyan-500/30 px-2.5 py-1 rounded-lg">
          LEFT: {questionsLeft}
        </span>
      </div>

      {/* Selected Person Display */}
      {selectedPerson ? (
        <div className="bg-slate-800/60 border border-slate-700/80 rounded-xl p-3 flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-lg bg-amber-500/20 text-amber-400 font-bold text-xs">
              {selectedPerson.gender}
            </div>
            <div>
              <div className="font-extrabold text-slate-100 text-sm">{selectedPerson.name}</div>
              <div className="text-xs text-slate-400">
                {selectedPerson.household_name || 'House'} • Gen {selectedPerson.generation}
              </div>
            </div>
          </div>
          <span className="text-[10px] font-semibold text-amber-400 bg-amber-500/10 px-2 py-0.5 rounded border border-amber-500/30">
            TARGETED
          </span>
        </div>
      ) : (
        <div className="bg-slate-950/60 border border-dashed border-slate-800 rounded-xl p-4 text-center text-xs text-slate-400">
          <User className="w-6 h-6 text-slate-600 mx-auto mb-1.5" />
          Click a person on the graph to ask an investigation question.
        </div>
      )}

      {/* Question Options Buttons */}
      <div className="space-y-2 flex-1 overflow-y-auto pr-1">
        <div className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">
          Available Questions:
        </div>

        <div className="grid grid-cols-1 gap-2">
          {availableQuestions.map((q) => {
            const isDisabled = !selectedPerson || questionsLeft <= 0 || isLoading;
            return (
              <button
                key={q.key}
                disabled={isDisabled}
                onClick={() => selectedPerson && onAskQuestion(selectedPerson.id, q.key)}
                className={`w-full p-2.5 rounded-xl border text-left text-xs font-semibold flex items-center justify-between transition-all ${
                  isDisabled
                    ? 'bg-slate-900/40 border-slate-800 text-slate-600 cursor-not-allowed opacity-60'
                    : 'bg-slate-800/40 border-slate-700/80 text-slate-200 hover:border-amber-500/60 hover:bg-slate-800/80 hover:text-amber-300'
                }`}
              >
                <div className="flex items-center gap-2">
                  <ChevronRight className="w-3.5 h-3.5 text-amber-400 shrink-0" />
                  <span>{q.text}</span>
                </div>
                <Send className="w-3.5 h-3.5 text-slate-500 shrink-0" />
              </button>
            );
          })}
        </div>
      </div>

      {/* Investigation Log History */}
      {askedQuestions.length > 0 && (
        <div className="border-t border-slate-800 pt-3 space-y-2">
          <div className="flex items-center gap-1.5 text-[11px] font-bold text-slate-400 uppercase tracking-wider">
            <History className="w-3.5 h-3.5 text-cyan-400" /> Discovered Leads Log ({askedQuestions.length})
          </div>
          <div className="max-h-28 overflow-y-auto space-y-1.5 text-xs pr-1">
            {askedQuestions.slice().reverse().map((aq, idx) => (
              <div key={idx} className="bg-slate-950/80 border border-slate-800 rounded-lg p-2 text-slate-300 space-y-0.5">
                <span className="font-bold text-amber-400">{aq.person_name}:</span>{' '}
                <span className="text-slate-200">{aq.answer_text}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
