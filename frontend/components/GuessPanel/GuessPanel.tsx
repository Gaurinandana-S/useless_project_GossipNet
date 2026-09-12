'use client';

import React from 'react';
import { Person, GuessLog } from '@/types/game';
import { Shield, CheckCircle2, XCircle } from 'lucide-react';

interface GuessPanelProps {
  selectedPerson: Person | null;
  guessesLeft?: number;
  guessCount?: number;
  guessesMade: GuessLog[];
  gameMode?: string;
  onMakeGuess: (personId: string) => void;
  isLoading: boolean;
}

export const GuessPanel: React.FC<GuessPanelProps> = ({
  selectedPerson,
  guessCount = 0,
  guessesMade,
  gameMode = 'GUESS_RUMOR_START',
  onMakeGuess,
  isLoading,
}) => {
  const isPhase2 = gameMode === 'GUESS_RUMOR_END';
  const lastGuess = guessesMade.length > 0 ? guessesMade[guessesMade.length - 1] : null;
  const currentGuessNum = guessesMade.length + 1;

  return (
    <div className="bg-slate-900/95 border border-slate-800 rounded-2xl p-4 shadow-xl backdrop-blur-xl flex flex-col space-y-3">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-slate-800 pb-2.5">
        <div className="flex items-center gap-2">
          <Shield className={`w-4 h-4 ${isPhase2 ? 'text-cyan-400' : 'text-amber-400'}`} />
          <h2 className="font-extrabold text-xs text-slate-100 uppercase tracking-wider">
            {isPhase2 ? 'FINAL RECIPIENT PREDICTION' : 'ACCUSATION SYSTEM'}
          </h2>
        </div>
        <span
          className={`text-xs font-mono font-bold px-2 py-0.5 rounded-md border ${
            isPhase2
              ? 'bg-cyan-950/60 border-cyan-500/30 text-cyan-300'
              : 'bg-amber-950/60 border-amber-500/30 text-amber-300'
          }`}
        >
          {isPhase2 ? 'PREDICTION' : 'GUESS'} #{currentGuessNum}
        </span>
      </div>

      {/* Action Button */}
      <button
        type="button"
        disabled={!selectedPerson || isLoading}
        onClick={() => selectedPerson && onMakeGuess(selectedPerson.id)}
        className={`w-full py-3 px-4 rounded-xl font-black text-xs tracking-wider uppercase flex items-center justify-center gap-2 transition-all shadow-lg ${
          !selectedPerson || isLoading
            ? 'bg-slate-800 border border-slate-700 text-slate-500 cursor-not-allowed'
            : isPhase2
            ? 'bg-gradient-to-r from-cyan-500 via-blue-500 to-cyan-600 text-slate-950 hover:brightness-110 active:scale-[0.98] shadow-cyan-500/20'
            : 'bg-gradient-to-r from-amber-500 via-orange-500 to-amber-600 text-slate-950 hover:brightness-110 active:scale-[0.98] shadow-amber-500/20'
        }`}
      >
        <Shield className="w-4 h-4" />
        {selectedPerson
          ? isPhase2
            ? `PREDICT ${selectedPerson.name.toUpperCase()} IS FINAL RECIPIENT`
            : `ACCUSE ${selectedPerson.name.toUpperCase()} OF STARTING RUMOR`
          : isPhase2
          ? 'SELECT A PERSON ON GRAPH TO PREDICT AS END'
          : 'SELECT A PERSON ON GRAPH TO ACCUSE'}
      </button>

      {/* Latest Feedback Banner */}
      {lastGuess && (
        <div
          className={`p-3 rounded-xl border text-xs flex items-start gap-2.5 shadow-md ${
            lastGuess.is_correct
              ? 'bg-emerald-950/90 border-emerald-500/60 text-emerald-200'
              : 'bg-rose-950/90 border-rose-500/60 text-rose-200'
          }`}
        >
          {lastGuess.is_correct ? (
            <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
          ) : (
            <XCircle className="w-4 h-4 text-rose-400 shrink-0 mt-0.5" />
          )}
          <div>
            <div className="font-extrabold">{isPhase2 ? 'Predicted:' : 'Accused:'} {lastGuess.person_name}</div>
            <div className="text-slate-300 mt-0.5 font-medium">{lastGuess.commentary}</div>
          </div>
        </div>
      )}
    </div>
  );
};
