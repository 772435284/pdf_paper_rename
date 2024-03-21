import spacy
import fitz  # PyMuPDF
import os
import shutil  # 用于文件移动

nlp = spacy.load("en_core_web_sm")

def extract_text_from_first_page(pdf_path):
    doc = fitz.open(pdf_path)
    first_page_text = doc[0].get_text()
    return first_page_text

def find_title_with_spacy(text):
    doc = nlp(text)
    first_sentence = next(doc.sents, None)
    if first_sentence:
        title = first_sentence.text.replace('\n', ' ')
        return title
    else:
        return "Title Not Found"

def clean_title(text):
    doc = nlp(text)
    exclude_entities = []
    for ent in doc.ents:
        if ent.label_ in ["PERSON", "ORG"]:
            exclude_entities.append(ent.text)
    
    cleaned_title = text
    for entity in exclude_entities:
        cleaned_title = cleaned_title.replace(entity, "")
    for ch in ['<', '>', ':', '"', '/', '\\', '|', '?', '*',',','{','}','.','(',')','-','@','ﬁ']:
        cleaned_title = cleaned_title.replace(ch, '')
    return cleaned_title.split('\n', 1)[0].strip()

def rename_pdf(pdf_path, title, output_folder_path):
    # 限制文件名长度，假设最大长度为100个字符
    # Windows整个路径长度限制为260字符，需要考虑到路径的部分
    max_length = 100
    sanitized_title = (title[:max_length] if len(title) > max_length else title) + ".pdf"
    new_filename = "".join([c for c in sanitized_title if c.isalnum() or c in ' .-_'])
    new_path = os.path.join(output_folder_path, new_filename)
    try:
        shutil.copy2(pdf_path, new_path)  # 使用shutil.move代替os.rename，以允许跨文件夹移动文件
        print(f"File moved and renamed to: {new_path}")
    except Exception as e:
        print(f"Error moving and renaming file {pdf_path}: {e}")

pdf_folder_path = "./papers"
output_folder_path = "./renamed_papers"  # 指定输出文件夹

# 如果输出文件夹不存在，则创建它
if not os.path.exists(output_folder_path):
    os.makedirs(output_folder_path)

for file in os.listdir(pdf_folder_path):
    if file.endswith(".pdf"):
        pdf_path = os.path.join(pdf_folder_path, file)
        text = extract_text_from_first_page(pdf_path)
        title = find_title_with_spacy(text)
        title = clean_title(title)
        rename_pdf(pdf_path, title, output_folder_path)