import os
import random
import re
from pathlib import Path
import yaml
from collections import defaultdict
import frontmatter
from io import BytesIO
import requests
import pygame
import keyboard
from etyma import mdx_reader

kowned_word_num = 0
unknown_word_num = 0

def study_word(file_path, content):
    print(f"{Path(file_path).stem} \n 内容: {content}")
    play_audio(file_path)
    global kowned_word_num, unknown_word_num
    user_input = input(f"\n 按 'y' 键确认掌握...")
    if user_input == "y":
        post = frontmatter.load(file_path)
        post['掌握'] = True
        with open(file_path, 'wb') as f:
            frontmatter.dump(post, f)

        kowned_word_num += 1
        print(f"{Path(file_path).stem} 已标记为掌握 已掌握单词数量: {kowned_word_num} 未掌握单词数量: {unknown_word_num}")

    else:
        unknown_word_num += 1
        print(f"{Path(file_path).stem} 保持未掌握状态 已掌握单词数量: {kowned_word_num} 未掌握单词数量: {unknown_word_num}")

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
        print(f"{Path(file_path).stem} 原始 tags: {raw_tags}")
        if ('级别/GRE' in raw_tags or '级别/托福' in raw_tags) and len(raw_tags) == 2:
            return None
        if '级别/GRE' in raw_tags and '级别/托福' in raw_tags and len(raw_tags) == 3:
            return None
        is_mastered = data.get('掌握')
        if is_mastered:
            # print(f"{Path(file_path).stem} 掌握情况: {is_mastered}")
            return None
        else:
            content = ""
            with open(file_path, 'r', encoding='utf-8') as f:
                post = frontmatter.load(f)
                content = post.content
                content = re.sub(r'##### 例句.*', '', content, flags=re.S)
            # study_word(file_path, content)

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

url = ""

def play_audio(file_path):
    """
    播放音频文件（示例使用 playsound 库）
    """
    try:
        if file_path is not None:
            global url
            url = "http://dict.youdao.com/dictvoice?type=0&audio=" + Path(file_path).stem

        # 1. 下载音频到内存
        # print("正在缓冲音频...", end="", flush=True)
        response = requests.get(url)
        audio_data = BytesIO(response.content)

        # 2. 初始化播放器
        pygame.mixer.init()
        pygame.mixer.music.load(audio_data)

        # 3. 播放
        pygame.mixer.music.play()
    except ImportError:
        print("请安装 playsound 库以播放音频：pip install playsound")
    except Exception as e:
        print(f"无法播放音频 {file_path}: {e}")

def scan_markdown_directory(root_dir, results):
    """
    递归迭代目录，处理所有 .md 文件
    """
    for root, dirs, files in os.walk(root_dir):
        random.shuffle(files)
        for file in files:
            if file.endswith('.md'):
                full_path = os.path.join(root, file)
                tags = extract_multi_tags(full_path)
                if tags:
                    # print(f"Processing {full_path} with tags: {tags}")
                    tagInfos = tags.get('级别', [])
                    if ('GRE' in tagInfos or '托福' in tagInfos) and len(tagInfos) == 1:
                        continue
                    results.add(Path(file).stem)

def on_triggered():
    play_audio(None)

def querry_word(words):
    dictionary = mdx_reader.create_mdx_dictionary(None)
    target_dir = ".\\output\\Temp"
    for word in words:
        _, content = mdx_reader.lookup_and_parse(dictionary, word)
        if len(content) > 0:
            with open(os.path.join(target_dir, f"{word}+.md"), 'w', encoding='utf-8') as f:
                f.write(f"# {word}\n")
                for item in content:
                    word_type, english_def, chinese_def = item
                    f.write(f"**{word_type}** ")
                    f.write(f"{english_def}\n")
                    f.write(f"{chinese_def}\n\n")


def main():
    keyboard.add_hotkey('b', on_triggered)
    raw_results = set()
    scan_markdown_directory(".\\英语\\英语单词\\words", raw_results)
    print(f"共找到 {len(raw_results)} 个单词：")
    new_results = set()
    scan_markdown_directory(".\\memory_words", new_results)
    print(f"共找到 {len(new_results)} 个单词：")
    diff = raw_results.difference(new_results)
    phres_results = [item for item in diff if ' ' in item or '-' in item]
    words_results = diff.difference(set(phres_results))
    print(f"需要记忆的单词数量：{len(words_results)} 短语数量：{len(phres_results)}")
    words_new = list(words_results)
    # for i in range(0, len(words_new), 200):
    #     print(*words_new[i:i+200], sep=", ")
    
    querry_word(words_results)
    # print(f"需要记忆的单词列表：{', '.join(words_results)}")
    # print(f"需要记忆的短语列表：{', '.join(phres_results)}")

if __name__ == "__main__":
    main()