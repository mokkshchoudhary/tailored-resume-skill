# Tailored resume skill

Give an AI agent one fact-only profile and a job description. It makes a tailored resume in one fixed LaTeX layout. Every claim is checked against the profile, and nothing is invented.

## What you get

- A locked, single-column layout that is readable by applicant tracking systems
- A resume of one to two pages
- An evidence check on every bullet and number
- A check for banned phrases
- A PDF when a LaTeX engine is present
- Otherwise, `resume.tex` for Overleaf

## Quick start

1. Get the skill: clone `https://github.com/mokkshchoudhary/tailored-resume-skill`, or choose Download ZIP.
2. Install it into your agent using the instructions in [Install and use, by agent](#install-and-use-by-agent).
3. Say “make my resume” and give the agent an old resume or profile plus the job description.
4. Keep the `profile.md` it gives you for next time.

## Works with

| Agent | How it is installed | Status |
| --- | --- | --- |
| Claude Code | Copy the folder to `~/.claude/skills/` or `<project>/.claude/skills/` | Not yet tested by the author |
| Claude (claude.ai and desktop) | Zip the folder and upload it under Settings > Capabilities > Skills | Not yet tested by the author |
| Codex CLI | Copy the folder to `~/.codex/skills/` or `<project>/.agents/skills/` | Not yet tested by the author |
| ChatGPT | Upload the zip under Skills | Not yet tested by the author |
| Gemini app | Settings > Skills > Upload | Not yet tested by the author |
| Gemini CLI | Copy it to `<project>/.agents/skills/` | Not yet tested by the author |
| Antigravity | Copy it to `<project>/.agents/skills/` or `~/.gemini/antigravity/skills/` | Tested by the author |
| Any other chat | Attach `SKILL.md`, `references/`, `assets/` and `examples/` | Not yet tested by the author |

Open an issue to report what works for you.

## Install and use, by agent

The folder name must stay `tailored-resume`.

### Making the zip

PowerShell:

```powershell
Compress-Archive -Path tailored-resume -DestinationPath tailored-resume.zip
```

bash:

```bash
zip -r tailored-resume.zip tailored-resume
```

### Claude Code

1. Copy `tailored-resume/` to `~/.claude/skills/` for all projects or `<project>/.claude/skills/`.
2. Say:

```text
Make my resume. Use my old resume or profile and this job description.
```

If the agent can run Python it will run the checker and build automatically; if not, it follows the written format guide.

### Claude (claude.ai and desktop)

1. Use [Making the zip](#making-the-zip) to zip the `tailored-resume` folder.
2. Upload the zip under Settings > Capabilities > Skills.
3. Say:

```text
Make my resume. Use my old resume or profile and this job description.
```

If the agent can run Python it will run the checker and build automatically; if not, it follows the written format guide.

### Codex CLI

1. Copy `tailored-resume/` to `~/.codex/skills/` or `<project>/.agents/skills/`.
2. Say:

```text
Make my resume. Use my old resume or profile and this job description.
```

If the agent can run Python it will run the checker and build automatically; if not, it follows the written format guide.

### ChatGPT

1. Use [Making the zip](#making-the-zip) to zip the `tailored-resume` folder.
2. Upload the zip under Skills. This is currently available in Business and Enterprise.
3. Say:

```text
Make my resume. Use my old resume or profile and this job description.
```

If the agent can run Python it will run the checker and build automatically; if not, it follows the written format guide.

### Gemini app

1. Use [Making the zip](#making-the-zip) to zip the `tailored-resume` folder.
2. Open Settings > Skills > Upload.
3. Say:

```text
Make my resume. Use my old resume or profile and this job description.
```

If the agent can run Python it will run the checker and build automatically; if not, it follows the written format guide.

### Gemini CLI

1. Copy `tailored-resume/` to `<project>/.agents/skills/`.
2. Say:

```text
Make my resume. Use my old resume or profile and this job description.
```

If the agent can run Python it will run the checker and build automatically; if not, it follows the written format guide.

### Antigravity

1. Copy `tailored-resume/` to `<project>/.agents/skills/` or `~/.gemini/antigravity/skills/`.
2. Say:

```text
Make my resume. Use my old resume or profile and this job description.
```

If the agent can run Python it will run the checker and build automatically; if not, it follows the written format guide.

### Any other chat

1. Attach `SKILL.md`, `references/`, `assets/` and `examples/`.
2. Say:

```text
Follow SKILL.md. Make my resume from my profile or old resume and this job description.
```

If the agent can run Python it will run the checker; if not, it follows the written format guide.

Install locations change between tool versions. Check the tool's own documentation if the skill is not found.

## Your profile

`profile.md` is the complete record of your facts. The skill builds it from an old resume, a LinkedIn PDF export, notes, or a plain description if you do not already have one. `TBD` marks a missing fact. To claim something new, add it to the profile first.

Use [`tailored-resume/assets/profile-template.md`](tailored-resume/assets/profile-template.md) as the profile structure. [`tailored-resume/examples/`](tailored-resume/examples/) contains a complete made-up example.

## Running the build script yourself

From the repository root, run:

```text
python tailored-resume/scripts/build_resume.py resume.json --profile profile.md --out resume-output
```

The script accepts `resume_json`, `--profile`, `--out`, and `--no-pdf`. It uses Python 3 standard library only. A PDF needs a LaTeX engine: Tectonic, pdflatex, xelatex, or lualatex. The script uses the first one it finds.

## Getting a PDF: install Tectonic

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

- Skill not found: check that the folder is named `tailored-resume`, check its location, and check the tool's documentation.
- No PDF: no LaTeX engine is available. [Install Tectonic](#getting-a-pdf-install-tectonic), or use Overleaf with `resume.tex`.
- Checker rejects a line: fix the content or add the fact to the profile. Never edit the checker.

## Tests

From the repository root, run:

```text
python -m unittest discover -s tests
```

## License

MIT. See [`LICENSE`](LICENSE).
