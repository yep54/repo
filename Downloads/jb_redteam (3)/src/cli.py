
import os, argparse, json, random
from .crawler import crawl_full_with_submodules as crawl_full
from .db import to_jsonl
from .generator import sample_generate
from .attack_dsl import generate as dsl_generate
from .multiturn import SCRIPTS
from .reducer import reduce_string
from .schedulers import UCB1
from .evo_search import evolve
from .dashboard import build as build_dashboard
from .adapters import LocalDetectorTarget
from .governance import WORMLogger

def cmd_build(args):
    count=crawl_full(args.owner, args.repo, args.out_txt, follow_links=not args.no_links, link_limit=args.link_limit)
    print(json.dumps({"collected":count,"out_txt":args.out_txt}))

def cmd_export(args):
    n=to_jsonl(args.in_txt, args.out_jsonl); print(json.dumps({"exported":n,"out_jsonl":args.out_jsonl}))

def cmd_gen(args):
    outs=sample_generate(args.db_txt, n=args.n, mutate_k=args.mutate_k)
    if args.out:
        with open(args.out,"w",encoding="utf-8") as f:
            for t in outs: f.write(t+"\n")
    else:
        for t in outs: print(t)

def cmd_run_dsl(args):
    spec=open(args.dsl,"r",encoding="utf-8").read()
    seeds=[l.strip() for l in open(args.seeds,"r",encoding="utf-8") if l.strip()]
    outs=dsl_generate(spec, seeds, seed=args.seed)
    with open(args.out,"w",encoding="utf-8") as f:
        for t in outs: f.write(t+"\n")
    print(json.dumps({"generated":len(outs),"out":args.out}))

def cmd_multiturn(args):
    script=SCRIPTS[args.script]; seeds=[l.strip() for l in open(args.seeds,"r",encoding="utf-8") if l.strip()]
    convos=[script.run(s) for s in seeds[:args.n]]
    with open(args.out,"w",encoding="utf-8") as f:
        for c in convos: f.write(json.dumps(c, ensure_ascii=False)+"\n")
    print(json.dumps({"conversations":len(convos),"out":args.out}))

def cmd_minimize(args):
    tgt=LocalDetectorTarget(args.model_dir); prompt=open(args.in_prompt,"r",encoding="utf-8").read()
    def test_fn(s): pred,_=tgt.infer([s]); return pred[0]==0
    reduced=reduce_string(prompt, test_fn, min_len=args.min_len)
    open(args.out,"w",encoding="utf-8").write(reduced)
    print(json.dumps({"original_len":len(prompt),"reduced_len":len(reduced),"out":args.out}))

def cmd_bandit(args):
    tgt=LocalDetectorTarget(args.model_dir); logger=WORMLogger(args.log_dir,"bandit")
    arms=["zero_width","spacing","json_wrap","yaml_wrap","xml_wrap","code_wrap","rand_case"]
    bandit=UCB1(arms); seeds=[l.strip() for l in open(args.seeds,"r",encoding="utf-8") if l.strip()]
    from .attack_dsl import OPS
    fns=0; total=0
    for _ in range(args.budget):
        a=bandit.select(); import random as _r; s=_r.choice(seeds)
        t=OPS[a](s) if a!="code_wrap" else OPS[a](s,"text")
        pred,_=tgt.infer([t]); is_fn=int(pred[0]==0); fns+=is_fn; total+=1; bandit.update(a, is_fn)
        logger.append([f"ARM {a} -> {'FN' if is_fn else 'TP'}", t, "-"*20])
    rate=fns/max(total,1); print(json.dumps({"budget":args.budget,"fns":fns,"fn_rate":rate}))

def cmd_evo(args):
    tgt=LocalDetectorTarget(args.model_dir); seeds=[l.strip() for l in open(args.seeds,"r",encoding="utf-8") if l.strip()]
    def mutate_fn(s):
        from .generator import sample_generate
        return random.choice(sample_generate(args.db_txt, n=1, mutate_k=3) or [s])
    def fitness_fn(x):
        pred,score=tgt.infer([x]); return (1.0 - score[0]) if pred[0]==0 else 0.0
    best, pop=evolve(seeds, mutate_fn, fitness_fn, pop_size=args.pop, gens=args.gens)
    with open(args.out,"w",encoding="utf-8") as f:
        for p,s in pop: f.write(json.dumps({"text":p,"score":s}, ensure_ascii=False)+"\n")
    print(json.dumps({"best_score":best[1],"out":args.out}))

def cmd_dashboard(args):
    obj={"fn_rate":args.fn_rate,"summary":{"runs":args.runs}}
    open(args.metrics,"w").write(json.dumps(obj, indent=2))
    out=build_dashboard(args.metrics, args.out_html); print(json.dumps({"html":out}))

def main():
    ap=argparse.ArgumentParser(prog="jb-redteam"); sub=ap.add_subparsers()
    a=sub.add_parser("build-db"); a.add_argument("--owner",default="CyberAlbSecOP"); a.add_argument("--repo",default="Awesome_GPT_Super_Prompting")
    a.add_argument("--out-txt",required=True); a.add_argument("--no-links",action="store_true"); a.add_argument("--link-limit",type=int,default=200); a.set_defaults(func=cmd_build)
    b=sub.add_parser("export-jsonl"); b.add_argument("--in-txt",required=True); b.add_argument("--out-jsonl",required=True); b.set_defaults(func=cmd_export)
    g=sub.add_parser("gen"); g.add_argument("--db-txt",required=True); g.add_argument("--n",type=int,default=50); g.add_argument("--mutate-k",type=int,default=3); g.add_argument("--out"); g.set_defaults(func=cmd_gen)
    dslp=sub.add_parser("dsl-gen"); dslp.add_argument("--dsl",required=True); dslp.add_argument("--seeds",required=True); dslp.add_argument("--seed",type=int,default=0); dslp.add_argument("--out",required=True); dslp.set_defaults(func=cmd_run_dsl)
    mt=sub.add_parser("multiturn"); mt.add_argument("--script",choices=list(SCRIPTS.keys()),required=True); mt.add_argument("--seeds",required=True); mt.add_argument("--n",type=int,default=50); mt.add_argument("--out",required=True); mt.set_defaults(func=cmd_multiturn)
    mn=sub.add_parser("minimize"); mn.add_argument("--model-dir",required=True); mn.add_argument("--in-prompt",required=True); mn.add_argument("--out",required=True); mn.add_argument("--min-len",type=int,default=16); mn.set_defaults(func=cmd_minimize)
    ba=sub.add_parser("bandit"); ba.add_argument("--model-dir",required=True); ba.add_argument("--seeds",required=True); ba.add_argument("--budget",type=int,default=500); ba.add_argument("--log-dir",required=True); ba.set_defaults(func=cmd_bandit)
    ev=sub.add_parser("evo"); ev.add_argument("--model-dir",required=True); ev.add_argument("--seeds",required=True); ev.add_argument("--db-txt",required=True); ev.add_argument("--pop",type=int,default=50); ev.add_argument("--gens",type=int,default=10); ev.add_argument("--out",required=True); ev.set_defaults(func=cmd_evo)
    dash=sub.add_parser("dashboard"); dash.add_argument("--metrics",required=True); dash.add_argument("--out-html",required=True); dash.add_argument("--fn-rate",type=float,default=0.0); dash.add_argument("--runs",type=int,default=0); dash.set_defaults(func=cmd_dashboard)
    args=ap.parse_args(); 
    if hasattr(args,"func"): args.func(args)
    else: ap.print_help()
if __name__=="__main__": main()
