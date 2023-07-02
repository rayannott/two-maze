from pathlib import Path


def get_english_words() -> list[str]:
    with open(Path('utils')/Path('words.txt')) as f:
        words = [el.strip() for el in f.readlines()]
    return [w for w in words if len(w) > 6]

def split_word_into(word: str, n_parts: int) -> list[str]:
    if n_parts == 2:
        return [word[:4], word[4:]]
    if n_parts == 3:
        return [word[:3], word[3:5], word[5:]]
    if n_parts == 4:
        return [word[:2], word[2:4], word[4:6], word[6:]]
