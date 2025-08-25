
import os, json
def to_jsonl(txt_path, jsonl_path):
    os.makedirs(os.path.dirname(jsonl_path), exist_ok=True)
    n=0; cur=[]
    with open(txt_path,"r",encoding="utf-8") as f, open(jsonl_path,"w",encoding="utf-8") as out:
        for line in f:
            if line.strip()=='---':
                t=" ".join(x.strip() for x in cur if x.strip())
                if t: out.write(json.dumps({"text":t,"label":1,"tags":["external","db"],"source":"local_db"})+"\n"); n+=1
                cur=[]
            else: cur.append(line)
        t=" ".join(x.strip() for x in cur if x.strip())
        if t: out.write(json.dumps({"text":t,"label":1,"tags":["external","db"],"source":"local_db"})+"\n"); n+=1
    return n
