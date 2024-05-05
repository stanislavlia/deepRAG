from PyPDF2 import PdfReader

def extract_information(pdf_path):
    with open(pdf_path, 'rb') as f:
        pdf = PdfReader(f)
        print(pdf.pages[5].extract_text())
        metada = pdf.metadata

    print(metada)
    return metada


def read_pdf_pages(pdf_path):
    
	with open(pdf_path, 'rb') as f:
		pdf = PdfReader(f)
	
		pages = []
		metadatas = []
		

		for i in range(len(pdf.pages)):
			pages.append(pdf.pages[i].extract_text())
			metadatas.append({"source" : pdf_path, "page" : (i + 1)})
		
		return pages, metadatas


pages, metadatas = read_pdf_pages("Netpractice.pdf")
        
print(pages)
print("\n\n", metadatas)