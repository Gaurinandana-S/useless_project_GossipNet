'use client';

import React, { useState } from 'react';
import { Search, UserCheck, ShieldAlert, Sparkles, Network, ArrowRight } from 'lucide-react';

interface MainMenuProps {
  onStartGame: (difficulty: number, gameMode?: string) => void;
  isLoading: boolean;
}

export const MainMenu: React.FC<MainMenuProps> = ({ onStartGame, isLoading }) => {
  const [selectedPlayerType, setSelectedPlayerType] = useState<'DETECTIVE' | 'VICTIM'>('DETECTIVE');
  const [selectedMode, setSelectedMode] = useState<'START' | 'CYCLE' | 'END'>('START');
  const [difficulty, setDifficulty] = useState<number>(1);

  const activeModeString = selectedMode === 'END' ? 'GUESS_RUMOR_END' : 'GUESS_RUMOR_START';

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col justify-center items-center p-4 relative overflow-hidden font-sans">
      {/* Background Glowing Gradients */}
      <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-amber-500/10 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute inset-0 bg-[radial-gradient(#1e293b_1px,transparent_1px)] [background-size:24px_24px] opacity-30 pointer-events-none" />

      <div className="relative z-10 max-w-2xl w-full bg-slate-900/80 backdrop-blur-xl border border-slate-800 rounded-3xl p-8 shadow-2xl shadow-black/80 space-y-8">
        
        {/* Header Branding */}
        <div className="text-center space-y-3">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-amber-500/10 border border-amber-500/30 text-amber-400 text-xs font-semibold tracking-wider uppercase">
            <Network className="w-3.5 h-3.5" /> Graph Detective Game • Phase 1 & 2
          </div>
          <h1 className="text-5xl font-extrabold tracking-tight bg-gradient-to-r from-amber-400 via-orange-300 to-amber-500 bg-clip-text text-transparent">
            GossipNet
          </h1>
          <p className="text-lg font-medium text-slate-300 italic">
            &ldquo;You were right. Unfortunately, you&apos;re wrong.&rdquo;
          </p>
          <p className="text-sm text-slate-400 font-mono">
            Nothing stays secret.
          </p>
        </div>

        {/* Step 1: Select Player Type */}
        <div className="space-y-3">
          <label className="text-xs font-bold text-slate-400 uppercase tracking-widest block">
            1. Select Player Role
          </label>
          <div className="grid grid-cols-2 gap-4">
            <button
              type="button"
              onClick={() => setSelectedPlayerType('DETECTIVE')}
              className={`flex items-center justify-between p-4 rounded-xl border transition-all ${
                selectedPlayerType === 'DETECTIVE'
                  ? 'bg-amber-500/15 border-amber-500/60 text-amber-300 ring-2 ring-amber-500/40 shadow-lg shadow-amber-500/10'
                  : 'bg-slate-800/40 border-slate-700/60 text-slate-400 hover:border-slate-600'
              }`}
            >
              <div className="flex items-center gap-3 text-left">
                <Search className="w-5 h-5 text-amber-400" />
                <div>
                  <div className="font-bold text-slate-100">DETECTIVE</div>
                  <div className="text-xs text-slate-400">Investigate & uncover leaks</div>
                </div>
              </div>
              <span className="text-xs px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-400 font-semibold">PLAYABLE</span>
            </button>

            <button
              type="button"
              disabled
              className="flex items-center justify-between p-4 rounded-xl border border-slate-800/80 bg-slate-900/40 text-slate-600 cursor-not-allowed opacity-60"
            >
              <div className="flex items-center gap-3 text-left">
                <UserCheck className="w-5 h-5 text-slate-600" />
                <div>
                  <div className="font-bold text-slate-500">VICTIM</div>
                  <div className="text-xs text-slate-600">Survive rumor spread</div>
                </div>
              </div>
              <span className="text-xs px-2 py-0.5 rounded bg-slate-800 text-slate-400 font-medium">COMING SOON</span>
            </button>
          </div>
        </div>

        {/* Step 2: Select Game Mode */}
        <div className="space-y-3">
          <label className="text-xs font-bold text-slate-400 uppercase tracking-widest block">
            2. Select Game Mode
          </label>
          <div className="space-y-2">
            <button
              type="button"
              onClick={() => setSelectedMode('START')}
              className={`w-full flex items-center justify-between p-4 rounded-xl border text-left transition-all ${
                selectedMode === 'START'
                  ? 'bg-gradient-to-r from-amber-500/20 to-orange-500/10 border-amber-500/60 text-amber-200 ring-2 ring-amber-500/30'
                  : 'bg-slate-800/40 border-slate-700/60 text-slate-400 hover:border-slate-600'
              }`}
            >
              <div>
                <div className="font-bold text-slate-100 flex items-center gap-2">
                  <Sparkles className="w-4 h-4 text-amber-400" /> GUESS THE RUMOR START
                </div>
                <div className="text-xs text-slate-400 mt-1">
                  Identify who initiated the secret in the extended Kerala family network.
                </div>
              </div>
              <span className="text-xs px-2.5 py-1 rounded bg-amber-500/20 text-amber-300 font-bold">PHASE 1</span>
            </button>

            <button
              type="button"
              onClick={() => setSelectedMode('END')}
              className={`w-full flex items-center justify-between p-4 rounded-xl border text-left transition-all ${
                selectedMode === 'END'
                  ? 'bg-gradient-to-r from-cyan-500/20 to-blue-500/10 border-cyan-500/60 text-cyan-200 ring-2 ring-cyan-500/30'
                  : 'bg-slate-800/40 border-slate-700/60 text-slate-400 hover:border-slate-600'
              }`}
            >
              <div>
                <div className="font-bold text-slate-100 flex items-center gap-2">
                  <Network className="w-4 h-4 text-cyan-400" /> GUESS THE RUMOR END
                </div>
                <div className="text-xs text-slate-400 mt-1">
                  Simulate rumor propagation & predict who will be the final recipient to hear the rumor!
                </div>
              </div>
              <span className="text-xs px-2.5 py-1 rounded bg-cyan-500/20 text-cyan-300 font-bold">PHASE 2</span>
            </button>

            <div className="flex items-center justify-between p-3 rounded-xl border border-slate-800/60 bg-slate-900/30 text-slate-500 opacity-60">
              <span className="font-semibold text-sm">GUESS THE RUMOR CYCLE</span>
              <span className="text-xs px-2 py-0.5 rounded bg-slate-800 text-slate-400">COMING SOON</span>
            </div>
          </div>
        </div>

        {/* Step 3: Select Difficulty */}
        <div className="space-y-2">
          <label className="text-xs font-bold text-slate-400 uppercase tracking-widest block">
            3. Initial Graph Scale (Difficulty)
          </label>
          <div className="grid grid-cols-3 gap-3">
            {[
              { level: 1, label: 'Round 1 (20-30 People)' },
              { level: 2, label: 'Round 2 (25-35 People)' },
              { level: 3, label: 'Round 3 (30-45 People)' },
            ].map((d) => (
              <button
                key={d.level}
                type="button"
                onClick={() => setDifficulty(d.level)}
                className={`py-2 px-3 rounded-lg border text-xs font-medium transition-all ${
                  difficulty === d.level
                    ? selectedMode === 'END'
                      ? 'bg-cyan-500/20 border-cyan-500/60 text-cyan-300 font-bold'
                      : 'bg-amber-500/20 border-amber-500/60 text-amber-300 font-bold'
                    : 'bg-slate-800/40 border-slate-700/50 text-slate-400 hover:border-slate-600'
                }`}
              >
                {d.label}
              </button>
            ))}
          </div>
        </div>

        {/* Play Button */}
        <button
          type="button"
          onClick={() => onStartGame(difficulty, activeModeString)}
          disabled={isLoading}
          className={`w-full py-4 px-6 rounded-2xl font-black text-lg tracking-wider uppercase hover:brightness-110 active:scale-[0.99] transition-all shadow-xl flex items-center justify-center gap-3 disabled:opacity-50 ${
            selectedMode === 'END'
              ? 'bg-gradient-to-r from-cyan-500 via-blue-500 to-cyan-600 text-slate-950 shadow-cyan-500/20'
              : 'bg-gradient-to-r from-amber-500 via-orange-500 to-amber-600 text-slate-950 shadow-amber-500/20'
          }`}
        >
          {isLoading ? (
            <div className="flex items-center gap-2">
              <div className="w-5 h-5 border-2 border-slate-950 border-t-transparent rounded-full animate-spin" />
              Generating Procedural Graph...
            </div>
          ) : (
            <>
              START {selectedMode === 'END' ? 'PROPAGATION' : ''} INVESTIGATION <ArrowRight className="w-5 h-5" />
            </>
          )}
        </button>
      </div>
    </div>
  );
};

