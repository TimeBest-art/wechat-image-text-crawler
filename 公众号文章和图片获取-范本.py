import requests
from bs4 import BeautifulSoup
from PIL import Image
from fpdf import FPDF
import io
import os

#自定义的函数
from my_defined import remove_emojis

"""
requests: 用于发送HTTP请求，获取网页内容。
BeautifulSoup: 用于解析HTML文档，方便提取网页中的信息。
PIL.Image: 用于处理图像文件，如打开和保存图像。
fpdf.FPDF: 用于创建PDF文件的库。
io: 用于处理字节流，特别是在需要使用字节流而不是文件时。
"""

# 网页链接
url = 'https://mp.weixin.qq.com/s/OHO5AQWSiUyrzVPF4S0g6g'
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36'}
response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.content, 'html.parser')

"""
url: 需要爬取的网页地址。
headers: 包含用户代理信息，模拟浏览器访问以防止被网站屏蔽。
response: 发送GET请求并获取响应。
soup: 使用BeautifulSoup解析获取的HTML内容，便于后续操作。
"""

# 初始化 PDF
pdf = FPDF()
# 添加支持中文的字体
pdf.add_font('SimSun', '', '/Users/tanwenyu/Desktop/python- code/pythonProject/simsun.ttf')
pdf.set_auto_page_break(auto=True)
pdf.add_page()

"""
pdf = FPDF(): 创建一个FPDF对象。
add_font(): 添加中文字体SimSun，以便在PDF中支持中文字符。
set_auto_page_break(): 设置自动分页，超过页面边界时自动换页。
add_page(): 添加一页PDF文档。
"""


# 设置字体为 SimSun
pdf.set_font('SimSun', '', 10)

# 遍历网页内容，按顺序添加到 PDF
"""
find_all(['p', 'img']): 找到所有的段落（<p>）和图片（<img>）元素。
使用循环遍历这些元素，分别处理文本和图片。
"""
want_get = soup.body.find_all(['p', 'img'])
for element in want_get:
    if element.name == 'p':
        span_elements = element.find_all('span')  #find_all('span'): 在每个段落中找到所有的<span>元素。
        for span_element in span_elements:
            span_text = span_element.get_text(strip=True) #get_text(strip=True): 提取文本，去除前后的空格。
            span_text = remove_emojis(span_text)
            if span_text:  #确认不是空文本
                # 计算文本宽度和页面剩余高度
                text_width = pdf.get_string_width(span_text)
                available_width = pdf.w - pdf.r_margin - pdf.l_margin
                line_height = 5  # 行高，根据需要调整
                remaining_height = pdf.h - pdf.get_y() - pdf.b_margin  # 计算页面剩余高度

                # 如果剩余高度不足，自动添加新页
                if remaining_height < line_height:
                    pdf.add_page()

                # 检查文本是否超出可用宽度
                if text_width > available_width:
                    # 使用 multi_cell 进行换行
                    pdf.multi_cell(0, line_height, span_text)
                else:
                    # 使用 cell 添加文本，不换行
                    pdf.cell(0, line_height, span_text)
                pdf.ln()  # 添加换行以便下一行文本从新的一行开始
    elif element.name == 'img':
        img_url = element.get('data-src') #get('data-src'): 获取图片的URL。
        if img_url:
            img_data = requests.get(img_url).content  #requests.get(img_url).content: 发送请求获取图片数据。
            img = Image.open(io.BytesIO(img_data))    #这是一个PIL图像对象，可以用来进行各种图像处理操作，比如获取图像的尺寸、格式转换、图像编辑等。
            width, height = img.size                  #img.size: 获取图片的宽度和高度。
            aspect_ratio = height / float(width)      #aspect_ratio: 计算图片的宽高比，以便在插入PDF时保持比例。
            pdf_width = 180                           #pdf_width: 设置PDF中图片的宽度（180）。
            pdf_height = pdf_width * aspect_ratio     #pdf_height: 计算根据宽度调整后的高度。

            # 判断剩余高度是否足够
            remaining_height = pdf.h - pdf.get_y() - pdf.b_margin   # 剩余高度=页面高度 - 当前的 Y 位置 - 下边距
            if pdf_height > remaining_height:
                pdf.add_page()  # 如果不够，添加新页面

            # 直接插入图片，不保存为临时文件
            pdf.image(img, x=10, y=pdf.get_y(), w=pdf_width)    #pdf.image(): 将图片插入PDF（要插入的图像文件的路径或文件对象），指定位置和宽度。
            pdf.ln(pdf_height)  # 添加额外的行高，以便下一个元素不会覆盖当前图片。

# 指定保存的文件夹路径（确保路径存在）
output_folder = '/Users/tanwenyu/Desktop/近期任务/获取数据集任务/公众号文章获取'  # output_folder: 这是一个字符串变量，定义了要保存 PDF 文件的目标文件夹路径。
pdf_file_path = os.path.join(output_folder, "中央空调技术人员操作规范手册.pdf")

"""
os.path.join(): 这个函数用于将多个路径组件组合成一个完整的路径。这样做的好处是，它能够自动处理不同操作系统中的路径分隔符，确保路径的正确性。
output_folder: 目标文件夹的路径。
"中央空调技术人员操作规范手册.pdf": 要保存的 PDF 文件的名称。
pdf_file_path: 这个变量将存储组合后的完整路径，包括文件夹路径和文件名，例如：/Users/tanwenyu/Desktop/近期任务/获取数据集任务/公众号文章获取/中央空调技术人员操作规范手册.pdf。
"""

# 保存生成的 PDF
pdf.output(pdf_file_path)  #pdf.output(pdf_file_path): 这个方法用于将生成的 PDF 文件保存到指定的路径（即 pdf_file_path 变量中的路径）。这个函数会创建一个新的 PDF 文件，并将当前的 PDF 内容写入该文件。如果路径中的文件夹不存在，代码将引发错误。
print("PDF 文件已生成，保存在:", pdf_file_path)

