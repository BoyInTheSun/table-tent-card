# 桌签PDF生成器

从CSV文件读取姓名，生成可打印桌签PDF。针对中文场景优化。

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 准备数据

创建 `names.csv`:

```csv
姓名
张三
李四
王五
```

### 3. 生成PDF

```bash
python generate_table_tent_card.py
```

### 4. 打印

使用粉纸打印后，沿线折叠，空白区域重叠并用胶棒或订书器粘合，即可制成简易三角桌签。也可以将其卡入透明桌签卡台使用。

## 用法

```bash
# 使用默认文件
python generate_table_tent_card.py

# 指定输入输出
python generate_table_tent_card.py -i 名单.csv -o 桌签.pdf
```

## 配置

编辑 `generate_table_tent_card.py` ，详见注释。

## 特性

- ✅ 自动适配：文字过长自动缩小
- ✅ 多平台：Windows/macOS/Linux 自动搜索系统字体
- ✅ 灵活配置：按字数调整字体、间隔
- ✅ 完整显示：两侧留有空白，不被裁剪

## 系统要求

- Python 3.7+
