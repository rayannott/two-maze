from pathlib import Path


def get_english_words() -> list[str]:
    with open(Path('assets') / Path('words.txt')) as f:
        words = [el.strip() for el in f.readlines()]
    return [w for w in words if len(w) > 6]

def split_word_into(word: str, n_parts: int) -> list[str]:
    part_len = len(word) // n_parts
    tmp = [word[part_len*i: part_len*(i+1)] for i in range(n_parts)]
    if len(word) % n_parts == 0: return tmp
    tmp[-1] += word[-1]
    return tmp
