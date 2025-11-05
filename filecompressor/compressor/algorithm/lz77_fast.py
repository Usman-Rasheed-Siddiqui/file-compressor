
# lz77_fast.py
from collections import deque, defaultdict

class LZ77Fast:
    WINDOW_SIZE = 4096
    LOOKAHEAD_SIZE = 258
    MIN_MATCH = 3
    HASH_SIZE = 3
    MAX_CANDIDATES = 32
    MATCH_FLAG = 255
    ESCAPE_FLAG = 254

    def __init__(self):
        pass

    def _hash3(self, a, b, c):
        return (a << 16) | (b << 8) | c

    def lz77_encode(self, data: bytes):
        if not data:
            return []
        d = memoryview(data)
        n = len(d)
        pos = 0
        table = defaultdict(lambda: deque(maxlen=16))
        tokens = []

        while pos < n:
            if pos + self.HASH_SIZE > n:
                tokens.append(('literal', int(d[pos])))
                pos += 1
                continue

            h = self._hash3(d[pos], d[pos+1], d[pos+2])
            candidates = table[h]
            best_len = 0
            best_dist = 0
            checked = 0

            # search recent candidates (newest first)
            for cand_pos in reversed(candidates):
                if checked >= self.MAX_CANDIDATES:
                    break
                checked += 1
                dist = pos - cand_pos
                if dist <= 0 or dist > self.WINDOW_SIZE:
                    continue

                # quick reject by checking end-of-current best
                max_len = min(self.LOOKAHEAD_SIZE, n - pos)
                match_len = 0
                # tight loop compare
                while match_len < max_len and d[cand_pos + match_len] == d[pos + match_len]:
                    match_len += 1

                if match_len > best_len:
                    best_len = match_len
                    best_dist = dist
                    if best_len >= 64:  # heuristic early-exit
                        break

            if best_len >= self.MIN_MATCH:
                tokens.append(('match', best_dist, best_len))
                # update table for positions we skip
                for k in range(best_len):
                    if pos + k + self.HASH_SIZE <= n:
                        hh = self._hash3(d[pos + k], d[pos + k + 1], d[pos + k + 2])
                        table[hh].append(pos + k)
                pos += best_len
            else:
                tokens.append(('literal', int(d[pos])))
                table[h].append(pos)
                pos += 1

        return tokens

    def lz77_decode(self, tokens):
        out = bytearray()
        for t in tokens:
            if t[0] == 'literal':
                out.append(t[1])
            else:
                _, dist, length = t
                start = len(out) - dist
                for i in range(length):
                    out.append(out[start + (i % dist)])
        return bytes(out)

    @staticmethod
    def tokens_to_bytes(tokens):
        out = bytearray()
        for t in tokens:
            if t[0] == 'literal':
                b = t[1]
                if b in (LZ77Fast.MATCH_FLAG, LZ77Fast.ESCAPE_FLAG):
                    out.append(LZ77Fast.ESCAPE_FLAG)
                out.append(b)
            else:
                _, dist, length = t
                out.append(LZ77Fast.MATCH_FLAG)
                out.extend(dist.to_bytes(2, 'little'))
                out.extend(length.to_bytes(2, 'little'))
        return bytes(out)

    @staticmethod
    def bytes_to_tokens(data: bytes):
        out = []
        i = 0
        n = len(data)
        while i < n:
            b = data[i]
            if b == LZ77Fast.MATCH_FLAG:
                if i + 4 >= n:
                    raise ValueError("Incomplete match token")
                dist = int.from_bytes(data[i+1:i+3], 'little')
                length = int.from_bytes(data[i+3:i+5], 'little')
                out.append(('match', dist, length))
                i += 5
            elif b == LZ77Fast.ESCAPE_FLAG:
                if i + 1 >= n:
                    raise ValueError("Incomplete escape")
                out.append(('literal', data[i+1]))
                i += 2
            else:
                out.append(('literal', b))
                i += 1
        return out
