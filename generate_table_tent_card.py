# -*- coding: utf-8 -*-
"""
姓名桌签PDF生成器
从CSV、XLS、XLSX等格式文件读取姓名，生成包含所有桌签的PDF文件
每个桌签包含四个部分：空白、文字（倒）、文字、空白
"""

import pandas as pd
import sys
from pathlib import Path
from reportlab.lib.pagesizes import A4, LETTER, A3, landscape
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# ==================== 全局配置 ====================

# 纸张尺寸 (例如: A4, landscape(A3), LETTER, 等)
PAGE_SIZE = A4

# 字体文件路径，如果不存在则会尝试使用黑体
FONT_NAME = ''

# 文字区域高度 (单位: mm, 倒文字和正文字区域各占此高度，剩余为上下空白)
TEXT_HEIGHT_MM = 93

# 粘合标记线距纸张边框距离 (单位: mm)
GLUE_LINE_MM = 20

# 根据字数设置字体大小 (键为字数，0为默认值，单位: pt)
FONT_SIZES = {
    0: 118,   # 默认
}

# 根据字数设置字符间隔 (键为字数，0为默认值，单位: pt)
CHAR_SPACING = {
    0: 0,    # 默认 - 无额外间隔
    2: 48,   # 两个字
    3: 12,    # 三个字
}

# 文字两侧最小空白 (单位: pt)
SIDE_MARGIN = 40

# 页头
HEADER = None  # 页头文字，优先级高于表格，留空则从表格读取
HEADER_MARGIN = 20  # 页头距区域顶部距离 (单位: pt)
HEADER_FONT_SIZE = 24  # 页头字号

# 页脚
FOOTER = None  # 页脚文字，优先级高于表格，留空则从表格读取
FOOTER_MARGIN = 20  # 页脚距区域底部距离 (单位: pt)
FOOTER_FONT_SIZE = 24  # 页脚字号

# ================================================


def read_names_from_file(input_file):
    """
    从多种格式文件读取姓名 (支持 CSV、XLS、XLSX等)
    
    支持的格式:
    - CSV (.csv)
    - Excel XLS (.xls)
    - Excel XLSX (.xlsx)
    
    自动检测文件格式并使用相应的读取方法。
    优先查找 '姓名' 列，其次是 'name' 列。
    如果存在 '页头'、'header'、'页脚'、'footer' 列，则逐行读取对应值。
    如果全局变量 HEADER/FOOTER 已设置，则优先使用全局值覆盖所有行。
    返回列表: [(name, header, footer), ...]
    """
    data = []
    try:
        file_path = Path(input_file)
        if not file_path.exists():
            print(f"【错误】文件 {input_file} 不存在")
            return []
        
        suffix = file_path.suffix.lower()
        
        # 根据文件扩展名选择读取方法
        if suffix == '.csv':
            df = pd.read_csv(input_file, dtype=str)
        elif suffix in ['.xls', '.xlsx']:
            df = pd.read_excel(input_file, dtype=str)
        else:
            print(f"【错误】不支持的文件格式 {suffix}。支持的格式: .csv, .xls, .xlsx")
            return []
        
        # 查找姓名列（优先查找中文列名）
        name_column = None
        if '姓名' in df.columns:
            name_column = '姓名'
        elif 'name' in df.columns:
            name_column = 'name'
        elif len(df.columns) > 0:
            name_column = df.columns[0]
            print(f"【警告】未找到'姓名'或'name'列，使用第一列: '{name_column}'")
        else:
            print("【错误】文件中没有数据列")
            return []

        # 检查页头/页脚列
        header_column = None
        footer_column = None
        for col in ['页头', 'header', 'Header', 'HEADER']:
            if col in df.columns:
                header_column = col
                break
        for col in ['页脚', 'footer', 'Footer', 'Footer']:
            if col in df.columns:
                footer_column = col
                break

        # 提取数据
        for idx, row in df.iterrows():
            name = str(row[name_column]).strip()
            if name and name.lower() not in ['nan', 'none', 'nan.']:
                # 页头：优先全局，否则逐行
                header = HEADER or (str(row[header_column]).strip() if header_column and not pd.isna(row[header_column]) else '')
                # 页脚：优先全局，否则逐行
                footer = FOOTER or (str(row[footer_column]).strip() if footer_column and not pd.isna(row[footer_column]) else '')
                data.append((name, header, footer))
        
        if not data:
            print(f"【错误】未从 '{name_column}' 列读取到任何数据")
            return []
        
    except pd.errors.ParserError as e:
        print(f"【错误】解析文件时出错: {e}")
        return []
    except Exception as e:
        print(f"【错误】读取文件出错: {e}")
        return []
    
    return data


