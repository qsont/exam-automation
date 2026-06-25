from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.text.paragraph import Paragraph
from docx.shared import Pt
from docx.oxml.ns import qn
from docx.oxml.shared import OxmlElement

def add_blue_bar(paragraph: Paragraph, point=36):
  tag = paragraph._p
  
  paragraph.paragraph_format.line_spacing = Pt(point)
  
  shading = OxmlElement('w:shd')
  shading.set(qn('w:val'), 'clear')
  shading.set(qn('w:color'), 'auto')
  shading.set(qn('w:fill'), '1E3A8A')

  tag.pPr.append(shading)

def white_space(doc, space_before=0, space_after=0, font_name='Times New Roman', font_size=10, isCentered=True):
  ws = doc.add_paragraph()
  ws.paragraph_format.space_before = Pt(space_before)
  ws.paragraph_format.space_after = Pt(space_after)
  ws.paragraph_format.line_spacing = 1
  
  ws.style.font.name = font_name
  ws.style.font.size = Pt(font_size)
  ws.alignment = WD_ALIGN_PARAGRAPH.CENTER if isCentered else WD_ALIGN_PARAGRAPH.LEFT