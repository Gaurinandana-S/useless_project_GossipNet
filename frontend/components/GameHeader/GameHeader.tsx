'use client';

import React from 'react';
import { Network, Trophy, HelpCircle, Shield, ArrowLeft } from 'lucide-react';

interface GameHeaderProps {
  round: number;
  score: number;
  questionsLeft: number;
  guessesLeft?: number;
  guessCount?: number;
  gameMode?: string;
  onResetToMenu: () => void;
}

export const GameHeader: React.FC<GameHeaderProps> = ({
  round,
  score,
  questionsLeft,
  guessesLeft,
  guessCount = 0,
  gameMode = 'GUESS_RUMOR_START',
  onResetToMenu,
}) => {
  const isPhase2 = gameMode === 'GUESS_RUMOR_END';

  return (
    <header className="bg-slate-900/90 backdrop-blur-md border-b border-slate-800 px-6 py-3 flex items-center justify-between z-20 relative shadow-lg shadow-black/40">
      {/* Left: Brand Logo & Title */}
      <div className="flex items-center gap-4">
        <button
          onClick={onResetToMenu}
          className="p-2 rounded-lg bg-slate-800/80 hover:bg-slate-700/80 text-slate-300 transition-colors border border-slate-700"
          title="Return to Main Menu"
        >
          <ArrowLeft className="w-4 h-4" />
        </button>
        <div className="flex items-center gap-2">
          <div className={`p-1.5 rounded-lg text-slate-950 ${
            isPhase2
              ? 'bg-gradient-to-br from-cyan-500 to-blue-600'
              : 'bg-gradient-to-br from-amber-500 to-orange-600'
          }`}>
            <Network className="w-5 h-5" />
          </div>
          <div>
            <h1 className={`text-xl font-black tracking-tight leading-none ${
              isPhase2 ? 'text-cyan-400' : 'text-amber-400'
            }`}>
              GossipNet
            </h1>
            <span className={`text-[10px] font-mono tracking-wider font-semibold ${
              isPhase2 ? 'text-cyan-300' : 'text-slate-400'
            }`}>
              {isPhase2 ? 'PHASE 2 • GUESS THE END' : 'PHASE 1 • GUESS THE START'}
            </span>
          </div>
        </div>
      </div>

      {/* Middle: Round & Stats */}
      <div className="flex items-center gap-6">
        <div className="flex items-center gap-2 bg-slate-800/60 px-3 py-1.5 rounded-xl border border-slate-700/60">
          <span className="text-xs text-slate-400 uppercase font-semibold">ROUND</span>
          <span className="text-sm font-extrabold text-amber-300 font-mono">{round}</span>
        </div>

        <div className="flex items-center gap-2 bg-slate-800/60 px-3 py-1.5 rounded-xl border border-slate-700/60">
          <Trophy className="w-4 h-4 text-amber-400" />
          <span className="text-xs text-slate-400 uppercase font-semibold">SCORE</span>
          <span className="text-sm font-extrabold text-slate-100 font-mono">{score}</span>
        </div>
      </div>

      {/* Right: Counters */}
      <div className="flex items-center gap-3">
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-cyan-950/40 border border-cyan-500/30 text-cyan-300">
          <HelpCircle className="w-4 h-4 text-cyan-400" />
          <span className="text-xs font-semibold">QUESTIONS LEFT:</span>
          <span className="text-sm font-extrabold font-mono text-cyan-200">{questionsLeft}</span>
        </div>

        <div className="flex items-center gap-2 px-3 py-1.5 rounded-xl border bg-amber-950/40 border-amber-500/30 text-amber-300">
          <Shield className="w-4 h-4 text-amber-400" />
          <span className="text-xs font-semibold">{isPhase2 ? 'PREDICTIONS:' : 'GUESSES:'}</span>
          <span className="text-sm font-extrabold font-mono text-amber-200">{guessCount}</span>
        </div>
      </div>
    </header>
  );
};
