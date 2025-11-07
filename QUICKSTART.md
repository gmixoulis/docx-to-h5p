# 🚀 Quick Start Guide - 5 Minutes to Your First H5P

## Step 1: Prepare Your System (1 min)

### Install Python & Dependencies

```bash
# Make sure Python 3.7+ is installed
python --version

# Install required packages
pip install -r requirements.txt
```

## Step 2: Organize Your Files (1 min)

### Create Input Folder

```bash
# Create folder for your DOCX files
mkdir english_docs

# Copy your DOCX files to this folder
cp /path/to/your/Activities-Module-*.docx english_docs/
```

### Verify Setup

```bash
# Check files are in place
ls english_docs/
# Should show: Activities-Module-1.docx, Activities-Module-2.docx, etc.

# Check scripts are present
ls *.py
# Should show: run_pipeline.py, batch_h5p_converter_final.py, combine_h5p_auto.py
```

## Step 3: Run the Pipeline (1 min)

```bash
# Execute the complete pipeline
python run_pipeline.py

# Wait for completion (usually 1-5 minutes depending on document size)
```

## Step 4: Check Results (1 min)

### Find Your H5P Files

```bash
# List generated H5P files
ls *.h5p

# You should see:
# - Activities_Module_1_multiple_choice.h5p
# - Activities_Module_1_truefalse.h5p
# - Activities_Module_1_crossword.h5p
# - etc.
```

### Verify JSON Files

```bash
# Check intermediate JSON files
ls -R Activities_Module_*/

# Should contain:
# - question_1.json, question_2.json, etc.
# - true_false_1.json, true_false_2.json, etc.
# - crossword_1.json, etc.
# - images/ folder (if images in DOCX)
```

## Step 5: Upload to Your LMS (1 min)

### Moodle

1. Go to your course
2. Click "Add activity or resource" → "H5P Content"
3. Click "Upload H5P file"
4. Select one of your `.h5p` files
5. Repeat for each file

### WordPress

1. Install H5P plugin (if not already)
2. Go to H5P Content
3. Click "Upload H5P file"
4. Select your `.h5p` file
5. Publish

### Canvas

1. Go to your course
2. Add content module
3. Upload H5P file directly
4. Canvas handles the rest

---

## 🎯 Command Reference

### Complete Pipeline (Recommended)

```bash
# Default: runs all stages
python run_pipeline.py

# Skip translations (faster)
python run_pipeline.py --skip-translations

# Verbose output for debugging
python run_pipeline.py --verbose
```

### Individual Stages

```bash
# Stage 1: DOCX to JSON only
python batch_h5p_converter_final.py

# Stage 2: JSON to H5P only  
python combine_h5p_auto.py

# Stage 3: Translations only
python translations.py
```

### Manual H5P Creation

If you already have content and h5p.json files:

```bash
# macOS/Linux
find . -name '.DS_Store' -delete  # Remove metadata
zip -r -D -X project_el.h5p content h5p.json language/ 2>/dev/null || \
zip -r -D -X project_el.h5p content h5p.json

# Windows PowerShell
Compress-Archive -Path content, h5p.json -DestinationPath project_el.h5p
```

---

## ✅ Checklist

Before running:

- [ ] Python 3.7+ installed
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] DOCX files in `english_docs/` folder
- [ ] DOCX files have proper structure (see README.md)
- [ ] Correct answers are **bold** in DOCX

After running:

- [ ] Check for `.h5p` files in root directory
- [ ] Verify no error messages in console
- [ ] H5P files can be opened (optional: `unzip -t file.h5p`)
- [ ] Ready to upload to LMS!

---

## 🐛 Quick Troubleshooting

### "No DOCX files found"

```bash
# Check folder exists and has files
ls -la english_docs/

# If empty, copy your DOCX files:
cp ~/Documents/Activities-Module-*.docx english_docs/
```

### "Python command not found"

```bash
# Verify Python is installed
python --version
# or
python3 --version

# Use python3 if needed:
python3 run_pipeline.py
```

### "ModuleNotFoundError: No module named 'docx'"

```bash
# Install the missing module
pip install python-docx
```

### ".h5p file won't open"

```bash
# Verify file is a valid zip
unzip -l project_el.h5p

# Should show:
# - h5p.json
# - content/content.json
# - content/images/ (optional)
# - language/ (optional)
```

---

## 📞 Need Help?

1. Read the full README.md for detailed documentation
2. Check troubleshooting section
3. Verify DOCX file format (see README.md for examples)
4. Run with `--verbose` flag to see detailed output

---

## 🎉 Success!

You now have professional, interactive H5P content ready for your LMS!

Next steps:
- Upload to Moodle/WordPress/Canvas
- Embed in course content
- Track student progress
- Iterate and improve

**Happy teaching! 🎓**
