from typing import List, Optional, Dict, Any
from pydantic import BaseModel

class PersonSchema(BaseModel):
    id: str
    name: str
    age: int
    gender: str
    household_id: Optional[str] = None
    household_name: Optional[str] = None
    generation: int
    tree_level: Optional[int] = 0
    is_social: Optional[bool] = False
    gossip_reputation: Optional[str] = "MED"
    previous_rumor_count: Optional[int] = 0
    trustworthiness: Optional[str] = "MED"
    communication_frequency: Optional[str] = "MED"
    secret_keeping: Optional[str] = "MED"

class HouseholdSchema(BaseModel):
    id: str
    name: str
    address_location: Optional[str] = None

class EdgeSchema(BaseModel):
    id: str
    source: str
    target: str
    relationship_type: str
    is_newly_discovered: bool = False

class RumorSchema(BaseModel):
    id: str
    content: str
    subject_id: str
    subject_name: str
    starter_id: Optional[str] = None
    starter_name: Optional[str] = None
    final_person_id: Optional[str] = None  # SANITIZED UNLESS SOLVED / GAVE_UP
    final_person_name: Optional[str] = None

class PropagationEventSchema(BaseModel):
    step: int
    source_id: str
    source_name: str
    target_id: str
    target_name: str
    time_str: str
    timestamp: str
    relationship: str

class GameCreateRequest(BaseModel):
    difficulty: Optional[int] = 1
    random_seed: Optional[int] = None
    game_mode: Optional[str] = "GUESS_RUMOR_START"  # GUESS_RUMOR_START or GUESS_RUMOR_END

class QuestionRequest(BaseModel):
    person_id: str
    question_key: Optional[str] = None
    custom_text: Optional[str] = None
    target_person_id: Optional[str] = None

class QuestionResponse(BaseModel):
    question_key: Optional[str] = "general"
    question_text: Optional[str] = "Question"
    answer_text: str
    persona_dialogue: Optional[str] = ""
    system_commentary: Optional[str] = ""
    newly_revealed_person_ids: List[str] = []
    newly_revealed_edges: List[EdgeSchema] = []
    unlocked_level: Optional[int] = None
    questions_remaining: int
    game_status: str

class GuessRequest(BaseModel):
    person_id: str

class GuessResponse(BaseModel):
    is_correct: bool
    commentary: str
    guess_count: Optional[int] = 1
    give_up_available: Optional[bool] = True
    guesses_remaining: Optional[int] = 999
    unlocked_level: Optional[int] = None
    newly_revealed_person_ids: Optional[List[str]] = []
    game_status: str
    starter_id: Optional[str] = None
    starter_name: Optional[str] = None
    final_person_id: Optional[str] = None
    final_person_name: Optional[str] = None
    propagation_tree: Optional[List[Dict[str, Any]]] = None
    final_score: int

class GiveUpResponse(BaseModel):
    starter_id: str
    starter_name: str
    final_person_id: Optional[str] = None
    final_person_name: Optional[str] = None
    subject_id: str
    subject_name: str
    rumor_content: str
    relationship_path: List[str]
    propagation_tree: Optional[List[Dict[str, Any]]] = None
    commentary: str
    final_score: int
    game_status: str

class GameResponse(BaseModel):
    game_id: str
    seed: int
    difficulty: int
    player_type: str
    game_mode: str
    status: str
    current_reveal_level: Optional[int] = 0
    max_tree_level: Optional[int] = 3
    guess_count: Optional[int] = 0
    give_up_available: Optional[bool] = False
    questions_remaining: int
    guesses_remaining: int
    score: int
    total_people_count: int
    visible_people_count: int
    rumor: RumorSchema
    visible_people: List[PersonSchema]
    visible_edges: List[EdgeSchema]
    households: List[HouseholdSchema]
    available_questions: List[Dict[str, Any]]
    asked_questions: List[Dict[str, Any]]
    guesses_made: List[Dict[str, Any]]
    starter_truth: Optional[Dict[str, Any]] = None
    final_person_truth: Optional[Dict[str, Any]] = None
    propagation_tree: Optional[List[Dict[str, Any]]] = None
