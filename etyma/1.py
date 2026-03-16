from bs4 import BeautifulSoup
from bs4 import NavigableString # 导入 NavigableString 类型

html_snippet = '''<span class="def_cn cn_before">
								<span class="chinese-text">心肝宝贝；掌上明珠</span>
							</span> If you say that someone is <b>the apple of</b> your <b>eye</b>, you mean that they are very important to you and you are extremely fond of them. <span class="def_cn cn_after">
								<span class="chinese-text">心肝宝贝；掌上明珠</span>
							</span>'''

# 解析HTML片段
soup = BeautifulSoup(html_snippet, 'html.parser')

# 查找第一个包含中文的span标签
first_chinese_span = soup.find('span', class_='def_cn cn_before')

if first_chinese_span:
    # 提取第一个中文
    first_chinese_text = first_chinese_span.find('span', class_='chinese-text').get_text(strip=True)
    
    # 获取该标签之后的所有文本兄弟节点，直到遇到下一个 .def_cn 标签
    current_element = first_chinese_span.next_sibling
    english_part = ""

    while current_element:
        # 如果遇到了下一个 .def_cn 标签（比如 cn_after），就停止
        if hasattr(current_element, 'name') and current_element.name == 'span' and 'def_cn' in current_element.get('class', []):
            break
        
        # 关键修改：使用 isinstance 来判断对象类型
        # NavigableString 是 BeautifulSoup 中代表文本节点的基类
        if isinstance(current_element, NavigableString):
            # 如果是文本节点，则添加其内容
            text_content = current_element.strip()
            if text_content: # 只添加非空的文本
                english_part += text_content
        # 如果是标签（Tag），则获取其文本内容
        elif hasattr(current_element, 'get_text'):
            english_part += current_element.get_text(strip=False) # 保留标签内的空格和格式
            
        current_element = current_element.next_sibling

    # 将两部分拼接起来
    result = f"{first_chinese_text} {english_part.strip()}"
    
    print(result)

else:
    print("未找到指定的HTML元素。")

# --- 更加健壮和通用的方法 ---
# 上面的方法依赖于HTML的严格结构。一个更健壮的方式是直接获取cn_before和cn_after之间的所有内容。

# 重新解析
soup2 = BeautifulSoup(html_snippet, 'html.parser')

# 找到第一个 .def_cn.cn_before 标签
start_span = soup2.find('span', class_='def_cn cn_before')

if start_span:
    # 找到第二个 .def_cn 标签 (即 cn_after)
    end_span = start_span.find_next_sibling('span', class_='def_cn')

    # 获取起始span的第一个中文
    first_chinese = start_span.get_text(strip=True)

    # 获取起始span和结束span之间的所有内容
    content_between = []
    current = start_span.next_sibling
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
    print("\n使用更通用方法的结果:")
    print(final_result)