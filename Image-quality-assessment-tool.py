import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import cv2
import numpy as np
import rawpy


def read_image(file_path):
    """
    读取图片文件，支持 RAW 格式和常见图片格式。
    :param file_path: 图片文件路径
    :return: 读取成功返回 PIL 图像对象，失败返回 None
    """
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


def preprocess_image(image, target_size=(512, 512)):
    """
    预处理图片，转换为 RGB 格式并调整大小。
    :param image: PIL 图像对象
    :param target_size: 目标大小，默认为 (512, 512)
    :return: 处理后的 PIL 图像对象
    """
    return image.convert('RGB').resize(target_size, Image.LANCZOS)


def evaluate_sharpness(image):
    """
    评估图片清晰度，使用拉普拉斯算法。
    :param image: PIL 图像对象
    :return: 清晰度值（拉普拉斯算子方差）
    """
    img = np.array(image)
    img_gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    return cv2.Laplacian(img_gray, cv2.CV_64F).var()


def evaluate_brightness_contrast(image):
    """
    评估图片亮度和对比度。
    :param image: PIL 图像对象
    :return: 亮度值和对比度值（标准差）
    """
    img = np.array(image)
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    return np.mean(gray), np.std(gray)


def get_image_resolution(image):
    """
    获取图片分辨率和分辨率标准。
    :param image: PIL 图像对象
    :return: 分辨率字符串、宽度、高度和分辨率标准
    """
    width, height = image.size
    resolution = f"{width}x{height}"
    resolution_standard = ""
    resolutions = [
        (7680, 4320, "8K"),
        (3840, 2160, "4K"),
        (2048, 1080, "2K"),
        (1920, 1080, "1080p"),
        (1280, 720, "720p")
    ]
    for w, h, std in resolutions:
        if width >= w and height >= h:
            resolution_standard = std
            break
    return resolution, width, height, resolution_standard


def get_image_composition(width, height):
    """
    根据图片宽高判断构图类型。
    :param width: 图片宽度
    :param height: 图片高度
    :return: 构图类型字符串
    """
    if width == height:
        return "方图"
    return "横图" if width > height else "竖图"


def get_file_format(file_path):
    """
    获取图片文件格式。
    :param file_path: 图片文件路径
    :return: 文件格式字符串
    """
    format_mapping = {
        ".bmp": "BMP",
        ".jpg": "JPG",
        ".jpeg": "JPG",
        ".png": "PNG",
        ".tif": "TIF",
        ".tiff": "TIF",
        ".gif": "GIF",
        ".pcx": "PCX",
        ".tga": "TGA",
        ".exif": "EXIF",
        ".fpx": "FPX",
        ".svg": "SVG",
        ".psd": "PSD",
        ".pcd": "PCD",
        ".webp": "WEBP",
        ".avif": "AVIF",
        ".apng": "APNG",
        ".raw": "RAW"
    }
    import os
    file_extension = os.path.splitext(file_path)[1].lower()
    return format_mapping.get(file_extension, "未知格式")


def get_image_quality_level(sharpness):
    """
    根据清晰度评估图片质量等级。
    :param sharpness: 清晰度值
    :return: 图片质量等级字符串
    """
    if sharpness > 100:
        return "高"
    return "中" if sharpness > 50 else "低"


