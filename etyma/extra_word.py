import os
import fitz  # PyMuPDF
import re
import sys
from collections import Counter
from pathlib import Path
import frontmatter
import shutil
from readmdict import MDX
from bs4 import BeautifulSoup
from bs4 import NavigableString

class MdxDictionary:
    def __init__(self, mdx_path):
        """
        初始化 MdxDictionary 实例。

        Args:
            mdx_path (str): MDX 文件的路径。
        """
        self.mdx_path = mdx_path
        # 加载 MDX 文件
        self.mdx_dict = MDX(mdx_path)
        # 将 keys() 结果转换为列表，方便后续操作
        self.key_list = list(self.mdx_dict.keys())
        
        # 构建一个内存中的字典用于快速查询
        # 这一步会消耗一些内存，但能换取 O(1) 的查询速度
        print("正在加载词典到内存...")
        self._dict_map = {}
        for key, value in self.mdx_dict.items():
            # key 和 value 都是 bytes 类型，解码后存入 map
            self._dict_map[key.decode('utf-8')] = value.decode('utf-8')
        print(f"词典加载完成，共有 {len(self._dict_map)} 个词条。")

    def lookup(self, word):
        """
        查询指定的单词。

        Args:
            word (str): 要查询的单词。

        Returns:
            str: 单词的释义，如果未找到则返回 None。
        """
        # 直接从内存中的字典查询，速度快
        return self._dict_map.get(word.lower(), None)
            
    def fuzzy_search(self, prefix, max_results=10):
        """
        根据前缀进行模糊搜索。

        Args:
            prefix (str): 搜索的前缀。
            max_results (int): 最大返回结果数量。

        Returns:
            list: 匹配的词头列表。
        """
        prefix_lower = prefix.lower()
        # 在内存字典的键中搜索
        matches = []
        for key in self._dict_map:
            if key.lower().startswith(prefix_lower):
                matches.append(key)
                if len(matches) >= max_results:
                    break
        return matches



def extract_words_from_pdfs(directory_path, all_extracted_words):
    word_pattern = re.compile(r'^([a-zA-Z]+)\s+\[')
    words_list_pattern = re.compile(r'[a-zA-Z]+')

    # print(f"Searching for MD files in '{directory_path}'...")
    md_files_found = False
    for filename in list(Path(directory_path).glob("**/*.md")):
        if str(filename).lower().endswith('.md'):
            md_files_found = True
            md_path = os.path.join(directory_path, filename)
            print(f"Processing {md_path}...")  
            try:
                # Extract text line by line
                with open(md_path, 'r', encoding='utf-8') as f:
                    for line in f.readlines():
                        match = word_pattern.search(line.strip())
                        if match:
                            # The first group of the match is the word
                            word = match.group(1)
                            all_extracted_words.add(word)
                        match = words_list_pattern.search(line.strip())
                        if match:
                            word = match.group(0)
                            all_extracted_words.add(word)
            except Exception as e:
                print(f"An error occurred while processing {md_path}: {e}", file=sys.stderr)

    if not md_files_found:
        print("No Markdown files found in the specified directory.")
        return

    if not all_extracted_words:
        print("No matching words were found in any of the PDF files.")
        return
    print(f"Total unique words extracted: {len(all_extracted_words)}")
    # --- File 1: Write all extracted words formatted as [[word]] ---
    # output_words_path = os.path.join(directory_path, "extracted_words.md")
    # with open(output_words_path, 'w', encoding='utf-8') as f:
    #     f.write("# Extracted Words\n\n")
    #     for word in all_extracted_words:
    #         f.write(f"[[{word}]]\n")
    # print(f"Successfully wrote all extracted words to {output_words_path}")

    # --- File 2: Write the statistics of the words ---
    # output_stats_path = os.path.join(directory_path, "word_statistics.md")
    # word_counts = Counter(all_extracted_words)
    # with open(output_stats_path, 'w', encoding='utf-8') as f:
    #     f.write("# Word Statistics\n\n")
    #     f.write("| Word | Count |\n")
    #     f.write("|------|-------|\n")
    #     # Sort by most common
    #     for word, count in word_counts.most_common():
    #         f.write(f"| [[{word}]] | {count} |\n")
    # print(f"Successfully wrote word statistics to {output_stats_path}")
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

def list_markdown_files_recursively(directory_path, all_extracted_words, target_directory):
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
                    weak_words.append(Path(file).stem)
                    # print(f"Found: {file} in {Path(md_path).resolve()}")
                    if not Path(os.path.join(target_directory, '..', 'etyma_words', file[0].upper())).exists():
                        os.makedirs(os.path.join(target_directory, '..', 'etyma_words', file[0].upper()), exist_ok=True)
                    shutil.move(md_path, os.path.join(target_directory, '..', 'etyma_words', file[0].upper(), file))
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

def build_vocabulary_list(word_list_file, words_set=None):
    """
    构建词汇列表
    """
    pattern = r'\b[a-zA-Z]+\b'
    with open(word_list_file, 'r') as f:
        for line in f:
            if words_set is not None:
                words_set.update(re.findall(pattern, line.strip().lower()))
            else:
                words_set.update(re.findall(pattern, line.strip().lower()))
    print(f"Total words in the list: {len(words_set)}")  # Print first 5 words as a sample
    return words_set

def build_vocabulary_card_from_list(word_list_directory, words_set=None):
    """
    从词汇列表目录构建词汇卡片
    """
    for root, _, files in os.walk(word_list_directory):
        for file in files:
            if file.lower().endswith('.md'):
                build_vocabulary_list(os.path.join(root, file), words_set)

