"""Read and write the transit-encoded templateData in a Retool workflow
export. encode() writes without transit's string cache, which Retool reads.
"""
import json


def decode(text):
    cache = []
    def idx(s):
        return ord(s[1]) - 48 if len(s) == 2 else (ord(s[1]) - 48) * 44 + (ord(s[2]) - 48)
    def push(v):
        nonlocal cache
        if len(cache) >= 1936:
            cache = []
        cache.append(v)
    def dstr(s):
        if s.startswith("~:") or s.startswith("~$"):
            return s[2:]
        if s.startswith("~~") or s.startswith("~^"):
            return s[1:]
        return s
    def p(n, as_key=False):
        if isinstance(n, str):
            if len(n) > 1 and n[0] == "^" and n != "^ ":
                return cache[idx(n)]
            v = {"__tag": n[2:]} if n.startswith("~#") else dstr(n)
            if len(n) > 3 and (as_key or n.startswith("~#") or n.startswith("~:") or n.startswith("~$")):
                push(v)
            return v
        if isinstance(n, list):
            if n and n[0] == "^ ":
                o = {}
                for i in range(1, len(n), 2):
                    k = p(n[i], True)
                    o[k if isinstance(k, str) else json.dumps(k)] = p(n[i + 1])
                return o
            if len(n) == 2 and isinstance(n[0], str) and (n[0].startswith("~#") or (n[0][:1] == "^" and n[0] != "^ ")):
                t = p(n[0])
                v = p(n[1])
                return {"__tag": t["__tag"], "v": v} if isinstance(t, dict) and "__tag" in t else [t, v]
            return [p(x) for x in n]
        return n
    return p(json.loads(text))

def encode(value):
    """Write transit JSON without the cache, which readers accept."""
    def esc(s):
        return "~" + s if s[:1] in ("~", "^") and s != "^ " else s
    def w(v):
        if isinstance(v, dict):
            if "__tag" in v and set(v) <= {"__tag", "v"}:
                return ["~#" + v["__tag"], w(v.get("v"))]
            out = ["^ "]
            for k, x in v.items():
                out += [esc(k), w(x)]
            return out
        if isinstance(v, list):
            return [w(x) for x in v]
        if isinstance(v, str):
            return esc(v)
        return v
    return json.dumps(w(value), separators=(",", ":"))
