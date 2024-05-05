from PyPDF2 import PdfReader
import os


def read_pdf_pages(pdf_path):
    
	with open(pdf_path, 'rb') as f:
		pdf = PdfReader(f)
	
		pages = []
		metadatas = []
		

		for i in range(len(pdf.pages)):
			pages.append(pdf.pages[i].extract_text())
			metadatas.append({"source" : pdf_path, "page" : (i + 1)})
		
		return pages, metadatas
	

def read_pdfdir_generator(dir_path):

	pdfs_in_dir = [os.path.join(dir_path, filename) for filename in os.listdir(dir_path) 
					if filename.endswith(".pdf")]
	
	for pdf_path in pdfs_in_dir:
		pages, metadata = read_pdf_pages(pdf_path)

		yield (pages, metadata)


red_gen = read_pdfdir_generator("./books")

for (pages, metadata) in red_gen:
	print(metadata)


