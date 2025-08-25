
import random, re
def insert_zero_width(s, rate=0.12):
    out=[]; 
    for ch in s:
        out.append(ch)
        if ch.isalpha() and random.random()<rate: out.append("\u200b")
    return "".join(out)
def space_attack(s): return re.sub(r"(\w)", r"\1 ", s)
def json_wrap(s):
    import json as _j; return _j.dumps({"q":s,"fmt":"text"})
def yaml_wrap(s): return f"q: |\n  {s}\nfmt: text\n"
def xml_wrap(s): return f"<q fmt='text'>{s}</q>"
def code_wrap(s, lang="text"): return f"```{lang}\n{s}\n```"
def rand_case(s):
    out=[]; 
    for ch in s:
        out.append(ch.upper() if ch.isalpha() and random.random()<0.5 else ch)
    return "".join(out)
OPS=[insert_zero_width, space_attack, json_wrap, yaml_wrap, xml_wrap, code_wrap, rand_case]
def read_db_txt(path):
    cur=[]; out=[]
    for line in open(path,"r",encoding="utf-8"):
        if line.strip()=='---':
            t=" ".join(x.strip() for x in cur if x.strip())
            if t: out.append(t); cur=[]
        else: cur.append(line)
    t=" ".join(x.strip() for x in cur if x.strip())
    if t: out.append(t)
    return out
def sample_generate(db_txt, n=50, mutate_k=3):
    base=read_db_txt(db_txt)
    random.shuffle(base); out=[]
    for s in base[:n]:
        t=s
        ops=random.sample(OPS, k=min(mutate_k, len(OPS)))
        for op in ops:
            try: t=op(t)
            except TypeError: t=op(t, "text")
        out.append(t)
    return out
