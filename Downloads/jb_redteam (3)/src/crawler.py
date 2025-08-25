
import os, re, json, time, hashlib, urllib.parse, urllib.request
UA = "jb-redteam/1.0 (research)"
def _req(url, headers=None, timeout=15):
    headers = headers or {}
    headers["User-Agent"] = UA
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()
def _json(url):
    b = _req(url, headers={"Accept":"application/vnd.github+json"})
    return json.loads(b.decode("utf-8", errors="ignore"))
def list_tree(owner, repo, branch="main"):
    for br in [branch, "main", "master"]:
        try:
            data = _json(f"https://api.github.com/repos/{owner}/{repo}/git/trees/{br}?recursive=1")
            if "tree" in data: return data["tree"]
        except Exception:
            continue
    return []
def fetch_raw(owner, repo, path, branch="main"):
    for br in [branch, "main", "master"]:
        url = f"https://raw.githubusercontent.com/{owner}/{repo}/{br}/{path}"
        try:
            return _req(url).decode("utf-8", errors="ignore")
        except Exception:
            continue
    return ""
def find_links(md):
    links = re.findall(r"\[[^\]]*\]\((https?://[^)]+)\)", md)
    links += re.findall(r"(https?://[^\s)]+)", md)
    seen=set(); out=[]
    for u in links:
        u=u.strip().strip(").,]"'")
        if u not in seen: seen.add(u); out.append(u)
    return out
def fetch_text(url):
    try:
        b = _req(url, timeout=15).decode("utf-8", errors="ignore")
        if "<html" in b.lower():
            b = re.sub(r"(?s)<(script|style)[^>]*>.*?</\1>", " ", b, flags=re.I)
            b = re.sub(r"(?s)<[^>]+>", " ", b)
        return re.sub(r"\s+", " ", b).strip()
    except Exception:
        return ""
def extract_prompts_from_markdown(md):
    out=[]
    for m in re.finditer(r"```[^\n]*\n(.*?)```", md, flags=re.S|re.M):
        blk=m.group(1).strip()
        if len(blk)>=32: out.append(blk)
    for m in re.finditer(r"^\s*>\s+(.*)$", md, flags=re.M):
        line=m.group(1).strip()
        if len(line)>=32: out.append(line)
    pats=[r"ignore previous instructions",r"do not refuse",r"remain in role",r"format.*mandatory",r"override.*constraints"]
    for para in re.split(r"\n\s*\n", md):
        p=para.strip()
        if len(p)>=32 and any(re.search(pa,p,flags=re.I) for pa in pats): out.append(p)
    def _norm(t): return re.sub(r"\s+"," ",t).strip()
    seen=set(); uniq=[]
    import hashlib
    for t in out:
        h=hashlib.sha256(_norm(t).encode("utf-8")).hexdigest()
        if h not in seen: seen.add(h); uniq.append(_norm(t))
    return uniq
def parse_gitmodules(owner, repo, branch="main"):
    txt = fetch_raw(owner, repo, ".gitmodules", branch=branch)
    if not txt: return []
    mods=[]; cur={}
    for line in txt.splitlines():
        line=line.strip()
        if line.startswith("[submodule"):
            if cur: mods.append(cur); cur={}
        elif line.startswith("path"): cur["path"]=line.split("=",1)[1].strip()
        elif line.startswith("url"):
            import re
            url=line.split("=",1)[1].strip()
            m=re.search(r"github\.com[:/](.+?)/(.+?)(\.git)?$", url)
            if m: cur["owner"],cur["repo"]=m.group(1),m.group(2)
    if cur: mods.append(cur)
    return mods
def crawl_full_with_submodules(owner, repo, out_txt, follow_links=True, link_limit=200):
    os.makedirs(os.path.dirname(out_txt), exist_ok=True)
    def crawl(owner, repo, out_txt):
        tree=list_tree(owner, repo)
        collected=0
        with open(out_txt,"a",encoding="utf-8") as outf:
            for node in tree:
                if node.get("type")!="blob": continue
                path=node.get("path","")
                if not path.lower().endswith(".md"): continue
                md=fetch_raw(owner, repo, path) or ""
                prompts=extract_prompts_from_markdown(md)
                for p in prompts:
                    outf.write(p+"\n\n---\n\n"); collected+=1
                if follow_links and link_limit>0:
                    for u in find_links(md)[:link_limit]:
                        txt=fetch_text(u)
                        if len(txt)<128: continue
                        for p in extract_prompts_from_markdown(txt):
                            outf.write(p+"\n\n---\n\n"); collected+=1
        return collected
    count=crawl(owner, repo, out_txt)
    for m in parse_gitmodules(owner, repo):
        try: count+=crawl(m["owner"], m["repo"], out_txt)
        except Exception: continue
    return count
