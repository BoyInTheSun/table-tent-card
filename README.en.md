[中文](README.md) | English

# Table Tent Card PDF Generator

Read names from CSV files and generate printable table tent card PDFs. Optimized for Chinese scenarios.

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Prepare Data

Create `names.csv` file with the following columns:

- **name**: Required, the main name displayed on the table tent
- **header**: Optional, small text above the name (e.g., conference name)
- **footer**: Optional, position or department info below the name

Example:

```csv
name,header,footer
John Doe
Jane Smith,Annual Conference,CEO
Christopher Alexander Montgomery,,VP of Engineering
```

### 3. Generate PDF

```bash
python generate_table_tent_card.py
```

### 4. Print

Print on cardstock, fold along the lines, overlap the blank areas and glue or staple to create simple triangular table tents. Can also be inserted into transparent table tent holders.

## Usage

```bash
# Use default file
python generate_table_tent_card.py

# Specify input and output
python generate_table_tent_card.py -i names.csv -o table_tents.pdf
```

## Configuration

Edit `generate_table_tent_card.py`, see comments for details.

## Features

- ✅ Auto-adapt: Automatically shrink text if too long
- ✅ Cross-platform: Automatically search system fonts on Windows/macOS/Linux
- ✅ Flexible config: Adjust font size and spacing by character count
- ✅ Complete display: Leave margins on both sides, no cropping

## System Requirements

- Python 3.7+