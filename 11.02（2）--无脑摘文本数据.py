import requests
from bs4 import BeautifulSoup
from PIL import Image
from fpdf import FPDF
import io
import os
import subprocess
from my_defined import remove_emojis

# 网页链接
url = 'https://mp.weixin.qq.com/s/1QWIvVkMQejCcewfnVDqlA'
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36'
}
response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.content, 'html.parser')

# 获取网页标题
title_element = soup.find('h1', class_='rich_media_title', id='activity-name')
title = title_element.get_text(strip=True) if title_element else '默认标题'  # 若找不到标题则使用默认值

# 删除标题中的斜杠以避免路径错误
title = title.replace('/', '')  # 替换斜杠

# 初始化 PDF
pdf = FPDF()
pdf.add_font('SimSun', '', '/Users/tanwenyu/Desktop/python- code/pythonProject/微信公众号获取文章/simsun.ttf')
pdf.set_auto_page_break(auto=True)
pdf.add_page()
pdf.set_font('SimSun', '', 10)

# 存储提取的内容
content_list = []

# 遍历网页内容，按顺序添加到 content_list
want_get = soup.body.find_all(['div','p', 'section', 'span', 'img', 'table'])
for element in want_get:
    # 处理 <p> 和 <section> 标签
    if element.name in ['p', 'section'] and not element.find_parent('table'):
        text = element.get_text(strip=True)
        #text = remove_emojis(text)
        if text and not any(text in item for item in content_list):  # 检查是否已经存在
            content_list.append(('text', text))

    # 处理 <div> 标签
    if element.name in ['div'] and not element.find_parent('table'):
        div_text = element.get_text(strip=True)
        #div_text = remove_emojis(div_text)
        if div_text and not any(div_text in item for item in content_list):  # 检查是否已经存在
            content_list.append(('text', div_text))

    # 处理 <span> 标签
    elif element.name == 'span' and not element.find_parent('table'):
        span_text = element.get_text(strip=True)
        #span_text = remove_emojis(span_text)
        if span_text and not any(span_text in item for item in content_list):  # 检查是否已经存在
            content_list.append(('text', span_text))


    # 处理图片
    elif element.name == 'img':
        img_url = element.get('data-src')
        if img_url and not any(img_url in item for item in content_list):  # 检查是否已经存在
            content_list.append(('img', img_url))

    # 处理表格
    elif element.name == 'table':
        rows = element.find_all('tr')
        table_data = []
        for row in rows:
            cells = row.find_all(['td', 'th'])
            row_data = []
            for cell in cells:
                spans = cell.find_all('span')
                cell_text = " ".join(span.get_text(strip=True) for span in spans)
                row_data.append(cell_text)
            table_data.append(row_data)

        if table_data and not any(table_data in item for item in content_list):  # 检查是否已经存在
            content_list.append(('table', table_data))

"""
# 遍历 content_list 中的内容
for content_type, content in content_list:
    # 检查是否为文本类型
    if content_type == 'text':
        print(content)  # 输出文本内容
"""

#计算页面的可用宽度。pdf.w 是页面宽度，pdf.r_margin 和 pdf.l_margin 是页面的左右边距。
available_width = pdf.w - pdf.r_margin - pdf.l_margin
line_height = 10

# 将提取的内容添加到 PDF
for content_type, content in content_list:
    if content_type == 'text':
        text_width = pdf.get_string_width(content)
        remaining_height = pdf.h - pdf.get_y() - pdf.b_margin
        if remaining_height < line_height:
            pdf.add_page()
        if text_width > available_width:
            pdf.multi_cell(0, line_height, content)
        else:
            pdf.cell(0, line_height, content)
        pdf.ln()


    elif content_type == 'img':
        img_data = requests.get(content).content
        img = Image.open(io.BytesIO(img_data))
        width, height = img.size
        aspect_ratio = height / float(width)
        pdf_width = 180
        pdf_height = pdf_width * aspect_ratio

        remaining_height = pdf.h - pdf.get_y() - pdf.b_margin
        if pdf_height > remaining_height:
            pdf.add_page()

        pdf.image(io.BytesIO(img_data), x=10, y=pdf.get_y(), w=pdf_width)
        pdf.ln(pdf_height + 10)  # 在图片后添加空行

    elif content_type == 'table':
        max_cols = max(len(row) for row in content)
        col_width = (pdf.w - pdf.r_margin - pdf.l_margin) / max_cols
        row_height = 8

        remaining_height = pdf.h - pdf.get_y() - pdf.b_margin
        table_height = len(content) * row_height
        if remaining_height < table_height:
            pdf.add_page()

        for row in content:
            for cell in row:
                pdf.cell(col_width, row_height, cell, border=1, align='C')
            pdf.ln(row_height + 10)

# 指定保存的文件夹路径，并使用网页标题作为文件名
output_folder = '/Users/tanwenyu/Desktop/近期任务/获取数据集任务/公众号文章获取'
pdf_file_path = os.path.join(output_folder, f"{title}.pdf")

# 保存生成的 PDF
pdf.output(pdf_file_path)
print("PDF 文件已生成，保存在:", pdf_file_path)

# 自动打开 PDF 文件
subprocess.Popen(['open', pdf_file_path])  # 在 macOS 上打开文件