def register_fonts(font_path=None):
    """
    注册中文字体 (多平台支持)
    
    优先尝试使用用户指定的字体。
    其次尝试在系统中查找常见的中文字体。
    最后回退到 Helvetica。
    """
    if font_path:
        if Path(font_path).exists():
            try:
                short_name = Path(font_path).stem
                pdfmetrics.registerFont(TTFont(short_name, font_path))
                return short_name
            except Exception:
                print(f"【警告】警告: 导入{font_path}失败，使用黑体")
        else:
            print(f"【警告】警告: 未找到{font_path}，使用黑体")
    
    # 定义不同平台的中文字体搜索路径 (黑体的各种可能名称)
    font_paths = []
    if sys.platform == 'win32':
        # Windows 字体路径 (黑体的各种可能名称)
        font_paths = [
            "C:\\Windows\\Fonts\\simhei.ttf",
            "C:\\Windows\\Fonts\\SimHei.ttf",
            "C:\\Windows\\Fonts\\SIMHEI.TTF",
            "C:\\Windows\\SysWOW64\\Fonts\\simhei.ttf",
            "C:\\Windows\\SysWOW64\\Fonts\\SimHei.ttf",
        ]
    elif sys.platform == 'darwin':
        # macOS 字体路径 (黑体和STHeiti)
        font_paths = [
            "/Library/Fonts/simhei.ttf",
            "/Library/Fonts/SimHei.ttf",
            "/Library/Fonts/STHeiti Light.ttc",
            "/Library/Fonts/STHeiti.ttc",
            "/System/Library/Fonts/STHeiti Light.ttc",
            "/System/Library/Fonts/STHeiti.ttc",
        ]
    else:
        # Linux 字体路径 (SimHei, Noto Sans CJK等)
        font_paths = [
            "/usr/share/fonts/chinese/simhei.ttf",
            "/usr/share/fonts/truetype/SimHei/simhei.ttf",
            "/usr/share/fonts/truetype/noto/NotoSansCJK-Medium.ttc",
            "/usr/share/fonts/opentype/noto/NotoSansCJK-Medium.ttc",
            "/usr/share/fonts/truetype/droid/DroidSansFallback.ttf",
        ]
    
    # 尝试找到并注册字体
    for font_path in font_paths:
        try:
            if Path(font_path).exists():
                short_name = Path(font_path).stem
                pdfmetrics.registerFont(TTFont(short_name, font_path))
                print(f"【提示】使用字体{font_path}")
                return short_name
        except Exception:
            continue
    print(f"【警告】未找到黑体，请手动指定。使用Helvetica（仅限ACSII）")
    return 'Helvetica'


def generate_pdf(data, output_file='table_tent_cards.pdf'):
    """
    生成包含所有桌签的PDF
    
    每个桌签占满整页，布局（从上到下）:
    1. 空白区域 
    2. 文字倒过来  - 给对面的人看
    3. 文字正常 - 给这一面的人看
    4. 空白区域 
    """
    if not data:
        print("【错误】️没有要处理的姓名")
        return False
    
    font_name = register_fonts(FONT_NAME)
    
    # 创建PDF - 使用配置的纸张类型，每个桌签占满整页
    c = canvas.Canvas(output_file, pagesize=PAGE_SIZE)
    
    page_width, page_height = PAGE_SIZE
    
    # 输出尺寸信息
    page_width_mm = page_width / mm
    page_height_mm = page_height / mm
    glue_height_mm = GLUE_LINE_MM
    bottom_height_mm = page_height_mm - TEXT_HEIGHT_MM * 2 - GLUE_LINE_MM
    text_area_height_mm = TEXT_HEIGHT_MM
    # 桌签立起后高度
    standing_height_mm = (text_area_height_mm ** 2 - (bottom_height_mm / 2) ** 2) ** .5
    
    print(f"【尺寸信息】纸张尺寸: {page_width_mm:.1f}mm x {page_height_mm:.1f}mm")
    print(f"【尺寸信息】粘合距离: {glue_height_mm:.1f}mm 底部实际距离: {bottom_height_mm:.1f}mm 文字区域高度: {text_area_height_mm:.1f}mm")
    print(f"【尺寸信息】桌签宽度: {page_width_mm:.1f}mm 桌签高度: {standing_height_mm:.1f}mm")
    
    for item_idx, (name, header_text, footer_text) in enumerate(data):
        # 检查是否需要新页面（第一个名字不需要新页面）
        if item_idx > 0:
            c.showPage()
        
        # 绘制占满整页的卡片
        draw_card(c, 0, 0, page_width, page_height, name, font_name,
                  header_text=header_text, footer_text=footer_text)
    
    c.save()
    print(f"【成功】生成PDF: {output_file}")
    return True


