
import math
def reduce_string(s, test_fn, min_len=16):
    if len(s)<=min_len: return s
    n=2
    while len(s)>min_len:
        chunk=math.ceil(len(s)/n); removed=False; i=0
        while i<len(s):
            cand=s[:i]+s[i+chunk:]
            if len(cand)<min_len: i+=chunk; continue
            if test_fn(cand): s=cand; removed=True
            else: i+=chunk
        if not removed:
            if n>=len(s): break
            n*=2
    return s
