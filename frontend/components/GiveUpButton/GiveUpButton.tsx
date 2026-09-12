'use client';

import React from 'react';
import { Flag } from 'lucide-react';

interface GiveUpButtonProps {
  available: boolean;
  guessCount: number;
  onGiveUp: () => void;
  isLoading: boolean;
}

export const GiveUpButton: React.FC<GiveUpButtonProps> = ({
  available,
  guessCount,
  onGiveUp,
  isLoading,
}) => {
  // Only available after the first guess has been made
  if (!available || guessCount < 1) {
    return null;
  }

  return (
    <div className="fixed bottom-6 right-6 z-50 pointer-events-auto animate-bounce-subtle">
      <button
        type="button"
        disabled={isLoading}
        onClick={onGiveUp}
        className="group flex items-center gap-2.5 px-5 py-3 rounded-full bg-gradient-to-r from-rose-600 via-red-600 to-rose-700 text-white font-black text-xs tracking-wider uppercase shadow-2xl shadow-rose-600/50 border-2 border-rose-400 hover:brightness-125 hover:scale-105 active:scale-95 transition-all duration-200 backdrop-blur-md"
        title="End the case and reveal the truth"
      >
        <Flag className="w-4 h-4 text-white group-hover:rotate-12 transition-transform duration-200 shrink-0" />
        <span>GIVE UP, BRO</span>
        <span className="text-[10px] bg-rose-950/90 px-2 py-0.5 rounded-full border border-rose-400/40 text-rose-200 font-mono">
          {guessCount} {guessCount === 1 ? 'GUESS' : 'GUESSES'}
        </span>
      </button>
    </div>
  );
};
