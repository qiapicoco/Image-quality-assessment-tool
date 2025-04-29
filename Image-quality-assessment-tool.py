import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import cv2
import numpy as np
import rawpy
from math import gcd
from resolution_info import resolution_info

# 新增的分辨率判断数据
additional_resolutions = [
    (7680, 4320, "8K"),
    (3840, 2160, "4K"),
    (2048, 1080, "2K"),
    (1920, 1080, "1080p"),
    (1280, 720, "720p")
]

# 读取图片文件，支持RAW格式和其他常见图片格式
def read_image(file_path):
    import os
    file_extension = os.path.splitext(file_path)[1].lower()
    try:
        if file_extension == '.raw':
            with rawpy.imread(file_path) as raw:
                rgb = raw.postprocess()
                return Image.fromarray(rgb)
        return Image.open(file_path)
    except Exception as e:
        print(f"读取图片时出错: {e}")
        return None

# 预处理图片：转换为RGB模式并调整大小
def preprocess_image(image, target_size=(512, 512)):
    return image.convert('RGB').resize(target_size, Image.LANCZOS)

# 评估图片清晰度，使用拉普拉斯算子计算灰度图方差
def evaluate_sharpness(image):
    img = np.array(image)
    img_gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    return cv2.Laplacian(img_gray, cv2.CV_64F).var()

# 评估图片亮度和对比度
def evaluate_brightness_contrast(image):
    img = np.array(image)
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    return np.mean(gray), np.std(gray)

# 获取图片分辨率信息
def get_image_resolution(image):
    width, height = image.size
    resolution = f"{width}×{height}"
    resolution_standard = ""

    # 先在 resolution_info 字典中查找
    for std, ratios in resolution_info.items():
        for ratio, res in ratios.items():
            w, h = map(int, res.split('x'))
            if width == w and height == h:
                resolution_standard = std
                break
        if resolution_standard:
            break

    # 如果在字典中未找到，使用 additional_resolutions 查找
    if not resolution_standard:
        for w, h, std in additional_resolutions:
            if width == w and height == h:
                resolution_standard = std
                break

    return resolution, width, height, resolution_standard

# 根据图片宽高比判断构图类型
def get_image_composition(width, height):
    if width == height:
        return "方图"
    return "横图" if width > height else "竖图"

# 获取图片文件格式
def get_file_format(file_path):
    format_mapping = {
        ".bmp": "BMP", ".jpg": "JPG", ".jpeg": "JPG", ".png": "PNG", ".tif": "TIF", ".tiff": "TIF",
        ".gif": "GIF", ".pcx": "PCX", ".tga": "TGA", ".svg": "SVG",
        ".psd": "PSD", ".webp": "WEBP", ".avif": "AVIF", ".apng": "APNG", ".raw": "RAW"
    }
    import os
    file_extension = os.path.splitext(file_path)[1].lower()
    return format_mapping.get(file_extension, "未知格式")

# 根据清晰度评估图片质量等级
def get_image_quality_level(sharpness):
    if sharpness > 100:
        return "高"
    return "中" if sharpness > 50 else "低"

# 计算图片的宽高比
def get_aspect_ratio(width, height):
    for std, ratios in resolution_info.items():
        for ratio_str, res in ratios.items():
            w, h = map(int, res.split('x'))
            if width == w and height == h:
                ratio_parts = ratio_str.split('(')[-1].split(')')[0]
                return ratio_parts
    common_divisor = gcd(width, height)
    simple_width = width // common_divisor
    simple_height = height // common_divisor
    return f"{simple_width}:{simple_height}"

# 弹出文件选择对话框，读取并分析图片
def select_image():
    supported_formats = [
        ("所有支持的图片格式",
         "*.bmp;*.jpg;*.jpeg;*.png;*.tif;*.tiff;*.gif;*.pcx;*.tga;*.svg;*.psd;*.webp;*.avif;*.apng;*.raw"),
        ("BMP 图片", "*.bmp"),
        ("JPEG 图片", "*.jpg;*.jpeg"),
        ("PNG 图片", "*.png"),
        ("TIFF 图片", "*.tif;*.tiff"),
        ("GIF 图片", "*.gif"),
        ("PCX 图片", "*.pcx"),
        ("TGA 图片", "*.tga"),
        ("SVG 图片", "*.svg"),
        ("PSD 图片", "*.psd"),
        ("WebP 图片", "*.webp"),
        ("AVIF 图片", "*.avif"),
        ("APNG 图片", "*.apng"),
        ("RAW 图片", "*.raw")
    ]
    file_path = filedialog.askopenfilename(filetypes=supported_formats)
    if file_path:
        image = read_image(file_path)
        if image:
            processed_image = preprocess_image(image)
            sharpness = evaluate_sharpness(processed_image)
            brightness, contrast = evaluate_brightness_contrast(processed_image)
            resolution, width, height, resolution_standard = get_image_resolution(image)
            composition = get_image_composition(width, height)
            file_format = get_file_format(file_path)
            quality_level = get_image_quality_level(sharpness)

            aspect_ratio = get_aspect_ratio(width, height)

            # 显示缩略图
            img = image.copy()
            img.thumbnail((400, 400))
            img_tk = ImageTk.PhotoImage(img)
            image_label.config(image=img_tk)
            image_label.image = img_tk

            # 显示评估结果
            result_text = f"图片读取成功. . . \n"
            result_text += f"清晰度: {sharpness:.2f}\n"
            result_text += f"亮  度: {brightness:.2f}\n"
            result_text += f"对比度: {contrast:.2f}\n"
            result_text += f"分辨率: {resolution}px  {resolution_standard}\n"
            result_text += f"宽  度: {width} px\n"
            result_text += f"高  度: {height} px\n"
            result_text += f"宽高比: {aspect_ratio}\n"
            result_text += f"构  图: {composition}\n"
            result_text += f"文件格式: {file_format}\n"
            result_text += f"图片质量等级: {quality_level}"

            result_text_widget.config(state=tk.NORMAL)
            result_text_widget.delete(1.0, tk.END)
            result_text_widget.insert(tk.END, result_text)
            result_text_widget.config(state=tk.DISABLED)
        else:
            show_result("图片读取失败，无法进行后续评估......")
    else:
        show_result("未选择文件路径......")

