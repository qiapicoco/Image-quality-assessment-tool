# 图片质量评估工具

*评估数据仅供参考*

## 项目简介

本项目是一个基于 Python 的图片质量评估工具，通过图形用户界面（GUI），用户能够方便地选择图片文件，并对其进行多项指标的评估，包括清晰度、亮度、对比度、分辨率、宽高比、构图方式、文件格式以及图片质量等级等。评估结果直观展示在界面上，同时提供了详细的参数说明，帮助用户理解各项指标的含义。

![演示图片](./image/演示.png)

## 功能特性

1. **多格式支持**

   支持读取常见的图片格式，包括 `.jpg`、`.jpeg`、`.png`、`.gif`、`.webp`、`.raw` 等多种图片格式。

2. **全面的指标评估**

   - **清晰度**：使用 [拉普拉斯算法](https://docs.opencv.ac.cn/4.11.0/d5/db5/tutorial_laplace_operator.html) 计算灰度图像的二阶导数，通过方差衡量图像边缘和细节的丰富程度。
   
   - **亮度与对比度**：将彩色图像转换为灰度图，计算像素灰度平均值得到亮度，通过像素灰度标准差评估对比度。
   
   
   - **分辨率与宽高比**：准确获取图像的水平和垂直像素数，判断分辨率标准（如 8K、4K 等），并计算宽高比，优先匹配预定义的分辨率信息，否则化简到最简形式。
   
   - **构图方式**：根据图像宽高关系，自动判断为横图、竖图或方图。
   
   - **文件格式识别**：准确识别图片文件的格式。
   
   
   - **质量等级划分**：依据清晰度等指标，将图片质量划分为高、中、低三个等级。
   
3. **图形化界面**：基于 `Tkinter` 库构建简洁易用的 GUI 界面，方便用户操作和查看结果。

## 安装与使用

### 安装依赖

> 如果下载速度太慢，就更换镜像库：
>
> ```python
>pip install -i https://pypi.tuna.tsinghua.edu.cn/simple pip -U
>pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
>```


确保已经安装以下 Python 库：

- `tkinter`：Python 标准 GUI 库，一般随 Python 安装自带。

- `Pillow`：用于图像处理，可通过 `pip install pillow` 安装。

- `opencv-python`：计算机视觉库，执行 `pip install opencv-python` 安装。

- `rawpy`：用于处理 RAW 格式图片，使用 `pip install rawpy` 安装。

**一键安装：**

```python
pip install pillow opencv-python rawpy 
```

### 运行程序

下载本项目代码后，找到 `Image-quality-assessment-tool.py` 文件，在命令行中进入该文件所在目录，运行程序。

### 使用步骤

1. 运行程序后，会弹出 “图片质量评估工具” 窗口。

1. 点击 “选择图片” 按钮，在弹出的文件选择对话框中，选择要评估的图片文件。支持多种图片格式，文件类型筛选框中列出了所有支持的格式。

1. 选择图片后，程序将自动进行各项指标的评估，并在右侧的 “评估结果和说明” 区域显示评估结果，同时在左侧显示图片的缩略图。

1. 下方的 “参数说明” 部分对各项评估指标进行了详细解释，方便用户理解评估结果。

## 代码结构

1. **Image-quality-assessment-tool.py**：主程序文件，包含图形用户界面的创建、图片选择功能、各项评估函数的调用以及结果显示逻辑。

1. **resolution_info.py**：存储分辨率相关信息的字典，用于辅助判断图像的分辨率标准和宽高比。

字典参考资料：

[aspect-ratio, 宽高比, 像素分辨率, 备忘清单 - 敲码拾光--编程开发者的百宝箱](https://www.zhifeiya.cn/reference/aspect-ratio.html)

[揭秘电视分辨率：1080p、2K、UHD、4K、8K，它们都是什么鬼？ - 科技行者](https://www.techwalker.com/2016/0128/3072316.shtml)

## 关于打包

1. 安装 `pyinstaller`：命令是 `pip install pyinstaller`
2. 要保证 `icon.ico` 、`Image-quality-assessment-tool.py` 和 `resolution_info.py` 都在同一个文件夹中。

 > ```python
 >`ico`文件是图标。
 > `Image-quality-assessment-tool.py`文件相当于main.py主文件。
 >`resolution_info.py`是字典，也就是主文件的部分数据进行关联，或者说是依赖文件。
 > ```

**打包命令：**

```python
pyinstaller --onefile --windowed --icon=image/icon.ico Image-quality-assessment-tool.py
```

