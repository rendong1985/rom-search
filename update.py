import json, re, os, sys

# 从环境变量获取 Issue 内容
body = os.environ.get("ISSUE_BODY", "")

def get_section(title):
    pattern = rf"### {title}\n\n(.*?)(?=\n\n###|$)"
    match = re.search(pattern, body, re.DOTALL)
    return match.group(1).strip() if match else ""

model = get_section("机型名称")
chip = get_section("芯片型号")
desc = get_section("描述信息")
link_raw = get_section("资源链接")

if "," in link_raw:
    name, url = link_raw.split(",", 1)
else:
    name, url = "资源下载", link_raw

new_entry = {
    "model": model,
    "chip": chip,
    "desc": desc,
    "links": [{"name": name.strip(), "url": url.strip()}]
}

# 读取并写入
if os.path.exists("data.json"):
    with open("data.json", "r", encoding="utf-8") as f:
        data = json.load(f)
else:
    data = []

data.append(new_entry)

with open("data.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=4)
