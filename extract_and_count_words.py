import os
import fitz  # PyMuPDF
import re
import sys
from collections import Counter
from pathlib import Path
import frontmatter
import shutil

def extract_words_from_pdfs(directory_path, all_extracted_words):
    """
    Extracts specific English words from all PDFs in a directory based on a regex,
    formats them, counts them, and saves the results to Markdown files.
    """
    # Regex to find a word at the start of a line followed by a space and a square bracket.
    # e.g., "reassert [riːəˈsɜːt] ..."
    word_pattern = re.compile(r'^([a-zA-Z]+)\s+\[')

    print(f"Searching for PDF files in '{directory_path}'...")
    pdf_files_found = False
    for filename in os.listdir(directory_path):
        if filename.lower().endswith('.pdf'):
            pdf_files_found = True
            pdf_path = os.path.join(directory_path, filename)
            print(f"Processing {pdf_path}...")
            
            try:
                doc = fitz.open(pdf_path)
                if doc.is_encrypted:
                    print(f"Warning: {pdf_path} is encrypted. Skipping.")
                    continue

                for page in doc:
                    # Extract text line by line
                    text = page.get_text("text")
                    lines = text.split('\n')

                    for line in lines:
                        # Apply the regex to each line
                        match = word_pattern.search(line.strip())
                        if match:
                            print(line)
                            print("----------------------------------")
                            # The first group of the match is the word
                            word = match.group(1)
                            all_extracted_words.add(word)
                doc.close()
            except Exception as e:
                print(f"An error occurred while processing {pdf_path}: {e}", file=sys.stderr)

    if not pdf_files_found:
        print("No PDF files found in the specified directory.")
        return

    if not all_extracted_words:
        print("No matching words were found in any of the PDF files.")
        return

    # --- File 1: Write all extracted words formatted as [[word]] ---
    output_words_path = os.path.join(directory_path, "extracted_words.md")
    with open(output_words_path, 'w', encoding='utf-8') as f:
        f.write("# Extracted Words\n\n")
        for word in all_extracted_words:
            f.write(f"[[{word}]]\n")
    print(f"Successfully wrote all extracted words to {output_words_path}")

    # --- File 2: Write the statistics of the words ---
    output_stats_path = os.path.join(directory_path, "word_statistics.md")
    word_counts = Counter(all_extracted_words)
    with open(output_stats_path, 'w', encoding='utf-8') as f:
        f.write("# Word Statistics\n\n")
        f.write("| Word | Count |\n")
        f.write("|------|-------|\n")
        # Sort by most common
        for word, count in word_counts.most_common():
            f.write(f"| [[{word}]] | {count} |\n")
    print(f"Successfully wrote word statistics to {output_stats_path}")
    return all_extracted_words

def extract_words_style_2(directory_path, all_extracted_words):
    """
    Extracts English words from PDFs based on a second pattern:
    A line with a single word, followed by a line with "分析词义".
    """
    # Regex to find a line containing only a single English word.
    word_pattern = re.compile(r'^([a-zA-Z]+)$')

    print(f"\n--- Running New Extraction (Style 2) in '{directory_path}' ---")
    pdf_files_found = False
    for filename in os.listdir(directory_path):
        if filename.lower().endswith('.pdf'):
            pdf_files_found = True
            pdf_path = os.path.join(directory_path, filename)
            print(f"Processing {pdf_path} for Style 2...")
            
            try:
                doc = fitz.open(pdf_path)
                if doc.is_encrypted:
                    print(f"Warning: {pdf_path} is encrypted. Skipping.")
                    continue

                for page in doc:
                    text = page.get_text("text")
                    lines = text.split('\n')
                    # Iterate through lines, stopping one before the end
                    for i in range(len(lines) - 1):
                        current_line = lines[i].strip()
                        next_line = lines[i+1].strip()
                        
                        # Check if current line is a single word
                        match = word_pattern.match(current_line)
                        # Check if next line contains "分析词义"
                        if match and "分析词义" in next_line:
                            word = match.group(1)
                            all_extracted_words.add(word.lower())
                doc.close()
            except Exception as e:
                print(f"An error occurred while processing {pdf_path} for Style 2: {e}", file=sys.stderr)

    if not pdf_files_found:
        return

    if not all_extracted_words:
        print("No matching words were found for Style 2 in any of the PDF files.")
        return

    # --- File 1: Write all extracted words formatted as [[word]] ---
    output_words_path = os.path.join(directory_path, "extracted_words_v2.md")
    with open(output_words_path, 'w', encoding='utf-8') as f:
        f.write("# Extracted Words (Style 2)\n\n")
        for word in all_extracted_words:
            f.write(f"[[{word}]]\n")
    print(f"Successfully wrote all Style 2 extracted words to {output_words_path}")

    # --- File 2: Write the statistics of the words ---
    output_stats_path = os.path.join(directory_path, "word_statistics_v2.md")
    word_counts = Counter(all_extracted_words)
    with open(output_stats_path, 'w', encoding='utf-8') as f:
        f.write("# Word Statistics (Style 2)\n\n")
        f.write("| Word | Count |\n")
        f.write("|------|-------|\n")
        # Sort by most common
        for word, count in word_counts.most_common():
            f.write(f"| [[{word}]] | {count} |\n")
    print(f"Successfully wrote Style 2 word statistics to {output_stats_path}")
    return all_extracted_words

