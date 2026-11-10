"""Build and validate a fact-checked resume using the locked LaTeX template."""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unicodedata
import zlib
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = ROOT / "assets" / "resume-template.tex"
MARKER = "%__TAILORED_RESUME_CONTENT__%"
MONTH_NAMES = {
    "january": "Jan", "jan": "Jan", "february": "Feb", "feb": "Feb",
    "march": "Mar", "mar": "Mar", "april": "Apr", "apr": "Apr",
    "may": "May", "june": "Jun", "jun": "Jun", "july": "Jul", "jul": "Jul",
    "august": "Aug", "aug": "Aug", "september": "Sep", "sept": "Sep", "sep": "Sep",
    "october": "Oct", "oct": "Oct", "november": "Nov", "nov": "Nov",
    "december": "Dec", "dec": "Dec",
}
SMART_DOUBLE = str.maketrans({"“": '"', "”": '"', "„": '"', "‟": '"'})
SMART_SINGLE = str.maketrans({"‘": "'", "’": "'", "‚": "'", "‛": "'"})


def format_text(value):
    text = unicodedata.normalize("NFKC", str(value or "")).replace("\u00a0", " ")
    text = text.translate(SMART_DOUBLE).translate(SMART_SINGLE)
    date_token = r"(?:(?:January|Jan|February|Feb|March|Mar|April|Apr|May|June|Jun|July|Jul|August|Aug|September|Sept|Sep|October|Oct|November|Nov|December|Dec)\.?\s+)?\d{4}|Present"
    protected = []

    def protect(match):
        protected.append(f"{match.group(1)} – {match.group(2)}")
        return f"\ue000{len(protected) - 1}\ue001"

    text = re.sub(rf"({date_token})\s+[—–-]\s+({date_token})", protect, text, flags=re.I)
    text = re.sub(r"\s+[—–]\s+", ", ", text)
    text = re.sub(r"[—―–]", "-", text)
    text = re.sub(r"…|\.{3,}", "", text)
    text = re.sub(r"[*•✓✔☑★☆⭐→➜➤]", "", text)
    text = "".join(ch for ch in text if not (unicodedata.category(ch) == "So" and ord(ch) > 0x1F000))
    text = re.sub(r"\s*\|\s*", " | ", text)
    text = re.sub(r"\s+([,.;:!?])", r"\1", text)
    text = re.sub(r",(?=\S)", lambda m: m.group(0) if re.match(r"\d", text[m.start()-1:m.start()]) and re.match(r"\d", text[m.end():m.end()+1]) else ", ", text)
    text = re.sub(r"(?<!\d):(?!/)(?=\S)", ": ", text)
    text = re.sub(r"[ \t\r\n]+", " ", text).strip()
    return re.sub(r"\ue000(\d+)\ue001", lambda m: protected[int(m.group(1))], text)


def clean_url(value):
    return re.sub(r"/+\Z", "", re.sub(r"^www\.", "", re.sub(r"^https?://", "", format_text(value), flags=re.I), flags=re.I))


def link_label(value, project=False):
    target = clean_url(value).lower()
    if re.search(r"(?:^|\.)github\.com(?:/|$)", target):
        return "GitHub"
    if re.search(r"(?:^|\.)gitlab\.com(?:/|$)", target):
        return "GitLab"
    if re.search(r"(?:^|\.)linkedin\.com(?:/|$)", target):
        return "LinkedIn"
    return "Live Demo" if project else "Portfolio"


def normalize_date_value(value):
    text = re.sub(r"\s*\([^)]*expected[^)]*\)\s*", " ", format_text(value), flags=re.I).strip()
    if not text:
        return ""
    if re.fullmatch(r"(?:present|current|now)", text, flags=re.I):
        return "Present"
    return re.sub(
        r"\b(January|Jan|February|Feb|March|Mar|April|Apr|May|June|Jun|July|Jul|August|Aug|September|Sept|Sep|October|Oct|November|Nov|December|Dec)\.?\s+(\d{4})\b",
        lambda m: f"{MONTH_NAMES[m.group(1).lower()]} {m.group(2)}", text, flags=re.I)


