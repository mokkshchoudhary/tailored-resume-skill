import ast
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr
from io import StringIO
from unittest.mock import patch
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "tailored-resume"
SCRIPT = SKILL / "scripts" / "build_resume.py"
EXAMPLE = SKILL / "examples"
sys.path.insert(0, str(SCRIPT.parent))
sys.dont_write_bytecode = True
import build_resume


def py():
    return sys.executable


def run_build(data, profile=None, pdf=False):
    with tempfile.TemporaryDirectory() as td:
        data_path = Path(td) / "resume.json"
        data_path.write_text(json.dumps(data), encoding="utf-8")
        env = os.environ.copy()
        engine = next((x for x in [env.get("TECTONIC_BIN"), shutil.which("tectonic"), str(Path(env.get("LOCALAPPDATA", "")) / "Tailor" / "bin" / "tectonic.exe")] if x and Path(x).exists()), None)
        if engine: env["TECTONIC_BIN"] = engine
        result = subprocess.run([py(), str(SCRIPT), str(data_path), "--profile", str(profile or EXAMPLE / "profile.md"), "--out", str(Path(td) / "out")] + (["--no-pdf"] if not pdf else []), capture_output=True, text=True, env=env)
        return result


class ResumeBuildTests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads((EXAMPLE / "resume.json").read_text(encoding="utf-8"))

    def test_example_builds_clean(self):
        result = run_build(self.data)
        self.assertEqual(result.returncode, 0, result.stderr)
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "out"
            result = subprocess.run([py(), str(SCRIPT), str(EXAMPLE / "resume.json"), "--profile", str(EXAMPLE / "profile.md"), "--out", str(out), "--no-pdf"], capture_output=True, text=True)
            tex = (out / "resume.tex").read_text(encoding="utf-8")
            self.assertLess(tex.index(r"\section{Summary}"), tex.index(r"\section{Education}"))
            self.assertLess(tex.index(r"\section{Education}"), tex.index(r"\section{Experience}"))
            self.assertLess(tex.index(r"\section{Experience}"), tex.index(r"\section{Projects}"))
            self.assertLess(tex.index(r"\section{Projects}"), tex.index(r"\section{Skills}"))
            self.assertIn("jordan.lee@example.com", tex)
            self.assertNotIn("Kafka", tex)
            self.assertNotIn("Go", tex)

    def test_real_compile_one_page(self):
        candidates = [os.environ.get("TECTONIC_BIN"), shutil.which("tectonic")]
        localappdata = os.environ.get("LOCALAPPDATA")
        if localappdata:
            candidates.append(str(Path(localappdata) / "Tailor" / "bin" / "tectonic.exe"))
        engine = next((x for x in candidates if x and Path(x).exists()), None)
        if not engine:
            self.skipTest("tectonic not installed")
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "out"
            env = os.environ.copy(); env["TECTONIC_BIN"] = engine
            result = subprocess.run([py(), str(SCRIPT), str(EXAMPLE / "resume.json"), "--profile", str(EXAMPLE / "profile.md"), "--out", str(out)], capture_output=True, text=True, env=env)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(build_resume.page_count(out / "resume.pdf"), 1)
            self.assertGreater((out / "resume.pdf").stat().st_size, 5000)
            summary = json.loads(result.stdout.strip().splitlines()[-1])
            self.assertGreaterEqual(summary["fill"], 0.88)
            self.assertLessEqual(summary["fill"], 0.98)

    def assert_mutation_fails(self, mutate, path):
        data = json.loads(json.dumps(self.data)); mutate(data)
        result = run_build(data)
        self.assertEqual(result.returncode, 1)
        self.assertIn(path, result.stderr)

    def test_truth_mutations(self):
        cases = [
            (lambda d: d["skills"][0]["items"].append("Kafka"), "skills[0].items[3]"),
            (lambda d: d["experience"][0]["bullets"][0].update(text="Built a shipment API that handled 1,300 requests per second"), "experience[0].bullets[0].text"),
            (lambda d: d["summary"]["evidence"].__setitem__(0, "This quote is absent from the profile entirely"), "summary.evidence[0]"),
            (lambda d: d["experience"][0]["bullets"][0].update(evidence=[]), "experience[0].bullets[0].evidence"),
            (lambda d: d["summary"].update(text="Results-driven backend engineer"), "summary.text"),
            (lambda d: d["candidate"].update(location="TBD"), "candidate.location"),
            (lambda d: d["experience"][0].update(company="Unknown Systems"), "experience[0].company"),
            (lambda d: d["summary"]["evidence"].__setitem__(0, "Short quote"), "summary.evidence[0]"),
        ]
        for mutate, path in cases:
            with self.subTest(path=path): self.assert_mutation_fails(mutate, path)

    def test_multiple_problems_reported(self):
        data = json.loads(json.dumps(self.data)); data["skills"][0]["items"].append("Kafka"); data["summary"]["text"] = "Results-driven engineer"
        result = run_build(data)
        self.assertEqual(result.returncode, 1)
        self.assertGreaterEqual(len([x for x in result.stderr.splitlines() if x[:1].isdigit()]), 2)

    def test_formatting_helpers(self):
        self.assertEqual(build_resume.escape_latex(r"\ # $ % & _ { } ^ ~"), r"\textbackslash{} \# \$ \% \& \_ \{ \} \textasciicircum{} \textasciitilde{}")
        self.assertIn("--", build_resume.escape_latex("A" + chr(0x2013) + "B"))
        self.assertEqual(build_resume.format_date_range("Jan 2021", "present"), "Jan 2021 " + chr(0x2013) + " Present")
        self.assertEqual(build_resume.format_text("B.S. in Computer Science"), "B.S. in Computer Science")
        self.assertEqual(build_resume.format_text("10:30"), "10:30")
        self.assertEqual(build_resume.format_text("3:1"), "3:1")
        self.assertEqual(build_resume.format_text("Python,SQL"), "Python, SQL")
        self.assertEqual(build_resume.format_text("1,200"), "1,200")

    def test_empty_projects_omitted_and_all_empty_rejected(self):
        data = json.loads(json.dumps(self.data)); data["projects"] = []
        result = run_build(data); self.assertEqual(result.returncode, 0, result.stderr)
        data["education"] = []; data["experience"] = []
        result = run_build(data); self.assertEqual(result.returncode, 1); self.assertIn("education/experience/projects", result.stderr)

    def test_number_evidence_uses_exact_number_set(self):
        data = json.loads(json.dumps(self.data))
        data["summary"] = {"text": "Grew usage 40%", "evidence": ["The service served 400 users every day"]}
        profile = EXAMPLE / "profile.md"
        with tempfile.TemporaryDirectory() as td:
            profile = Path(td) / "profile.md"
            profile.write_text((EXAMPLE / "profile.md").read_text(encoding="utf-8") + "\nThe service served 400 users every day.\nThe service grew usage 40% this quarter.", encoding="utf-8")
            result = run_build(data, profile=profile, pdf=False)
        self.assertEqual(result.returncode, 1)
        self.assertIn('summary.text: number "40"', result.stderr)
        data["summary"]["evidence"] = ["The service grew usage 40% this quarter"]
        with tempfile.TemporaryDirectory() as td:
            profile = Path(td) / "profile.md"
            profile.write_text((EXAMPLE / "profile.md").read_text(encoding="utf-8") + "\nThe service grew usage 40% this quarter.", encoding="utf-8")
            self.assertEqual(run_build(data, profile=profile, pdf=False).returncode, 0)

    def test_truth_matching_uses_boundaries_and_phone_runs(self):
        data = json.loads(json.dumps(self.data)); data["skills"][0]["items"] = ["Go"]
        profile = (EXAMPLE / "profile.md").read_text(encoding="utf-8") + "\nGoogle and years ago."
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "profile.md"; p.write_text(profile, encoding="utf-8")
            result = run_build(data, profile=p, pdf=False)
        self.assertEqual(result.returncode, 1); self.assertIn("skills[0].items[0]", result.stderr)
        for skill in ("C++", "Node.js"):
            data = json.loads(json.dumps(self.data)); data["skills"][0]["items"] = [skill]
            profile = (EXAMPLE / "profile.md").read_text(encoding="utf-8") + f"\nSkill: {skill}."
            with tempfile.TemporaryDirectory() as td:
                p = Path(td) / "profile.md"; p.write_text(profile, encoding="utf-8")
                self.assertEqual(run_build(data, profile=p, pdf=False).returncode, 0)
        data = json.loads(json.dumps(self.data)); data["candidate"]["phone"] = "+1 555 0101"
        # "+1 555" and "0101" are separate numbers; joining every digit in the profile would wrongly find "15550101".
        profile = (EXAMPLE / "profile.md").read_text(encoding="utf-8").replace("+1 555 0100", "+1 555 | Ext: 0101")
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "profile.md"; p.write_text(profile, encoding="utf-8")
            result = run_build(data, profile=p, pdf=False)
        self.assertEqual(result.returncode, 1); self.assertIn("candidate.phone", result.stderr)

    def test_truth_crash_is_reported_and_does_not_write(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "out"
            with patch.object(build_resume, "truth_errors", side_effect=KeyError("broken")):
                stderr = StringIO()
                with redirect_stderr(stderr):
                    result = build_resume.main([str(EXAMPLE / "resume.json"), "--profile", str(EXAMPLE / "profile.md"), "--out", str(out), "--no-pdf"])
            self.assertEqual(result, 1); self.assertIn("internal: truth check failed", stderr.getvalue()); self.assertFalse((out / "resume.tex").exists())

    def test_banned_phrase_is_reported_once_per_path(self):
        data = json.loads(json.dumps(self.data)); data["summary"]["text"] = "Results-driven engineer"
        result = run_build(data, pdf=False)
        lines = [line for line in result.stderr.splitlines() if "summary.text: contains banned phrase" in line]
        self.assertEqual(len(lines), 1)

    def test_html_comments_are_not_profile_facts(self):
        data = json.loads(json.dumps(self.data)); data["summary"]["evidence"] = ["Secret evidence only in a comment"]
        profile = (EXAMPLE / "profile.md").read_text(encoding="utf-8") + "\n<!-- Secret evidence only in a comment -->"
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "profile.md"; p.write_text(profile, encoding="utf-8")
            result = run_build(data, profile=p, pdf=False)
        self.assertEqual(result.returncode, 1); self.assertIn("summary.evidence[0]", result.stderr)

    def test_fill_parser_reads_last_measurement(self):
        self.assertAlmostEqual(build_resume.parse_fill("RESUME-FILL 500.0pt 600.0pt\nRESUME-FILL 880.0pt 1000.0pt"), 0.88)

    def test_cut_down_resume_warns_but_succeeds(self):
        data = json.loads(json.dumps(self.data)); data["experience"] = data["experience"][:1]; data["experience"][0]["bullets"] = data["experience"][0]["bullets"][:1]; data["projects"] = []
        result = run_build(data, pdf=True)
        self.assertEqual(result.returncode, 0, result.stderr); self.assertRegex(result.stderr, r"warning: the page is only \d+% full")
        summary = json.loads(result.stdout.strip().splitlines()[-1]); self.assertIsInstance(summary["fill"], float)

    def test_banned_list_and_template(self):
        banned = build_resume.banned_phrases(); self.assertGreaterEqual(len(banned), 10); self.assertIn("results-driven", banned)
        template = (SKILL / "assets" / "resume-template.tex").read_text(encoding="utf-8")
        self.assertEqual(template.count(build_resume.MARKER), 1); self.assertIn(r"\documentclass[letterpaper,11pt]{article}", template)
        for command in (r"\newcommand{\resumeSummary}", r"\newcommand{\resumeSubheading}", r"\newcommand{\resumeProjectHeading}", r"\newcommand{\resumeItemPlain}"): self.assertIn(command, template)

    def test_page_count_real_pdf(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "out"; env = os.environ.copy(); engine = next((x for x in [env.get("TECTONIC_BIN"), shutil.which("tectonic"), str(Path(env.get("LOCALAPPDATA", "")) / "Tailor" / "bin" / "tectonic.exe")] if x and Path(x).exists()), None)
            if not engine: self.skipTest("tectonic not installed")
            env["TECTONIC_BIN"] = engine
            result = subprocess.run([py(), str(SCRIPT), str(EXAMPLE / "resume.json"), "--profile", str(EXAMPLE / "profile.md"), "--out", str(out)], capture_output=True, text=True, env=env)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(build_resume.page_count(out / "resume.pdf"), 1)

    def test_portability_and_forbidden_paths(self):
        stdlib = getattr(sys, "stdlib_module_names", set())
        for p in SKILL.rglob("*.py"):
            tree = ast.parse(p.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for a in node.names: self.assertIn(a.name.split(".")[0], stdlib, p)
                if isinstance(node, ast.ImportFrom) and node.level == 0: self.assertIn((node.module or "").split(".")[0], stdlib, p)
        forbidden = ["resume" + " " + "maker", "resume" + "-data", "g:" + "\\", "users" + "\\" + "moksh"]
        for p in ROOT.rglob("*"):
            if p.is_file() and p.suffix != ".pyc":
                if "__pycache__" in p.parts: continue
                text = p.read_text(encoding="utf-8", errors="ignore").lower()
                for item in forbidden: self.assertNotIn(item, text, p)

    def test_profile_template_is_placeholder_only(self):
        text = (SKILL / "assets" / "profile-template.md").read_text(encoding="utf-8")
        self.assertNotRegex(text, r"@|example\.com|Jordan")


if __name__ == "__main__": unittest.main()
