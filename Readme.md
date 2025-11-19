# 🗜️ Huffman File Compressor & Decompressor

A simple Django web application to **compress and decompress files** using **Huffman coding**.  
Supports text and binary files, shows compression ratio, processing time, and provides downloadable files.
---

## 🗂️ Table of Contents

- [🗃️ Project File Structure](#️project-file-structure)
- [⚡ Installation](#installation)
- [✨ Features](#features)
- [📦 Requirements](#requirements)
- [❗ Potential Problems](#potential-problems)
- [🧪 Testing Checklist](#testing)
- [📘 License](#license)
---

## 🗃️ Project File Structure

```bash
FILECOMPRESSOR/
├── compressor/
│   ├── __pycache__/
│   ├── Algorithm/
│   │   ├── __pycache__/
│   │   ├── __init__.py
│   │   └── huffman_full.py
│   ├── migrations/
│   ├── templates/
│   │   └── compressor/
│   │       ├── compressor.html
│   │       ├── decompressor.html
│   │       └── home.html
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
└── filecompressor/
    ├── __pycache__/
    ├── __init__.py
    ├── asgi.py
    ├── settings.py
    ├── urls.py
    ├── wsgi.py
    └── static/
    └── templates/
        └── main.html
        └── navbar.html

---

## Getting Started

```

### ⚡ Installation

1. Open CMD
  - Press
```bash
WIN + R
```
  - Type
```bash
cmd
```

2. Clone the repository (After moving to your desirable directory)
```bash
git clone https://github.com/Usman-Rasheed-Siddiqui/file-compressor.git
```
  Note: In case you don't have git downloaded, download the zip file of the repository and extract it in your desired folder.
        Then open cmd and follow the following steps.

3. Navigate to the directory
```bash
cd file-compressor/filecompressor
```

4. Set up virtual environment
```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate    # Windows
```

5. Run requirements.txt
```bash
pip install -r requirements.txt
```

6. Run development server
```bash
python manage.py migrate
python manage.py runserver
```

7. Copy this link and paste as URL
  - For page
```bash
http://127.0.0.1:8000/
```

---

## ✨ Features

- **📂 File Compression**
  - Compress text and binary files using **Huffman coding**.
  - Supports multiple file types (`.txt`, `.csv`, `.log`, etc.).
  - Displays **compression ratio** and **time taken** for each operation.
  - Provides downloadable compressed files (`.huff` format).

- **📤 File Decompression**
  - Decompress previously compressed `.huff` files.
  - Automatically restores the original file extension.
  - Shows **decompressed file size** and **processing time**.
  - Provides downloadable decompressed files.

- **🖥️ User-Friendly Web Interface**
  - Simple and clean **Django web app UI**.
  - Upload and download files with ease.
  - Shows informative messages for **errors**, **warnings**, and **successes**.

- **⚠️ Error Handling**
  - Handles invalid files, unsupported formats, and empty uploads.
  - Prevents decompression of files that are not Huffman-compressed.

- **📊 Performance Metrics**
  - Displays original and compressed file sizes.
  - Calculates and displays **compression efficiency**.

- **🌐 Cross-Platform**
  - Works on any system with **Python 3.10+**, Django 5.2, and `bitarray`.

- **💡 Lightweight**
  - No database required; fully functional without `sqlite3`.


## 📦 Requirements

- **Prerequisites**
    - Python 3.10 or Python 3.11
    - django
    - bitarray
    - Any other from requirements.txt
---


## ❗ Potential Problems

### 1. The requirements.txt not running
Open the requirements.txt and install the libraries manually.
```bash
pip install <library_name> 
```

## 🧪 Testing Checklist
Use this checklist to ensure the Huffman Compressor & Decompressor is working correctly:

### General
- [ ] Application loads without errors on browser at `http://127.0.0.1:8000`
- [ ] Home page displays proper navigation links
- [ ] No database errors appear (app works without `sqlite3`)

### File Compression
- [ ] Upload a text file (`.txt`) and compress it
- [ ] Upload a CSV file (`.csv`) and compress it
- [ ] Upload a binary file (`.bin`) and compress it
- [ ] Compression success message is displayed
- [ ] Compression ratio and original/compressed file sizes are shown correctly
- [ ] Downloaded `.huff` file is available and non-empty
- [ ] Warnings appear when compressing already compressed files (e.g., `.jpg`, `.mp3`)

### File Decompression
- [ ] Upload a `.huff` file and decompress it
- [ ] Decompression success message is displayed
- [ ] Decompressed file restores the original file name and extension
- [ ] Decompressed file is downloadable
- [ ] Sizes of compressed and decompressed files are displayed correctly
- [ ] Error appears if a non-`.huff` file is uploaded

### Error Handling
- [ ] No file uploaded → error message displayed
- [ ] Corrupted `.huff` file → proper error message displayed

### Performance & Metrics
- [ ] Time taken for compression/decompression is displayed
- [ ] Compression ratio calculations are correct
- [ ] Application handles multiple small files in sequence without crashing

### Cross-browser
- [ ] Test on Chrome, Firefox, and Edge
- [ ] UI displays correctly without layout issues  
---


## 📘 License

This project is developed solely for educational use and academic evaluation. It is not intended for commercial deployment or distribution.

---
