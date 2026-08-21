"""
SHACK ENTERTAINMENT — shack_docs_pdf.py
[DOCS] Render every .md in Shack_Project\Docs to PDF (Arial)
into Desktop\ALLM - Docs & Manuals. Bit-for-bit identical.
"""
import os
from fpdf import FPDF

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
SRC = os.path.join(project_root, 'Docs')
OUT = os.path.join(os.path.expanduser('~'), 'Desktop', 'ALLM - Docs & Manuals')
os.makedirs(SRC, exist_ok=True)
os.makedirs(OUT, exist_ok=True)

def render(md_path, out_path):
    text = open(md_path, encoding='utf-8').read()
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=18)
    pdf.add_page()
    try:
        pdf.add_font('Arial', '', r'C:\Windows\Fonts\arial.ttf')
        pdf.add_font('Arial', 'B', r'C:\Windows\Fonts\arialbd.ttf')
        pdf.add_font('Arial', 'I', r'C:\Windows\Fonts\ariali.ttf')
        fam = 'Arial'
    except Exception:
        fam = 'Helvetica'
    for line in text.splitlines():
        s = line.rstrip()
        if s.startswith('# '):
            pdf.set_font(fam, 'B', 18)
            pdf.ln(2); pdf.multi_cell(0, 9, s[2:].strip()); pdf.ln(3)
        elif s.startswith('## '):
            pdf.set_font(fam, 'B', 14)
            pdf.ln(2); pdf.multi_cell(0, 8, s[3:].strip()); pdf.ln(2)
        elif s.startswith('### '):
            pdf.set_font(fam, 'B', 12)
            pdf.ln(1); pdf.multi_cell(0, 7, s[4:].strip()); pdf.ln(1)
        elif s.strip() == '---':
            pdf.ln(2)
        elif s.strip():
            pdf.set_font(fam, '', 11)
            pdf.multi_cell(0, 6, s)
            pdf.ln(1.2)
        else:
            pdf.ln(2)
    pdf.output(out_path)

def main():
    n = 0
    for f in sorted(os.listdir(SRC)):
        if f.lower().endswith('.md'):
            render(os.path.join(SRC, f), os.path.join(OUT, f[:-3] + '.pdf'))
            n += 1
            print('rendered', f)
    print(f'{n} PDF(s) in', OUT)

if __name__ == '__main__':
    main()