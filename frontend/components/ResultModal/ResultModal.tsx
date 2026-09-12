'use client';

import React from 'react';
import { Trophy, ArrowRight, ShieldCheck, Flag, GitCommit, Clock, Network } from 'lucide-react';
import { StarterTruth, FinalPersonTruth, PropagationEvent } from '@/types/game';

interface ResultModalProps {
  status: 'SOLVED' | 'GAVE_UP' | null;
  score: number;
  gameMode?: string;
  starterTruth?: StarterTruth | null;
  finalPersonTruth?: FinalPersonTruth | null;
  giveUpData?: {
    starter_name: string;
    subject_name: string;
    final_person_name?: string | null;
    rumor_content: string;
    relationship_path: string[];
    propagation_tree?: PropagationEvent[];
    commentary: string;
  } | null;
  onNextRumor: () => void;
  isLoading: boolean;
}

export const ResultModal: React.FC<ResultModalProps> = ({
  status,
  score,
  gameMode = 'GUESS_RUMOR_START',
  starterTruth,
  finalPersonTruth,
  giveUpData,
  onNextRumor,
  isLoading,
}) => {
  if (!status) return null;

  const isSolved = status === 'SOLVED';
  const isPhase2 = gameMode === 'GUESS_RUMOR_END';

  const starterName =
    finalPersonTruth?.starter_name ||
    starterTruth?.starter_name ||
    giveUpData?.starter_name ||
    'Hidden Starter';

  const finalPersonName =
    finalPersonTruth?.final_person_name ||
    giveUpData?.final_person_name ||
    'Final Ear';

  const subjectName =
    starterTruth?.subject_name ||
    giveUpData?.subject_name ||
    'Subject';

  const rumorText =
    finalPersonTruth?.rumor_content ||
    starterTruth?.rumor_content ||
    giveUpData?.rumor_content ||
    'Rumor';

  const commentary = giveUpData?.commentary || 'The investigation has concluded.';
  const path = giveUpData?.relationship_path || [];
  const propagationEvents: PropagationEvent[] =
    finalPersonTruth?.propagation_tree ||
    giveUpData?.propagation_tree ||
    [];

  return (
    <div className="fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-xl flex items-center justify-center p-4">
      <div className="max-w-lg w-full bg-slate-900 border border-slate-800 rounded-3xl p-6 shadow-2xl shadow-black space-y-6 text-center relative overflow-hidden">
        
        {/* Top Glow Accent */}
        <div
          className={`absolute -top-24 left-1/2 -translate-x-1/2 w-72 h-72 rounded-full blur-3xl pointer-events-none ${
            isSolved ? (isPhase2 ? 'bg-cyan-500/20' : 'bg-emerald-500/20') : 'bg-rose-500/20'
          }`}
        />

        {/* Header Badge */}
        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-slate-800/80 border border-slate-700 text-xs font-mono font-semibold">
          <Network className="w-3.5 h-3.5 text-amber-400" />
          {isPhase2 ? 'PHASE 2 • GUESS THE END' : 'PHASE 1 • GUESS THE START'}
        </div>

        {/* Victory Scenario */}
        {isSolved ? (
          <div className="space-y-4">
            <div className={`w-16 h-16 rounded-full mx-auto flex items-center justify-center shadow-lg ${
              isPhase2
                ? 'bg-cyan-500/20 border border-cyan-500/40 text-cyan-400 shadow-cyan-500/20'
                : 'bg-emerald-500/20 border border-emerald-500/40 text-emerald-400 shadow-emerald-500/20'
            }`}>
              <ShieldCheck className="w-8 h-8" />
            </div>

            <div className="space-y-1">
              <div className={`text-2xl font-black ${isPhase2 ? 'text-cyan-400' : 'text-emerald-400'}`}>
                ✅ YOU WERE RIGHT.
              </div>
              <div className="text-lg font-serif italic text-slate-300">
                Unfortunately...
              </div>
              <div className="text-2xl font-black text-rose-400">
                YOU WERE WRONG.
              </div>
            </div>

            <p className="text-xs text-slate-400 font-mono">
              {isPhase2 ? (
                <>You deduced the final recipient: <strong className="text-cyan-300 font-bold">{finalPersonName}</strong></>
              ) : (
                <>You identified the rumor starter: <strong className="text-amber-300 font-bold">{starterName}</strong></>
              )}
            </p>
          </div>
        ) : (
          /* Give Up Scenario */
          <div className="space-y-4">
            <div className="w-16 h-16 rounded-full bg-rose-500/20 border border-rose-500/40 text-rose-400 mx-auto flex items-center justify-center shadow-lg shadow-rose-500/20">
              <Flag className="w-8 h-8" />
            </div>

            <div className="space-y-1">
              <h3 className="text-xs font-bold text-rose-400 tracking-widest uppercase">
                TRUTH REVEALED
              </h3>
              <div className="text-xl font-extrabold text-slate-100">
                {commentary}
              </div>
            </div>
          </div>
        )}

        {/* Truth Details Card */}
        <div className="bg-slate-950/80 border border-slate-800 rounded-2xl p-4 text-left space-y-3 text-xs">
          <div>
            <span className="text-slate-500 font-bold uppercase block text-[10px]">RUMOR</span>
            <p className="text-slate-200 italic font-serif text-sm">&ldquo;{rumorText}&rdquo;</p>
          </div>

          <div className={`grid ${isPhase2 ? 'grid-cols-2' : 'grid-cols-2'} gap-2 pt-1 border-t border-slate-800/80`}>
            {isPhase2 ? (
              <>
                <div>
                  <span className="text-slate-500 font-bold uppercase block text-[10px]">STARTER</span>
                  <span className="text-amber-300 font-bold text-sm">{starterName}</span>
                </div>
                <div>
                  <span className="text-slate-500 font-bold uppercase block text-[10px]">FINAL RECIPIENT</span>
                  <span className="text-cyan-300 font-bold text-sm">{finalPersonName}</span>
                </div>
              </>
            ) : (
              <>
                <div>
                  <span className="text-slate-500 font-bold uppercase block text-[10px]">SUBJECT</span>
                  <span className="text-amber-300 font-bold text-sm">{subjectName}</span>
                </div>
                <div>
                  <span className="text-slate-500 font-bold uppercase block text-[10px]">STARTED BY</span>
                  <span className="text-rose-400 font-bold text-sm">{starterName}</span>
                </div>
              </>
            )}
          </div>

          {/* Phase 2: Chronological Temporal Propagation Timeline */}
          {isPhase2 && propagationEvents.length > 0 && (
            <div className="pt-2 border-t border-slate-800/80 space-y-1.5 text-left">
              <span className="text-slate-400 font-bold uppercase block text-[10px] flex items-center gap-1.5">
                <Clock className="w-3.5 h-3.5 text-cyan-400" /> TEMPORAL PROPAGATION TIMELINE
              </span>
              <div className="max-h-40 overflow-y-auto space-y-1.5 pr-1 font-mono text-[11px]">
                {propagationEvents.map((ev, i) => (
                  <div key={i} className="flex items-center justify-between p-2 rounded-lg bg-slate-900/90 border border-slate-800">
                    <div className="flex items-center gap-2">
                      <span className="text-[10px] px-1.5 py-0.5 rounded bg-cyan-950/90 text-cyan-300 font-bold border border-cyan-800/60 shrink-0">
                        {ev.time_str}
                      </span>
                      <span className="text-slate-300 text-xs truncate">
                        <strong className="text-slate-200">{ev.source_name}</strong>
                        <span className="text-slate-500 mx-1">→</span>
                        <strong className={i === propagationEvents.length - 1 ? 'text-cyan-300 font-bold' : 'text-slate-200'}>
                          {ev.target_name}
                        </strong>
                      </span>
                    </div>
                    <span className="text-[10px] text-slate-500 italic shrink-0">
                      {ev.relationship}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Phase 1: Relationship Path */}
          {!isPhase2 && path.length > 0 && (
            <div className="pt-2 border-t border-slate-800/80">
              <span className="text-slate-500 font-bold uppercase block text-[10px] mb-1 flex items-center gap-1">
                <GitCommit className="w-3 h-3 text-amber-400" /> TRANSMISSION PATH
              </span>
              <div className="flex items-center gap-1.5 flex-wrap font-mono text-[11px] text-slate-300">
                {path.map((name, i) => (
                  <React.Fragment key={i}>
                    <span className={`px-1.5 py-0.5 rounded ${i === 0 ? 'bg-rose-500/20 text-rose-300 font-bold' : i === path.length - 1 ? 'bg-amber-500/20 text-amber-300 font-bold' : 'bg-slate-800 text-slate-300'}`}>
                      {name}
                    </span>
                    {i < path.length - 1 && <span className="text-slate-600">→</span>}
                  </React.Fragment>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Score Card */}
        <div className="bg-slate-950/60 border border-slate-800 rounded-xl p-3 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Trophy className="w-5 h-5 text-amber-400" />
            <span className="text-xs font-bold text-slate-300">ROUND SCORE</span>
          </div>
          <span className="text-xl font-extrabold text-amber-400 font-mono">{score}</span>
        </div>

        {/* Next Rumor Button */}
        <button
          type="button"
          disabled={isLoading}
          onClick={onNextRumor}
          className={`w-full py-4 px-6 rounded-2xl font-black text-base tracking-wider uppercase hover:brightness-110 active:scale-[0.99] transition-all shadow-xl flex items-center justify-center gap-2 ${
            isPhase2
              ? 'bg-gradient-to-r from-cyan-500 via-blue-500 to-cyan-600 text-slate-950 shadow-cyan-500/20'
              : 'bg-gradient-to-r from-amber-500 via-orange-500 to-amber-600 text-slate-950 shadow-amber-500/20'
          }`}
        >
          {isLoading ? (
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 border-2 border-slate-950 border-t-transparent rounded-full animate-spin" />
              Generating Completely New Graph...
            </div>
          ) : (
            <>
              NEXT RUMOR <ArrowRight className="w-5 h-5" />
            </>
          )}
        </button>
      </div>
    </div>
  );
};
