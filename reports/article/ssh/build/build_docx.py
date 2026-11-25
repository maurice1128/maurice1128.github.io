#!/usr/bin/env python3
"""Convert the SSH markdown files to Word files that follow the journal's format:
12-point type, double-spaced throughout, one-inch margins.

Usage: python3 build_docx.py   (run from reports/article/ssh/build)
Outputs go to ../submission/.
"""
import pathlib
import subprocess
import sys

from docx import Document
from docx.enum.text import WD_LINE_SPACING
from docx.shared import Inches, Pt

HERE = pathlib.Path(__file__).resolve().parent
SRC = HERE.parent
OUT = SRC / "submission"
FILES = {
    "manuscript_ssh.md": "SSH_manuscript_anonymous.docx",
    "tables_ssh.md": "SSH_tables.docx",
    "title_page_ssh.md": "SSH_title_page.docx",
    "bio_note_ssh.md": "SSH_bio_note.docx",
    "supplement_ssh.md": "SSH_supplementary_material.docx",
    "cover_letter_ssh.md": "SSH_cover_letter.docx",
}


def restyle(path):
    doc = Document(path)
    for section in doc.sections:
        section.left_margin = section.right_margin = Inches(1)
        section.top_margin = section.bottom_margin = Inches(1)
    for style in doc.styles:
        try:
            if style.font is not None:
                style.font.name = "Times New Roman"
                if style.type == 1 and not style.name.startswith("Heading") and style.name != "Title":
                    style.font.size = Pt(12)
        except (AttributeError, ValueError):
            pass

    def fix(par):
        par.paragraph_format.line_spacing_rule = WD_LINE_SPACING.DOUBLE
        for run in par.runs:
            run.font.name = "Times New Roman"
            if run.font.size is None or run.font.size != Pt(12):
                if not par.style.name.startswith("Heading") and par.style.name != "Title":
                    run.font.size = Pt(12)

    for par in doc.paragraphs:
        fix(par)
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for par in cell.paragraphs:
                    fix(par)
    doc.save(path)


def main():
    OUT.mkdir(exist_ok=True)
    built = []
    for src, dst in FILES.items():
        s = SRC / src
        if not s.exists():
            print(f"skip (missing): {src}")
            continue
        d = OUT / dst
        subprocess.run(
            ["pandoc", str(s), "-f", "markdown+footnotes+pipe_tables+smart", "-o", str(d)],
            check=True,
        )
        restyle(d)
        built.append(dst)
    print("built:", ", ".join(built))


if __name__ == "__main__":
    sys.exit(main())