def format_date_range(start_date, end_date, expected=False):
    start, end = normalize_date_value(start_date), normalize_date_value(end_date)
    if not start and not end:
        return ""
    result = " – ".join(x for x in (start, end) if x)
    return result + (" (expected)" if expected or re.search(r"expected", str(end_date or ""), re.I) else "")


def normalize_bullet(value, current=False):
    text = re.sub(r"^[\s•*\-–—]+", "", format_text(value))
    text = re.sub(r"[.!?;:,]$", "", text).strip()
    return text[:1].upper() + text[1:] if text else ""


def escape_latex(value):
    replacements = {"\\": r"\textbackslash{}", "#": r"\#", "$": r"\$", "%": r"\%", "&": r"\&", "_": r"\_", "{": r"\{", "}": r"\}", "^": r"\textasciicircum{}", "~": r"\textasciitilde{}"}
    return "".join(replacements.get(ch, ch) for ch in format_text(str(value or "").replace("–", "--").replace("—", "--")))


def href_target(value):
    return re.sub(r"[\r\n{}]", "", str(value or "").strip()).replace("–", "-").replace("—", "-")


def web_target(value):
    target = href_target(value)
    return target if re.match(r"https?://", target, re.I) else (f"https://{target}" if target else "")


def is_project_url(value):
    target = href_target(value)
    return bool(re.match(r"https?://\S+$", target, re.I) or re.match(r"[^\s/]+\.[^\s/]+(?:/\S*)?$", target))


def latex_link(target, label):
    return f"\\href{{\\detokenize{{{href_target(target)}}}}}{{{escape_latex(label)}}}" if target and label else ""


def render_header(candidate):
    email, phone = str(candidate.get("email", "")).strip(), str(candidate.get("phone", "")).strip()
    linkedin, website = str(candidate.get("linkedin", "")).strip(), str(candidate.get("website", "")).strip()
    left = [f"\\textbf{{\\Large {escape_latex(candidate.get('name', ''))}}}", escape_latex(candidate.get("location", "")), latex_link(web_target(linkedin), link_label(linkedin)) if linkedin else ""]
    right = [latex_link(f"mailto:{email}", email) if email else "", latex_link(f"tel:{re.sub(r'[^\d+]', '', phone)}", phone) if phone else "", latex_link(web_target(website), link_label(website)) if website else ""]
    rows = [f"  {l} & {right[i]} \\\\" for i, l in enumerate(left)]
    return "\n".join([r"\begin{tabular*}{\textwidth}{l@{\extracolsep{\fill}}r}"] + rows + [r"\end{tabular*}"])


def render_bullets(items):
    bullets = [normalize_bullet(x) for x in items if normalize_bullet(x)]
    return "\n".join([r"    \resumeItemListStart"] + [f"      \\resumeItemPlain{{{escape_latex(x)}}}" for x in bullets] + [r"    \resumeItemListEnd"]) if bullets else ""


def render_education(items):
    if not items: return ""
    rows = ["\n".join([r"  \resumeSubheading", f"    {{{escape_latex(i['institution'])}}}{{{escape_latex(i['location'])}}}", f"    {{{escape_latex(i['qualification'])}}}{{{escape_latex(format_date_range(i['startDate'], i['endDate']))}}}"]) for i in items]
    return "\n".join([r"\section{Education}", r"\resumeSubHeadingListStart"] + rows + [r"\resumeSubHeadingListEnd"])


def render_experience(items):
    if not items: return ""
    rows = ["\n".join([r"  \resumeSubheading", f"    {{{escape_latex(i['company'])}}}{{{escape_latex(i['location'])}}}", f"    {{{escape_latex(i['role'])}}}{{{escape_latex(format_date_range(i['startDate'], i['endDate']))}}}", render_bullets([b['text'] for b in i['bullets']])]).strip() for i in items]
    return "\n".join([r"\section{Experience}", r"\resumeSubHeadingListStart"] + rows + [r"\resumeSubHeadingListEnd"])


def render_projects(items):
    if not items: return ""
    rows = []
    for i in items:
        link = latex_link(web_target(i["link"]), link_label(i["link"], project=True)) if is_project_url(i["link"]) else ""
        rows.append("\n".join([f"  \\resumeProjectHeading{{{escape_latex(i['name'])}}}{{{link}}}", render_bullets([b['text'] for b in i['bullets']])]).strip())
    return "\n".join([r"\section{Projects}", r"\resumeSubHeadingListStart"] + rows + [r"\resumeSubHeadingListEnd"])