def draw_card(c, x, y, width, height, name, font_name, header_text='', footer_text=''):
    """
    绘制单个桌签（占满整页）
    
    布局(根据TEXT_HEIGHT_MM计算):
    ========================
    |    上空白 (自动计算)   | 
    +-------- -- ---------+
    |     文字(倒过来)    | (TEXT_HEIGHT_MM)
    +-------- -- ---------+
    |      文字(正常)     | (TEXT_HEIGHT_MM)
    +-------- -- ---------+
    |    下空白 (自动计算)   | 
    ========================
    
    文字根据字数自动调整大小、间隔和水平缩放
    并为每个文字区域添加页头/页脚小字（header/footer）。
    """
    # 计算各区域高度
    text_height_pt = TEXT_HEIGHT_MM * mm
    empty_height = (height - 2 * text_height_pt) / 2
    section_heights = [empty_height, text_height_pt, text_height_pt, empty_height]
    
    # 设置横向分割线 - 浅灰色
    c.setLineWidth(0.5)
    light_gray = colors.HexColor('#D3D3D3')  # 浅灰色
    c.setStrokeColor(light_gray)
    
    # 绘制3条横线（分隔4个部分）
    line_y_positions = [
        y + section_heights[0],
        y + section_heights[0] + section_heights[1],
        y + section_heights[0] + section_heights[1] + section_heights[2]
    ]
    
    for line_y in line_y_positions:
        c.line(x, line_y, x + width, line_y)
    
    # 绘制粘合标记线 - 黑色实线
    c.setLineWidth(1.0)
    c.setStrokeColor(colors.black)
    
    glue_top_y = y + GLUE_LINE_MM * mm
    glue_bottom_y = y + height - GLUE_LINE_MM * mm
    
    c.line(x, glue_top_y, x + width, glue_top_y)
    c.line(x, glue_bottom_y, x + width, glue_bottom_y)
    
    # 根据字数获取字体参数
    name_length = len(name)
    font_size = FONT_SIZES.get(name_length, FONT_SIZES[0])
    char_spacing = CHAR_SPACING.get(name_length, CHAR_SPACING[0])
    
    c.setFont(font_name, font_size)
    c.setFillColor(colors.black)
    
    # 第1部分: 空白 (y + sum(section_heights[1:]) 到 y + height)
    # 保持空白
    
    # 第2部分: 文字倒过来
    section_y = y + section_heights[0] + section_heights[1]
    section_height = section_heights[1]
    draw_text_block(c, x, section_y, width, section_height, header_text, name, footer_text,
                    font_name, font_size, char_spacing, rotated=True)
    
    # 第3部分: 文字正常
    section_y = y + section_heights[0]
    section_height = section_heights[2]
    draw_text_block(c, x, section_y, width, section_height, header_text, name, footer_text,
                    font_name, font_size, char_spacing, rotated=False)
    
    # 第4部分: 空白 (y 到 y + section_heights[0])
    # 保持空白


def draw_text_block(c, x, y, width, height, header_text, main_text, footer_text,
                    font_name, font_size, char_spacing, rotated=False):
    """
    在一个文本区域内绘制页头、姓名、页脚三行文字。

    header_text：区域顶部的小字
    main_text：区域中间的大字
    footer_text：区域底部的小字
    """
    if not header_text and not main_text and not footer_text:
        return

    # 倒置区域需要在绘制前交换页头/页脚位置，旋转后呈现正确顺序
    if rotated:
        if footer_text:
            draw_text_centered(c, x, y + height - FOOTER_MARGIN - FOOTER_FONT_SIZE,
                              width, FOOTER_FONT_SIZE + 2, footer_text,
                              font_name, FOOTER_FONT_SIZE, 0, rotated)
        if header_text:
            draw_text_centered(c, x, y + HEADER_MARGIN,
                              width, HEADER_FONT_SIZE + 2, header_text,
                              font_name, HEADER_FONT_SIZE, 0, rotated)
        inner_y = y + HEADER_MARGIN + (HEADER_FONT_SIZE + 2 if header_text else 0)
        inner_height = height - HEADER_MARGIN - FOOTER_MARGIN - (HEADER_FONT_SIZE + 2 if header_text else 0) - (FOOTER_FONT_SIZE + 2 if footer_text else 0)
    else:
        # 常规区域
        if header_text:
            draw_text_centered(c, x, y + height - HEADER_MARGIN - HEADER_FONT_SIZE,
                              width, HEADER_FONT_SIZE + 2, header_text,
                              font_name, HEADER_FONT_SIZE, 0, rotated)
        if footer_text:
            draw_text_centered(c, x, y + FOOTER_MARGIN,
                              width, FOOTER_FONT_SIZE + 2, footer_text,
                              font_name, FOOTER_FONT_SIZE, 0, rotated)
        inner_y = y + FOOTER_MARGIN + (FOOTER_FONT_SIZE + 2 if footer_text else 0)
        inner_height = height - HEADER_MARGIN - FOOTER_MARGIN - (HEADER_FONT_SIZE + 2 if header_text else 0) - (FOOTER_FONT_SIZE + 2 if footer_text else 0)

    # 中间主体文字区域
    if inner_height > 0 and main_text:
        draw_text_centered(c, x, inner_y, width, inner_height, main_text,
                          font_name, font_size, char_spacing, rotated)


