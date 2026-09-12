import random

RUMOR_TEMPLATES = [
    "{subject_name} came home at 11 PM carrying a suspicious parcel.",
    "{subject_name} bought a brand new luxury phone without telling anyone.",
    "{subject_name} was seen talking secretly to a stranger near the railway station.",
    "{subject_name} suddenly stopped attending family Sunday dinners.",
    "{subject_name} ordered something very expensive online.",
    "{subject_name} is secretly planning a surprise trip to Dubai.",
    "{subject_name} was spotted eating hot parotta at midnight at the local junction.",
    "{subject_name} was overhead whispering about a secret gold deal.",
    "{subject_name} is secretly learning a new language for a mysterious job.",
    "{subject_name} was seen hiding a large paper envelope behind the almirah."
]

def generate_rumor(subject_name: str, seed: int = None) -> str:
    """Generates a harmless fictional rumor for the given subject name."""
    rng = random.Random(seed) if seed is not None else random.Random()
    template = rng.choice(RUMOR_TEMPLATES)
    return template.format(subject_name=subject_name)
