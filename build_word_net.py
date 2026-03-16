import re

def parse_markdown_sections(md_file_path):
    """
    解析 markdown 文件，提取 ## words 和 ## 整理 下面的内容
    """
    target_headers = ["## words", "## 整理"]
    current_section = None  # 标记当前正在读取哪个段落
    word_content = []
    整理_content = []

    with open(md_file_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")  # 去掉换行符

            # 如果遇到新的 ## 标题，切换当前段落
            if line.startswith("## "):
                if line in target_headers:
                    current_section = line
                else:
                    current_section = None  # 其他标题，停止读取
                continue

            # 把内容加入对应的段落
            if current_section == "## words":
                word_content.append(line)
            elif current_section == "## 整理":
                整理_content.append(line)

    # 去掉空行（可选）
    word_content = [line for line in word_content if line.strip()]
    整理_content = [line for line in 整理_content if line.strip()]

    return {
        "word": "\n".join(word_content),
        "整理": "\n".join(整理_content)
    }

def main():
    total_words = set()  # 用于存储所有 word 中的字母
    for i in range(1, 16):
        print(f"===== 第{i}个文件 =====")
        # 替换成你的 markdown 文件路径
        md_path = f".\\memory_words\\{i}.md"
        
        # 解析
        result = parse_markdown_sections(md_path)
        
        # 输出结果
        # print(f"===== ## word 内容 ===== \n {result}")
        # raw_words = set("".join(result["word"]).split(','))
        raw_words = {item.strip() for item in "".join(result["word"]).split(',') if item.strip()}
        # print(raw_words)

        words = re.findall(r'\b[a-zA-Z]+\b', result["整理"])
        # 转 set 自动去重
        explain_words = set(word.lower() for word in words)  # 小写统一
        # print(f"共{len(raw_words)}个单词，解析了{len(explain_words)}个单词 \n {result['整理']}\n explain_words: {explain_words}")
        diff = raw_words.difference(explain_words)
        diff_str = ", ".join(diff)
        print(f"word 中有但整理 中没有的字母（共 {len(diff)} 个）：\n{diff_str}")
        total_words.update(diff)
        # print(f"word 中的字母（共 {len(raw_words)} 个）：{raw_words}")
        # print(f"整理 中的字母（共 {len(explain_words)} 个）：{explain_words}")
        # print(f"word 中有但整理 中没有的字母（共 {len(diff  )} 个）：{diff}")
        # print("\n===== ## 整理 内容 =====")
        # print(result["整理"])

    print(f"所有文件中 word 有但整理 没有的字母（共 {len(total_words)} 个）")

    # for i in range(0, len(total_words), 200):
        # print(*list(total_words)[i:i+200], sep=", ")
# ========== 使用方法 ==========
if __name__ == "__main__":
    main()