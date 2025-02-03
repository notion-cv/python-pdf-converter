from weasyprint import HTML, CSS

# link가 살아있는 pdf 만들기
# issue) 링크 위치의 문제
def convert_html_to_pdf(htmlPath, pdfSavePath):
    HTML(htmlPath).write_pdf(
        pdfSavePath,           
        presentational_hints=True, 
        optimize_images=False
    )
    