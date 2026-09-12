export interface Person {
  id: string;
  name: string;
  age: number;
  gender: string;
  household_id?: string;
  household_name?: string;
  generation: number;
  tree_level: number;
  is_social?: boolean;
  gossip_reputation?: string;
  previous_rumor_count?: number;
  trustworthiness?: string;
  communication_frequency?: string;
  secret_keeping?: string;
}

export interface Household {
  id: string;
  name: string;
  address_location?: string;
}

export interface RelationshipEdge {
  id: string;
  source: string;
  target: string;
  relationship_type: string;
  is_newly_discovered?: boolean;
}

export interface Rumor {
  id: string;
  content: string;
  subject_id: string;
  subject_name: string;
  starter_id?: string | null;
  starter_name?: string | null;
  final_person_id?: string | null;
  final_person_name?: string | null;
}

export interface AvailableQuestion {
  key: string;
  text: string;
  description: string;
}

export interface AskedQuestion {
  person_id: string;
  person_name: string;
  question_key: string;
  question_category?: string;
  question_text?: string;
  answer_text: string;
  persona_dialogue?: string;
  system_commentary?: string;
}

export interface GuessLog {
  person_id: string;
  person_name: string;
  is_correct: boolean;
  commentary: string;
}

export interface StarterTruth {
  starter_id: string;
  starter_name: string;
  subject_id: string;
  subject_name: string;
  rumor_content: string;
}

export interface PropagationEvent {
  step: number;
  source_id: string;
  source_name: string;
  target_id: string;
  target_name: string;
  time_str: string;
  timestamp: string;
  relationship: string;
}

export interface FinalPersonTruth {
  final_person_id: string;
  final_person_name: string;
  starter_id: string;
  starter_name: string;
  rumor_content: string;
  propagation_tree: PropagationEvent[];
}

export interface GameState {
  game_id: string;
  seed: number;
  difficulty: number;
  player_type: string;
  game_mode: string;
  status: 'ACTIVE' | 'SOLVED' | 'GAVE_UP' | 'ROUND_COMPLETE';
  current_reveal_level?: number;
  max_tree_level?: number;
  guess_count?: number;
  give_up_available?: boolean;
  questions_remaining: number;
  guesses_remaining: number;
  score: number;
  total_people_count: number;
  visible_people_count: number;
  rumor: Rumor;
  visible_people: Person[];
  visible_edges: RelationshipEdge[];
  households: Household[];
  available_questions: AvailableQuestion[];
  asked_questions: AskedQuestion[];
  guesses_made: GuessLog[];
  starter_truth?: StarterTruth | null;
  final_person_truth?: FinalPersonTruth | null;
  propagation_tree?: PropagationEvent[];
}

export interface QuestionResponse {
  question_key: string;
  question_text: string;
  answer_text: string;
  persona_dialogue: string;
  system_commentary: string;
  newly_revealed_person_ids: string[];
  newly_revealed_edges: RelationshipEdge[];
  unlocked_level?: number | null;
  questions_remaining: number;
  game_status: string;
}

export interface GuessResponse {
  is_correct: boolean;
  commentary: string;
  guess_count?: number;
  give_up_available?: boolean;
  unlocked_level?: number | null;
  newly_revealed_person_ids?: string[];
  guesses_remaining: number;
  game_status: string;
  starter_id?: string | null;
  starter_name?: string | null;
  final_person_id?: string | null;
  final_person_name?: string | null;
  propagation_tree?: PropagationEvent[];
  final_score: number;
}

export interface GiveUpResponse {
  starter_id: string;
  starter_name: string;
  final_person_id?: string | null;
  final_person_name?: string | null;
  subject_id: string;
  subject_name: string;
  rumor_content: string;
  relationship_path: string[];
  propagation_tree?: PropagationEvent[];
  commentary: string;
  final_score: number;
  game_status: string;
}
