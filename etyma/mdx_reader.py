from readmdict import MDX
from bs4 import BeautifulSoup
from bs4 import Tag

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

def parse_content(html_content, word):
    # 解析HTML内容
    soup = BeautifulSoup(html_content, 'html.parser')

    # 查找所有包含定义的 caption 标签
    captions = soup.find_all('div', {'class': 'caption hide_cn'})
    results = []
    for caption in captions:
        # 查找词性标签
        st_tag = caption.find('span', {'class': 'st'})
        if st_tag:
            # 提取词性 (e.g., N-VAR, PHRASE)
            word_type = st_tag.get_text(strip=True)
            
            # 查找中文释义 (第一个)
            first_chinese_span = caption.find('span', {'class': 'def_cn cn_before'})
            if first_chinese_span:
                tag = first_chinese_span.find('span', class_='chinese-text')
                chinese_def = tag.get_text(strip=True) if tag else ""
                # chinese_def = first_chinese_span.find('span', {'class': 'chinese-text'}).get_text(strip=True)
            else:
                # 如果没有cn_before，可能在after里，或者结构不同
                chinese_def = ""
            
            # 提取整行的文本内容，并移除所有内部标签（如<b>, <a>等）以获得纯净的文本
            # 我们需要复制一份caption对象来操作，以免影响原soup
            caption_text_clone = BeautifulSoup(str(caption), 'html.parser')
            
            # 移除所有标签，只保留文本
            for tag in caption_text_clone.find_all():
                if tag.name not in ['br']:  # 保留换行标签，如果有的话
                    tag.unwrap()
            
            # 获取清理后的纯文本
            full_text = caption_text_clone.get_text(separator=' ', strip=True)
            
            # 我们的目标是从完整文本中分离出 "类型", "中文", "英文定义" 部分
            # 一种更可靠的方法是，从找到的元素位置开始分割
            # 找到英文定义部分：从中文标签后开始，到下一个中文标签前结束
            
            # 为了更精确，我们直接获取caption下的所有文本节点
            parts = []
            for element in caption.children:
                # print(f"元素类型: {type(element)}, 内容: {str(element)}")  # 打印元素类型和内容预览
                if hasattr(element, 'name') and element.name == 'span':
                    # 如果是span，获取其文本
                    if 'st' in element.get('class', []) or 'def_cn' in element.get('class', []):
                        parts.append(element.get_text(strip=True))
                elif hasattr(element, 'strip'):  # 如果是字符串节点
                    stripped_text = element.strip
                    if stripped_text and not callable(stripped_text):
                        parts.append(stripped_text)
            
            # 组合文本，通常顺序是 [序号, 词性, 中文, 英文定义...]
            # 我们可以根据已知的词性和中文来截取英文部分
            combined_text = ' '.join(parts)
            
            # 从combined_text中，我们可以找到中文的位置，然后提取其后的英文部分
            # 为了简化，我们直接使用BeautifulSoup的get_text方法，但排除掉特定的span
            # 重新构建一个不含中文span的文本
            
            # 创建一个副本用于处理
            caption_for_en_def = BeautifulSoup(str(caption), 'html.parser')
            # 删除包含中文的span
            for span in caption_for_en_def.find_all('span', {'class': 'def_cn'}):
                span.decompose() # 彻底删除该标签及其内容
            
            # 现在获取剩余的文本，这就是英文定义部分
            english_def_part = caption_for_en_def.get_text(separator=' ', strip=True)
            # 清理掉序号、词性等部分
            import re
            # 移除开头的数字和词性标注
            cleaned_en_def = re.sub(r'^\d+\s*', '', english_def_part) # 移除开头的数字
            cleaned_en_def = re.sub(rf'{re.escape(word_type)}\s*', '', cleaned_en_def, count=1) # 移除第一个出现的词性
            cleaned_en_def = cleaned_en_def.strip()
            results.append((word_type, cleaned_en_def, chinese_def))
            # print(f"{word_type} {cleaned_en_def} {chinese_def}")    
    return word, results

def create_mdx_dictionary(mdx_file_path):
    if not mdx_file_path:
        # MDX 词典文件路径
        mdx_file_path = 'H:\\Program Files\\eudic\\Dict\\柯林斯双解增强版\\CollinsCOBUILDOverhaul V 2-30.mdx'        
    try:
        # 创建词典实例
        dictionary = MdxDictionary(mdx_file_path)

        return dictionary
    except FileNotFoundError:
        print(f"错误：找不到文件 {mdx_file_path}")
        raise
    except Exception as e:
        print(f"加载词典时发生错误: {e}")
        raise

def lookup_and_parse(dictionary, word):

    try:
        # 精确查询
        word_to_find = word
        definition = dictionary.lookup(word_to_find)
        
        if definition:
            print(f"\n--- 查询 '{word_to_find}' ---")
            return parse_content(definition, word)
        else:
            print(f"\n未找到单词: '{word_to_find}'")
            return word, []

        # TODO: 模糊查询
        # prefix_to_search = "app"
        # suggestions = dictionary.fuzzy_search(prefix_to_search, max_results=5)
        # print(f"\n--- 以 '{prefix_to_search}' 开头的单词 ---")
        # for word in suggestions:
        #     print(f"- {word}")

    except FileNotFoundError:
        print(f"错误：找不到文件 {mdx_file_path}")
    except Exception as e:
        print(f"加载或读取词典时发生错误: {e}")
        raise e
    
def main():
    dictionary = create_mdx_dictionary(None)
    lookup_and_parse(dictionary, "grate")

# --- 使用示例 ---
if __name__ == "__main__":
    main()