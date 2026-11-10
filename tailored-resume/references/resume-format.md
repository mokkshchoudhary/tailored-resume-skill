# Hand-writing the locked resume

1. Start with `assets/resume-template.tex` and replace the single `%__TAILORED_RESUME_CONTENT__%` marker with the content below.

Header:

```tex
\begin{tabular*}{\textwidth}{l@{\extracolsep{\fill}}r}
  \textbf{\Large NAME} & \href{\detokenize{mailto:EMAIL}}{EMAIL} \\
  LOCATION & \href{\detokenize{tel:PHONE-DIGITS}}{PHONE} \\
  \href{\detokenize{https://LINKEDIN}}{LinkedIn} & \href{\detokenize{https://WEBSITE}}{Portfolio} \\
\end{tabular*}
```

Sections use these exact forms:

```tex
\section{Summary}
\resumeSummary{SUMMARY}

\section{Education}
\resumeSubHeadingListStart
  \resumeSubheading
    {INSTITUTION}{LOCATION}
    {QUALIFICATION}{START -- END}
\resumeSubHeadingListEnd

\section{Experience}
\resumeSubHeadingListStart
  \resumeSubheading
    {COMPANY}{LOCATION}
    {ROLE}{START -- END}
    \resumeItemListStart
      \resumeItemPlain{BULLET}
    \resumeItemListEnd
\resumeSubHeadingListEnd

\section{Projects}
\resumeSubHeadingListStart
  \resumeProjectHeading{PROJECT}{\href{\detokenize{https://LINK}}{Live Demo}}
    \resumeItemListStart
      \resumeItemPlain{BULLET}
    \resumeItemListEnd
\resumeSubHeadingListEnd

\section{Skills}
\resumeSubHeadingListStart
  \item\small{\textbf{CATEGORY}{: ITEM, ITEM}}
\resumeSubHeadingListEnd
```

Normalisation rules: bullets have no leading bullet mark or trailing punctuation, and their first letter is capitalised. Dates shorten month names to Jan through Dec; present, current and now become `Present`; ranges use `START -- END`; append ` (expected)` when the end date says expected. An empty project link renders as `\resumeProjectHeading{NAME}{}`. Leave out empty Education, Experience and Projects sections.

Escape these characters in content: `\` → `\textbackslash{}`, `#` → `\#`, `$` → `\$`, `%` → `\%`, `&` → `\&`, `_` → `\_`, `{` → `\{`, `}` → `\}`, `^` → `\textasciicircum{}`, `~` → `\textasciitilde{}`. Date ranges use an en dash in the source data and render as `--` in LaTeX. Links use `\href{\detokenize{...}}{...}`. Email and phone targets use `mailto:` and `tel:`. Recognized labels are GitHub, GitLab, LinkedIn, Portfolio and Live Demo.

See `examples/resume.tex` for a complete worked example.

Final checklist: every evidence quote is verbatim and at least 12 characters; every number is backed by that claim's evidence; no skill, employer, title, date or credential is outside the profile; no banned phrase from `SKILL.md`; no `TBD`; sections are in Summary, Education, Experience, Projects, Skills order; the result is at most 2 pages.
