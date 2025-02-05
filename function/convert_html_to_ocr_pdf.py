import os
from pdf2image import convert_from_path
from weasyprint import HTML
from PyPDF2 import PdfMerger
import pytesseract
import pymupdf # PyMuPDF

def convert_html_to_ocr_pdf(htmlPath, pdfSavePath):
    # 임시 저장 pdf
    TEMP_PDF_PATH = '/tmp/temp.pdf'
    MERGED_PDF_PATH = '/tmp/merged.pdf'

    # 1. html to pdf
    HTML(htmlPath).write_pdf(TEMP_PDF_PATH, resolution=300)

    # 2. 원본 PDF에서 링크 정보 추출
    doc = pymupdf.open(TEMP_PDF_PATH)
    all_links = []
    original_page_sizes = []
    
    for page_num, page in enumerate(doc):
        original_page_sizes.append(page.rect)
        links = page.get_links()
        cleaned_links = []
        for link in links:
            if 'uri' in link and 'from' in link:
                cleaned_links.append({
                    'link_info': link,
                    'page_num': int(page_num)  # 페이지 번호 저장
                })
        all_links.extend(cleaned_links)  # 리스트를 평탄화
    doc.close()
    

    # 3. pdf를 이미지로 저장
    pages = convert_from_path(TEMP_PDF_PATH, 300)

    # 4. OCR 처리 가능한 PDF 로 생성
    page_files = []  # 생성된 페이지 파일들의 리스트를 저장 

    for i, page in enumerate(pages):
        output_file = f'/tmp/page_{i}.pdf'
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

    # 5. 모든 페이지 병합
    merger = PdfMerger()

    for pdf_file in page_files:
        merger.append(pdf_file)

    merger.write(MERGED_PDF_PATH)
    merger.close()

    # 6. 링크 다시 추가
    final_doc = pymupdf.open(MERGED_PDF_PATH)

    for link in all_links:
        try:
            link_info = link['link_info']
            page = final_doc[link['page_num']]
            
            # 링크 위치 조정
            original_size = original_page_sizes[link['page_num']]
            scale_x = page.rect.width / original_size.width
            scale_y = page.rect.height / original_size.height

            rect = link_info['from']
            new_rect = pymupdf.Rect(
                rect.x0 * scale_x,
                rect.y0 * scale_y,
                rect.x1 * scale_x,
                rect.y1 * scale_y
            )

            # rect만 바꿔넣기
            link_info['from'] = new_rect
            page.insert_link(link_info)

        except Exception as e:
            print(f'error: {e}')
            continue
    
    # 7. 최종 PDF 저장
    final_doc.save(pdfSavePath)
    final_doc.close()

    # temp pdf 제거
    os.remove(TEMP_PDF_PATH)
    os.remove(MERGED_PDF_PATH)

