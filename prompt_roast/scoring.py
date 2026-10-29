"""Cálculo determinístico; a interpretação do prompt pertence ao agente."""

TITLES = {
    0: ("🙏", "Hail Mary"), 1: ("🎰", "Slot Machine"),
    2: ("😶‍🌫️", "Foggy"), 3: ("🚶", "Wandering"),
    4: ("🤔", "Getting There"), 5: ("🧭", "On Track"),
    6: ("🎯", "Focused"), 7: ("🧠", "Sharp"),
    8: ("🦾", "Commander"), 9: ("💎", "Flawless"),
    10: ("🦸", "Tony Stark"),
}
CAPS = {"none": 10, "hail_mary": 2, "just_do_it": 1,
        "why_no_context": 1, "copy_paste_loop": 1}


def evaluate(prompt_type, p1, p2, p3, pattern="none", butler=False):
    if prompt_type not in ("request", "question"):
        raise ValueError("tipo deve ser request ou question")
    if any(type(value) is not int or not 0 <= value <= 3 for value in (p1, p2, p3)):
        raise ValueError("cada pilar deve ser um inteiro entre 0 e 3")
    if pattern not in CAPS:
        raise ValueError("antipadrão deve ser um de: " + ", ".join(CAPS))
    if type(butler) is not bool:
        raise ValueError("butler deve ser verdadeiro ou falso")
    base = 0 if butler else 1
    total = min(base + p1 + p2 + p3, CAPS[pattern])
    emoji, title = TITLES[total]
    names = ("origin", "destination", "boundary") if prompt_type == "request" else ("hypothesis", "scope", "context")
    scores = (p1, p2, p3)
    weakest = scores.index(min(scores))
    return {"score": total, "base": base, "pillar_scores": list(scores),
            "type": prompt_type, "butler_mode": butler, "pattern": pattern,
            "emoji": emoji, "title": title, "weakest": names[weakest]}
