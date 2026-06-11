import os
import re

# 定义要写入的内容模板
content_template = """# Words

## Expression

## Recap
### Patterns&Grammar
nil
### Words
nil
### Expression
nil

---

---


---

# Grammar

## Expression

## Recap
### Patterns&Grammar
nil
### Words
nil
### Expression
nil

---

---


---

# Essay

## Expression

## Recap
### Patterns&Grammar
nil
### Words
nil
### Expression
nil

---

---


---"""

content_template1 = """# Words & Grammer & Eaasy

## Essay

## Expression

## Recap
### Patterns&Grammar
nil

### Words
nil

### Expression
nil"""

# 生成文件名列表 (NCE1-L20 到 NCE1-L140，间隔为5)
file_names = []
for i in range(20, 141, 1):
    file_name = f"NCE1-L{i}.md"
    file_names.append(file_name)

# 创建文件夹（如果不存在）
folder_name = "./"

# 批量写入文件
for file_name in file_names:
    print(f"正在处理文件: {file_name}")
    match = re.search(r'L(\d+)(?=[^\d]*$)', file_name)  # 匹配末尾的 L+数字
    if match:
        print(f"正在处理文件: {file_name}，提取到的数字: {match.group(1)}")
        if int(match.group(1)) % 2 == 0:
            file_path = os.path.join(folder_name, file_name)
            with open(file_path, "w") as f:  # "r+" = 读写模式
                pass
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content_template1)
    else:
        print(f"文件名 {file_name} 不符合预期格式，跳过。")
        continue    


print(f"已成功创建 {len(file_names)} 个笔记模板文件：")
for file_name in file_names:  # 打印前5个文件名作为示例
    print(f"- {file_name}")

print(f"\n所有文件已保存在 '{folder_name}' 文件夹中。")