def select_image():
    """
    选择图片文件并进行评估，更新界面显示结果。
    """
    supported_formats = [
        ("所有支持的图片格式",
         "*.bmp;*.jpg;*.jpeg;*.png;*.tif;*.tiff;*.gif;*.pcx;*.tga;*.exif;*.fpx;*.svg;*.psd;*.pcd;*.webp;*.avif;*.apng;*.raw"),
        ("BMP 图片", "*.bmp"),
        ("JPEG 图片", "*.jpg;*.jpeg"),
        ("PNG 图片", "*.png"),
        ("TIFF 图片", "*.tif;*.tiff"),
        ("GIF 图片", "*.gif"),
        ("PCX 图片", "*.pcx"),
        ("TGA 图片", "*.tga"),
        ("EXIF 图片", "*.exif"),
        ("FPX 图片", "*.fpx"),
        ("SVG 图片", "*.svg"),
        ("PSD 图片", "*.psd"),
        ("PCD 图片", "*.pcd"),
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

            # 计算宽高比
            from math import gcd
            common_divisor = gcd(width, height)
            aspect_ratio = f"{width // common_divisor}:{height // common_divisor}"

            img = image.copy()
            img.thumbnail((400, 400))
            img_tk = ImageTk.PhotoImage(img)
            image_label.config(image=img_tk)
            image_label.image = img_tk

            result_text = f"图片读取成功：\n"
            result_text += f"清晰度: {sharpness:.2f}（无特定单位）\n"
            result_text += f"亮 度: {brightness:.2f}（灰度值范围 0-255）\n"
            result_text += f"对比度: {contrast:.2f}（标准差）\n"
            result_text += f"分辨率: {resolution}px（{resolution_standard}）\n"
            result_text += f"宽 度: {width}px\n"
            result_text += f"高 度: {height}px\n"
            result_text += f"宽高比: {aspect_ratio}\n"
            result_text += f"构 图: {composition}\n"
            result_text += f"文件格式: {file_format}\n"
            result_text += f"图片质量等级: {quality_level}"

            result_text_widget.config(state=tk.NORMAL)
            result_text_widget.delete(1.0, tk.END)
            result_text_widget.insert(tk.END, result_text)
            result_text_widget.config(state=tk.DISABLED)
        else:
            show_result("图片读取失败，无法进行后续评估")
    else:
        show_result("未选择文件路径")


def show_result(text):
    """
    在结果文本框中显示指定文本。
    :param text: 要显示的文本
    """
    result_text_widget.config(state=tk.NORMAL)
    result_text_widget.delete(1.0, tk.END)
    result_text_widget.insert(tk.END, text)
    result_text_widget.config(state=tk.DISABLED)


# 创建主窗口
root = tk.Tk()
root.title("图片质量评估工具")
# 设置窗口大小并居中
window_width = 1000
window_height = 600
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x = (screen_width / 2) - (window_width / 2)
y = (screen_height / 2) - (window_height / 2)
root.geometry(f"{window_width}x{window_height}+{int(x)}+{int(y)}")
# 设置窗口背景颜色
root.configure(bg='#ffffff')

# 创建选择图片按钮
select_button = tk.Button(root, text="选择图片", command=select_image,
                          font=("宋体", 13, 'bold'), bg='#007acc', fg='white', padx=10, pady=5)
select_button.grid(row=0, column=0, columnspan=3, pady=10)

# 创建左边框架（图片显示区域）
left_frame = tk.Frame(root, bg='#ffffff')
left_frame.grid(row=1, column=0, padx=10, pady=10)

# 创建显示图片的框架，固定大小
image_frame = tk.Frame(left_frame, bg='#ffffff', width=485, height=485)
image_frame.pack_propagate(0)
image_frame.pack(pady=10)
image_label = tk.Label(image_frame, bg='#ffffff')
image_label.pack()

# 创建分隔线
separator = tk.Frame(root, bg='black', width=2, height=window_height - 100)
separator.grid(row=1, column=1, sticky="ns")

# 创建右边框架（包含结果显示区域和指标说明区域）
right_frame = tk.Frame(root, bg='#ffffff')
right_frame.grid(row=1, column=2, padx=10, pady=10)

# 创建显示评估结果的框架，并添加滚动条
result_frame = tk.Frame(right_frame, bg='#ffffff')
result_frame.pack(pady=10)
result_frame.grid_propagate(False)
result_frame.config(width=300, height=200)
scrollbar = tk.Scrollbar(result_frame)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
result_text_widget = tk.Text(result_frame, bg='#ffffff', font=("宋体", 13, 'bold'), yscrollcommand=scrollbar.set,
                             height=12, width=40, spacing2=8)
result_text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
result_text_widget.config(state=tk.DISABLED)
scrollbar.config(command=result_text_widget.yview)

# 创建显示指标说明的框架
info_frame = tk.Frame(right_frame, bg='#ffffff')
info_frame.pack(pady=10)
info_text = [
    "清晰度：拉普拉斯算法算灰度二阶导数，方差大则边缘和细节丰富。",
    "亮 度：彩色图转灰度图，算像素灰度平均值衡量整体亮度。",
    "对比度：算灰度图像素灰度标准差，标准差大则对比度高。",
    "分辨率：图像水平和垂直像素数，格式为“宽x高”。",
    "宽 度：图像水平方向像素数量。",
    "高 度：图像垂直方向像素数量。",
    "宽高比：图片宽度与高度的最简整数比。",
    "构 图：据宽高关系判断横、竖、方图。",
    "文件格式：识别图像文件格式。",
    "图片质量等级：依清晰度等指标分高、中、低等级。"
]
for line in info_text:
    info_label = tk.Label(info_frame, text=line, bg='#ffffff', font=("楷体", 11), justify=tk.LEFT, anchor="w")
    info_label.pack(anchor="w")

root.mainloop()
