import os
from function.convert_image_to_base64 import convert_image_to_base64

# zip 파일로부터 html, image 가져옴
def extract_files_from_zip(notion_dir):
    html_file = None
    image_files = {}
    
    for root, dirs, files in os.walk(notion_dir):
        # HTML 파일 찾기 
        if not html_file:
            html_file = next((os.path.join(root, f) for f in files if f.endswith('.html')), None)
        
        # 이미지 파일 찾아서 base64로 변환
        for f in files:
            if f.endswith(('.png', '.jpg', '.jpeg', '.webp', '.svg')):
                filename = os.path.basename(f)
                image_path = os.path.join(root, f)
                image_files[filename] = convert_image_to_base64(image_path)

    return html_file, image_files
