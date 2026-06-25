from decouple import config
from pathlib import Path
from docx import Document
from docx.shared import Mm, Inches

from document.elements.page import create_cover_page, define_header_and_footer, create_question, create_mark_scheme

BASE_DIR = config("BASE_DIR")

def doc_builder(path: Path, properties: dict, withMarkScheme: bool = True):
  
  # Initialize document
  doc = Document()
  doc.sections[0].different_first_page_header_footer = True
  
  create_cover_page(doc, properties, withMarkScheme)
  define_header_and_footer(doc, properties)
  
  seen_prefixes = set()
  filtered_paths = []

  # Loop through files, sorted naturally by name
  for file_path in sorted(path.iterdir()):
    # path.stem gets 'q01_question' (ignores .txt, .docx, etc.)
    # [:3] grabs just the first 3 characters ('q01')
    prefix = file_path.stem[:3]  

    if prefix not in seen_prefixes:
        seen_prefixes.add(prefix)
        filtered_paths.append(file_path)

  # Enumerate gives you the 0, 1, 2 index automatically
  for i, file_path in enumerate(filtered_paths):
    create_question(doc, file_path, i + 1)
    if (withMarkScheme): create_mark_scheme(doc, file_path, i + 1)
  
  # Adjust page properties
  for section in doc.sections:
    # A4 size
    section.page_width = Mm(210)
    section.page_height = Mm(297)
    
    section.top_margin = Inches(1.0)
    section.bottom_margin = Inches(1.0)
    section.left_margin = Inches(1.0)
    section.right_margin = Inches(0.97)
    
  # 'paper_and_type' can be empty, so concat underscore if it exists
  paper_and_type = f"_{properties['paper_and_type']}_" if properties['paper_and_type'] else ""
    
  save_dir = (
    f'{BASE_DIR}\\{properties["subject"]}\\{properties["topic"]}\\{paper_and_type}\\{properties['subject']}_{properties['topic']}{paper_and_type}Topic Questions and Mark Scheme.docx' if withMarkScheme 
    else f'{BASE_DIR}\\{properties["subject"]}\\{properties["topic"]}\\{paper_and_type}\\{properties['subject']}_{properties['topic']}{paper_and_type}Questions Only.docx')
  
  if not Path(save_dir).parent.is_dir(): 
    print("Path doesn't exist. Creating directory...")
    Path(save_dir).parent.mkdir(parents=True, exist_ok=True) 
  
  doc.save(save_dir)
  print(f"✅ Document saved successfully at:\n\'{save_dir}\'")