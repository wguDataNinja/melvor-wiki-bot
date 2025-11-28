# Git and GitHub Setup — melvor-wiki-bot

## Repository Information

- **Local path:**  
  `/Users/buddy/Desktop/projects/melvor-wiki-bot`

- **Remote (SSH):**  
  `git@github.com:wguDataNinja/melvor-wiki-bot.git`

- **Default branch:** `master`  
  (created automatically on first commit)

This project uses **SSH authentication** and a **local virtual environment** (`.venv`) that is intentionally excluded from Git.

---

## What We Have Done on GitHub So Far

### ✔ Created remote repo
- Repository created under GitHub user/org: `wguDataNinja`.
- No template or initial files; repo started empty.

### ✔ Initialized local repo + SSH remote
Commands used:

```bash
git init
git remote add origin git@github.com:wguDataNinja/melvor-wiki-bot.git
```

### ✔ First commit
Included:
- `.gitignore`
- `README.md`
- initial docs
- initial source code structure
- probe + scraper + manifest

### ✔ Fixed IDE noise
`.idea/` was accidentally committed before `.gitignore` was added.
We cleaned it properly:

```bash
git rm -r --cached .idea
git commit -m "Remove IDE files from repo; now ignored via .gitignore"
git push
```

### ✔ Pushed master branch and set upstream

```bash
git push --set-upstream origin master
```

Now regular `git push` works without flags.

---

## Project Git Rules (How We Use Git Here)

### 1) Never commit generated data  
Everything in `outputs/` is excluded.

This includes:
- scraped JSON
- probe results
- future embeddings
- future chunk output

### 2) Never commit virtual environments
`.venv/`, `env/`, `venv/` are fully ignored.

### 3) Never commit IDE noise  
`.idea/`, `.vscode/`, `.DS_Store` are ignored and removed if accidentally added.

### 4) Repo structure must always be runnable on a fresh clone  
This means:
- All code needed for wiki scraping + chunking lives in `src/`
- All scripts for running stages are in `scripts/`
- All documentation lives in `docs/` and `dev/`
- Running:

```bash
python scripts/wiki_scrape_run.py
```

must work immediately after installing dependencies.

### 5) Commit in milestones, not tiny fragments
Examples of good milestone commits:
- “Add wiki manifest + manifest loader”
- “Add probe scraper + output directory”
- “Add full wiki scraper + structured JSON outputs”
- “Add chunking pipeline”
- “Add keyword retrieval demo”

---

## Day-to-Day Workflow

### 1) Activate environment
```bash
cd /Users/buddy/Desktop/projects/melvor-wiki-bot
source .venv/bin/activate
```

### 2) Check what changed
```bash
git status
```

### 3) Stage the files you want to push
Typically:

```bash
git add .
```

### 4) Commit with a useful message
```bash
git commit -m "Describe the change here"
```

### 5) Push to GitHub
Since `master` tracks `origin/master`:

```bash
git push
```

---

## Fresh Clone Setup

If cloning on another system or reinstalling locally:

```bash
git clone git@github.com:wguDataNinja/melvor-wiki-bot.git
cd melvor-wiki-bot

python3.12 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
```

After that, all scripts should run immediately:

```bash
python scripts/wiki_probe_run.py
python scripts/wiki_scrape_run.py
```

---

## Branching (Optional)

Current project is small; `master` is fine.

If you want to use branches for experiments:

```bash
git checkout -b feature/chunking
# work...
git commit -m "Add chunking core logic"
git push -u origin feature/chunking
```

---

## Summary

- SSH remote configured  
- Local repo initialized  
- Upstream tracking set  
- IDE noise cleaned  
- Output directories ignored  
- All core scraper code committed  

This repo is now clean, reproducible, and ready for **chunking → retrieval → RAG** steps.