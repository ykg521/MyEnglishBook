import json
from openai import OpenAI
import os
import yaml
import re
from collections import defaultdict
from pathlib import Path

# 初始化客户端，指向本地 Ollama 地址
client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama",  # 本地部署无需真实 key
)

def generate_word_study(word):
    prompt = f"""
    You are an expert English linguist and a Senior Android Engineer. 
    Analyze the English word: "{word}".
    Please provide the following in JSON format:
    1. "Sentences": Two natural sentences (one general, one technical/professional).
    2. "Synonyms": 3-5 synonyms with subtle differences explained.
    3. "Associations": Concepts or objects commonly linked to this word.
    4. "Native_Usage": 2 idiomatic expressions or phrasal verbs using this word.

    Language: Respond in English, but explain the 'Synonyms' and 'Native_Usage' in Chinese.
    """

    response = client.chat.completions.create(
        model="qwen3:8b", # 也可以改用 qwen3.5 或 llama4
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"} # 强制要求返回 JSON
    )
    
    return response.choices[0].message.content

def extract_multi_tags(file_path):
    """
    解析 MD 文件，支持同类 key 对应多个 value (如多个级别)
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 匹配 YAML Frontmatter
        match = re.search(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
        if not match:
            return None

        data = yaml.safe_load(match.group(1))
        raw_tags = data.get('tags', [])

        # 使用 defaultdict(list) 存储，防止覆盖
        structured = defaultdict(list)
        
        for tag in raw_tags:
            if '/' in tag:
                key, val = tag.split('/', 1)
                structured[key].append(val)
            else:
                structured['others'].append(tag)
        
        # 转换为普通字典输出
        return dict(structured)
    except Exception as e:
        print(f"Skipping {file_path}: {e}")
        return None

def scan_markdown_directory(root_dir):
    """
    递归迭代目录，处理所有 .md 文件
    """
    results = {}

    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file.endswith('.md'):
                full_path = os.path.join(root, file)
                tags = extract_multi_tags(full_path)
                if tags:
                    tagInfos = tags.get('级别', [])
                    if ('GRE' in tagInfos or '托福' in tagInfos) and len(tagInfos) == 1:
                        continue
                    others = tags.get('others', [])
                    if len(others) > 0 :
                        results[full_path] = others
                    else:
                        results[full_path] = tags
    
    return results

def update_markdown_file(original_path, new_content):
    """
    更新 MD 文件内容，保留原有 YAML Frontmatter 和标签
    """
    try:
        with open(original_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Updated file: {original_path}")
    except Exception as e:
        print(f"Error updating {original_path}: {e}")

def main():
    # 替换为你存放单词笔记的实际路径
    target_dir = "./英语/英语单词/words" 
    update_dir = "./memory_words"
    if os.path.exists(target_dir):
        all_data = scan_markdown_directory(target_dir)
        for path, tags in all_data.items():
            print(f"File: {Path(path).stem} | Tags: {tags}")
            update_path = os.path.join(update_dir, Path(path).stem + "_.md")
            if Path(update_path).exists():
                print(f"File already exists, skipping: {update_path}")
                continue
            result = generate_word_study(Path(path).stem)
            update_markdown_file(update_path, result)
            

        print(f"\n扫描完成，共找到 {len(all_data)} 个带标签的有效文件。")
    else:
        print("目录不存在，请检查路径。")
    # 测试单词: Buffer (这对 A/V 开发非常常用)
    # result = generate_word_study("Buffer")
    # print(result)

# 使用示例
if __name__ == "__main__":
    main()
