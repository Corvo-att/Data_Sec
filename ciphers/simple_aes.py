def letter_to_num(ch: str) -> int:
    """Convert A-Z to 1-26 (matches the lecture's CAT/MKX walkthrough)."""
    return ord(ch) - ord('A') + 1


def num_to_letter(num: int) -> str:
    """Wrap any integer back into 1-26 and convert to A-Z."""
    wrapped = ((num - 1) % 26) + 1
    return chr(wrapped + ord('A') - 1)


def parse_round_keys(key_input: str) -> tuple[str, str]:
    """
    Accepts two keys separated by a comma or space (e.g. 'KEY, DOG').
    Defaults to ('KEY', 'DOG') if left blank.
    """
    parts = [
        ''.join(c for c in part.upper() if 'A' <= c <= 'Z')
        for part in key_input.replace(',', ' ').split()
    ]
    parts = [p for p in parts if p]
    if len(parts) >= 2:
        return parts[0], parts[1]
    if len(parts) == 1:
        return parts[0], parts[0]
    return 'KEY', 'DOG'


# --- The 4 Lecture Steps ---

def add_round_key(text: str, key: str, inverse: bool = False) -> str:
    """Step 1 & 4: Add key letters (encrypt) or subtract key letters (decrypt)."""
    out = []
    for i, ch in enumerate(text):
        if 'A' <= ch <= 'Z':
            k_val = letter_to_num(key[i % len(key)])
            t_val = letter_to_num(ch)
            new_val = (t_val - k_val) if inverse else (t_val + k_val)
            out.append(num_to_letter(new_val))
        else:
            out.append(ch)
    return ''.join(out)


def sub_bytes(text: str, inverse: bool = False) -> str:
    """Step 2 (S-Box): Shift every letter +3 (encrypt) or -3 (decrypt)."""
    shift = -3 if inverse else 3
    out = []
    for ch in text:
        if 'A' <= ch <= 'Z':
            out.append(num_to_letter(letter_to_num(ch) + shift))
        else:
            out.append(ch)
    return ''.join(out)


def shift_rows(text: str, inverse: bool = False) -> str:
    """Step 3 (Permutation): Shift left by 1 (encrypt) or right by 1 (decrypt)."""
    if len(text) <= 1:
        return text
    return (text[-1] + text[:-1]) if inverse else (text[1:] + text[0])


# --- Public Functions Called by main.py ---

def encrypt(text: str, key: str = 'KEY, DOG') -> str:
    key1, key2 = parse_round_keys(key)
    state = text.upper()
    state = add_round_key(state, key1, inverse=False)  # Step 1: AddRoundKey 1
    state = sub_bytes(state, inverse=False)            # Step 2: SubBytes (+3)
    state = shift_rows(state, inverse=False)           # Step 3: ShiftRows (Left)
    state = add_round_key(state, key2, inverse=False)  # Step 4: AddRoundKey 2
    return state


def decrypt(text: str, key: str = 'KEY, DOG') -> str:
    key1, key2 = parse_round_keys(key)
    state = text.upper()
    state = add_round_key(state, key2, inverse=True)   # Step 1: InvAddRoundKey 2
    state = shift_rows(state, inverse=True)            # Step 2: InvShiftRows (Right)
    state = sub_bytes(state, inverse=True)             # Step 3: InvSubBytes (-3)
    state = add_round_key(state, key1, inverse=True)   # Step 4: InvAddRoundKey 1
    return state


