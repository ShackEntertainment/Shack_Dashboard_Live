"""
SHACK ENTERTAINMENT — shack_equipment_view.py
[VIEW] Regenerates Data\equipment_view.ods from Data\equipment.csv:
dressed column widths, wrapped text, styled header. One command.
"""
import os
import csv
from odf import opendocument, table, style, text

script_dir = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(os.path.dirname(script_dir), 'Data')
CSV = os.path.join(DATA, 'equipment.csv')
ODS = os.path.join(DATA, 'equipment_view.ods')

WIDTHS = ['2cm', '8cm', '2.5cm', '4.5cm', '2cm', '2cm',
          '2.8cm', '2.2cm', '6cm', '6cm']

def main():
    doc = opendocument.OpenDocumentSpreadsheet()

    hdr = style.Style(name='hdr', family='table-cell')
    hdr.addElement(style.TableCellProperties(backgroundcolor='#404040'))
    hdr.addElement(style.TextProperties(color='#ffffff',
                                        fontweight='bold'))
    doc.automaticstyles.addElement(hdr)

    body = style.Style(name='body', family='table-cell')
    body.addElement(style.TableCellProperties(verticalalign='top',
                                              wrapoption='wrap'))
    doc.automaticstyles.addElement(body)

    colstyles = []
    for i, w in enumerate(WIDTHS):
        cs = style.Style(name='col%d' % i, family='table-column')
        cs.addElement(style.TableColumnProperties(columnwidth=w))
        doc.automaticstyles.addElement(cs)
        colstyles.append(cs)

    with open(CSV, encoding='utf-8') as f:
        rows = list(csv.reader(f))

    t = table.Table(name='equipment')
    for cs in colstyles:
        t.addElement(table.TableColumn(stylename=cs))
    for r_i, row in enumerate(rows):
        tr = table.TableRow()
        st = hdr if r_i == 0 else body
        for val in (list(row) + [''] * 10)[:10]:
            c = table.TableCell(stylename=st, valuetype='string')
            c.addElement(text.P(text=val))
            tr.addElement(c)
        t.addElement(tr)
    doc.spreadsheet.addElement(t)
    doc.save(ODS)
    print('view rebuilt: %s (%d rows)' % (ODS, len(rows) - 1))

if __name__ == '__main__':
    main()