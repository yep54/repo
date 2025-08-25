
Red-team standalone tool
========================

Install:
    python -m pip install flask pyyaml requests beautifulsoup4

Build DB from repo (subs + links):
    python -m jb_redteam.src.cli build-db --owner CyberAlbSecOP --repo Awesome_GPT_Super_Prompting --out-txt /mnt/data/jb_redteam/redteam_db.txt

Export JSONL:
    python -m jb_redteam.src.cli export-jsonl --in-txt /mnt/data/jb_redteam/redteam_db.txt --out-jsonl /mnt/data/jb_redteam/redteam_db.jsonl

Generate prompts:
    python -m jb_redteam.src.cli gen --db-txt /mnt/data/jb_redteam/redteam_db.txt --n 200 --mutate-k 3 --out /mnt/data/jb_redteam/samples.txt
