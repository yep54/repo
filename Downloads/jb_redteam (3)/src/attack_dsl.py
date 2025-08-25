
import yaml, random, re, json
def zero_width(s, rate=0.12):
    out=[]; 
    for ch in s:
        out.append(ch)
        if ch.isalpha() and random.random()<rate: out.append("\u200b")
    return "".join(out)
def spacing(s): 
    import re; return re.sub(r"(\w)", r"\1 ", s)
def json_wrap(s): return json.dumps({"q": s, "fmt":"text"})
def yaml_wrap(s): return f"q: |\n  {s}\nfmt: text\n"
def xml_wrap(s): return f"<q fmt='text'>{s}</q>"
def code_wrap(s, lang="text"): return f"```{lang}\n{s}\n```"
def rand_case(s):
    out=[]; 
    for ch in s:
        out.append(ch.upper() if (ch.isalpha() and random.random()<0.5) else ch)
    return "".join(out)
OPS={"zero_width":zero_width,"spacing":spacing,"json_wrap":json_wrap,"yaml_wrap":yaml_wrap,"xml_wrap":xml_wrap,"code_wrap":code_wrap,"rand_case":rand_case}
def generate(yaml_spec, seeds, seed=0):
    random.seed(seed); spec=yaml.safe_load(yaml_spec); out=[]
    for s in seeds:
        t=s
        for step in spec.get("pipeline", []):
            if "op" in step:
                fn=OPS[step["op"]]; args={k:v for k,v in step.items() if k!="op"}
                t=fn(t, **args) if args else fn(t)
            elif "choose" in step:
                c=random.choice(step["choose"]["oneof"]); fn=OPS[c["op"]]; args={k:v for k,v in c.items() if k!="op"}
                t=fn(t, **args) if args else fn(t)
        out.append(t)
    return out
