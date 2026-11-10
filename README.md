# Tailored resume skill

Give an AI agent one fact-only profile and a job description. It makes a tailored resume in one fixed LaTeX layout. Every claim is checked against the profile, and nothing is invented.

## What you get

- A locked, single-column layout that is readable by applicant tracking systems
- A resume of one to two pages
- An evidence check on every bullet and number
- A check for banned phrases
- A PDF built automatically where the agent can run Python and reach the internet
- Otherwise, `resume.tex` for Overleaf

## Quick start

1. Get the skill: clone `https://github.com/mokkshchoudhary/tailored-resume-skill`, or choose Download ZIP.
2. Install it into your agent using the instructions in [Install and use, by agent](#install-and-use-by-agent).
3. Say “make my resume” and give the agent an old resume or profile plus the job description.
4. Keep the `profile.md` it gives you for next time.

## Install and use, by agent

The skill is the `tailored-resume` folder in this repository. Every agent below reads the same folder; only the place you put it differs. Two rules apply everywhere:

- The folder name must stay `tailored-resume`.
- `SKILL.md` must sit directly inside that folder.

Menus and folder locations change between versions. Each section links to the agent's own documentation; check it if a step does not match what you see.

### Two ways to install

**Copy the folder** (agents that run on your computer). Replace `DEST` with the folder named in your agent's section.

macOS and Linux:

```bash
mkdir -p DEST
cp -r tailored-resume DEST/
```

Windows PowerShell:

```powershell
New-Item -ItemType Directory -Force DEST
Copy-Item -Recurse tailored-resume DEST
```

**Upload a zip** (chat apps). Make the zip from the repository root, so the zip contains the `tailored-resume` folder itself.

macOS and Linux:

```bash
zip -r tailored-resume.zip tailored-resume
```

Windows PowerShell:

```powershell
Compress-Archive -Path tailored-resume -DestinationPath tailored-resume.zip
```

### What to say

In every agent, the same request works:

```text
Make my resume for this job. Here is my old resume and the job description.
```

Attach or paste your old resume (or your `profile.md` if you already have one) and the job description. The first time, the agent builds your `profile.md`, shows it to you, and asks about anything missing. Keep that file. Next time you give it `profile.md` and the new job description, and it goes straight to the resume.

### Claude Code

1. Copy the folder to `~/.claude/skills/` to use it in every project, or to `.claude/skills/` inside one project.
2. Start a new Claude Code session.
3. Ask for a resume in plain words, or type `/tailored-resume` to call the skill by name.

Claude Code runs the build script on your computer, so you get the checks and a PDF.

Documentation: [Claude Code skills](https://code.claude.com/docs/en/skills).

### Claude (claude.ai and the desktop app)

1. Turn on code execution: open Settings > Capabilities and switch on "Code execution and file creation". On Team and Enterprise plans an owner turns it on in Organization settings.
2. Make the zip.
3. Open Customize > Skills, click "+", then "+ Create skill", then "Upload a skill", and choose the zip.
4. Check that `tailored-resume` is switched on in the skills list.
5. Start a new chat, attach your resume or profile, paste the job description, and ask for a resume. Claude picks the skill by itself; you can also name it ("use the tailored-resume skill").

Custom skills are available on all plans, Free included. Claude runs the checker in its own sandbox. If that sandbox cannot download Tectonic, you get `resume.tex` and the Overleaf steps instead of a PDF.

Documentation: [Using skills in Claude](https://support.claude.com/en/articles/12512180-using-skills-in-claude).

### Codex (CLI and IDE extension)

1. Copy the folder to `~/.agents/skills/` to use it everywhere, or to `.agents/skills/` inside one repository.
2. Codex notices new skills by itself. If it does not appear, restart Codex.
3. Ask for a resume in plain words, or type `$tailored-resume` to call it by name. `/skills` lists the skills Codex has found.

Codex runs the build script on your computer, so you get the checks and a PDF.

Documentation: [Build skills](https://learn.chatgpt.com/docs/build-skills).

### ChatGPT

OpenAI documents skills that you add yourself for the ChatGPT desktop app. It reads the same folders as Codex.

1. Copy the folder to `~/.agents/skills/`.
2. Open the ChatGPT desktop app. The skill is listed under Skills in the sidebar.
3. In a chat, type `@` and choose `tailored-resume`, or just ask for a resume.

Some accounts also have an upload button in ChatGPT on the web: profile icon > Skills > New skill > Upload from your computer, then choose the zip. Whether you have it depends on your plan and, at work, on your administrator.

If you have neither, use [Any other chat](#any-other-chat).

Documentation: [Build skills](https://learn.chatgpt.com/docs/build-skills), [Skills and plugins](https://learn.chatgpt.com/docs/skills-and-plugins).

### Gemini app

1. Make the zip.
2. On gemini.google.com or in the Gemini app for Mac, click Customize in the sidebar (under More if you do not see it), then Skills.
3. Click Create, then Upload, choose the zip, then Upload, then Create.
4. In a chat, type `/` (or `@`) and choose `tailored-resume`, or just ask for a resume.

Upload works on the web and on Mac. The mobile app can use a skill but cannot upload one. For now this needs a personal Google account; work and school accounts do not have it yet.

Scripts inside a Gemini app skill cannot reach the internet, so Tectonic cannot be downloaded there. Expect `resume.tex` and the Overleaf steps instead of a PDF.

Documentation: [Create and manage skills for Gemini Apps](https://support.google.com/gemini/answer/17094296).

### Antigravity (app, IDE and CLI)

1. Copy the folder to `.agents/skills/` inside your workspace, or to `~/.gemini/config/skills/` to use it in every workspace.
2. In the CLI, run `/skills reload` or start a new conversation. In the app and IDE, start a new conversation.
3. Ask for a resume in plain words. In the app and the CLI you can also type `/tailored-resume`.

Antigravity runs the build script on your computer, so you get the checks and a PDF.

Documentation: [Antigravity agent skills](https://antigravity.google/docs/skills).

### Gemini CLI

Google replaced Gemini CLI with the Antigravity CLI in June 2026. If you still use Gemini CLI:

1. Copy the folder to `~/.gemini/skills/` to use it everywhere, or to `.gemini/skills/` inside one project. `~/.agents/skills/` and `.agents/skills/` work too.
2. Run `/skills reload`, then `/skills list` to see that `tailored-resume` is there.
3. Ask for a resume. Gemini CLI asks you to approve the skill the first time it uses it.

Documentation: [Gemini CLI agent skills](https://geminicli.com/docs/cli/skills/).

### Any other chat

Any assistant that accepts file attachments can follow the skill without installing anything.

1. Attach `SKILL.md` and the files in `references/`, `assets/` and `examples/`.
2. Say:

```text
Follow SKILL.md. Make my resume from my old resume and this job description.
```

Without the build script, the assistant writes `resume.tex` by hand from the written format guide and works through its checklist. Upload `resume.tex` to Overleaf to get the PDF.

## Your profile

`profile.md` is the complete record of your facts. The skill builds it from an old resume, a LinkedIn PDF export, notes, or a plain description if you do not already have one. `TBD` marks a missing fact. To claim something new, add it to the profile first.

Use [`tailored-resume/assets/profile-template.md`](tailored-resume/assets/profile-template.md) as the profile structure. [`tailored-resume/examples/`](tailored-resume/examples/) contains a complete made-up example.

## Running the build script yourself

From the repository root, run:

```text
python tailored-resume/scripts/build_resume.py resume.json --profile profile.md --out resume-output
```

The script accepts `resume_json`, `--profile`, `--out`, `--no-pdf`, and `--no-install-engine`. It uses Python 3 standard library only. A PDF needs a LaTeX engine: Tectonic, pdflatex, xelatex, or lualatex. The script uses the first one it finds.

## Getting a PDF

You normally do nothing; the script looks for Tectonic on PATH and in the common install folders, and if there is no LaTeX engine it downloads Tectonic 0.17.0 once from the official GitHub release, checks its SHA-256, and keeps it in `~/.tailored-resume/bin`; `--no-install-engine` turns this off.

To install it yourself instead:

Tectonic is a free LaTeX engine that comes as a single program. Install it once and the skill makes the PDF for you. These commands come from the [Tectonic installation guide](https://tectonic-typesetting.github.io/book/latest/installation/).

Windows (PowerShell). This unpacks `tectonic.exe` into the current folder. Move it to a folder on your `PATH`, or run the skill from that folder.

```powershell
[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
iex ((New-Object System.Net.WebClient).DownloadString('https://drop-ps1.fullyjustified.net'))
```

macOS:

```bash
brew install tectonic
```

Linux and macOS without Homebrew. This puts `tectonic` in the current folder. Move it to a folder on your `PATH`.

```bash
curl --proto '=https' --tlsv1.2 -fsSL https://drop-sh.fullyjustified.net | sh
```

Other options: `conda install -c conda-forge tectonic`, `sudo pacman -S tectonic` (Arch Linux), `sudo port install tectonic` (MacPorts), `cargo install tectonic`.

Check it with `tectonic --version`. The first build needs an internet connection, because Tectonic downloads the LaTeX files it needs and then keeps them.

Chat apps such as claude.ai, ChatGPT and the Gemini app run in their own sandbox, so you cannot install Tectonic there. In those apps you get `resume.tex`.

No LaTeX engine? Use Overleaf: open overleaf.com, choose New Project, choose Upload Project, select `resume.tex`, and download the PDF it compiles.

## Rules the skill will not break

- It never invents facts.
- It keeps the locked format and section order.
- It does not use banned phrases.
- It does not add a photo or personal data such as date of birth.

## Troubleshooting

- Skill not found: check that the folder is named `tailored-resume`, that `SKILL.md` is directly inside it, and that it is in the folder your agent reads. Then start a new session.
- No PDF: the automatic download needs internet and write access to your home folder; chat apps without those give `resume.tex` for Overleaf.
- Checker rejects a line: fix the content or add the fact to the profile. Never edit the checker.

## Tests

From the repository root, run:

```text
python -m unittest discover -s tests
```

## License

MIT. See [`LICENSE`](LICENSE).
