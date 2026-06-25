from docx.text.paragraph import Paragraph
from docx.shared import Pt
from docx.oxml.ns import qn
from docx.oxml.shared import OxmlElement

def add_bottom_border(paragraph: Paragraph, style="single", sz="12", space="1", color="1E3A8A"):
  pPr = paragraph._p.get_or_add_pPr()
  
  pBdr = pPr.find(qn('w:pBdr'))
  if pBdr is None:
      pBdr = OxmlElement('w:pBdr')
      pPr.append(pBdr)
  
  bottom_border = OxmlElement('w:bottom')
  bottom_border.set(qn('w:val'), style)
  bottom_border.set(qn('w:sz'), str(sz))
  bottom_border.set(qn('w:space'), str(space))
  bottom_border.set(qn('w:color'), color)

  pPr.append(bottom_border)

def add_top_border(paragraph: Paragraph, style="single", sz="12", space="1", color="1E3A8A"):
  pPr = paragraph._p.get_or_add_pPr()
  
  pBdr = pPr.find(qn('w:pBdr'))
  if pBdr is None:
      pBdr = OxmlElement('w:pBdr')
      pPr.append(pBdr)
  
  top_border = OxmlElement('w:top')
  top_border.set(qn('w:val'), style)
  top_border.set(qn('w:sz'), str(sz))
  top_border.set(qn('w:space'), str(space))
  top_border.set(qn('w:color'), color)

  pPr.append(top_border)

def add_left_border(paragraph: Paragraph, style="single", sz="24", space="8", color="1E3A8A"):
  pPr = paragraph._p.get_or_add_pPr()
  
  pBdr = pPr.find(qn('w:pBdr'))
  if pBdr is None:
      pBdr = OxmlElement('w:pBdr')
      pPr.append(pBdr)
  
  left_border = OxmlElement('w:left')
  left_border.set(qn('w:val'), style)
  left_border.set(qn('w:sz'), str(sz))
  left_border.set(qn('w:space'), str(space))
  left_border.set(qn('w:color'), color)
  

  pPr.append(left_border)
  

def add_field_element(run, field_name):
    """Helper function to inject an OpenXML field element (PAGE or NUMPAGES) into a run."""
    # Start the field code block
    fldChar1 = OxmlElement('w:fldChar')
    fldChar1.set(qn('w:fldCharType'), 'begin')
    
    # Define the specific instruction command (e.g., PAGE)
    instrText = OxmlElement('w:instrText')
    instrText.set(qn('xml:space'), 'preserve')
    instrText.text = field_name
    
    # End the field code block
    fldChar2 = OxmlElement('w:fldChar')
    fldChar2.set(qn('w:fldCharType'), 'end')
    
    # Append the OpenXML XML markers directly to the run
    run._r.append(fldChar1)
    run._r.append(instrText)
    run._r.append(fldChar2)