def main():
    """
    Main function to get user input and start the process.
    """
    # directory = input("Enter the path to the folder containing PDF files (press Enter for current directory): ") or '.'
    directory = os.getcwd()
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
    list_markdown_files_recursively(os.path.join(directory, '..', '英语', '英语单词', 'words'), all_extracted_words, directory)

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

def filter_markdown_files(words_set, directory_path):
    # 遍历目录及其子目录中的所有 Markdown 文件，删除不在 words_set 中的文件
    pattern_with_tag = r'#形态/(\w+)\s+([a-zA-Z]+)'
    for root, _, files in os.walk(directory_path):
        for file in files:
            if file.lower().endswith('.md'):
                if Path(file).stem in words_set:
                    words_set.remove(Path(file).stem)
            # 剔除变形词
            with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                content = f.read()
                tagged_words = re.findall(pattern_with_tag, content, re.MULTILINE)
                tagged_dict = {tag: word for tag, word in tagged_words}
                if tagged_dict:
                    for tag, word in tagged_dict.items():
                        if word in words_set:
                            words_set.remove(word)
                            # print(f"Found tagged word: {word} with tag: {tag} in {file}")
                    # print(f"Found tagged words in {file}: {tagged_dict.values()}")
    
    print(f"Total Markdown files found: {len(words_set)}")

def parse_html_content(html_content):
    # 解析HTML内容
    soup = BeautifulSoup(html_content, 'html.parser')

    # 查找所有的定义
    definitions = soup.find_all('div', {'class': 'collins_en_cn example'})

    extracted_info = []

    for definition in definitions:
        # 获取类型（如 N-VAR, PHRASE）
        st_tag = definition.find('span', {'class': 'st'})
        if not st_tag: continue  # 如果没有找到类型标签，则跳过
        
        # 获取英文解释和中文翻译
        def_cn_tags = definition.find_all('span', {'class': 'def_cn cn_before'})
        for def_cn_tag in def_cn_tags:
            # 找到第二个 .def_cn 标签 (即 cn_after)
            end_span = def_cn_tag.find_next_sibling('span', class_='def_cn')

            # 获取起始span的第一个中文
            first_chinese = def_cn_tag.get_text(strip=True)

            # 获取起始span和结束span之间的所有内容
            content_between = []
            current = def_cn_tag.next_sibling
            while current and current != end_span:
                if hasattr(current, 'get_text'):
                    # 如果是标签，获取其文本
                    content_between.append(current.get_text())
                elif isinstance(current, NavigableString):
                    # 如果是文本节点，直接添加
                    text_node_content = current.strip()
                    if text_node_content: # 避免添加空字符串
                        content_between.append(text_node_content)
                current = current.next_sibling

            # 拼接结果
            final_result = first_chinese + " " + "".join(content_between).strip()
            
            extracted_info.append({
                'type': st_tag.get_text(strip=True),
                'zh_definition': final_result
            })

    # 拼接字符串
    formatted_lines = [f"## {s['type']}\n{s['zh_definition']}\n" for s in extracted_info]
    # 使用 ''.join() 将所有行连接起来
    return ''.join(formatted_lines)

    return extracted_info

def build_markdown_files_form_words(dictionary, words_set, directory_path):

    for word in words_set:
        definition = dictionary.lookup(word)
        extracted_info = []
        if definition:
            extracted_info = parse_html_content(definition)

        md_file_path = os.path.join(directory_path, f"{word}.md")
        if os.path.exists(md_file_path):
            print(f"Found: {md_file_path}")
        else:
            with open(md_file_path, 'w', encoding='utf-8') as f_out:
                        f_out.write(f'''---
tags:
  - COCA2w
掌握: false
模糊: false
间隔: 0
重复次数: 0
易记因子: 250
到期日: 2025-04-30
---
# {word}

{extracted_info}
''')
    print(f"Total Markdown files build: {len(words_set)}")

def main_1():
    mdx_path = "H:\\Program Files\\eudic\\Dict\\柯林斯双解增强版\\CollinsCOBUILDOverhaul V 2-30.mdx"  # 替换为你的MDX文件路径
    mdd_path = "H:\\Program Files\\eudic\\Dict\\柯林斯双解增强版\\CollinsCOBUILDOverhaul V 2-30.mdd"  # 可选，无资源文件可忽略

    # 创建词典实例
    dictionary = MdxDictionary(mdx_path)

    words_set = set()
    all_extracted_words = set()
    directory = os.getcwd()
    """统计词根词缀词表"""
    extract_words_from_pdfs(directory, all_extracted_words)
    """COCA2w词频表：https://www.wordfrequency.info/free.asp?s=y"""
    build_vocabulary_list(word_list_file = "D:\\work\\EnglishLearn\\20000.txt", words_set=words_set)
    # build_vocabulary_list(word_list_file = "D:\\work\\EnglishLearn\\COCA_20000.txt", words_set=words_set)

    """不背单词词表"""
    build_vocabulary_list(word_list_file = "D:\\work\\EnglishLearn\\bubeidanci.md", words_set=words_set)
    print(f"Total unique words in both lists: {len(words_set)}")
    filter_markdown_files(words_set, "D:\\work\\EnglishLearn\\英语\\英语单词\\words")
    # filter_markdown_files(words_set, "D:\\work\\EnglishLearn\\COCA")
    diff = words_set.difference(all_extracted_words)
    build_markdown_files_form_words(dictionary, diff, "D:\\work\\EnglishLearn\\英语\\英语单词\\words\\COCA")
    print(f"Unique words in vocabulary lists but not in extracted words: {len(diff)}")

if __name__ == "__main__":
    # main()
    main_1()