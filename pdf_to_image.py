import fitz  # PyMuPDF

doc = fitz.open("CVs/Can_Resume1.pdf")
for page_num in range(len(doc)):
    page = doc[page_num]
    pix = page.get_pixmap(dpi=300)
    pix.save(f"page_{page_num + 1}.png")