def render_skills(groups, certifications):
    rows = [f"  \\item\\small{{\\textbf{{{escape_latex(g['category'])}}}{{: {', '.join(escape_latex(x) for x in g['items'])}}}}}" for g in groups]
    if certifications: rows.append(f"  \\item\\small{{\\textbf{{Certifications}}{{: {', '.join(escape_latex(x) for x in certifications)}}}}}")
    return "\n".join([r"\section{Skills}", r"\resumeSubHeadingListStart"] + rows + [r"\resumeSubHeadingListEnd"])


def render_resume_latex(resume):
    parts = [render_header(resume["candidate"]), r"\section{Summary}", f"\\resumeSummary{{{escape_latex(resume['summary']['text'])}}}", render_education(resume["education"]), render_experience(resume["experience"]), render_projects(resume["projects"]), render_skills(resume["skills"], resume["certifications"])]
    return "\n\n".join(x for x in parts if x).strip()


def assert_canonical_template(template):
    if r"\documentclass[letterpaper,11pt]{article}" not in template: raise ValueError("Canonical resume template must use Letter paper at 11 pt.")
    if template.count(MARKER) != 1: raise ValueError("Canonical resume template must contain exactly one content marker.")
    for command in (r"\newcommand{\resumeSummary}", r"\newcommand{\resumeSubheading}", r"\newcommand{\resumeProjectHeading}", r"\newcommand{\resumeItemPlain}"):
        if command not in template: raise ValueError(f"Canonical resume template is missing {command}.")


def build_canonical_latex(resume, template_path=TEMPLATE):
    template = Path(template_path).read_text(encoding="utf-8")
    assert_canonical_template(template)
    content = render_resume_latex(resume)
    present = [s for s in ("Summary", "Education", "Experience", "Projects", "Skills") if f"\\section{{{s}}}" in content]
    if present != sorted(present, key=("Summary", "Education", "Experience", "Projects", "Skills").index): raise ValueError("Canonical resume content has misordered sections.")
    if "Summary" not in present or "Skills" not in present: raise ValueError("Summary and Skills sections are required.")
    return template.replace(MARKER, content)


def _path_join(path, key): return f"{path}.{key}" if path else key