# 在结果显示区域显示文本
def show_result(text):
    result_text_widget.config(state=tk.NORMAL)
    result_text_widget.delete(1.0, tk.END)
    result_text_widget.insert(tk.END, text)
    result_text_widget.config(state=tk.DISABLED)

# 创建主窗口
root = tk.Tk()
root.title("图片质量评估工具[仅供参考]")
# 设置窗口大小并居中
window_width = 1180
window_height = 690
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x = (screen_width / 2) - (window_width / 2)
y = (screen_height / 2) - (window_height / 2)
root.geometry(f"{window_width}x{window_height}+{int(x)}+{int(y)}")
# 设置窗口背景颜色
root.configure(bg='#e8d7c6')
# 禁止窗口最大化
root.resizable(width=False, height=False)
# 创建选择图片按钮
select_button = tk.Button(root, text="选择图片", command=select_image, font=("宋体", 13, 'bold'), bg='#007acc', fg='white', padx=10, pady=5)
select_button.grid(row=0, column=0, columnspan=1, pady=10)

# 创建选择标签
label = tk.Label(root, text="评估结果和说明", font=("宋体", 13, 'bold'), bg='#6A5ACD', fg='white', padx=10, pady=5)
label.grid(row=0, column=2, columnspan=10, pady=(20,10))

# 创建左边框架（图片显示区域）
left_frame = tk.Frame(root, bg='#e8d7c6')
left_frame.grid(row=1, column=0, padx=10, pady=35)

# 创建显示图片的框架，固定大小
image_frame = tk.Frame(left_frame, bg='#e8d7c6', width=500, height=500)
image_frame.pack_propagate(0)
image_frame.pack(pady=20)
image_label = tk.Label(image_frame, bg='#e8d7c6')
image_label.pack()

# 创建分隔线
separator = tk.Frame(root, bg='#d68910', width=1, height=window_height - 100)
# 增加分隔线的 padx 值，使其向右移动
separator.grid(row=1, column=1, sticky="ns")

# 创建右边框架（包含结果显示区域和指标说明区域）
right_frame = tk.Frame(root, bg='#e8d7c6')
right_frame.grid(row=1, column=2, padx=10, pady=10)

# 创建显示评估结果的框架，并添加滚动条
result_frame = tk.Frame(right_frame, bg='#e8d7c6')
result_frame.pack(pady=10)
result_frame.grid_propagate(False)
result_frame.config(width=300, height=200)
scrollbar = tk.Scrollbar(result_frame)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
result_text_widget = tk.Text(result_frame, bg='#ffffff', font=("微软雅黑", 13), yscrollcommand=scrollbar.set,
                             height=12, width=50, spacing2=8)
result_text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
result_text_widget.config(state=tk.DISABLED)
scrollbar.config(command=result_text_widget.yview)

# 创建显示指标说明的框架
info_frame = tk.Frame(right_frame, bg='#e8d7c6')
info_frame.pack(padx=10,pady=10)
info_text = [
    "参数说明:",
    "清晰度：拉普拉斯算法算灰度二阶导数，方差大则边缘和细节丰富。(无特定单位)",
    "亮 度：彩色图转灰度图，算像素灰度平均值衡量整体亮度。(灰度值范围0~255)",
    "对比度：算灰度图像素灰度标准差，标准差大则对比度高。",
    "分辨率：图像水平和垂直像素数，格式为“宽×高”。",
    "宽 度：图像水平方向像素数量。",
    "高 度：图像垂直方向像素数量。",
    "宽高比：优先使用分辨率信息字典里的宽高比，无匹配则化简到最简。",
    "构 图：据宽高关系判断横、竖、方图。",
    "文件格式：识别图像文件格式。",
    "图片质量等级：依清晰度等指标分高、中、低等级。"
]
for line in info_text:
    info_label = tk.Label(info_frame, text=line, bg='#e8d7c6', font=("微软雅黑", 11), justify=tk.LEFT, anchor="w")
    info_label.pack(anchor="w")

root.mainloop()



