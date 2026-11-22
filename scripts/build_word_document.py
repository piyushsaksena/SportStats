import os
import re
import zipfile
import xml.sax.saxutils as saxutils
from PIL import Image

def escape(text):
    return saxutils.escape(text)

def create_docx(markdown_path, output_docx_path):
    with open(markdown_path, 'r', encoding='utf-8') as f:
        md_text = f.read()

    # Image mapping
    # Maps figure path in markdown to media path in docx
    images = {}
    rel_id_counter = 10
    
    # Pre-scan for images
    img_pattern = r'!\[([^\]]*)\]\(([^)]+)\)'
    for m in re.finditer(img_pattern, md_text):
        caption = m.group(1)
        src = m.group(2)
        # normalize path
        clean_src = src.replace('figures/', 'reports/figures/').replace('\\', '/')
        if clean_src not in images and os.path.exists(clean_src):
            images[clean_src] = {
                'rId': f'rIdImg{len(images)+1}',
                'target': f'media/image{len(images)+1}.png',
                'caption': caption,
                'path': clean_src
            }
        elif clean_src not in images and os.path.exists(src):
            images[src] = {
                'rId': f'rIdImg{len(images)+1}',
                'target': f'media/image{len(images)+1}.png',
                'caption': caption,
                'path': src
            }

    print(f"Discovered {len(images)} images to embed.")

    # Build document.xml body
    body_xml = []
    
    # Split markdown by sections / lines
    lines = md_text.splitlines()
    i = 0
    in_table = False
    table_rows = []

    def flush_table():
        nonlocal table_rows
        if not table_rows:
            return ""
        
        tbl_xml = ['<w:tbl>',
                   '<w:tblPr>',
                   '<w:tblW w:w="0" w:type="auto"/>',
                   '<w:jc w:val="center"/>',
                   '<w:tblBorders>',
                   '  <w:top w:val="single" w:sz="6" w:space="0" w:color="1B2432"/>',
                   '  <w:bottom w:val="single" w:sz="6" w:space="0" w:color="1B2432"/>',
                   '  <w:insideH w:val="single" w:sz="4" w:space="0" w:color="DCE7F3"/>',
                   '  <w:left w:val="none"/>',
                   '  <w:right w:val="none"/>',
                   '  <w:insideV w:val="none"/>',
                   '</w:tblBorders>',
                   '</w:tblPr>']
        
        for r_idx, row in enumerate(table_rows):
            tbl_xml.append('<w:tr>')
            is_header = (r_idx == 0)
            for c_idx, cell in enumerate(row):
                bg_xml = '<w:shd w:val="clear" w:color="auto" w:fill="F3F8FE"/>' if is_header else ''
                tbl_xml.append(f'<w:tc><w:tcPr>{bg_xml}<w:tcMar><w:top w:w="120" w:type="dxa"/><w:bottom w:w="120" w:type="dxa"/><w:left w:w="160" w:type="dxa"/><w:right w:w="160" w:type="dxa"/></w:tcMar></w:tcPr>')
                tbl_xml.append(f'<w:p><w:pPr><w:spacing w:after="40" w:line="240" w:lineRule="auto"/></w:pPr><w:r><w:rPr><w:rFonts w:ascii="Calibri" w:hAnsi="Calibri"/>{"<w:b/>" if is_header else ""}<w:sz w:val="18"/><w:szCs w:val="18"/><w:color w:val="1B2432"/></w:rPr><w:t>{escape(cell)}</w:t></w:r></w:p></w:tc>')
            tbl_xml.append('</w:tr>')
            
        tbl_xml.append('</w:tbl>')
        table_rows = []
        return "".join(tbl_xml)

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Check for page break comment
        if '<!-- PAGE BREAK -->' in line:
            if in_table:
                body_xml.append(flush_table())
                in_table = False
            body_xml.append('<w:p><w:r><w:br w:type="page"/></w:r></w:p>')
            i += 1
            continue

        # Check for horizontal rule
        if stripped in ('---', '***', '___'):
            if in_table:
                body_xml.append(flush_table())
                in_table = False
            body_xml.append('<w:p><w:pPr><w:pBdr><w:bottom w:val="single" w:sz="6" w:space="4" w:color="DCE7F3"/></w:pBdr><w:spacing w:after="160"/></w:pPr></w:p>')
            i += 1
            continue

        # Table row
        if stripped.startswith('|') and stripped.endswith('|'):
            # check if it's separator line | :--- | :--- |
            if re.match(r'^\|[\s\-:]+(\|[\s\-:]+)+\|$', stripped):
                i += 1
                continue
            cells = [c.strip() for c in stripped.strip('|').split('|')]
            in_table = True
            table_rows.append(cells)
            i += 1
            continue
        elif in_table:
            body_xml.append(flush_table())
            in_table = False

        # Image
        img_match = re.search(img_pattern, stripped)
        if img_match:
            caption = img_match.group(1)
            src = img_match.group(2)
            clean_src = src.replace('figures/', 'reports/figures/').replace('\\', '/')
            img_info = images.get(clean_src) or images.get(src)
            if img_info and os.path.exists(img_info['path']):
                # Read image dimensions
                try:
                    with Image.open(img_info['path']) as img:
                        w, h = img.size
                    max_width_emu = 5486400  # 6.0 inches
                    max_height_emu = 3657600 # 4.0 inches
                    # calculate proportional EMU
                    aspect = h / w
                    cx = max_width_emu
                    cy = int(cx * aspect)
                    if cy > max_height_emu:
                        cy = max_height_emu
                        cx = int(cy / aspect)
                except Exception:
                    cx = 5029200
                    cy = 3200400

                rId = img_info['rId']
                drawing_xml = f'''<w:p><w:pPr><w:jc w:val="center"/><w:spacing w:before="120" w:after="80"/></w:pPr>
                  <w:r>
                    <w:drawing>
                      <wp:inline distT="0" distB="0" distL="0" distR="0" xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing">
                        <wp:extent cx="{cx}" cy="{cy}"/>
                        <wp:docPr id="{rel_id_counter}" name="Picture"/>
                        <a:graphic xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">
                          <a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture">
                            <pic:pic xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture">
                              <pic:nvPicPr>
                                <pic:cNvPr id="0" name="Picture"/>
                                <pic:cNvPicPr/>
                              </pic:nvPicPr>
                              <pic:blipFill>
                                <a:blip r:embed="{rId}" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"/>
                                <a:stretch><a:fillRect/></a:stretch>
                              </pic:blipFill>
                              <pic:spPr>
                                <a:xfrm><a:off x="0" y="0"/><a:ext cx="{cx}" cy="{cy}"/></a:xfrm>
                                <a:prstGeom prst="rect"><a:avLst/></a:prstGeom>
                              </pic:spPr>
                            </pic:pic>
                          </a:graphicData>
                        </a:graphic>
                      </wp:inline>
                    </w:drawing>
                  </w:r>
                </w:p>'''
                rel_id_counter += 1
                body_xml.append(drawing_xml)
            i += 1
            continue

        # Figure Caption line (e.g. *Figure 1: ...*)
        if stripped.startswith('*Figure ') and stripped.endswith('*'):
            cap_text = stripped.strip('*')
            body_xml.append(f'<w:p><w:pPr><w:jc w:val="center"/><w:spacing w:after="160"/></w:pPr><w:r><w:rPr><w:rFonts w:ascii="Calibri" w:hAnsi="Calibri"/><w:i/><w:sz w:val="19"/><w:szCs w:val="19"/><w:color w:val="5A6B82"/></w:rPr><w:t>{escape(cap_text)}</w:t></w:r></w:p>')
            i += 1
            continue

        # Heading 1 (# ...)
        if stripped.startswith('# '):
            h_text = stripped[2:].strip()
            # If it's a chapter heading, prepend a page break unless it's the very first title
            page_br = '<w:r><w:br w:type="page"/></w:r>' if ('Chapter ' in h_text and len(body_xml) > 2) else ''
            body_xml.append(f'<w:p><w:pPr><w:pStyle w:val="Heading1"/><w:spacing w:before="240" w:after="140"/></w:pPr>{page_br}<w:r><w:rPr><w:rFonts w:ascii="Calibri" w:hAnsi="Calibri"/><w:b/><w:sz w:val="36"/><w:szCs w:val="36"/><w:color w:val="1B2432"/></w:rPr><w:t>{escape(h_text)}</w:t></w:r></w:p>')
            i += 1
            continue

        # Heading 2 (## ...)
        if stripped.startswith('## '):
            h_text = stripped[3:].strip()
            body_xml.append(f'<w:p><w:pPr><w:pStyle w:val="Heading2"/><w:spacing w:before="200" w:after="100"/></w:pPr><w:r><w:rPr><w:rFonts w:ascii="Calibri" w:hAnsi="Calibri"/><w:b/><w:sz w:val="28"/><w:szCs w:val="28"/><w:color w:val="1B2432"/></w:rPr><w:t>{escape(h_text)}</w:t></w:r></w:p>')
            i += 1
            continue

        # Heading 3 (### ...)
        if stripped.startswith('### '):
            h_text = stripped[4:].strip()
            body_xml.append(f'<w:p><w:pPr><w:pStyle w:val="Heading3"/><w:spacing w:before="160" w:after="80"/></w:pPr><w:r><w:rPr><w:rFonts w:ascii="Calibri" w:hAnsi="Calibri"/><w:b/><w:sz w:val="24"/><w:szCs w:val="24"/><w:color w:val="1B2432"/></w:rPr><w:t>{escape(h_text)}</w:t></w:r></w:p>')
            i += 1
            continue

        # Code block (``` ... ```)
        if stripped.startswith('```'):
            code_lines = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith('```'):
                code_lines.append(lines[i])
                i += 1
            i += 1
            code_text = "\n".join(code_lines)
            body_xml.append(f'<w:p><w:pPr><w:shd w:val="clear" w:color="auto" w:fill="F3F8FE"/><w:pBdr><w:left w:val="single" w:sz="12" w:space="6" w:color="1B2432"/><w:top w:val="single" w:sz="4" w:space="4" w:color="DCE7F3"/><w:bottom w:val="single" w:sz="4" w:space="4" w:color="DCE7F3"/><w:right w:val="single" w:sz="4" w:space="4" w:color="DCE7F3"/></w:pBdr><w:spacing w:before="100" w:after="120" w:line="240" w:lineRule="auto"/></w:pPr><w:r><w:rPr><w:rFonts w:ascii="Consolas" w:hAnsi="Consolas"/><w:sz w:val="18"/><w:szCs w:val="18"/><w:color w:val="1B2432"/></w:rPr><w:t xml:space="preserve">{escape(code_text)}</w:t></w:r></w:p>')
            continue

        # Bullet point (* ... or - ...)
        if re.match(r'^[\*\-]\s+', stripped):
            bullet_text = re.sub(r'^[\*\-]\s+', '', stripped)
            runs_xml = parse_formatted_runs(bullet_text)
            body_xml.append(f'<w:p><w:pPr><w:ind w:left="360" w:hanging="180"/><w:spacing w:after="80" w:line="276" w:lineRule="auto"/></w:pPr><w:r><w:rPr><w:rFonts w:ascii="Calibri" w:hAnsi="Calibri"/><w:b/><w:sz w:val="24"/><w:szCs w:val="24"/><w:color w:val="1B2432"/></w:rPr><w:t>• </w:t></w:r>{runs_xml}</w:p>')
            i += 1
            continue

        # Numbered list (1. ...)
        if re.match(r'^\d+\.\s+', stripped):
            num_prefix = re.match(r'^\d+\.\s+', stripped).group(0)
            list_text = stripped[len(num_prefix):]
            runs_xml = parse_formatted_runs(list_text)
            body_xml.append(f'<w:p><w:pPr><w:ind w:left="420" w:hanging="260"/><w:spacing w:after="80" w:line="276" w:lineRule="auto"/></w:pPr><w:r><w:rPr><w:rFonts w:ascii="Calibri" w:hAnsi="Calibri"/><w:b/><w:sz w:val="24"/><w:szCs w:val="24"/><w:color w:val="1B2432"/></w:rPr><w:t>{escape(num_prefix)}</w:t></w:r>{runs_xml}</w:p>')
            i += 1
            continue

        # Math block ($$ ... $$)
        if stripped.startswith('$$') and stripped.endswith('$$'):
            math_text = stripped.strip('$')
            body_xml.append(f'<w:p><w:pPr><w:jc w:val="center"/><w:shd w:val="clear" w:color="auto" w:fill="F3F8FE"/><w:spacing w:before="120" w:after="120"/></w:pPr><w:r><w:rPr><w:rFonts w:ascii="Cambria Math" w:hAnsi="Cambria Math"/><w:i/><w:b/><w:sz w:val="24"/><w:szCs w:val="24"/><w:color w:val="1B2432"/></w:rPr><w:t>{escape(math_text)}</w:t></w:r></w:p>')
            i += 1
            continue

        # Normal paragraph
        if stripped:
            runs_xml = parse_formatted_runs(stripped)
            body_xml.append(f'<w:p><w:pPr><w:spacing w:after="120" w:line="276" w:lineRule="auto"/></w:pPr>{runs_xml}</w:p>')
        else:
            # Blank line
            pass
        i += 1

    if in_table:
        body_xml.append(flush_table())

    # Section properties: 1 inch (1440 dxa) margins all around
    body_xml.append('''<w:sectPr>
      <w:pgSz w:w="12240" w:h="15840"/>
      <w:pgMar w:top="1440" w:right="1440" w:bottom="1440" w:left="1440" w:header="720" w:footer="720" w:gutter="0"/>
      <w:cols w:space="720"/>
      <w:docGrid w:linePitch="360"/>
    </w:sectPr>''')

    full_document_xml = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n' + \
        '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math" xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing" xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture">\n' + \
        '<w:body>\n' + "".join(body_xml) + '\n</w:body>\n</w:document>'

    # document.xml.rels
    rels_xml = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
                '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">',
                '  <Relationship Id="rIdStyles" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>',
                '  <Relationship Id="rIdSettings" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/settings" Target="settings.xml"/>']
    
    for img_info in images.values():
        rels_xml.append(f'  <Relationship Id="{img_info["rId"]}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="{img_info["target"]}"/>')
    rels_xml.append('</Relationships>')
    full_doc_rels_xml = "\n".join(rels_xml)

    # Content_Types.xml
    content_types = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
                     '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">',
                     '  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>',
                     '  <Default Extension="xml" ContentType="application/xml"/>',
                     '  <Default Extension="png" ContentType="image/png"/>',
                     '  <Default Extension="jpeg" ContentType="image/jpeg"/>',
                     '  <Default Extension="jpg" ContentType="image/jpeg"/>',
                     '  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>',
                     '  <Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>',
                     '  <Override PartName="/word/settings.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.settings+xml"/>',
                     '</Types>']
    full_content_types_xml = "\n".join(content_types)

    # _rels/.rels
    root_rels = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
                 '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">',
                 '  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>',
                 '</Relationships>']
    full_root_rels_xml = "\n".join(root_rels)

    # styles.xml (Default 12pt Calibri, 1.15 line spacing, 1B2432 text color)
    styles_xml = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:docDefaults>
    <w:rPrDefault>
      <w:rPr>
        <w:rFonts w:ascii="Calibri" w:hAnsi="Calibri" w:eastAsia="Calibri" w:cs="Calibri"/>
        <w:sz w:val="24"/>
        <w:szCs w:val="24"/>
        <w:color w:val="1B2432"/>
        <w:lang w:val="en-US"/>
      </w:rPr>
    </w:rPrDefault>
    <w:pPrDefault>
      <w:pPr>
        <w:spacing w:line="276" w:lineRule="auto" w:after="120"/>
      </w:pPr>
    </w:pPrDefault>
  </w:docDefaults>
  <w:style w:type="paragraph" w:default="1" w:styleId="Normal">
    <w:name w:val="Normal"/>
    <w:qFormat/>
  </w:style>
  <w:style w:type="paragraph" w:styleId="Heading1">
    <w:name w:val="heading 1"/>
    <w:basedOn w:val="Normal"/>
    <w:next w:val="Normal"/>
    <w:qFormat/>
    <w:pPr>
      <w:spacing w:before="280" w:after="140"/>
    </w:pPr>
    <w:rPr>
      <w:b/>
      <w:sz w:val="36"/>
      <w:szCs w:val="36"/>
      <w:color w:val="1B2432"/>
    </w:rPr>
  </w:style>
  <w:style w:type="paragraph" w:styleId="Heading2">
    <w:name w:val="heading 2"/>
    <w:basedOn w:val="Normal"/>
    <w:next w:val="Normal"/>
    <w:qFormat/>
    <w:pPr>
      <w:spacing w:before="220" w:after="100"/>
    </w:pPr>
    <w:rPr>
      <w:b/>
      <w:sz w:val="28"/>
      <w:szCs w:val="28"/>
      <w:color w:val="1B2432"/>
    </w:rPr>
  </w:style>
  <w:style w:type="paragraph" w:styleId="Heading3">
    <w:name w:val="heading 3"/>
    <w:basedOn w:val="Normal"/>
    <w:next w:val="Normal"/>
    <w:qFormat/>
    <w:pPr>
      <w:spacing w:before="160" w:after="80"/>
    </w:pPr>
    <w:rPr>
      <w:b/>
      <w:sz w:val="24"/>
      <w:szCs w:val="24"/>
      <w:color w:val="1B2432"/>
    </w:rPr>
  </w:style>