def shape_errors(data):
    errors = []
    def obj(value, path, required, allowed):
        if not isinstance(value, dict): errors.append(f"{path}: must be an object"); return False
        for key in required:
            if key not in value: errors.append(f"{_path_join(path,key)}: is required")
        for key in value:
            if key not in allowed: errors.append(f"{_path_join(path,key)}: additional property is not allowed")
        return True
    def string(value, path, nonempty=False):
        if not isinstance(value, str): errors.append(f"{path}: must be a string")
        elif nonempty and not value: errors.append(f"{path}: must not be empty")
    if not obj(data, "", ["candidate","summary","education","experience","projects","skills","certifications"], {"candidate","summary","education","experience","projects","skills","certifications"}): return errors
    if obj(data.get("candidate"), "candidate", ["name","email","phone","location","linkedin","website"], {"name","email","phone","location","linkedin","website"}):
        for k in ("name","email","phone","location","linkedin","website"): string(data["candidate"].get(k), f"candidate.{k}", k in ("name","email"))
    if obj(data.get("summary"), "summary", ["text","evidence"], {"text","evidence"}):
        string(data["summary"].get("text"), "summary.text"); ev=data["summary"].get("evidence")
        if not isinstance(ev,list) or len(ev)<1: errors.append("summary.evidence: must have at least one quote")
        elif any(not isinstance(x,str) for x in ev): errors.append("summary.evidence: must contain strings")
    def array(value, path):
        if not isinstance(value,list): errors.append(f"{path}: must be an array"); return []
        return value
    def bullets(value, path):
        arr=array(value,path)
        if len(arr)<1: errors.append(f"{path}: must have at least one bullet")
        for j,b in enumerate(arr):
            bp=f"{path}[{j}]"
            if obj(b,bp,["text","evidence"],{"text","evidence"}):
                string(b.get("text"),bp+".text"); ev=b.get("evidence")
                if not isinstance(ev,list) or len(ev)<1: errors.append(bp+".evidence: must have at least one quote")
                elif any(not isinstance(x,str) for x in ev): errors.append(bp+".evidence: must contain strings")
        return arr
    for i,e in enumerate(array(data.get("education"),"education")):
        p=f"education[{i}]"
        if obj(e,p,["institution","qualification","location","startDate","endDate"],{"institution","qualification","location","startDate","endDate"}):
            for k in ("institution","qualification","location","startDate","endDate"): string(e.get(k),p+"."+k)
    for i,e in enumerate(array(data.get("experience"),"experience")):
        p=f"experience[{i}]"
        if obj(e,p,["company","role","location","startDate","endDate","bullets"],{"company","role","location","startDate","endDate","bullets"}):
            for k in ("company","role","location","startDate","endDate"): string(e.get(k),p+"."+k)
            bullets(e.get("bullets"),p+".bullets")
    for i,e in enumerate(array(data.get("projects"),"projects")):
        p=f"projects[{i}]"
        if obj(e,p,["name","link","bullets"],{"name","link","bullets"}):
            for k in ("name","link"): string(e.get(k),p+"."+k)
            bullets(e.get("bullets"),p+".bullets")
    for i,g in enumerate(array(data.get("skills"),"skills")):
        p=f"skills[{i}]"
        if obj(g,p,["category","items"],{"category","items"}):
            string(g.get("category"),p+".category"); items=array(g.get("items"),p+".items")
            if len(items)<1: errors.append(p+".items: must have at least one item")
            for j,x in enumerate(items): string(x,f"{p}.items[{j}]")
    cert=array(data.get("certifications"),"certifications")
    for i,x in enumerate(cert): string(x,f"certifications[{i}]")
    if not array(data.get("education"),"education") and not array(data.get("experience"),"experience") and not array(data.get("projects"),"projects"): errors.append("education/experience/projects: at least one section must be non-empty")
    return errors


def normalize_truth(value, profile=False):
    text = unicodedata.normalize("NFKC", str(value or "")).translate(SMART_DOUBLE).translate(SMART_SINGLE).replace("—", "-").replace("–", "-")
    if profile: text = text.replace("*", "").replace("_", "").replace("`", "")
    return re.sub(r"\s+", " ", text).strip().lower()


def strip_html_comments(value):
    return re.sub(r"<!--.*?-->", "", value, flags=re.S)


def _number_key(value): return re.sub(r"[.,]", "", value)


def banned_phrases():
    text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    match = re.search(r"^## Banned phrases\s*$([\s\S]*?)(?=^#|\Z)", text, re.M)
    phrases = re.findall(r"^-\s+(.+?)\s*$", match.group(1), re.M) if match else []
    if not phrases: raise ValueError("SKILL.md has no banned phrases")
    return phrases


