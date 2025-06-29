import os
import requests
from bs4 import BeautifulSoup
import re

# 目标URL列表
# 这些URL是用于获取优选IP地址的来源
urls = [
    'https://api.uouin.com/cloudflare.html',
    'https://ip.164746.xyz'
]

# 正则表达式用于匹配标准IPv4地址格式
ip_pattern = r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}'

# 定义要从每个网站获取的优选IP数量
TOP_N_IPS = 10

# ------------------------- 脚本开始执行 -------------------------

print("正在准备收集IP地址...")

# 检查ip.txt文件是否存在，如果存在则删除它
# 这样可以确保每次运行时都从一个干净的文件开始
if os.path.exists('ip.txt'):
    os.remove('ip.txt')
    print("已删除旧的 ip.txt 文件，准备写入新的IP。")
else:
    print("ip.txt 文件不存在，将创建新文件。")

# 使用一个集合 (set) 来存储从所有网站收集到的最终唯一IP地址
# 集合会自动处理重复项，确保最终文件中每个IP只出现一次
all_unique_ips_collected = set()

# 遍历目标URL列表，逐个网站获取IP
for url in urls:
    print(f"\n正在从网站: {url} 获取IP地址...")
    try:
        # 发送HTTP GET请求获取网页内容
        # timeout参数设置了请求的超时时间，防止长时间无响应
        response = requests.get(url, timeout=10)
        # 检查HTTP响应状态码，如果不是200（成功），则抛出HTTPError异常
        response.raise_for_status()
        
        # 使用BeautifulSoup解析网页的HTML内容
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 定义一个列表来临时存储当前网站找到的所有IP地址
        # 即使这里有重复或超过TOP_N_IPS，后续也会进行处理
        raw_ips_from_current_url = []
        
        # 根据这两个网站的HTML结构，IP地址通常包含在 <tr> 标签中
        elements_containing_ips = soup.find_all('tr')
        
        # 遍历所有找到的 <tr> 元素，提取其中的IP地址
        for element in elements_containing_ips:
            element_text = element.get_text()
            # 使用正则表达式在元素文本中查找所有匹配的IP地址
            ip_matches = re.findall(ip_pattern, element_text)
            
            # 将找到的IP地址添加到当前网站的IP列表中
            for ip in ip_matches:
                raw_ips_from_current_url.append(ip)
        
        # 从当前网站的原始IP列表中，筛选出前 TOP_N_IPS 个不重复的IP
        # 使用一个临时的集合来追踪已经添加过的IP，确保唯一性
        unique_and_top_ips_from_url = []
        seen_ips_for_current_url = set()
        
        for ip in raw_ips_from_current_url:
            # 如果IP不在已“见过”的集合中，并且尚未达到所需的TOP_N_IPS数量
            if ip not in seen_ips_for_current_url and len(unique_and_top_ips_from_url) < TOP_N_IPS:
                unique_and_top_ips_from_url.append(ip) # 添加到有序列表
                seen_ips_for_current_url.add(ip) # 标记为已“见过”
        
        print(f"从 {url} 成功获取到 {len(unique_and_top_ips_from_url)} 个优选IP。")
        
        # 将当前网站收集到的优选IP添加到所有网站的唯一IP总集合中
        for ip in unique_and_top_ips_from_url:
            all_unique_ips_collected.add(ip)

    except requests.exceptions.RequestException as e:
        # 捕获请求相关的异常，如网络问题、超时等
        print(f"从 {url} 获取数据时发生网络或HTTP错误: {e}")
    except Exception as e:
        # 捕获其他任何可能发生的未知错误
        print(f"处理 {url} 时发生未知错误: {e}")

# 所有网站的IP收集完毕后，将汇总的唯一IP地址写入ip.txt文件
# 'w' 模式会覆盖现有文件，这在脚本开始时已通过 os.remove() 确保
with open('ip.txt', 'w') as file:
    for ip in sorted(list(all_unique_ips_collected)): # 可选：写入前对IP进行排序，使文件内容有序
        file.write(ip + '\n')

print(f'\n已将 {len(all_unique_ips_collected)} 个优选IP地址保存到 ip.txt 文件中。')
print("脚本执行完毕。")

