from page_parser import parse_page

with open("./page.html", encoding="utf-8") as file:
    html_content = file.read()
res = parse_page(html_content)
print(res)
