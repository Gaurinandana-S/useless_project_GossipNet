def calculate_score(
    questions_asked: int,
    wrong_guesses: int,
    is_solved: bool,
    gave_up: bool,
    guesses_remaining: int,
    difficulty: int = 1
) -> int:
    """Calculates final or active game score based on rules."""
    base_score = 1000
    
    question_penalty = questions_asked * 25
    guess_penalty = wrong_guesses * 100
    
    score = base_score - question_penalty - guess_penalty
    
    if is_solved:
        early_bonus = max(100, 600 - wrong_guesses * 100)
        score += early_bonus
    elif gave_up:
        score -= 300

    difficulty_multiplier = 1.0 + max(0, difficulty - 1) * 0.25
    final_score = int(score * difficulty_multiplier)
    
    return max(0, final_score)
