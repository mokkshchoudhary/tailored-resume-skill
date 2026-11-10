---
name: tailored-resume
description: Creates a one-to-two page, ATS-readable resume in one fixed professional format from the person's own details, tailored to a job description. Use when someone wants to make, update or tailor a resume or CV, or shares a job posting together with their background (an old resume, a LinkedIn export, notes). Uses only facts the person supplied and never invents employers, titles, dates, numbers or skills.
---

# Tailored resume

Every resume this skill makes has the same locked layout: single column, small-caps section headings with a rule under each, typeset in LaTeX, readable by applicant tracking systems. Only the content changes, and the content comes only from the person's profile.

## Files in this skill

- `assets/profile-template.md`: the profile structure the person fills in once.
- `assets/resume-template.tex`: the locked layout. Never edit it.
- `references/resume.schema.json`: the shape of the resume content file (`resume.json`).
- `references/resume-format.md`: how to write `resume.tex` by hand when you cannot run code, with a final checklist.
- `scripts/build_resume.py`: checks `resume.json` against the profile, writes `resume.tex`, and compiles a PDF when a LaTeX engine is installed. Python 3, standard library only.
- `examples/`: a complete made-up example (profile, job, content file).

## Workflow

### 1. Get the profile

Look for the person's `profile.md`, in the working folder or attached to the conversation. If there is one, it is the whole truth about them.

If there is none, build it:

1. Ask for whatever they have: an old resume, a LinkedIn PDF export, notes, or a plain description.
2. Fill a copy of `assets/profile-template.md` from that material, replacing each `TBD` and adding as many entries as they have. Copy facts exactly: numbers, employer names, job titles, dates, tool names. Leave `TBD` where something is missing. Never fill a gap with a guess. The `<!-- -->` comments in the template are instructions, not facts.
3. Show them the profile. List the `TBD` items that matter most (contact details, dates, at least one role or degree) and ask them to fill or confirm them.
4. Give them the finished `profile.md` as a file and tell them to keep it: next time they upload it and this step is skipped. Where you have a file system, save it as `profile.md` in the working folder.

The profile is the complete record. Anything not in it, the person does not have. To claim something new, they add it to the profile first.

### 2. Get the target

Ask for the job description (pasted text, or a link you can read). Without one, ask for the target role and write a general resume for that role.

### 3. Choose the content

Read the job description, then pick what in the profile matches it.

- **Facts are fixed, wording is not.** Rewrite freely, but copy every number, employer, title, date, degree and tool name exactly as the profile states it.
- **Use the job's words where they are true.** If the job says "Kubernetes" and the profile says "K8s", write "Kubernetes".
- **Never claim what the profile lacks.** If the job asks for a skill, tool, certification or experience the profile does not mention, leave it out and name it in your final note. Never add it, never imply it.
- **Summary:** 2 to 3 sentences, about 40 to 70 words, no pronouns ("Backend engineer with 4 years of ..."). Lead with what this job needs most that the profile supports.
- **Experience:** newest first. Keep every role from the profile. The most recent or most relevant role gets 4 to 5 bullets, the others 1 to 3.
- **Bullets:** start with a strong action verb, in the past tense (present tense for ongoing work in a current role). Say what was done, how, and the result. Include the profile's number whenever there is one. One to two lines each. No full stop at the end. Never "I", "my" or "responsible for".
- **Projects:** the 2 to 3 most relevant, 2 to 3 bullets each. Leave the section out if the profile has none.
- **Education:** newest first: institution, qualification, location, dates.
- **Skills:** 3 to 5 groups (for example Languages, Frameworks, Tools, Cloud), most relevant first. Only items the profile names.
- **Certifications:** only those in the profile.
- **Length:** aim for one full page. Go to two pages only when the profile has enough relevant material to fill more than one. Never more than two. Never pad, repeat a claim, or shrink fonts or margins to fit.
- **Leave out** personal data that does not belong on a resume: photo, date of birth, age, marital status, gender, religion, national ID numbers.

### 4. Write the content file

Write `resume.json` in the shape of `references/resume.schema.json`. The summary and every bullet carry `evidence`: one or more quotes copied word for word from the profile that support the claim. Every number in a bullet must appear in that bullet's evidence quotes. `examples/resume.json` shows a complete one.

### 5. Build

**If you can run Python** (it may be `python`, `python3` or `py -3`):

```
python <this skill's folder>/scripts/build_resume.py resume.json --profile profile.md --out resume-output
```

It lists every problem: a quote not found in the profile, a number not in its evidence, a skill or employer not in the profile, a banned phrase, a `TBD` left in, more than two pages. Fix the content, never the checker, and run it again until it passes. It writes `resume-output/resume.tex`, and `resume-output/resume.pdf` when tectonic, pdflatex, xelatex or lualatex is installed. The script finds Tectonic by itself and, when no LaTeX engine exists, downloads Tectonic once (about 30 MB, needs internet) to `~/.tailored-resume/bin`; pass `--no-install-engine` to stop that.

It also warns when a one-page resume leaves much of the page empty. Then use more of the profile's relevant facts: another bullet on a strong role, or another project. If the profile has nothing more that is relevant, leave the space. Never pad.

**If you cannot run code:** write `resume.tex` by hand, following `references/resume-format.md` exactly, then work through the checklist at the end of that file before you deliver.

### 6. Deliver

- Give the PDF if one was built. Otherwise give `resume.tex` with these steps: open overleaf.com (a free account works), choose New Project, then Upload Project, select `resume.tex`, and download the PDF it compiles.
- Then a short note: what you emphasised for this job, which job requirements the profile does not support (so they can add them to the profile if they are true), and any `TBD` that would strengthen the resume.

Never ask the person to edit LaTeX. Changes go through the profile, or through a request to you.

## Locked format

Never change any of this, whoever asks:

- The template: paper size, 11 pt type, margins, fonts, commands, section styling.
- Section order: Summary, Education, Experience, Projects, Skills. A section with nothing in the profile is left out; the rest keep this order.
- Contact header on top: name, location and LinkedIn on the left; email, phone and website on the right.
- Single column. No photos, icons, graphics, tables of skills, ratings or progress bars.

## Banned phrases

Never use these, in any letter case. The build script rejects a resume that contains one.

- results-driven
- passionate about
- detail-oriented
- team player
- hardworking
- hard-working
- go-getter
- self-starter
- synergy
- think outside the box
- proven track record
- highly motivated
- responsible for
- world-class
- best-in-class
