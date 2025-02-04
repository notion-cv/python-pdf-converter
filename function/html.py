def fix_double_br(soup):    
    # strong 태그 찾기
    strong_tags = soup.find_all('strong')
    
    for strong in strong_tags:
        # strong 태그 내의 연속된 br 태그 찾기
        br_tags = strong.find_all('br')
        
        for i in range(len(br_tags) - 1):
            next_element = br_tags[i].next_sibling
            if (isinstance(next_element, type(br_tags[i])) or
                (next_element and str(next_element).strip() == '<br/>')):
                next_element.decompose()
    
    return soup


def remove_resolution_attr(soup):
    '''image resolution 제거 '''
    # 모든 이미지 태그 찾기
    images = soup.find_all('img')
    
    for img in images:
        # resolution 속성이 있다면 제거
        if 'resolution' in img.attrs:
            print('resolution 제거')
            del img['resolution']
    
    return soup