def draw_text_centered(c, x, y, width, height, text, font_name, font_size, 
                      char_spacing, rotated=False):
    """
    在指定区域内绘制居中的文字
    
    默认不缩放。如果文字宽度超出可用宽度，使用水平缩放以保证显示完整。
    两侧保留最小空白 SIDE_MARGIN。
    水平缩放时，字体和间距都会按比例缩放。
    
    参数:
        c: canvas对象
        x, y, width, height: 绘制区域坐标和尺寸
        text: 要绘制的文字
        font_name: 字体名称
        font_size: 字号
        char_spacing: 字符间隔 (点)
        rotated: 是否旋转180度
    """
    if not text:
        return
    
    c.setFont(font_name, font_size)
    
    # 可用宽度（留出两侧空白）
    available_width = width - 2 * SIDE_MARGIN
    
    # 计算文字宽度
    total_spacing = char_spacing * (len(text) - 1) if len(text) > 1 else 0
    
    # 计算每个字的宽度
    char_widths = []
    for char in text:
        char_widths.append(c.stringWidth(char, font_name, font_size))
    text_width = sum(char_widths) + total_spacing
    
    # 检查是否需要缩放
    scale_factor = 1.0
    if text_width > available_width:
        scale_factor = available_width / text_width
    
    # 垂直居中 - 使用更好的基线计算
    text_y = y + (height - font_size) / 2 + font_size * 0.2
    
    if rotated:
        # 旋转180度显示
        c.saveState()
        center_x = x + width / 2
        center_y = y + height / 2
        c.translate(center_x, center_y)
        c.rotate(180)
        
        # 应用水平缩放
        if scale_factor != 1.0:
            c.scale(scale_factor, 1)
        
        # 在缩放后的坐标系中，文字宽度不变
        current_x = -text_width / 2
        draw_y = -(font_size / 2) + font_size * 0.2
        
        for i, char in enumerate(text):
            c.drawString(current_x, draw_y, char)
            # 推进：原始字宽 + 原始间距（都在缩放坐标系中）
            current_x += char_widths[i] + char_spacing
        
        c.restoreState()
    else:
        # 正常显示
        c.saveState()
        
        if scale_factor != 1.0:
            center_x = x + width / 2
            c.translate(center_x, 0)
            c.scale(scale_factor, 1)
            
            # 在缩放后的坐标系中，文字宽度不变
            current_x = -text_width / 2
        else:
            # 无缩放，直接水平居中
            current_x = x + (width - text_width) / 2
        
        draw_y = text_y
        
        for i, char in enumerate(text):
            c.drawString(current_x, draw_y, char)
            # 推进：原始字宽 + 原始间距
            current_x += char_widths[i] + char_spacing
        
        c.restoreState()


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='姓名桌签PDF生成器')
    parser.add_argument('-i', '--input', default='names.csv', help='输入文件 (支持格式: .csv, .xls, .xlsx, 默认: names.csv)')
    parser.add_argument('-o', '--output', default='table_tent_cards.pdf', help='输出PDF文件 (默认: table_tent_cards.pdf)')
    
    args = parser.parse_args()
    
    print(f"【信息】读取文件: {args.input}")
    data = read_names_from_file(args.input)
    
    if not data:
        print("【错误】未能读取任何姓名")
        return
    
    print(f"【成功】读取 {len(data)} 个姓名")
    
    generate_pdf(data, args.output)


if __name__ == '__main__':
    main()