</w:styles>'''

    # settings.xml
    settings_xml = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:settings xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:defaultTabStop w:val="720"/>
</w:settings>'''

    # Write out ZIP archive
    with zipfile.ZipFile(output_docx_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.writestr('[Content_Types].xml', full_content_types_xml)
        zf.writestr('_rels/.rels', full_root_rels_xml)
        zf.writestr('word/_rels/document.xml.rels', full_doc_rels_xml)
        zf.writestr('word/document.xml', full_document_xml)
        zf.writestr('word/styles.xml', styles_xml)
        zf.writestr('word/settings.xml', settings_xml)
        
        # Add images
        for img_info in images.values():
            if os.path.exists(img_info['path']):
                with open(img_info['path'], 'rb') as img_f:
                    zf.writestr(f"word/{img_info['target']}", img_f.read())
                    print(f"Archived image: {img_info['target']} ({os.path.getsize(img_info['path'])} bytes)")

    print(f"Successfully compiled {output_docx_path} ({os.path.getsize(output_docx_path)} bytes)!")

def parse_formatted_runs(text):
    # Parses bold **text**, italics *text*, and plain text into OpenXML runs
    tokens = re.split(r'(\*\*[^*]+\*\*|\*[^*]+\*|`[^`]+`)', text)
    runs_xml = []
    for tok in tokens:
        if not tok:
            continue
        if tok.startswith('**') and tok.endswith('**'):
            inner = tok[2:-2]
            runs_xml.append(f'<w:r><w:rPr><w:rFonts w:ascii="Calibri" w:hAnsi="Calibri"/><w:b/><w:sz w:val="24"/><w:szCs w:val="24"/><w:color w:val="1B2432"/></w:rPr><w:t xml:space="preserve">{escape(inner)}</w:t></w:r>')
        elif tok.startswith('*') and tok.endswith('*'):
            inner = tok[1:-1]
            runs_xml.append(f'<w:r><w:rPr><w:rFonts w:ascii="Calibri" w:hAnsi="Calibri"/><w:i/><w:sz w:val="24"/><w:szCs w:val="24"/><w:color w:val="1B2432"/></w:rPr><w:t xml:space="preserve">{escape(inner)}</w:t></w:r>')
        elif tok.startswith('`') and tok.endswith('`'):
            inner = tok[1:-1]
            runs_xml.append(f'<w:r><w:rPr><w:rFonts w:ascii="Consolas" w:hAnsi="Consolas"/><w:sz w:val="20"/><w:szCs w:val="20"/><w:color w:val="1B2432"/></w:rPr><w:t xml:space="preserve">{escape(inner)}</w:t></w:r>')
        else:
            runs_xml.append(f'<w:r><w:rPr><w:rFonts w:ascii="Calibri" w:hAnsi="Calibri"/><w:sz w:val="24"/><w:szCs w:val="24"/><w:color w:val="1B2432"/></w:rPr><w:t xml:space="preserve">{escape(tok)}</w:t></w:r>')
    return "".join(runs_xml)

if __name__ == '__main__':
    md_in = 'reports/SPORTSTATS_PROJECT_REPORT.md'
    docx_out = 'reports/SPORTSTATS_PROJECT_REPORT.docx'
    create_docx(md_in, docx_out)
