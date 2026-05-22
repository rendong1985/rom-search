import urllib.request
import csv
import json
import io
import re

# 【用你自己的谷歌表格 CSV 链接替换这里】
EXCEL_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRTIvrt1znX5OZRt_W9r4bVXlsSZrXtr_d-wuPOH2ggH8Ncp74up9lInFOPzWRiA0qG6WF71yppDrbE/pub?gid=0&single=true&output=csv
"

def parse_link_item(raw_item):
    if ',' not in raw_item:
        return None
    name, content = raw_item.split(',', 1)
    name, content = name.strip(), content.strip()
    
    # 提取提取码/密码
    pwd_match = re.search(r'(?:密码|pwd|提取码)[:=：]\s*([a-zA-Z0-9]+)', content)
    password = pwd_match.group(1) if pwd_match else ""
    
    # 提取纯净 URL
    url_match = re.search(r'(https?://[^\s]+)', content)
    url = url_match.group(1) if url_match else content
    
    if not url.startswith('http'):
        return {"name": name, "url": "", "value": content}
        
    return {"name": name, "url": url, "pwd": password}

def sync_excel():
    try:
        response = urllib.request.urlopen(EXCEL_CSV_URL)
        csv_text = response.read().decode('utf-8')
        reader = csv.reader(io.StringIO(csv_text))
        next(reader) # 跳过表头
        
        rom_database = []
        for row in reader:
            if not row or not row[0].strip():
                continue
            model, chip, desc, raw_links = row[0].strip(), row[1].strip(), row[2].strip(), row[3].strip()
            
            links_list = []
            if raw_links:
                items = re.split(r'[\|｜]', raw_links)
                for item in items:
                    parsed = parse_link_item(item)
                    if parsed:
                        links_list.append(parsed)
            
            rom_database.append({"model": model, "chip": chip, "desc": desc, "links": links_list})
            
        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(rom_database, f, ensure_ascii=False, indent=4)
        print("🎉 Sync Success!")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    sync_excel()
