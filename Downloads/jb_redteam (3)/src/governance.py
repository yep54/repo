
import os, re, json, time, hashlib, threading
PII_PATTERNS=[re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I), re.compile(r"\b(\+?\d[\d\s\-()]{7,}\d)\b")]
def scrub_pii(text):
    out=text
    for pat in PII_PATTERNS: out=pat.sub("[REDACTED]", out)
    return out
def sha256(b): return hashlib.sha256(b).hexdigest()
class WORMLogger:
    def __init__(self, log_dir, name="redteam"):
        self.log_dir=log_dir; os.makedirs(log_dir, exist_ok=True); self.name=name; self.lock=threading.Lock(); self._open_log()
    def _open_log(self):
        self.cur_date=time.strftime("%Y%m%d"); self.path=os.path.join(self.log_dir, f"{self.name}_{self.cur_date}.log")
        if not os.path.exists(self.path): open(self.path,"x").close()
        self.manifest=os.path.join(self.log_dir, "MANIFEST.json")
        if not os.path.exists(self.manifest): open(self.manifest,"w").write(json.dumps({"files":{}}))
    def _rotate_if_needed(self):
        d=time.strftime("%Y%m%d")
        if d!=self.cur_date: self._open_log()
    def append(self, lines):
        clean=[scrub_pii(x.rstrip("\n")) for x in lines]
        with self.lock:
            self._rotate_if_needed()
            with open(self.path,"a",encoding="utf-8") as f:
                for line in clean: f.write(line+"\n")
            h=sha256(open(self.path,"rb").read()); mani=json.load(open(self.manifest,"r")); mani["files"][os.path.basename(self.path)]={"sha256":h,"updated":time.time()}
            open(self.manifest,"w").write(json.dumps(mani, indent=2))
