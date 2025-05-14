from utils import segment_text_file, extract_info_from_segmented_text
from utils_image import extract_info
from db import insert_into_postgresql

if __name__ == "__main__":
    
    FILE_PATH = "input/jigyasaYadav_1++.pdf"

    text, has_image = segment_text_file(FILE_PATH)

    text, has_image = segment_text_file(FILE_PATH)

    if has_image:
        info = extract_info(text, FILE_PATH)
    else:
        info = extract_info_from_segmented_text(text, FILE_PATH)
        
    insert_into_postgresql(info)