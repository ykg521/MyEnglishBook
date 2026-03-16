import re

def extract_markdown_headers(file_path):
    # 定义正则表达式：匹配以 1-6 个 # 开头，后接空格，再接内容的行
    # ^ 匹配行首，(#{1,6}) 捕获 1-6 个井号，\s+ 匹配空格，(.+) 捕获标题内容
    header_pattern = re.compile(r'^(#{1,6})\s+(.+)$')
    
    headers = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                match = header_pattern.match(line.strip())
                if match:
                    level = len(match.group(1))  # 井号的数量即级别
                    title = match.group(2)      # 标题文字
                    headers.append({"level": level, "title": title})
                    
    except FileNotFoundError:
        print(f"文件未找到，请检查路径。{file_path}")
    
    return headers

def extract_title():
    with open("extra_title.md", 'w', encoding='utf-8') as f:
        for i in range(1, 16):
            md_file = f".\\{i}.md"
            results = extract_markdown_headers(md_file)
            f.write(f"\n从文件 {md_file} 提取的标题：")
            for h in results:
                # 格式化输出：根据级别缩进，方便观察层级
                indent = "  " * (h['level'] - 1)
                f.write(f"{indent}H{h['level']}: {h['title']}\n")

def merge_md_files():
    explain_words = set()
    all_words = set()
    with open("..\\0.md", 'r', encoding='utf-8') as f:
        for line in f.readlines():
            words = re.findall(r'\b[a-zA-Z]+\b', line)
            all_words.update(set(word.lower() for word in words))
        for i in range(1, 2):
            md_file = f"..\\0{i}.md"
            try:
                with open(md_file, 'r', encoding='utf-8') as md_f:
                    for line in md_f.readlines():
                        if line.startswith("#????"):
                            f.write(line)
                        else:
                            words = re.findall(r'\b[a-zA-Z]+\b', line)
                            # 转 set 自动去重
                            explain_words.update(set(word.lower() for word in words))  # 小写统一

            except FileNotFoundError:
                print(f"文件未找到，请检查路径。{md_file}")
    print(f"所有文件中 word 有但整理 没有的字母（共 {len(explain_words)} 个）；单词表中共计（共 {len(all_words)} 个）")
    diff_words = all_words - explain_words
    diff_words2 = explain_words - all_words
    diff_words_str = ",".join(diff_words)
    diff_words2_str = ",".join(diff_words2)
    print(f"差集{len(diff_words)}个 {len(diff_words2)}个 \n{diff_words_str}")

def main():
    # extract_title()
    merge_md_files()

if __name__ == "__main__":
    main()