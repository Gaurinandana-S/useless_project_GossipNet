'use client';

import React, { memo } from 'react';
import { Handle, Position } from '@xyflow/react';
import { User, Home, Sparkles, Network } from 'lucide-react';

interface PersonNodeData {
  name: string;
  age: number;
  gender: string;
  household_name?: string;
  generation: number;
  tree_level?: number;
  is_social?: boolean;
  isSubject?: boolean;
  isSelected?: boolean;
  isSearchMatch?: boolean;
}

const LEVEL_LABELS: { [key: number]: string } = {
  0: 'L0 Elders',
  1: 'L1 Adults',
  2: 'L2 Youth',
  3: 'L3 Kids',
};

export const PersonNode = memo(({ data }: { data: PersonNodeData }) => {
  const {
    name,
    age,
    gender,
    household_name,
    generation,
    tree_level = 0,
    is_social = false,
    isSubject,
    isSelected,
    isSearchMatch,
  } = data;

  const levelTag = is_social ? 'Social' : (LEVEL_LABELS[tree_level] || `L${tree_level}`);

  return (
    <div
      className={`px-4 py-3 rounded-2xl border backdrop-blur-md transition-all duration-300 cursor-pointer min-w-[180px] max-w-[210px] shadow-lg ${
        isSelected
          ? 'bg-amber-500/25 border-amber-400 ring-4 ring-amber-400/30 scale-105 shadow-amber-500/20'
          : isSubject
          ? 'bg-gradient-to-br from-rose-950/90 to-amber-950/90 border-rose-400 ring-2 ring-rose-400/40 shadow-rose-500/20'
          : isSearchMatch
          ? 'bg-cyan-950/80 border-cyan-400 ring-2 ring-cyan-400/50'
          : is_social
          ? 'bg-purple-950/70 border-purple-600/60 hover:border-purple-400 hover:bg-purple-900/60'
          : 'bg-slate-900/90 border-slate-700/80 hover:border-slate-500 hover:bg-slate-850'
      }`}
    >
      <Handle type="target" position={Position.Top} className="!bg-amber-400 !w-2.5 !h-2.5" />
      
      <div className="flex flex-col gap-1">
        {/* Top Badges */}
        <div className="flex items-center justify-between text-[10px] font-semibold text-slate-400 gap-1">
          <span
            className={`px-1.5 py-0.5 rounded border text-[10px] font-bold ${
              is_social
                ? 'bg-purple-900/60 border-purple-500/50 text-purple-300'
                : tree_level === 0
                ? 'bg-emerald-950/80 border-emerald-500/50 text-emerald-300'
                : tree_level === 1
                ? 'bg-sky-950/80 border-sky-500/50 text-sky-300'
                : tree_level === 2
                ? 'bg-indigo-950/80 border-indigo-500/50 text-indigo-300'
                : 'bg-amber-950/80 border-amber-500/50 text-amber-300'
            }`}
          >
            {levelTag}
          </span>
          <span className="flex items-center gap-1 text-slate-400 font-mono">
            <User className="w-3 h-3 text-slate-400" /> {gender} • {age}y
          </span>
        </div>

        {/* Person Name */}
        <div className="flex items-center gap-1.5 font-bold text-sm text-slate-100 mt-0.5">
          {isSubject && <Sparkles className="w-4 h-4 text-rose-400 shrink-0" />}
          {is_social && <Network className="w-3.5 h-3.5 text-purple-400 shrink-0" />}
          <span className="truncate">{name}</span>
        </div>

        {/* Household / Origin */}
        {household_name && (
          <div className="flex items-center gap-1 text-[11px] text-amber-300/80 font-medium truncate mt-0.5">
            <Home className="w-3 h-3 text-amber-400 shrink-0" />
            <span className="truncate">{household_name}</span>
          </div>
        )}

        {isSubject && (
          <div className="mt-1 text-[9px] font-extrabold uppercase tracking-wider text-rose-300 bg-rose-500/20 px-1.5 py-0.5 rounded text-center border border-rose-500/30">
            RUMOR SUBJECT
          </div>
        )}
      </div>

      <Handle type="source" position={Position.Bottom} className="!bg-amber-400 !w-2.5 !h-2.5" />
    </div>
  );
});

PersonNode.displayName = 'PersonNode';
