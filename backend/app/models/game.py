import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, DateTime, Text, JSON
from sqlalchemy.orm import relationship
from app.database import Base

def generate_uuid():
    return str(uuid.uuid4())

class Game(Base):
    __tablename__ = "games"

    id = Column(String, primary_key=True, default=generate_uuid)
    seed = Column(Integer, nullable=False)
    difficulty = Column(Integer, default=1)
    player_type = Column(String, default="DETECTIVE")
    game_mode = Column(String, default="GUESS_RUMOR_START")
    status = Column(String, default="ACTIVE")  # ACTIVE, SOLVED, GAVE_UP, ROUND_COMPLETE
    
    current_reveal_level = Column(Integer, default=0)  # Progressive vertical level expansion
    guess_count = Column(Integer, default=0)
    give_up_available = Column(Boolean, default=False)
    questions_remaining = Column(Integer, default=10)
    guesses_remaining = Column(Integer, default=5)
    score = Column(Integer, default=1000)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # JSON stored fields for active in-memory / fast graph queries
    visible_nodes = Column(JSON, default=list)  # list of person_ids
    visible_edges = Column(JSON, default=list)  # list of edge dicts: {source, target, label}
    asked_questions = Column(JSON, default=list)  # list of dicts {person_id, question_key, answer}
    guesses_made = Column(JSON, default=list)  # list of dicts {person_id, is_correct, commentary}
    propagation_log = Column(JSON, default=list)  # list of transmission events (Phase 2)

    people = relationship("Person", back_populates="game", cascade="all, delete-orphan", foreign_keys="[Person.game_id]")
    households = relationship("Household", back_populates="game", cascade="all, delete-orphan")
    relationships = relationship("Relationship", back_populates="game", cascade="all, delete-orphan")
    rumor = relationship("Rumor", uselist=False, back_populates="game", cascade="all, delete-orphan")
    events = relationship("GameEvent", back_populates="game", cascade="all, delete-orphan")


class Household(Base):
    __tablename__ = "households"

    id = Column(String, primary_key=True, default=generate_uuid)
    game_id = Column(String, ForeignKey("games.id"), nullable=False)
    name = Column(String, nullable=False)
    address_location = Column(String, nullable=True)

    game = relationship("Game", back_populates="households")
    people = relationship("Person", back_populates="household")


class Person(Base):
    __tablename__ = "people"

    id = Column(String, primary_key=True, default=generate_uuid)
    game_id = Column(String, ForeignKey("games.id"), nullable=False)
    household_id = Column(String, ForeignKey("households.id"), nullable=True)
    name = Column(String, nullable=False)
    age = Column(Integer, nullable=False)
    gender = Column(String, nullable=False)  # M / F
    generation = Column(Integer, nullable=False)  # 1 to 5
    tree_level = Column(Integer, default=0)  # Explicit downward family tree level (0, 1, 2, 3...)
    is_social = Column(Boolean, default=False)  # True if friend/colleague/neighbor side contact
    gossip_reputation = Column(String, default="MED")
    previous_rumor_count = Column(Integer, default=0)
    trustworthiness = Column(String, default="MED")
    communication_frequency = Column(String, default="MED")
    secret_keeping = Column(String, default="MED")

    game = relationship("Game", back_populates="people", foreign_keys=[game_id])
    household = relationship("Household", back_populates="people")


class Relationship(Base):
    __tablename__ = "relationships"

    id = Column(String, primary_key=True, default=generate_uuid)
    game_id = Column(String, ForeignKey("games.id"), nullable=False)
    person_a_id = Column(String, ForeignKey("people.id"), nullable=False)
    person_b_id = Column(String, ForeignKey("people.id"), nullable=False)
    primitive_type = Column(String, nullable=False)  # parent, child, spouse, sibling, neighbor, friend, colleague

    game = relationship("Game", back_populates="relationships")


class Rumor(Base):
    __tablename__ = "rumors"

    id = Column(String, primary_key=True, default=generate_uuid)
    game_id = Column(String, ForeignKey("games.id"), nullable=False)
    content = Column(Text, nullable=False)
    subject_id = Column(String, ForeignKey("people.id"), nullable=False)
    starter_id = Column(String, ForeignKey("people.id"), nullable=False)
    final_person_id = Column(String, ForeignKey("people.id"), nullable=True)  # Phase 2 Rumor End target

    game = relationship("Game", back_populates="rumor")


class GameEvent(Base):
    __tablename__ = "game_events"

    id = Column(String, primary_key=True, default=generate_uuid)
    game_id = Column(String, ForeignKey("games.id"), nullable=False)
    event_type = Column(String, nullable=False)
    details = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    game = relationship("Game", back_populates="events")
