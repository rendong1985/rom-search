import urllib.request
import csv
import json
import io
import re

# 请确保这里替换成你最新的谷歌 CSV 链接
EXCEL_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRTIvrt1znX5OZRt_W9r4bVXlsSZrXtr_d-wuPOH2ggH8Ncp74up9lInFOPzWRiA0qG6WF71yppDrbE/pub?gid=0&single=true&output=csv"

def parse_link_item(raw_item):
    if ',' not in raw_item:
        return None
    name, content = raw_item.split(',', 1)
    name, content = name.strip(), content.strip()
    pwd_match = re.search(r'(?:密码|pwd|提取码)[:=：]\s*([a-zA-Z0-9]+)', content)
    password = pwd_match.group(1) if pwd_match else ""
    url_match = re.search(r'(https?://[^\s]+)', content)
    url = url_match.group(1) if url_match else content
    if not url.startswith('http'):
        return {"name": name, "url": "", "value": content}
    return {"name": name, "url": url, "pwd": password}

def sync_excel():
    try:
        response = urllib.request.urlopen(EXCEL_CSV_URL)
        csv_text = response.read().decode('utf-8')
        
        # 使用 DictReader 智能读取，它会自动把第一行当作“钥匙”来配对
        reader = csv.DictReader(io.StringIO(csv_text))
        
        # 打印一下它在你的表格第一行都找到了什么词（用于调试）
        headers = reader.fieldnames
        print(f"📡 成功读取表格！第一行检测到的表头为: {headers}")
        
        rom_database = []
        
        for index, row in enumerate(reader, start=2):
            # 智能提取，无视列的先后顺序，只要名字对上就行
            # 如果表格里写的是大写或者带空格，这里做了容错清洗
            model = (row.get('model') or row.get('model ') or '').strip()
            chip = (row.get('chip') or row.get('chip ') or '').strip()
            desc = (row.get('desc') or row.get('desc ') or '').strip()
            raw_links = (row.get('links') or row.get('links ') or '').strip()
            
            # 如果连机型都没填，说明是空行，跳过
            if not model:
                continue
                
            links_list = []
            if raw_links:
                items = re.split(r'[\|｜]', raw_links)
                for item in items:
                    parsed = parse_link_item(item)
                    if parsed:
                        links_list.append(parsed)
            
            rom_database.append({
                "model": model,
                "chip": chip,
                "desc": desc,
                "links": links_list
            })
            print(f"✅ 成功加载第 {index} 行: {model} ({chip})")
            
        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(rom_database, f, ensure_ascii=False, indent=4)
            
        print(f"\n🎉 终极大功告成！共成功写入 {len(rom_database)} 个资源到 data.json")
        
    except Exception as e:
        print(f"❌ 脚本运行崩溃: {e}")

if __name__ == "__main__":
    sync_excel()
