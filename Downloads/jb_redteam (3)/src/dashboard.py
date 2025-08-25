
import json, time
TEMPLATE = "<html><body><h1>Red-team Dashboard</h1><p>FN rate: {fn}%</p><pre>{summary}</pre></body></html>"
def build(metrics_json, out_html):
    obj=json.load(open(metrics_json,"r")); html=TEMPLATE.format(fn=round(obj.get("fn_rate",0)*100,2), summary=json.dumps(obj.get("summary",{}), indent=2))
    open(out_html,"w").write(html); return out_html
