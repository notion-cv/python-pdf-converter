import os
from pdf2image import convert_from_path
from weasyprint import HTML
from PyPDF2 import PdfMerger
import pytesseract



def convert_html_to_ocr_pdf(htmlPath, pdfSavePath):
    # 임시 저장 pdf
    PATH_TEMP_PDF = 'tmp/image_pdf.pdf'

    # 1. html to pdf
    HTML(htmlPath).write_pdf(PATH_TEMP_PDF, resolution=300)

    # 2. pdf를 이미지로 저장
    pages = convert_from_path(PATH_TEMP_PDF, 300)

    # 3. OCR 처리 가능한 PDF 로 생성
    page_files = []  # 생성된 페이지 파일들의 리스트를 저장 

    for i, page in enumerate(pages):
        output_file = f'tmp/page_{i}.pdf'
        page_files.append(output_file)
        
        # OCR 처리 - 한글과 영어 모두 처리
        text = pytesseract.image_to_pdf_or_hocr(
            page, 
            extension='pdf',
            lang='kor+eng'  # 한글과 영어 모두 인식
        )
        
        # 새 PDF 생성
        with open(output_file, 'wb') as f:
            f.write(text)

    # 4. 모든 페이지 병합
    merger = PdfMerger()

    for pdf_file in page_files:
        merger.append(pdf_file)

    merger.write(pdfSavePath)
    merger.close()

    # temp pdf 제거
    os.remove(PATH_TEMP_PDF)