def truth_errors(data, profile_text):
    errors=[]; profile=normalize_truth(strip_html_comments(profile_text), True); phrases=banned_phrases()
    def contains(v,path,digits=False):
        target=normalize_truth(v)
        if digits:
            target_digits = re.sub(r"\D", "", target)
            runs = [re.sub(r"\D", "", run) for run in re.findall(r"\d(?:[\d\s().+\-]*\d)?", profile)]
            ok = any(target_digits in run for run in runs)
        else:
            ok = re.search(rf"(?<![a-z0-9]){re.escape(target)}(?![a-z0-9])", profile) is not None
        if not ok: errors.append(f"{path}: must appear in profile")
    def number_errors(text, evidence, path):
        evidence_numbers = {_number_key(num) for num in re.findall(r"\d+(?:[.,]\d+)*", evidence)}
        for num in re.findall(r"\d+(?:[.,]\d+)*", text):
            if _number_key(num) not in evidence_numbers: errors.append(f"{path}: number \"{num}\" is not in this claim's evidence")
    def evidence_quotes(evs,path):
        for j,q in enumerate(evs):
            qn=normalize_truth(q); qp=f"{path}[{j}]"
            if len(qn)<12: errors.append(f"{qp}: quote must be at least 12 characters")
            elif qn not in profile: errors.append(f"{qp}: quote is not in profile")
    for v,p in [(data["candidate"]["name"],"candidate.name"),(data["candidate"]["email"],"candidate.email"),(data["candidate"]["phone"],"candidate.phone")]: contains(v,p,p.endswith("phone"))
    for k in ("location","linkedin","website"):
        if data["candidate"][k]: contains(re.sub(r"^https?://|^www\.|/$", "", data["candidate"][k], flags=re.I),"candidate."+k)
    evidence_quotes(data["summary"]["evidence"],"summary.evidence")
    summary_evidence = " ".join(normalize_truth(q) for q in data["summary"]["evidence"])
    number_errors(data["summary"]["text"], summary_evidence, "summary.text")
    for i,e in enumerate(data["education"]):
        for k in ("institution","qualification"): contains(e[k],f"education[{i}].{k}")
        for k in ("location",):
            if e[k]: contains(e[k],f"education[{i}].{k}")
        for k in ("startDate","endDate"):
            for year in re.findall(r"\b\d{4}\b",e[k]):
                if not re.search(rf"(?<![a-z0-9]){year}(?![a-z0-9])", profile): errors.append(f"education[{i}].{k}: year \"{year}\" must appear in profile")
    for i,e in enumerate(data["experience"]):
        for k in ("company","role"): contains(e[k],f"experience[{i}].{k}")
        if e["location"]: contains(e["location"],f"experience[{i}].location")
        for k in ("startDate","endDate"):
            for year in re.findall(r"\b\d{4}\b",e[k]):
                if not re.search(rf"(?<![a-z0-9]){year}(?![a-z0-9])", profile): errors.append(f"experience[{i}].{k}: year \"{year}\" must appear in profile")
        for j,b in enumerate(e["bullets"]):
            p=f"experience[{i}].bullets[{j}]"; evidence_quotes(b["evidence"],p+".evidence")
            evidence=" ".join(normalize_truth(q) for q in b["evidence"])
            number_errors(b["text"], evidence, p+".text")
    for i,pj in enumerate(data["projects"]):
        contains(pj["name"],f"projects[{i}].name")
        for j,b in enumerate(pj["bullets"]):
            p=f"projects[{i}].bullets[{j}]"; evidence_quotes(b["evidence"],p+".evidence")
            evidence=" ".join(normalize_truth(q) for q in b["evidence"])
            number_errors(b["text"], evidence, p+".text")
    for i,g in enumerate(data["skills"]):
        for j,x in enumerate(g["items"]): contains(x,f"skills[{i}].items[{j}]")
    for i,x in enumerate(data["certifications"]): contains(x,f"certifications[{i}]")
    def walk(value_item, path):
        if isinstance(value_item, str): values.append((value_item, path))
        elif isinstance(value_item, list):
            for i, item in enumerate(value_item): walk(item, f"{path}[{i}]")
        elif isinstance(value_item, dict):
            for key, item in value_item.items(): walk(item, f"{path}.{key}" if path else key)
    values = []
    walk(data, "")
    for v,p in list(values):
        if re.search(r"\bTBD\b",v,re.I): errors.append(f"{p}: must not contain TBD")
        for phrase in phrases:
            if re.search(rf"\b{re.escape(phrase)}\b",v,re.I): errors.append(f"{p}: contains banned phrase \"{phrase}\"")
    return errors


def page_count(pdf_path):
    data=Path(pdf_path).read_bytes()
    pages=re.findall(rb"Output written on .*?\((\d+) page", data)
    if pages: return int(pages[-1])
    expanded = data
    for stream in re.findall(rb"stream\r?\n(.*?)\r?\nendstream", data, re.S):
        try:
            expanded += b"\n" + zlib.decompress(stream)
        except zlib.error:
            pass
    count=len(re.findall(rb"/Type\s*/Page(?!s)\b",expanded))
    if count: return count
    matches=re.findall(rb"/Type\s*/Pages\b.{0,500}?/Count\s+(\d+)",expanded,re.S)
    return int(matches[-1]) if matches else None


def engine_path():
    candidates=[os.environ.get("TECTONIC_BIN"),"tectonic","pdflatex","xelatex","lualatex"]
    for c in candidates:
        if c and (Path(c).is_file() if Path(c).is_absolute() else shutil.which(c)):
            return c
    return None


