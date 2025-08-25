
import re, json
from collections import Counter
def char_classes(s):
    return {"ascii": sum(1 for ch in s if ord(ch)<128),
            "non_ascii": sum(1 for ch in s if ord(ch)>=128),
            "digit": sum(1 for ch in s if ch.isdigit()),
            "space": sum(1 for ch in s if ch.isspace()),
            "zero_width": s.count("\u200b")}
def summarize(samples, seeds):
    totals=Counter(); dists=[]
    for i,s in enumerate(samples):
        for k,v in char_classes(s).items(): totals[k]+=v
    return {"char_totals": dict(totals)}