def analyze_md(file_path, keywords):
    """
    检查 Markdown 文件的 tags 属性中是否包含指定的任一关键字
    """
    try:
        # 加载文件
        post = frontmatter.load(file_path)
        
        # 获取 tags 列表，如果没有 tags 则返回空列表 []
        tags = post.metadata.get('tags', [])
        
        # 核心逻辑：检查 keywords 中的任何一个词是否出现在 tags 列表的任何一个元素中
        matched_keywords = [
            kw for kw in keywords 
            if any(kw in tag for tag in tags)
        ]
        
        return matched_keywords  # 返回匹配到的关键字列表，若为空则说明没匹配到
    except Exception as e:
        print(f"读取文件 {file_path} 出错: {e}")
        return []

def list_markdown_files_recursively(directory_path, all_extracted_words):
    """
    Recursively lists all Markdown (.md) files in a given directory and its subdirectories.
    """
    file_num = 0
    print(f"\n--- Recursively Listing Markdown Files in '{directory_path}' ---")
    md_files_found = False
    weak_words = []
    # os.walk() generates the file names in a directory tree by walking the tree.
    for root, _, files in os.walk(directory_path):
        for file in files:
            if file.lower().endswith('.md'):
                file_num += 1
                isExist = Path(file).stem in all_extracted_words
                md_files_found = True
                md_path = os.path.join(root, file)
                if isExist:
                    # os.remove(md_path)
                    weak_words.append(Path(file).stem)
                    shutil.move(md_path, os.path.join(directory_path, '..', 'liubin'))
                    # print(f"Found: {md_path}")
                # if analyze_md(md_path, ['小学', '中考', '高考', '四级', '六级', '考研', '雅思']):
                #     print(f"Found tag: {md_path}")
                #     weak_words.append(Path(file).stem)
                #     # if Path(os.path.join(directory_path, 'other', file)).exists():
                #     #     os.remove(os.path.join(directory_path, 'other', file))
                #     shutil.move(md_path, os.path.join(directory_path, '..', 'other'))
    
    if not md_files_found:
        print("No Markdown files found in the directory or its subdirectories.")

    print(f"Total Markdown files found: {file_num}")
    print(f"Total Markdown tag found: {len(weak_words)} all_extracted_words: {len(all_extracted_words)}")

def main():
    """
    Main function to get user input and start the process.
    """
    directory = input("Enter the path to the folder containing PDF files (press Enter for current directory): ") or '.'

    if not os.path.isdir(directory):
        print(f"Error: The directory '{directory}' does not exist.", file=sys.stderr)
        return

    # Run the first style of extraction
    print("\n--- Running Original Extraction (Style 1) ---")
    all_extracted_words = set()
    extract_words_from_pdfs(directory, all_extracted_words)

    # Run the second style of extraction
    # extract_words_style_2(directory, all_extracted_words)

    # After all processing, recursively list all markdown files in the same directory.
    
    list_markdown_files_recursively(os.path.join(directory, 'words'), all_extracted_words)

def create_markdown_file():
    directory_path = "D:\\work\\EnglishLearn\\liubin20000\\【03】思维导图"
    for root, _, files in os.walk(directory_path):
        for file in files:
            if file.lower().endswith('.jpg'):
                if os.path.exists(Path(directory_path) / (Path(file).stem + '.md')):
                    continue
                else:
                    file_path = os.path.join(root, Path(file).stem + '.md') 
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(
                            '''---
mindmap-plugin: basic
title: {}
markmap:
colorFreezeLevel: 2
---       
                '''.format(Path(file_path).stem)
                        )
                    print(f"Successfully created {file_path}")


def copy_markdown_file():
    source_dir = "F:\\PaddleOCR-VL\\outputs\\"
    target_dir = "D:\\work\\EnglishLearn\\liubin20000\\06\\"
    for root, _, files in os.walk(source_dir):
        for file in files:
            if file.lower().endswith('.md') and file.startswith('词汇课'):
                source_path = os.path.join(root, file)
                target_path = os.path.join(target_dir, file)
                shutil.copy(source_path, target_path)
                print(f"Successfully copied {source_path} to {target_path}")

if __name__ == "__main__":
    # main()
    copy_markdown_file()
#     word_pattern = re.compile(r'^([a-zA-Z]+)\s+\[')
#     word_orgin = '''
# exceedingly [ik'si:diŋli] adv. 非常；极其；极端；极度地         11078
#     '''
#     match = word_pattern.match(word_orgin.strip())
#     if match:
#         # The first group of the match is the word
#         word = match.group(1)
#         print(word)