def parse_fill(text):
    matches = re.findall(r"RESUME-FILL\s+([0-9.]+)pt\s+([0-9.]+)pt", text)
    if not matches: return None
    amount, goal = map(float, matches[-1])
    return amount / goal if goal else None


def compile_pdf(tex_path, out_dir):
    engine=engine_path()
    if not engine: return None,None,None
    with tempfile.TemporaryDirectory() as tmp:
        work=Path(tmp); local_tex=work/"resume.tex"
        source = Path(tex_path).read_text(encoding="utf-8")
        source = source.replace(r"\end{document}", "\\par\\immediate\\write16{RESUME-FILL \\the\\pagetotal\\space\\the\\pagegoal}\n\\end{document}")
        local_tex.write_text(source, encoding="utf-8")
        output = []
        try:
            if Path(engine).name.lower().startswith("tectonic"):
                cmd=[engine,"--keep-logs","--outdir",str(work),str(local_tex)]
                result = subprocess.run(cmd,cwd=work,text=True,capture_output=True,timeout=180,check=True)
                output.extend((result.stdout, result.stderr))
            else:
                cmd=[engine,"-interaction=nonstopmode","-halt-on-error","resume.tex"]
                for _ in range(2):
                    result = subprocess.run(cmd,cwd=work,text=True,capture_output=True,timeout=180,check=True)
                    output.extend((result.stdout, result.stderr))
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
            log=(work/"resume.log").read_text(encoding="utf-8",errors="replace") if (work/"resume.log").exists() else str(exc)
            raise RuntimeError(log[-3000:])
        pdf=work/"resume.pdf"
        if not pdf.exists(): raise RuntimeError("LaTeX compilation did not produce resume.pdf")
        destination=Path(out_dir)/"resume.pdf"; shutil.copyfile(pdf,destination)
        log = (work / "resume.log").read_text(encoding="utf-8", errors="replace") if (work / "resume.log").exists() else ""
        fill = parse_fill(log) or parse_fill("\n".join(output))
        return destination,page_count(pdf),fill


def main(argv=None):
    parser=argparse.ArgumentParser(); parser.add_argument("resume_json"); parser.add_argument("--profile",required=True); parser.add_argument("--out",required=True); parser.add_argument("--no-pdf",action="store_true"); args=parser.parse_args(argv)
    try: data=json.loads(Path(args.resume_json).read_text(encoding="utf-8")); profile=Path(args.profile).read_text(encoding="utf-8")
    except Exception as exc: print(str(exc),file=sys.stderr); return 1
    problems=shape_errors(data) if isinstance(data,dict) else ["$: must be an object"]
    if isinstance(data, dict) and not problems:
        try:
            problems.extend(truth_errors(data, profile))
        except Exception as exc:
            problems.append(f"internal: truth check failed: {exc}")
    if problems:
        for i,p in enumerate(problems,1): print(f"{i}. {p}",file=sys.stderr)
        return 1
    out=Path(args.out); out.mkdir(parents=True,exist_ok=True); tex=out/"resume.tex"
    try: tex.write_text(build_canonical_latex(data),encoding="utf-8")
    except Exception as exc: print(str(exc),file=sys.stderr); return 1
    pdf=None; pages=None; fill=None; engine=engine_path()
    if not args.no_pdf:
        try: pdf,pages,fill=compile_pdf(tex,out)
        except RuntimeError as exc: print(str(exc),file=sys.stderr); return 1
        if pages is not None and pages>2: print(f"resume is {pages} pages; the limit is 2",file=sys.stderr); return 1
        if pages == 1 and fill is not None and fill < 0.85:
            print(f"warning: the page is only {round(fill * 100)}% full. If the profile has more relevant facts, use them; never pad.", file=sys.stderr)
        if engine is None: print(f"No LaTeX engine found. Upload {tex} to Overleaf (New Project > Upload Project) to get the PDF.")
    print(json.dumps({"ok":True,"tex":str(tex),"pdf":str(pdf) if pdf else None,"pages":pages,"fill":round(fill, 2) if fill is not None else None,"engine":Path(engine).name if engine else None}))
    return 0


if __name__ == "__main__": sys.exit(main())
