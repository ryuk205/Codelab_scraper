# Google Codelab Scraper and Exporter GUI

A local web application with a stunning, premium GUI built using Streamlit that enables you to scrape any Google Codelab, preview its content, and export it as a single-page HTML, Markdown (.md), or PDF document.

## Features
* 🔍 **Interactive Live Preview**: Browse step-by-step contents with syntax-highlighted code blocks, tables, and notes before exporting.
* 📄 **Clean Markdown Exporter**: Converts custom Codelabs elements to standard markdown.
* 🎨 **Interactive HTML Exporter**: Includes premium CSS styling, dark/light theme toggle, and collapsible sidebars.
* 📕 **Polished PDF Exporter**: Renders steps using a custom PDF layout (via `fpdf2`) complete with document covers, headers/footers, note boxes, and embedded images.
* 📁 **Local Folder Selection**: Saves compiled files directly to any local directory of your choice.

## Prerequisites
* **Python 3.12** or higher.
* `pip3` package manager.

## Installation and Setup

1. **Clone/Navigate to the directory**:
   ```bash
   cd /home/ank/Codelab_rip
   ```

2. **Initialize Python Virtual Environment**:
   ```bash
   python3 -m venv --without-pip .venv
   ```

3. **Install Pip inside virtual environment**:
   ```bash
   curl -sS https://bootstrap.pypa.io/get-pip.py -o get-pip.py
   .venv/bin/python3 get-pip.py
   rm get-pip.py
   ```

4. **Install Dependencies**:
   ```bash
   .venv/bin/pip install -r requirements.txt
   ```

## Running the Application

To launch the Streamlit GUI:
```bash
.venv/bin/streamlit run app.py --server.port 8501
```

Once running, open your web browser and navigate to:
**`http://localhost:8501`**

## How to Use
1. **Enter URL**: Copy and paste any Google Codelab URL (e.g., `https://codelabs.developers.google.com/developer-knowledge-mcp-antigravity`) into the **Codelab URL** input in the sidebar.
2. **Fetch and Preview**: Click **Fetch & Preview**. This parses the Codelab content and loads an interactive step-by-step browser on the right side.
3. **Configure Export**:
   * Select your output format (HTML, Markdown, or PDF).
   * Enter the path to the folder where you want to save the document (defaults to the `outputs/` folder in the project root).
4. **Save Document**: Click **Export File**. Your compiled Codelab document will be saved directly to your disk!
