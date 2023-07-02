from pathlib import Path


def get_english_words() -> list[str]:
    with open(Path('utils')/Path('words.txt')) as f:
        words = [el.strip() for el in f.readlines()]
    return [w for w in words if len(w) > 6]

def split_word_into(word: str, n_parts: int) -> list[str]:
    part_len = len(word) // n_parts
    if n_parts == 2:
        return [word[:part_len], word[part_len:]]
    if n_parts == 3:
        return [word[:part_len], word[part_len:2*part_len], word[2*part_len:]]
    if n_parts == 4:
        return [word[:part_len], word[part_len:2*part_len], word[2*part_len:3*part_len], word[4*part_len:]]
