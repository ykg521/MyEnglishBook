def sort_md_by_number(input_file, output_file):
    """
    按数字排序MD文件中的行（格式：数字 + 空格 + 内容）
    :param input_file: 输入MD文件路径
    :param output_file: 输出新MD文件路径
    """
    # 步骤1：读取文件内容并解析
    lines_data = []
    with open(input_file, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            # 去除行首尾空白（换行、空格）
            clean_line = line.strip()
            if not clean_line:  # 跳过空行
                continue
            
            # 步骤2：拆分数字和内容（按第一个空格/制表符分割）
            try:
                # 分割：数字部分 + 内容部分（兼容多个空格/制表符）
                parts = clean_line.split(maxsplit=1)
                if len(parts) < 2:  # 跳过格式错误的行
                    print(f"警告：第{line_num}行格式错误，已跳过 → {clean_line}")
                    continue
                
                # 转换数字为整数（核心排序依据）
                num = int(parts[0].strip())
                content = parts[1].strip()
                lines_data.append((num, content))  # 存储为(数字, 内容)元组
            
            except ValueError:
                # 数字转换失败（非数字开头）
                print(f"警告：第{line_num}行不是数字开头，已跳过 → {clean_line}")
                continue
    
    # 步骤3：按数字升序排序
    lines_data.sort(key=lambda x: x[0])
    
    # 步骤4：写入新文件（保持原格式：数字 + 多个空格 + 内容）
    with open(output_file, 'w', encoding='utf-8') as f:
        for num, content in lines_data:
            # 用4个空格分隔（和示例格式一致，可自行调整）
            f.write(f"{num}     {content}\n")
    
    print(f"排序完成！已写入新文件：{output_file}")
    print(f"共处理 {len(lines_data)} 行有效内容")

# ==================== 调用示例 ====================
if __name__ == "__main__":
    # 替换为你的输入/输出文件路径
    INPUT_FILE = "C:\\Users\\yyykg\\output\\雅思词汇-词根联想记忆法\\Test.md"   # 原MD文件
    OUTPUT_FILE = "C:\\Users\\yyykg\\output\\雅思词汇-词根联想记忆法\\Test1.md"  # 排序后的新文件
    
    # 执行排序
    sort_md_by_number(INPUT_FILE, OUTPUT_FILE)