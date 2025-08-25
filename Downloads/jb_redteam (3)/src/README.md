
Red-team tool
=============
Commands:
- Build DB: python -m jb_redteam.src.cli build-db --owner CyberAlbSecOP --repo Awesome_GPT_Super_Prompting --out-txt /path/redteam_db.txt
- Export JSONL: python -m jb_redteam.src.cli export-jsonl --in-txt /path/redteam_db.txt --out-jsonl /path/redteam_db.jsonl
- Generate samples: python -m jb_redteam.src.cli gen --db-txt /path/redteam_db.txt --n 200 --mutate-k 3 --out /path/samples.txt
- DSL pipeline: python -m jb_redteam.src.cli dsl-gen --dsl pipeline.yaml --seeds seeds.txt --out out.txt
- Minimize failing prompt: python -m jb_redteam.src.cli minimize --model-dir /path/models --in-prompt fail.txt --out minimized.txt
- Bandit search: python -m jb_redteam.src.cli bandit --model-dir /path/models --seeds seeds.txt --budget 500 --out bandit.log
