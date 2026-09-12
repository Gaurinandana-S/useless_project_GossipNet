'use client';

import React, { useState } from 'react';
import { GameState, Person, GiveUpResponse } from '@/types/game';
import { createGame, getGame, askQuestion, makeGuess, giveUp, nextGame } from '@/lib/api';

import { MainMenu } from '@/components/MainMenu/MainMenu';
import { GameHeader } from '@/components/GameHeader/GameHeader';
import { GraphViewer } from '@/components/GraphViewer/GraphViewer';
import { RumorCard } from '@/components/RumorCard/RumorCard';
import { ChatbotPanel } from '@/components/ChatbotPanel/ChatbotPanel';
import { GuessPanel } from '@/components/GuessPanel/GuessPanel';
import { GiveUpButton } from '@/components/GiveUpButton/GiveUpButton';
import { ResultModal } from '@/components/ResultModal/ResultModal';

export default function Home() {
  const [gameState, setGameState] = useState<GameState | null>(null);
  const [selectedPersonId, setSelectedPersonId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [giveUpData, setGiveUpData] = useState<GiveUpResponse | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // Handle Start New Game from Main Menu
  const handleStartGame = async (difficulty: number, gameMode: string = 'GUESS_RUMOR_START') => {
    setIsLoading(true);
    setErrorMsg(null);
    try {
      const state = await createGame(difficulty, undefined, gameMode);
      setGameState(state);
      setSelectedPersonId(state.visible_people[0]?.id || null);
      setGiveUpData(null);
    } catch (err: any) {
      setErrorMsg(err.message || 'Failed to start game. Make sure backend is running on http://localhost:8000');
    } finally {
      setIsLoading(false);
    }
  };

  // Handle Asking Question in Chat
  const handleAskQuestion = async (personId: string, questionKey?: string, customText?: string) => {
    if (!gameState) return;
    setIsLoading(true);
    setErrorMsg(null);
    try {
      const res = await askQuestion(gameState.game_id, personId, questionKey, customText);
      
      setGameState((prev) => {
        if (!prev) return null;
        return {
          ...prev,
          questions_remaining: res.questions_remaining,
          status: res.game_status as any,
          asked_questions: [
            ...prev.asked_questions,
            {
              person_id: personId,
              person_name: prev.visible_people.find((p) => p.id === personId)?.name || 'Person',
              question_key: res.question_key,
              question_text: res.question_text || customText || res.question_key,
              answer_text: res.answer_text,
              persona_dialogue: res.persona_dialogue,
              system_commentary: res.system_commentary,
            } as any,
          ],
        };
      });

      // Refetch updated game state for graph node expansion
      const updated = await fetchGameUpdatedState(gameState.game_id);
      if (updated) setGameState(updated);

    } catch (err: any) {
      setErrorMsg(err.message || 'Failed to evaluate question');
    } finally {
      setIsLoading(false);
    }
  };

  // Handle Submitting Guess
  const handleMakeGuess = async (personId: string) => {
    if (!gameState) return;
    setIsLoading(true);
    setErrorMsg(null);
    try {
      const res = await makeGuess(gameState.game_id, personId);
      
      if (res.is_correct) {
        setGameState((prev) => {
          if (!prev) return null;
          return {
            ...prev,
            status: res.game_status as any,
            score: res.final_score,
            guess_count: res.guess_count || ((prev.guess_count || 0) + 1),
            give_up_available: true,
            guesses_made: [
              ...prev.guesses_made,
              {
                person_id: personId,
                person_name: prev.visible_people.find((p) => p.id === personId)?.name || 'Person',
                is_correct: true,
                commentary: res.commentary,
              },
            ],
            starter_truth: res.starter_id
              ? {
                  starter_id: res.starter_id,
                  starter_name: res.starter_name || '',
                  subject_id: prev.rumor.subject_id,
                  subject_name: prev.rumor.subject_name,
                  rumor_content: prev.rumor.content,
                }
              : prev.starter_truth,
            final_person_truth: res.final_person_id
              ? {
                  final_person_id: res.final_person_id,
                  final_person_name: res.final_person_name || '',
                  starter_id: res.starter_id || prev.rumor.starter_id || '',
                  starter_name: res.starter_name || prev.rumor.starter_name || '',
                  rumor_content: prev.rumor.content,
                  propagation_tree: res.propagation_tree || [],
                }
              : prev.final_person_truth,
            propagation_tree: res.propagation_tree || prev.propagation_tree,
          };
        });
      } else {
        // Wrong guess: fetch updated state for downward tree expansion
        const updated = await fetchGameUpdatedState(gameState.game_id);
        if (updated) {
          setGameState(updated);
        } else {
          setGameState((prev) => {
            if (!prev) return null;
            return {
              ...prev,
              score: res.final_score,
              guess_count: res.guess_count || ((prev.guess_count || 0) + 1),
              give_up_available: true,
              guesses_made: [
                ...prev.guesses_made,
                {
                  person_id: personId,
                  person_name: prev.visible_people.find((p) => p.id === personId)?.name || 'Person',
                  is_correct: false,
                  commentary: res.commentary,
                },
              ],
            };
          });
        }
      }
    } catch (err: any) {
      setErrorMsg(err.message || 'Failed to submit guess');
    } finally {
      setIsLoading(false);
    }
  };

  // Handle Give Up
  const handleGiveUp = async () => {
    if (!gameState) return;
    setIsLoading(true);
    setErrorMsg(null);
    try {
      const res = await giveUp(gameState.game_id);
      setGiveUpData(res);
      setGameState((prev) => {
        if (!prev) return null;
        return {
          ...prev,
          status: 'GAVE_UP',
          score: res.final_score,
          propagation_tree: res.propagation_tree || prev.propagation_tree,
          final_person_truth: res.final_person_id
            ? {
                final_person_id: res.final_person_id,
                final_person_name: res.final_person_name || '',
                starter_id: res.starter_id,
                starter_name: res.starter_name,
                rumor_content: res.rumor_content,
                propagation_tree: res.propagation_tree || [],
              }
            : prev.final_person_truth,
        };
      });
    } catch (err: any) {
      setErrorMsg(err.message || 'Failed to give up');
    } finally {
      setIsLoading(false);
    }
  };

  // Handle Next Rumor (Fresh Graph per Round)
  const handleNextRumor = async () => {
    if (!gameState) return;
    setIsLoading(true);
    setErrorMsg(null);
    try {
      const nextState = await nextGame(gameState.game_id);
      setGameState(nextState);
      setSelectedPersonId(nextState.visible_people[0]?.id || null);
      setGiveUpData(null);
    } catch (err: any) {
      setErrorMsg(err.message || 'Failed to load next rumor round');
    } finally {
      setIsLoading(false);
    }
  };

  const fetchGameUpdatedState = async (gameId: string) => {
    try {
      return await getGame(gameId);
    } catch (e) {
      console.error(e);
    }
    return null;
  };

  if (!gameState) {
    return (
      <>
        {errorMsg && (
          <div className="fixed top-4 left-1/2 -translate-x-1/2 z-50 bg-rose-950 border border-rose-500 text-rose-200 px-4 py-2 rounded-xl text-xs shadow-xl">
            {errorMsg}
          </div>
        )}
        <MainMenu onStartGame={handleStartGame} isLoading={isLoading} />
      </>
    );
  }

  const selectedPerson =
    gameState.visible_people.find((p) => p.id === selectedPersonId) || null;

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans overflow-hidden">
      {/* Header */}
      <GameHeader
        round={gameState.difficulty}
        score={gameState.score}
        questionsLeft={gameState.questions_remaining}
        guessesLeft={gameState.guesses_remaining}
        guessCount={gameState.guess_count || gameState.guesses_made.length}
        gameMode={gameState.game_mode}
        onResetToMenu={() => setGameState(null)}
      />

      {errorMsg && (
        <div className="bg-rose-950/80 border-b border-rose-500/60 px-4 py-2 text-center text-xs text-rose-200 font-medium">
          {errorMsg}
        </div>
      )}

      {/* Main Game Interface Layout */}
      <main className="flex-1 p-4 grid grid-cols-1 lg:grid-cols-12 gap-4 h-[calc(100vh-65px)] overflow-hidden relative">
        
        {/* Left Column: Rumor Card & React Flow Graph (7 Cols) */}
        <div className="lg:col-span-7 flex flex-col gap-3 h-full overflow-hidden">
          <RumorCard rumor={gameState.rumor} />
          
          <div className="flex-1 h-full min-h-[400px]">
            <GraphViewer
              visiblePeople={gameState.visible_people}
              visibleEdges={gameState.visible_edges}
              totalPeopleCount={gameState.total_people_count}
              subjectId={gameState.rumor.subject_id}
              selectedPersonId={selectedPersonId}
              onSelectPerson={(id) => setSelectedPersonId(id)}
              currentRevealLevel={gameState.current_reveal_level}
              maxTreeLevel={gameState.max_tree_level}
            />
          </div>
        </div>

        {/* Right Column: Chatbot Interrogation & Guess Panels (5 Cols) */}
        <div className="lg:col-span-5 flex flex-col gap-3 h-full overflow-y-auto pr-1">
          <div className="flex-1 min-h-[420px]">
            <ChatbotPanel
              selectedPerson={selectedPerson}
              questionsLeft={gameState.questions_remaining}
              availableQuestions={gameState.available_questions}
              askedQuestions={gameState.asked_questions}
              onAskQuestion={handleAskQuestion}
              isLoading={isLoading}
            />
          </div>

          <div className="space-y-3 shrink-0">
            <GuessPanel
              selectedPerson={selectedPerson}
              guessCount={gameState.guess_count || gameState.guesses_made.length}
              guessesLeft={gameState.guesses_remaining}
              guessesMade={gameState.guesses_made}
              gameMode={gameState.game_mode}
              onMakeGuess={handleMakeGuess}
              isLoading={isLoading}
            />
          </div>
        </div>

        {/* Persistent Floating Give Up Button (available after guess 1) */}
        <GiveUpButton
          available={!!gameState.give_up_available || (gameState.guess_count !== undefined && gameState.guess_count > 0) || gameState.guesses_made.length > 0}
          guessCount={gameState.guess_count || gameState.guesses_made.length}
          onGiveUp={handleGiveUp}
          isLoading={isLoading}
        />
      </main>

      {/* Result / Truth Reveal Modal */}
      <ResultModal
        status={
          gameState.status === 'SOLVED' || gameState.status === 'GAVE_UP'
            ? gameState.status
            : null
        }
        score={gameState.score}
        gameMode={gameState.game_mode}
        starterTruth={gameState.starter_truth}
        finalPersonTruth={gameState.final_person_truth}
        giveUpData={giveUpData}
        onNextRumor={handleNextRumor}
        isLoading={isLoading}
      />
    </div>
  );
}
