'use client';

import React, { useState, useEffect, useMemo } from 'react';
import {
  ReactFlow,
  MiniMap,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  Node,
  Edge,
  MarkerType,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';

import { Person, RelationshipEdge } from '@/types/game';
import { PersonNode } from './PersonNode';
import { Search, Eye, Layers, ChevronDown } from 'lucide-react';

interface GraphViewerProps {
  visiblePeople: Person[];
  visibleEdges: RelationshipEdge[];
  totalPeopleCount: number;
  subjectId: string;
  selectedPersonId: string | null;
  onSelectPerson: (personId: string) => void;
  currentRevealLevel?: number;
  maxTreeLevel?: number;
}

const nodeTypes = {
  personNode: PersonNode,
};

const LEVEL_DESCRIPTIONS: { [key: number]: string } = {
  0: 'Level 0: Grandparents & Elders (Founding Generation)',
  1: 'Level 1: Parents, Aunts & Uncles (Core Households)',
  2: 'Level 2: Youth, Siblings & Cousins (Next Generation)',
  3: 'Level 3: Children & Grandchildren (Youngest Branch)',
};

export const GraphViewer: React.FC<GraphViewerProps> = ({
  visiblePeople,
  visibleEdges,
  totalPeopleCount,
  subjectId,
  selectedPersonId,
  onSelectPerson,
  currentRevealLevel = 0,
  maxTreeLevel = 3,
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [nodes, setNodes, onNodesChange] = useNodesState<Node>([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState<Edge>([]);

  // Downward progressive hierarchical tree layout calculation
  useEffect(() => {
    // Group people by explicit tree_level
    const levelGroups: { [lvl: number]: Person[] } = {};
    visiblePeople.forEach((p) => {
      const lvl = p.tree_level !== undefined ? p.tree_level : Math.max(0, p.generation - 1);
      if (!levelGroups[lvl]) levelGroups[lvl] = [];
      levelGroups[lvl].push(p);
    });

    const newNodes: Node[] = [];
    const levels = Object.keys(levelGroups).map(Number).sort((a, b) => a - b);

    // LEVEL_SPACING: Y = tree_level * 240px (Strict vertical progression downward)
    const LEVEL_SPACING_Y = 240;
    const NODE_SPACING_X = 230;

    levels.forEach((lvl) => {
      const allInLevel = levelGroups[lvl];
      const yPos = lvl * LEVEL_SPACING_Y;

      // Split into family members vs horizontal social contacts
      const familyMembers = allInLevel.filter((p) => !p.is_social);
      const socialMembers = allInLevel.filter((p) => !!p.is_social);

      // Group family members by household to keep couples & siblings adjacent
      const householdGroups: { [hh: string]: Person[] } = {};
      familyMembers.forEach((p) => {
        const hhKey = p.household_id || p.household_name || 'default';
        if (!householdGroups[hhKey]) householdGroups[hhKey] = [];
        householdGroups[hhKey].push(p);
      });

      // Calculate positions for family members
      const householdKeys = Object.keys(householdGroups);
      let currentX = 0;
      const familyNodePositions: { person: Person; x: number; y: number }[] = [];

      householdKeys.forEach((hhKey, hhIdx) => {
        const hhMembers = householdGroups[hhKey];
        hhMembers.forEach((p) => {
          familyNodePositions.push({
            person: p,
            x: currentX,
            y: yPos,
          });
          currentX += NODE_SPACING_X;
        });
        // Add padding between different households
        if (hhIdx < householdKeys.length - 1) {
          currentX += 50;
        }
      });

      // Center the family members around X = 0
      const totalFamilyWidth = currentX - (householdKeys.length > 0 ? 50 : 0);
      const startOffsetX = -(totalFamilyWidth / 2);

      familyNodePositions.forEach(({ person, x, y }) => {
        const isSearchMatch =
          searchTerm.trim().length > 0 &&
          person.name.toLowerCase().includes(searchTerm.toLowerCase());

        newNodes.push({
          id: person.id,
          type: 'personNode',
          position: { x: startOffsetX + x, y },
          data: {
            name: person.name,
            age: person.age,
            gender: person.gender,
            household_name: person.household_name,
            generation: person.generation,
            tree_level: person.tree_level ?? lvl,
            is_social: false,
            isSubject: person.id === subjectId,
            isSelected: person.id === selectedPersonId,
            isSearchMatch,
          },
        });
      });

      // Position social contacts horizontally on the outer lateral flank
      let socialStartX = startOffsetX + totalFamilyWidth + 60;
      socialMembers.forEach((socialPerson) => {
        const isSearchMatch =
          searchTerm.trim().length > 0 &&
          socialPerson.name.toLowerCase().includes(searchTerm.toLowerCase());

        newNodes.push({
          id: socialPerson.id,
          type: 'personNode',
          position: { x: socialStartX, y: yPos },
          data: {
            name: socialPerson.name,
            age: socialPerson.age,
            gender: socialPerson.gender,
            household_name: socialPerson.household_name || 'Social Contact',
            generation: socialPerson.generation,
            tree_level: socialPerson.tree_level ?? lvl,
            is_social: true,
            isSubject: socialPerson.id === subjectId,
            isSelected: socialPerson.id === selectedPersonId,
            isSearchMatch,
          },
        });
        socialStartX += NODE_SPACING_X;
      });
    });

    setNodes(newNodes);
  }, [visiblePeople, subjectId, selectedPersonId, searchTerm, setNodes]);

  // Transform edges for React Flow
  useEffect(() => {
    const newEdges: Edge[] = visibleEdges.map((e) => ({
      id: e.id,
      source: e.source,
      target: e.target,
      label: e.relationship_type,
      type: 'smoothstep',
      animated: !!e.is_newly_discovered,
      style: {
        stroke: e.is_newly_discovered ? '#f59e0b' : '#64748b',
        strokeWidth: e.is_newly_discovered ? 2.5 : 1.5,
      },
      labelStyle: {
        fill: e.is_newly_discovered ? '#fbbf24' : '#94a3b8',
        fontWeight: 600,
        fontSize: 11,
      },
      labelBgStyle: {
        fill: '#0f172a',
        fillOpacity: 0.95,
        rx: 4,
        ry: 4,
      },
      markerEnd: {
        type: MarkerType.ArrowClosed,
        color: e.is_newly_discovered ? '#f59e0b' : '#64748b',
        width: 14,
        height: 14,
      },
    }));

    setEdges(newEdges);
  }, [visibleEdges, setEdges]);

  // Calculate highest tree level currently visible
  const highestVisibleLevel = useMemo(() => {
    return Math.max(...visiblePeople.map((p) => p.tree_level ?? 0), 0);
  }, [visiblePeople]);

  return (
    <div className="relative w-full h-full bg-slate-950 rounded-2xl overflow-hidden border border-slate-800 shadow-inner flex flex-col">
      {/* Top Bar Overlay Controls */}
      <div className="absolute top-4 left-4 right-4 z-10 flex items-center justify-between pointer-events-none gap-2">
        {/* Left: Search Input */}
        <div className="relative pointer-events-auto max-w-xs w-full">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Search family member..."
            className="w-full pl-9 pr-4 py-2 bg-slate-900/90 backdrop-blur-md border border-slate-700/80 rounded-xl text-xs text-slate-100 placeholder-slate-400 focus:outline-none focus:border-amber-400 shadow-lg"
          />
        </div>

        {/* Center/Right: Level Depth Indicator & Visible People Counter */}
        <div className="pointer-events-auto flex items-center gap-2.5">
          <div className="flex items-center gap-1.5 bg-slate-900/90 backdrop-blur-md border border-slate-700 px-3 py-1.5 rounded-xl shadow-lg">
            <Layers className="w-4 h-4 text-sky-400" />
            <span className="text-xs font-bold text-slate-300">
              DEPTH: <span className="text-sky-400 font-mono">LEVEL {highestVisibleLevel}</span>
              <span className="text-slate-500 text-[10px] ml-1 font-mono">/ L{maxTreeLevel}</span>
            </span>
          </div>

          <div className="flex items-center gap-2 bg-slate-900/90 backdrop-blur-md border border-slate-700 px-3.5 py-1.5 rounded-xl shadow-lg">
            <Eye className="w-4 h-4 text-amber-400" />
            <span className="text-xs font-bold text-slate-300">
              VISIBLE: <span className="text-amber-400 font-mono">{visiblePeople.length}</span> /{' '}
              <span className="text-slate-400 font-mono">{totalPeopleCount}</span>
            </span>
          </div>
        </div>
      </div>

      {/* Level Depth Marker Rail (Bottom-Left Overlay) */}
      <div className="absolute bottom-4 left-4 z-10 pointer-events-none hidden md:flex flex-col gap-1.5 bg-slate-900/80 backdrop-blur-md border border-slate-800 p-2.5 rounded-xl shadow-lg">
        <div className="text-[10px] font-bold uppercase tracking-wider text-slate-400 flex items-center gap-1">
          <ChevronDown className="w-3 h-3 text-amber-400" /> Family Tree Hierarchy
        </div>
        {[0, 1, 2, 3].map((lvl) => {
          const isRevealed = lvl <= highestVisibleLevel;
          return (
            <div
              key={lvl}
              className={`flex items-center gap-2 text-[11px] px-2 py-0.5 rounded ${
                isRevealed
                  ? 'text-slate-200 font-medium bg-slate-800/80 border border-slate-700/60'
                  : 'text-slate-600 font-normal'
              }`}
            >
              <span
                className={`w-2 h-2 rounded-full ${
                  isRevealed ? 'bg-amber-400 shadow-sm shadow-amber-400/50' : 'bg-slate-700'
                }`}
              />
              <span>{LEVEL_DESCRIPTIONS[lvl]}</span>
              {!isRevealed && <span className="text-[9px] text-slate-600 italic">(Locked)</span>}
            </div>
          );
        })}
      </div>

      {/* Main React Flow Graph Canvas */}
      <div className="w-full h-full">
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          nodeTypes={nodeTypes}
          onNodeClick={(_, node) => onSelectPerson(node.id)}
          fitView
          fitViewOptions={{ padding: 0.2 }}
          minZoom={0.2}
          maxZoom={1.8}
        >
          <Background color="#334155" gap={24} size={1} />
          <Controls className="!bg-slate-900 !border-slate-700 !text-slate-200" />
          <MiniMap
            nodeColor={(n) => {
              if (n.data?.isSubject) return '#f43f5e';
              if (n.data?.isSelected) return '#f59e0b';
              if (n.data?.is_social) return '#a855f7';
              return '#475569';
            }}
            maskColor="rgba(15, 23, 42, 0.7)"
            className="!bg-slate-900 !border-slate-800"
          />
        </ReactFlow>
      </div>
    </div>
  );
};
