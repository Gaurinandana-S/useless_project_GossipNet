from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.game import Game
from app.schemas.game_schema import (
    GameCreateRequest, GameResponse, QuestionRequest, QuestionResponse,
    GuessRequest, GuessResponse, GiveUpResponse
)
from app.services.game_service import (
    create_game_session, serialize_game_state, process_question,
    process_guess, process_give_up, process_next_game
)

router = APIRouter()

@router.post("/game/create", response_model=GameResponse, status_code=status.HTTP_201_CREATED)
def create_game_endpoint(req: GameCreateRequest = GameCreateRequest(), db: Session = Depends(get_db)):
    """Creates a new procedurally generated GossipNet game."""
    try:
        game = create_game_session(
            db=db,
            difficulty=req.difficulty or 1,
            random_seed=req.random_seed,
            game_mode=req.game_mode or "GUESS_RUMOR_START"
        )
        return serialize_game_state(game, db)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/game/{game_id}", response_model=GameResponse)
def get_game_endpoint(game_id: str, db: Session = Depends(get_db)):
    """Retrieves the active state of a game."""
    game = db.get(Game, game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    return serialize_game_state(game, db)


@router.post("/game/{game_id}/question", response_model=QuestionResponse)
def ask_question_endpoint(game_id: str, req: QuestionRequest, db: Session = Depends(get_db)):
    """Asks an investigation question about a revealed node."""
    try:
        res = process_question(
            db=db,
            game_id=game_id,
            person_id=req.person_id,
            question_key=req.question_key,
            custom_text=req.custom_text
        )
        return res
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/game/{game_id}/guess", response_model=GuessResponse)
def make_guess_endpoint(game_id: str, req: GuessRequest, db: Session = Depends(get_db)):
    """Evaluates a rumor starter guess."""
    try:
        res = process_guess(
            db=db,
            game_id=game_id,
            person_id=req.person_id
        )
        return res
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/game/{game_id}/give-up", response_model=GiveUpResponse)
def give_up_endpoint(game_id: str, db: Session = Depends(get_db)):
    """Gives up when 0 guesses remain and reveals the truth."""
    try:
        res = process_give_up(db=db, game_id=game_id)
        return res
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/game/{game_id}/next", response_model=GameResponse)
def next_game_endpoint(game_id: str, db: Session = Depends(get_db)):
    """Generates a completely new round with a brand new graph."""
    try:
        new_game = process_next_game(db=db, current_game_id=game_id)
        return serialize_game_state(new_game, db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate next game: {str(e)}")
