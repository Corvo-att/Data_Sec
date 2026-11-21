def encrypt(text: str, keyword: str) -> str:
 
    if not text or not keyword:
        return text

    key = keyword.upper()
    num_cols = len(key)

    col_order = sorted(range(num_cols), key=lambda i: (key[i], i))

    cols = [[] for _ in range(num_cols)]
    for i, char in enumerate(text):
        cols[i % num_cols].append(char)

    result = []
    for c in col_order:
        result.extend(cols[c])

    return ''.join(result)


def decrypt(text: str, keyword: str) -> str:
    
    if not text or not keyword:
        return text

    key = keyword.upper()
    num_cols = len(key)
    total_len = len(text)

    
    col_order = sorted(range(num_cols), key=lambda i: (key[i], i))

    rem = total_len % num_cols
    col_lengths = [
        (total_len // num_cols) + (1 if c < rem else 0)
        for c in range(num_cols)
    ]

    
    cols = [[] for _ in range(num_cols)]
    idx = 0
    for c in col_order:
        length = col_lengths[c]
        cols[c] = list(text[idx : idx + length])
        idx += length


    result = []
    num_rows = (total_len + num_cols - 1) // num_cols
    for r in range(num_rows):
        for c in range(num_cols):
            if r < len(cols[c]):
                result.append(cols[c][r])

    return ''.join(result)
