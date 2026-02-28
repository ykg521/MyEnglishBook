import json
import os

def json_lines_to_md_files(input_file, output_dir="md_output", encoding='utf-8'):
    """
    按行读取JSON文件，每行生成一个独立的.md文件，并存放到指定文件夹
    
    Args:
        input_file (str): 源JSON文件路径（每行一个JSON）
        output_dir (str): 存放md文件的目标文件夹，默认md_output
        encoding (str): 文件编码，默认utf-8
    """
    # 记录错误行和成功生成的文件
    error_lines = []
    generated_files = []
    
    # 1. 创建目标文件夹（不存在则创建）
    try:
        os.makedirs(output_dir, exist_ok=True)
        print(f"目标文件夹已准备好：{os.path.abspath(output_dir)}")
    except Exception as e:
        print(f"创建文件夹失败：{str(e)}")
        return

    # 2. 逐行读取源文件并处理
    try:
        with open(input_file, 'r', encoding=encoding) as f_in:
            for line_num, line in enumerate(f_in, start=1):
                # 去除行首尾空白，跳过空行
                line_stripped = line.strip()
                if not line_stripped:
                    continue

                try:
                    # 解析JSON字符串
                    json_data = json.loads(line_stripped)

                    # 3. 定义md文件路径（按行号命名，避免重复）
                    word = json_data.get("word", "")
                    if '/' in word:
                        word = word.replace('/', '')  # 去除斜杠，避免文件命名问题
                    content = json_data.get("content", "")
                    print(f"正在处理第 {line_num} 行，单词：{word}")
                    md_filename = f"{word}.md"
                    md_filepath = os.path.join(output_dir, md_filename)
                    
                    # 4. 将JSON内容写入md文件（格式化，易读）
                    with open(md_filepath, 'w', encoding=encoding) as f_out:
                        f_out.write(f'''---
tags:
  - 威威
掌握: false
模糊: false
间隔: 0
重复次数: 0
易记因子: 250
到期日: 2025-04-30
---
# {word}

{content}
''')

                        # # 写入标题（行号）
                        # f_out.write(f"# 第 {line_num} 行数据\n\n")
                        # # 遍历JSON键值对，逐行写入
                        # if isinstance(json_data, dict):
                        #     for key, value in json_data.items():
                        #         f_out.write(f"## {key}\n{value}\n\n")
                        # elif isinstance(json_data, list):
                        #     # 若JSON是列表，按序号写入
                        #     f_out.write("## 列表数据\n")
                        #     for idx, item in enumerate(json_data, start=1):
                        #         f_out.write(f"{idx}. {item}\n")
                        # else:
                        #     # 其他类型（字符串/数字）直接写入
                        #     f_out.write(f"## 数据内容\n{json_data}\n")
                    
                    generated_files.append(md_filepath)
                    print(f"✅ 生成文件：{md_filepath}")

                except json.JSONDecodeError as e:
                    # 记录JSON解析错误
                    error_msg = f"第{line_num}行解析失败: {str(e)}"
                    error_lines.append(error_msg)
                    print(f"❌ {error_msg}")

        # 5. 输出处理总结
        print("\n" + "-"*50)
        print(f"处理完成！总计：")
        print(f"✅ 成功生成 {len(generated_files)} 个md文件")
        print(f"❌ 解析失败 {len(error_lines)} 行")
        if error_lines:
            print("错误详情：")
            for err in error_lines:
                print(f"  - {err}")

    except FileNotFoundError as e:
        print(f"错误：源文件 '{input_file}' 不存在，请检查路径！", str(e))
    except PermissionError:
        print(f"错误：没有权限读取/写入文件，请检查权限！")
    except Exception as e:
        print(f"未知错误：{str(e)}")

# 示例调用
if __name__ == "__main__":
    # 替换为你的源JSON文件路径
    INPUT_FILE = "gptwords.json"  
    # 生成的md文件会存放在这个文件夹（自动创建）
    OUTPUT_DIR = "./output"     
    
    # 执行函数
    json_lines_to_md_files(INPUT_FILE, OUTPUT_DIR)