import requests
from bs4 import BeautifulSoup
from PIL import Image
from fpdf import FPDF
import io
import os
import subprocess
from my_defined import remove_emojis

# 网页链接
url = 'https://mp.weixin.qq.com/s/TmlPfBD3inRLY37SDGz42Q'
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36'
}
response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.content, 'html.parser')

# 获取网页标题
title_element = soup.find('h1', class_='rich_media_title', id='activity-name')
title = title_element.get_text(strip=True) if title_element else '默认标题'  # 若找不到标题则使用默认值

# 初始化 PDF
pdf = FPDF()
pdf.add_font('SimSun', '', '/Users/tanwenyu/Desktop/python- code/pythonProject/微信公众号获取文章/simsun.ttf')
pdf.set_auto_page_break(auto=True)
pdf.add_page()
pdf.set_font('SimSun', '', 10)

# 遍历网页内容，按顺序添加到 PDF
want_get = soup.body.find_all(['p', 'section','span', 'img', 'table'])
for element in want_get:
    # 处理没有子标签且包含文本的 <p>、<section> 或 <span> 标签
    if element.name in ['p', 'section'] and not element.find_parent('table') and len(element.find_all(recursive=False)) == 0:
        text = element.get_text(strip=True)
        text = remove_emojis(text)
        if text:
            text_width = pdf.get_string_width(text)
            available_width = pdf.w - pdf.r_margin - pdf.l_margin
            line_height = 10
            remaining_height = pdf.h - pdf.get_y() - pdf.b_margin

            if remaining_height < line_height:
                pdf.add_page()

            if text_width > available_width:
                pdf.multi_cell(0, line_height, text)
            else:
                pdf.cell(0, line_height, text)
            pdf.ln()

    # 处理直接包含文本的 <span> 标签
    elif element.name == 'span' and not element.find_parent('table')and len(element.find_all(recursive=False)) == 0:
        span_text = element.get_text(strip=True)
        span_text = remove_emojis(span_text)
        if span_text:
            text_width = pdf.get_string_width(span_text)
            available_width = pdf.w - pdf.r_margin - pdf.l_margin
            line_height = 10
            remaining_height = pdf.h - pdf.get_y() - pdf.b_margin

            if remaining_height < line_height:
                pdf.add_page()

            if text_width > available_width:
                pdf.multi_cell(0, line_height, span_text)
            else:
                pdf.cell(0, line_height, span_text)
            pdf.ln()

    elif element.name == 'img':
        img_url = element.get('data-src')
        if img_url:
            img_data = requests.get(img_url).content
            img = Image.open(io.BytesIO(img_data))
            width, height = img.size
            aspect_ratio = height / float(width)
            pdf_width = 180
            pdf_height = pdf_width * aspect_ratio

            remaining_height = pdf.h - pdf.get_y() - pdf.b_margin
            if pdf_height > remaining_height:
                pdf.add_page()

            pdf.image(img, x=10, y=pdf.get_y(), w=pdf_width)
            pdf.ln(pdf_height)
        pdf.ln(10)  # 在表格和其他内容之间添加空行

    elif element.name == 'table':
        # 提取表格数据
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

        max_cols = max(len(row) for row in table_data)
        col_width = (pdf.w - pdf.r_margin - pdf.l_margin) / max_cols
        row_height = 8

        remaining_height = pdf.h - pdf.get_y() - pdf.b_margin
        table_height = len(table_data) * row_height
        if remaining_height < table_height:
            pdf.add_page()

        for row in table_data:
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
