import os
import re

def process_md_files(directory):
    """
    处理指定目录下的所有.md文件，匹配指定正则的行并在前方加换行符
    
    Args:
        directory (str): 目标目录路径
    """
    # 定义正则表达式：匹配 ([a-zA-Z-' ]+) 后跟空格和 [ 的行
    pattern = re.compile(r"([a-zA-Z-' ]+)\s+\[")
    
    # 遍历目录下所有文件
    for filename in os.listdir(directory):
        # 筛选.md文件
        if filename.lower().endswith('.md'):
            file_path = os.path.join(directory, filename)
            print(f"正在处理文件: {file_path}")
            
            try:
                # 读取文件内容
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                # 处理每一行内容
                modified_lines = []
                for line in lines:
                    # 检查当前行是否匹配正则
                    if pattern.search(line):
                        # 在匹配行前添加换行符（注意：如果行首已有换行，可调整为只加一个）
                        modified_line = '\n' + line
                        modified_lines.append(modified_line)
                        print(f"匹配到行并修改: {line.strip()} -> {modified_line.strip()}")
                    else:
                        # 不匹配的行保持原样
                        modified_lines.append(line)
                
                # 将修改后的内容写回文件（如需备份原文件，可先复制再覆盖）
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.writelines(modified_lines)
                
                print(f"文件 {filename} 处理完成\n")
            
            except Exception as e:
                print(f"处理文件 {filename} 时出错: {str(e)}\n")

# 示例：处理当前目录下的.md文件
if __name__ == "__main__":
    # 替换为你的目标目录路径（如：r"C:\Users\XXX\Documents\md_files"）
    target_directory = "."  # "." 表示当前目录
    process_md_files(target_directory)