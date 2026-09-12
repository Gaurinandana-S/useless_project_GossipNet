'use client';

import React from 'react';
import { MessageSquare, Sparkles } from 'lucide-react';
import { Rumor } from '@/types/game';

interface RumorCardProps {
  rumor: Rumor;
}

export const RumorCard: React.FC<RumorCardProps> = ({ rumor }) => {
  return (
    <div className="bg-gradient-to-r from-slate-900 via-amber-950/30 to-slate-900 border border-amber-500/30 rounded-2xl p-4 shadow-xl backdrop-blur-md relative overflow-hidden flex items-start gap-4">
      <div className="p-3 rounded-xl bg-amber-500/15 border border-amber-500/40 text-amber-400 shrink-0">
        <MessageSquare className="w-5 h-5" />
      </div>

      <div className="flex-1 space-y-1">
        <div className="flex items-center justify-between text-xs text-amber-400 font-bold uppercase tracking-wider">
          <span className="flex items-center gap-1">
            <Sparkles className="w-3.5 h-3.5" /> CURRENT RUMOR UNDER INVESTIGATION
          </span>
          <span className="text-slate-400 font-normal">
            SUBJECT: <strong className="text-amber-300 font-semibold">{rumor.subject_name}</strong>
          </span>
        </div>

        <p className="text-slate-100 font-serif text-lg italic leading-snug">
          &ldquo;{rumor.content}&rdquo;
        </p>
      </div>
    </div>
  );
};
