from pathlib import Path
from datetime import datetime


today = datetime.today().strftime("%d %B %Y")

TITLE = "BA Seminar: The ABC of Computational Text Analysis"
AUTHOR = "Alex Flückiger"
TITLE = "BA Seminar: The ABC of Computational Text Analysis"
AUTHOR = "Alex Flückiger"
COURSE_NAME = "KED2025"

MAIN_DIR = Path(".").cwd() / "ked"
CSSFILE = MAIN_DIR / "lectures/resources/custom_style_reveal.scss"
LECTURES_DIR = MAIN_DIR / "lectures"
LECTURES_MD_DIR = LECTURES_DIR / "md"
LECTURES_HTML_DIR = LECTURES_DIR / "html"
LECTURES_PDF_DIR = LECTURES_DIR / "pdf"
LECTURES_NOTES_DIR = LECTURES_DIR / "notes"

ASSIGNMENTS_DIR = MAIN_DIR / "assignments"
MATERIALS_DIR = MAIN_DIR / "materials"

BIB_FILE="/home/alex/zotero.bib"


def task_prepare_dir():
    """Create all directories"""

    for outdir in (
        LECTURES_PDF_DIR,
        LECTURES_HTML_DIR,
        LECTURES_MD_DIR,
        LECTURES_NOTES_DIR,
        ASSIGNMENTS_DIR,
        MATERIALS_DIR,
    ):
        yield {
            "name": outdir,
            "actions": [f"mkdir -p {outdir}"],
            "targets": [outdir],
        }


def task_update_website():
    """Render with quarto"""
    return {
        "actions": [f"quarto render {MAIN_DIR}"],
    }


def task_create_html_slide():
    infiles = sorted(LECTURES_MD_DIR.glob("*.md"))

    for infile in infiles:
        outfile = Path(LECTURES_HTML_DIR) / Path(infile).with_suffix(".html").name
        # TODO: involves a dirty hack of changing working directory as Quarto can not handle relative paths
        yield {
            "name": infile,
            "file_dep": [infile, CSSFILE],
            "actions": [
                f"cd {LECTURES_MD_DIR} && quarto render {infile.name} -o {outfile.name} --quiet",
            ],
            "targets": [outfile],
            "title": show_cmd,
        }


def task_create_pdf_slide():
    infiles = sorted(LECTURES_HTML_DIR.glob("*.html"))

    for infile in infiles:
        outfile = Path(LECTURES_PDF_DIR) / Path(infile).with_suffix(".pdf").name
        yield {
            "name": infile,
            "file_dep": [infile],
            "actions": [
                # generate PDF from HTML
                # REMOVE? use 4:3 format because of this bug: https://github.com/astefanutti/decktape/issues/151 --size='1050x700'
                f"decktape reveal --chrome-path /usr/bin/google-chrome-stable --load-pause 500 --pdf-author '{AUTHOR}' --pdf-title '{TITLE}' {infile} {outfile}",
                # compress
                f"gs -sDEVICE=pdfwrite -dCompatibilityLevel=1.4 -dPDFSETTINGS=/prepress -dNOPAUSE -dQUIET -dBATCH -sOutputFile={outfile}.temp {outfile}",
                f"mv {outfile}.temp {outfile}",
            ],
            "targets": [outfile],
        }


# def task_create_lecture_notes():
#     infiles = sorted(LECTURES_MD_DIR.glob("*.md"))

#     for infile in infiles:
#         outfile = Path(LECTURES_NOTES_DIR) / infile.with_suffix(".notes.pdf").name
#         yield {
#             "name": infile,
#             "file_dep": [infile],
#             "actions": [
#                 f"python lib/extract_notes.py < {infile} | pandoc -o {outfile} -f markdown --pdf-engine=xelatex -V geometry:margin=2cm",
#             ],
#             "targets": [outfile],
#         }


def task_create_syllabus():
    outfile = MAIN_DIR / f"{COURSE_NAME}_syllabus.pdf"

    fdependencies = [
        MAIN_DIR / fname
        for fname in ["index.qmd", "schedule.qmd", "lectures.qmd", "assignments.qmd"]
    ]
    return {
        "file_dep": fdependencies,
        "actions": [
            f"cd {MAIN_DIR} && \
            cat index.qmd <(echo '[Go to Course Website](https://aflueckiger.github.io/{COURSE_NAME}/)' ) | grep -v '< fa' | sed '/<div/,/div>/d'> index.md.tmp && \
            sed '5 a # Schedule' schedule.qmd > schedule.md.tmp && \
            sed '5 a # Lectures' lectures.qmd | grep -P -v '< .+ >' | sed -E 's/The slides .+ icon://g' > lectures.md.tmp && \
            sed '5 a # Assignments' assignments.qmd > assignments.md.tmp && \
            pandoc -o {outfile} index.md.tmp schedule.md.tmp lectures.md.tmp assignments.md.tmp \
            --from markdown \
            --toc --toc-depth=1 \
            --number-sections \
            -V geometry:margin=2.5cm \
            -V urlcolor='[HTML]{{111bab}}' \
            -V linkcolor='[HTML]{{111bab}}' \
            -V filecolor='[HTML]{{111bab}}' \
            --metadata title='{TITLE}' \
            --metadata date='{today}'",
            f"rm {MAIN_DIR}/*.tmp",
        ],
        "targets": [outfile],
        # 'title': show_cmd
    }


def task_create_assignment():
    infiles = sorted(ASSIGNMENTS_DIR.glob("**/*.md"))

    for infile in infiles:
        outfile = infile.with_suffix(".pdf")
        yield {
            "name": infile,
            "file_dep": [infile],
            "actions": [
                f"pandoc -f  markdown+rebase_relative_paths -o {outfile} {infile} \
            --number-sections \
            --metadata date='{today}' \
            --citeproc \
            --bibliography {BIB_FILE} \
            -V citecolor='[HTML]{{111bab}}' \
            -V urlcolor='[HTML]{{111bab}}' \
            -V linkcolor='[HTML]{{111bab}}' \
            -V filecolor='[HTML]{{111bab}}' \
            -V toccolor='[HTML]{{111bab}}' \
            -V geometry:margin=2.5cm"
            ],
            "targets": [outfile],
            # 'title': show_cmd
        }


def task_create_materials():

    infiles = sorted(MATERIALS_DIR.glob("*.md"))

    for infile in infiles:
        outfile = Path(infile).with_suffix(".pdf")
        # TODO: involves a dirty hack of changing working directory as Quarto can not handle relative paths
        yield {
            "name": infile,
            "file_dep": [infile],
            "actions": [
                f"cd {MATERIALS_DIR} && quarto render {infile.name} -o {outfile.name}",
            ],
            "targets": [outfile],
            "title": show_cmd,
        }


def show_cmd(task):
    return "executing... %s" % task.actions[0]
