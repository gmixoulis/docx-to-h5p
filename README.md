# 🎓 H5P Content Pipeline - Complete Automation Suite

> **Transform DOCX documents → Interactive H5P content with minimal effort**

A powerful Python automation suite for educators and content creators to convert Word documents containing multiple choice, true/false, and crossword questions into professional H5P interactive learning packages.

---

## 📋 Table of Contents

- [Features](#features)
- [Quick Start](#quick-start)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Usage Guide](#usage-guide)
  - [Automated Pipeline](#automated-pipeline)
  - [Stage-by-Stage Processing](#stage-by-stage-processing)
  - [Manual H5P Creation](#manual-h5p-creation)
- [Folder Structure](#folder-structure)
- [Script Documentation](#script-documentation)
- [Advanced Features](#advanced-features)
- [Troubleshooting](#troubleshooting)
- [License](#license)

---

## ✨ Features

### 🚀 Main Capabilities

- **📄 DOCX to JSON Conversion**
  - Extracts Multiple Choice questions (with bold formatting for answers)
  - Extracts True/False questions (with bold formatting for correct answers)
  - Extracts Crossword puzzles
  - Automatically detects embedded images

- **🧩 JSON to H5P Packaging**
  - Auto-detects Activity/Module folders
  - Creates separate H5P files by question type
  - Supports multilingual content (English, Greek, Spanish)
  - Includes image handling and library metadata

- **🌍 Optional Translation Support**
  - Translate content to multiple languages
  - Automatic language file generation
  - Seamless integration with H5P files

- **⚡ Full Automation Pipeline**
  - Run entire workflow with one command
  - Stage-by-stage execution for granular control
  - Verbose output for debugging

### 💡 Smart Detection

- Automatically finds all DOCX files in source folders
- Detects question types (Multiple Choice, True/False, Crossword)
- Identifies Activity/Module folders without manual configuration
- Handles multiple document encoding formats

### 📦 H5P Compatible

- Works with any H5P-enabled LMS:
  - Moodle
  - WordPress (with H5P plugin)
  - Canvas
  - Brightspace
  - OpenedX

---

## 🚀 Quick Start

### Installation

```bash
# Clone or download the repository
git clone <repository-url>
cd h5p-content-pipeline

# Install Python dependencies
pip install python-docx

# Verify scripts are present
ls -la *.py
```

### Basic Usage

```bash
# Run the complete pipeline
python run_pipeline.py

# That's it! Your H5P files will be created automatically.
```

---

## 📁 Project Structure

```
docx-to-h5p/
│
├── 📜 README.md                              # This file
├── 📜 run_pipeline.py                        # 🎯 Main orchestrator (START HERE!)
│
├── 🔧 CORE SCRIPTS
├── batch_h5p_converter_final.py              # Stage 1: DOCX → JSON
├── combine_h5p_auto.py                       # Stage 2: JSON → H5P
├── translations.py                           # Stage 3: Translation (optional)
│
├── 📁 INPUT FOLDERS (Create these)
├── english_docs/                             # Put your English DOCX files here
│   ├── Activities-Module-1.docx
│   ├── Activities-Module-2.docx
│   └── Activities-Module-3.docx
│
├── spanish_docs/                               # (Optional) Spanish DOCX files
│   └── ...
│
├── 📁 OUTPUT FOLDERS (Auto-generated)
├── Activities_Module_1/                      # Generated JSON files
│   ├── question_1.json
│   ├── question_2.json
│   ├── true_false_1.json
│   ├── crossword_1.json
│   └── images/
│
├── Activities_Module_1_multiple_choice.h5p   # Generated H5P file
├── Activities_Module_1_truefalse.h5p         # Generated H5P file
├── Activities_Module_1_crossword.h5p         # Generated H5P file

---

## 📦 Installation & Setup

### Prerequisites

- Python 3.7 or higher
- pip (Python package manager)

### Step 1: Clone Repository

```bash
git clone <your-repo-url>
cd h5p-content-pipeline
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

Or install manually:

```bash
pip install python-docx
```

### Step 3: Prepare Your Documents

Create the input folder structure:

```bash
mkdir english_docs
mkdir spanish_docs
```

Add your DOCX files to `english_docs/`:

```
english_docs/
├── Activities-Module-1.docx
├── Activities-Module-2.docx
└── Activities-Module-3.docx
```

---

## 🎯 Usage Guide

### Option 1: Automated Pipeline (Recommended)

Run the complete pipeline with a single command:

```bash
python run_pipeline.py
```

**What happens:**
1. ✅ Validates environment
2. ✅ Stage 1: Converts DOCX files to JSON
3. ✅ Stage 2: Combines JSON files into H5P packages
4. ✅ Stage 3: (Optional) Translates content
5. ✅ Generates output summary

**With Options:**

```bash
# Skip translations
python run_pipeline.py --skip-translations

# Run specific stage
python run_pipeline.py --stage 1    # DOCX → JSON
python run_pipeline.py --stage 2    # JSON → H5P
python run_pipeline.py --stage 3    # Translate

# Verbose output for debugging
python run_pipeline.py --verbose
```

### Option 2: Stage-by-Stage Processing

For more control, run each stage separately:

```bash
# Stage 1: Convert DOCX to JSON
python batch_h5p_converter_final.py

# This creates folders like:
# - Activities_Module_1/
# - Activities_Module_2/
# - Activities_Module_3/

# Stage 2: Combine JSON into H5P files
python combine_h5p_auto.py

# This creates H5P files:
# - Activities_Module_1_multiple_choice.h5p
# - Activities_Module_1_truefalse.h5p
# - Activities_Module_1_crossword.h5p
# - etc.

# Stage 3: (Optional) Translate content
python translations.py
```

### Option 3: Manual H5P Creation

If you already have `content/` and `h5p.json` files:

#### macOS/Linux

```bash
# 1. Remove macOS metadata files
find . -name '.DS_Store' -delete

# 2. Create H5P file by zipping

zip -r -D -X project.h5p ./{folder_name}

# Expected result: project.h5p ✅
```

#### Windows (PowerShell)

```powershell
# 1. Create H5P file
Compress-Archive -Path content, h5p.json -DestinationPath project.h5p

# Or using 7-Zip
7z a -tzip project.h5p content h5p.json
```

---

## 📄 DOCX Format Requirements

### ✅ Document Structure

Your DOCX files should be organized as follows:

```
Module 2 - Activities Unit 1

Activity 1 - Quiz (Multiple Choice Questions)

1. What is the main goal?
a. Option A (incorrect)
b. Option B (correct - make this BOLD)
c. Option C (incorrect)
d. Option D (incorrect)

2. Another question?
a. Answer option
...

Activity 2 - True or False

True or False section starts here

The statement is true. **True**
Another statement. **False**
...

Activity 3 - Crossword Puzzle

Part I - Crossword Puzzle

Across
1. Definition of word (WORD)

Down
2. Another definition (ANOTHER)
```

### Key Points

✅ **Question Formatting:**
- Multiple Choice: Use letters (a, b, c, d)
- Make correct answer **bold** in the document
- True/False: End with **True** or **False**
- Crossword: Include clues with answers in parentheses or bold

✅ **Section Headers:**
- Use "Activity X" or "Quiz" to mark sections
- Use "True or False" or "True/False" for T/F sections
- Use "Activity 3, Part X - Crossword" for crosswords

✅ **Formatting:**
- Bold text = Correct answer
- Consistent formatting ensures accurate detection

---

## 🔧 Script Documentation

### 1. `run_pipeline.py` - Main Orchestrator

**Purpose:** Automates the entire workflow

**Usage:**
```bash
python run_pipeline.py [OPTIONS]

Options:
  --stage N              Run specific stage (1, 2, or 3)
  --skip-translations    Skip translation stage
  --verbose             Show detailed output
  --help                Show help message
```

**Features:**
- Environment validation
- Stage execution
- Error handling
- Summary reporting

---

### 2. `batch_h5p_converter_final.py` - DOCX to JSON

**Purpose:** Converts DOCX files to JSON question files

**Usage:**
```bash
python batch_h5p_converter_final.py
```

**Input:** DOCX files in `english_docs/`

**Output:**
- `Activities_Module_1/`, `Activities_Module_2/`, etc.
- Each folder contains JSON files for questions and images

**Features:**
- Extracts Multiple Choice questions
- Extracts True/False questions
- Extracts Crossword puzzles
- Handles embedded images
- Auto-detects document structure

---

### 3. `combine_h5p_auto.py` - JSON to H5P

**Purpose:** Combines JSON files into H5P packages

**Usage:**
```bash
python combine_h5p_auto.py
```

**Input:** JSON files in Activity/Module folders

**Output:** `.h5p` files ready for LMS upload

**Features:**
- Auto-detects Activity/Module folders
- Categorizes by question type
- Creates separate H5P files for each type
- Includes language files
- Includes image files

---

### 4. `translations.py` - Translation Support

**Purpose:** Translates content to multiple languages

**Usage:**
```bash
python translations.py
```

**Features:**
- Multi-language support
- Automatic translation API integration
- Generates language JSON files

---

## 🌟 Advanced Features

### Multilingual Content

Create `el.json` and `es.json` for Greek and Spanish translations:

```json
{
  "true": "Σωστό",
  "false": "Λάθος",
  "checkAnswer": "Έλεγχος",
  "showSolution": "Εμφάνιση λύσης",
  ...
}
```

These files are automatically included in the H5P packages.

### Custom Metadata

Edit `library.json` to customize H5P metadata:

```json
{
  "title": "My Custom Quiz",
  "language": "en",
  "license": "CC BY-SA",
  ...
}
```

### Image Handling

Images are automatically extracted from DOCX files and included in H5P packages:

```
content/
├── content.json
└── images/
    ├── image_1.jpg
    ├── image_2.png
    └── ...
```

---

## 🐛 Troubleshooting

### Problem: "No DOCX files found in english_docs"

**Solution:**
```bash
# Verify folder exists
ls -la english_docs/

# Create if missing
mkdir -p english_docs

# Add DOCX files
cp /path/to/your/files.docx english_docs/
```

### Problem: "Missing required scripts"

**Solution:**
```bash
# Check all scripts are present
ls -la *.py

# Required files:
# - run_pipeline.py
# - batch_h5p_converter_final.py
# - combine_h5p_auto.py
```

### Problem: Python module not found

**Solution:**
```bash
# Install required dependencies
pip install python-docx

# Verify installation
python -c "import docx; print('OK')"
```

### Problem: ".DS_Store" files interfering (macOS)

**Solution:**
```bash
# Remove macOS metadata
find . -name '.DS_Store' -delete

# Then recreate H5P file
zip -r -D -X project_el.h5p content h5p.json language/
```

### Problem: H5P file won't upload to LMS

**Solution:**
1. Verify H5P structure:
```bash
unzip -l project_el.h5p
# Should contain:
# - h5p.json (at root)
# - content/content.json
# - content/images/ (if applicable)
# - language/ (if applicable)
```

2. Check file sizes (shouldn't exceed LMS limits)

3. Verify JSON syntax:
```bash
python -c "import json; json.load(open('content/content.json'))"
```

---

## 📊 Example Workflow

### Complete Example

```bash
# 1. Setup
git clone <repo>
cd h5p-content-pipeline
pip install python-docx

# 2. Prepare documents
mkdir english_docs
cp ~/Documents/Activities-Module-*.docx english_docs/

# 3. Run pipeline
python run_pipeline.py

# Output:
# ✅ Stage 1: DOCX → JSON (generates Activities_Module_1/, etc.)
# ✅ Stage 2: JSON → H5P (generates .h5p files)
# ✅ Stage 3: Translation (optional)
# ✅ Done!

# 4. Upload to LMS
# Open Moodle/WordPress/Canvas
# Import Activities_Module_1_multiple_choice.h5p
# Import Activities_Module_1_truefalse.h5p
# Import Activities_Module_1_crossword.h5p
# Repeat for other modules
```

---

## 📈 Supported Question Types

| Type | DOCX Format | H5P Library | Status |
|------|-------------|-------------|--------|
| Multiple Choice | Options a-d, bold = correct | H5P.MultiChoice | ✅ Supported |
| True/False | Statement + **True/False** | H5P.TrueFalse | ✅ Supported |
| Crossword | Clues + Answers | H5P.Crossword | ✅ Supported |
| Fill in Blanks | (Future) | H5P.Blanks | 🚧 Planned |
| Drag & Drop | (Future) | H5P.DragDrop | 🚧 Planned |

---

## 🔐 Security & Privacy

- Scripts run locally on your machine
- No data uploaded to external servers
- Optional API usage only for translations
- Full source code transparency

---

## 📝 License

This project is licensed under the MIT License - see LICENSE file for details

---

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

## 📞 Support

For issues, questions, or suggestions:

1. Check the Troubleshooting section
2. Review script documentation
3. Check GitHub Issues
4. Contact support via email

---

## 🙏 Acknowledgments

Built with Python 🐍 for educators 🎓

- python-docx for DOCX parsing
- H5P for interactive content standards
- The open-source community

---

**Ready to get started?** Run `python run_pipeline.py` now! 🚀
