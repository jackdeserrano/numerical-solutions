import os
from operations import *

THIS_PATH = os.path.dirname(os.path.realpath(__file__))
TEMPLATE_PATH = os.path.join(THIS_PATH, "template.tex")
PTEX_PATH = os.path.realpath("pdflatex")

if not os.path.exists(PTEX_PATH):
    if os.path.exists("/Library/TeX/texbin/pdflatex"):
        PTEX_PATH = "/Library/TeX/texbin/pdflatex"
        
    else:
        raise ImportError("pdflatex not found")
        
def make_file(USE_TEX, FILE_NAME, TEXT):
    
    FILE = open(TEMPLATE_PATH, "r").read()
    if USE_TEX:
        FILE = FILE.replace("usertext",
                            "\\begin{align*}\nusertext\n\\end{align*}")
        
    FILE = FILE.replace("usertext", TEXT)
    TEX_FILE = open(f"{FILE_NAME}.tex", "w+")
    TEX_FILE.write(FILE)
    TEX_FILE.close()
    
    FILE_PATH = os.path.join(THIS_PATH, f"{FILE_NAME}.tex")
    os.system(f"{PTEX_PATH} {FILE_PATH}")
    FILE_PATH = os.path.join(THIS_PATH, f"{FILE_NAME}.pdf")
    os.system(f"open {FILE_PATH}")
    
    print(os.system(f"open {FILE_PATH}"))
