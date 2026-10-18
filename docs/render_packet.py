"""Render docs/DEPLOYMENT.md to one PDF."""

import re
from pathlib import Path

from fpdf import FPDF

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "DEPLOYMENT.md"
OUTPUT = ROOT / "deployment-packet.pdf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"


class Packet(FPDF):
    def footer(self):
        self.set_y(-12)
        self.set_font("DejaVu", size=8)
        self.set_text_color(80, 80, 80)
        self.cell(0, 8, f"{self.page_no()}", align="C")


def write_inline(pdf, text, size=10, height=5):
    parts = re.split(r"(`[^`]+`)", text)
    for part in parts:
        if part.startswith("`") and part.endswith("`") and len(part) > 2:
            pdf.set_font("Mono", size=size - 1)
            pdf.write(height, part[1:-1])
        else:
            pdf.set_font("DejaVu", size=size)
            pdf.write(height, part)
    pdf.ln(height + 1)


def parse_table(lines):
    rows = []
    for line in lines:
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if cells and all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells):
            continue
        rows.append(cells)
    return rows


def draw_table(pdf, rows):
    pdf.set_font("DejaVu", size=8)
    pdf.ln(1)
    with pdf.table(
        width=pdf.epw,
        first_row_as_headings=True,
        line_height=4.2,
        text_align="LEFT",
    ) as table:
        for data_row in rows:
            row = table.row()
            for cell in data_row:
                row.cell(re.sub(r"`([^`]*)`", r"\1", cell))
    pdf.ln(2)


def draw_code(pdf, lines):
    pdf.set_font("Mono", size=7.5)
    pdf.set_fill_color(244, 244, 244)
    for line in lines:
        pdf.multi_cell(pdf.epw, 3.6, line if line else " ", fill=True)
    pdf.ln(2)


def render():
    pdf = Packet(format="Letter")
    pdf.set_auto_page_break(auto=True, margin=16)
    pdf.add_font("DejaVu", "", SANS)
    pdf.add_font("DejaVu", "B", SANS_BOLD)
    pdf.add_font("Mono", "", MONO)
    pdf.add_page()
    pdf.set_left_margin(14)
    pdf.set_right_margin(14)

    lines = SOURCE.read_text().splitlines()
    index = 0
    while index < len(lines):
        line = lines[index]
        if not line.strip():
            index += 1
            continue
        if line.startswith("## "):
            pdf.add_page()
            pdf.set_font("DejaVu", "B", size=14)
            pdf.multi_cell(pdf.epw, 7, line[3:].strip())
            pdf.ln(1)
            index += 1
            continue
        if line.startswith("# "):
            pdf.set_font("DejaVu", "B", size=16)
            pdf.multi_cell(pdf.epw, 8, line[2:].strip())
            pdf.ln(2)
            index += 1
            continue
        if line.startswith("### "):
            pdf.set_font("DejaVu", "B", size=12)
            pdf.multi_cell(pdf.epw, 6, line[4:].strip())
            pdf.ln(1)
            index += 1
            continue
        if line.startswith("```"):
            block = []
            index += 1
            while index < len(lines) and not lines[index].startswith("```"):
                block.append(lines[index])
                index += 1
            index += 1
            draw_code(pdf, block)
            continue
        if line.startswith("|"):
            block = []
            while index < len(lines) and lines[index].startswith("|"):
                block.append(lines[index])
                index += 1
            draw_table(pdf, parse_table(block))
            continue
        paragraph = [line.strip()]
        index += 1
        while index < len(lines) and lines[index].strip() and not lines[index].startswith(("#", "|", "```")):
            paragraph.append(lines[index].strip())
            index += 1
        write_inline(pdf, " ".join(paragraph))
    pdf.output(OUTPUT)


if __name__ == "__main__":
    render()
