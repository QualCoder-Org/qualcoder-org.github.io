#!/bin/bash
set -euo pipefail

# =============================================
# Script to generate PDFs from the structure
# defined in zensical.toml (QualCoder)
# ✅ Compatible with GitHub Actions
# ✅ Automatically detects languages
# ✅ Uses actual section titles from TOML
# =============================================

# ⚙️ Configuration (can be overridden via environment variables)
TOML_URL="${TOML_URL:-https://github.com/QualCoder-Org/qualcoder-org.github.io/main/zensical.toml}"
OUTPUT_DIR="${OUTPUT_DIR:-output_pdfs}"
DOCS_PREFIX="${DOCS_PREFIX:-docs/doc}"  # Path to your files (e.g., "doc" or "docs/doc")
mkdir -p "$OUTPUT_DIR"

# 📋 Check if Pandoc is installed
if ! command -v pandoc &> /dev/null; then
    echo "❌ **Error**: Pandoc is not installed."
    echo "💡 For GitHub Actions, use the workflow provided below."
    exit 1
fi

# 📥 Download zensical.toml
echo "🌍 Downloading zensical.toml..."
TOML_FILE=$(mktemp /tmp/zensical_XXXXXX.toml)

# Try curl first (available in GitHub Actions)
if command -v curl &> /dev/null; then
    curl -s -f -L "$TOML_URL" -o "$TOML_FILE"
elif command -v wget &> /dev/null; then
    wget -q -O "$TOML_FILE" "$TOML_URL"
else
    echo "❌ **Error**: Neither curl nor wget is available."
    exit 1
fi

if [ ! -s "$TOML_FILE" ]; then
    echo "❌ **Error**: Unable to download $TOML_URL"
    exit 1
fi

# 🐍 Parse TOML and generate PDFs with Python (available in GitHub Actions)
echo "🔍 Parsing TOML file and generating PDFs..."
python3 << 'PYTHON_EOF' "$TOML_FILE" "$OUTPUT_DIR" "$DOCS_PREFIX"
import sys
import tomllib
import os
import subprocess
import re

def main():
    toml_file = sys.argv[1]
    output_dir = sys.argv[2]
    docs_prefix = sys.argv[3]

    # Read TOML file
    with open(toml_file, "rb") as f:
        data = tomllib.load(f)

    # Extract navigation
    nav = data.get("nav", [])

    # Extract languages and their content
    languages = {}
    for item in nav:
        if isinstance(item, dict):
            for lang_code, content in item.items():
                if isinstance(content, list) and len(content) > 2:  # Filter languages with content
                    languages[lang_code.strip("/")] = content

    if not languages:
        print("❌ No languages with complete structure found in nav.", file=sys.stderr)
        return

    print(f"🌍 **Detected languages**: {', '.join(languages.keys())}")

    # Function to extract sections for a language
    def extract_sections(lang_content, lang_code, docs_prefix):
        sections = []
        for item in lang_content:
            if isinstance(item, str):
                file_path = os.path.join(docs_prefix, lang_code, item)
                sections.append({"type": "file", "path": file_path})
            elif isinstance(item, dict):
                for title, files in item.items():
                    if isinstance(files, list):
                        file_paths = [os.path.join(docs_prefix, lang_code, f) for f in files]
                        sections.append({"type": "section", "title": title, "files": file_paths})
        return sections

    # Function to generate PDF for a language
    def generate_pdf(lang_code, sections, output_dir):
        print(f"\n📖 **[{lang_code}]** Generating PDF...")

        temp_md = f"/tmp/qualcoder_{lang_code}_{os.getpid()}.md"
        missing_files = 0

        with open(temp_md, "w", encoding="utf-8") as f:
            # Header
            f.write(f"# **QualCoder Documentation** ({lang_code})\n\n")
            f.write(f"*Automatically generated from [zensical.toml]({TOML_URL})\n\n")
            f.write(f"*Date: {subprocess.getoutput('date +%Y-%m-%d')}\n\n")
            f.write("---\n\n")

            # Add each section
            for section in sections:
                if section["type"] == "file":
                    file_path = section["path"]
                    if os.path.exists(file_path):
                        with open(file_path, "r", encoding="utf-8", errors="replace") as sf:
                            content = sf.read()
                            # Remove main title (level 1)
                            lines = content.split("\n")
                            if lines and re.match(r'^#\s', lines[0]):
                                content = "\n".join(lines[1:]).lstrip()
                            f.write(content + "\n\n---\n\n")
                    else:
                        print(f"⚠️  [{lang_code}] Missing file: {file_path}", file=sys.stderr)
                        missing_files += 1
                elif section["type"] == "section":
                    f.write(f"\n# {section['title']}\n\n")
                    for file_path in section["files"]:
                        if os.path.exists(file_path):
                            with open(file_path, "r", encoding="utf-8", errors="replace") as sf:
                                content = sf.read()
                                lines = content.split("\n")
                                if lines and re.match(r'^#\s', lines[0]):
                                    content = "\n".join(lines[1:]).lstrip()
                                f.write(content + "\n\n---\n\n")
                        else:
                            print(f"⚠️  [{lang_code}] Missing file: {file_path}", file=sys.stderr)
                            missing_files += 1

        if missing_files > 0:
            print(f"⚠️  [{lang_code}] {missing_files} file(s) missing. PDF generated partially.", file=sys.stderr)

        # Generate PDF with Pandoc
        output_pdf = os.path.join(output_dir, f"QualCoder_{lang_code}.pdf")
        cmd = [
            "pandoc",
            temp_md,
            "-o", output_pdf,
            "--toc",
            "--toc-depth=3",
            "--pdf-engine=xelatex",
            f"-V lang={lang_code}",
            "-V documentclass=book",
            "-V geometry:a4paper,margin=2.5cm",
            "-V mainfont=DejaVu Sans",
            "-V fontsize=11pt",
            "-V linestretch=1.2"
        ]

        print(f"🔧 [{lang_code}] Running Pandoc...")
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ [{lang_code}] **Pandoc Error**:", file=sys.stderr)
            print(result.stderr, file=sys.stderr)
        else:
            print(f"✅ [{lang_code}] **PDF generated**: {output_pdf}")

        # Clean up
        if os.path.exists(temp_md):
            os.remove(temp_md)

    # Generate PDF for each language
    for lang_code, lang_content in languages.items():
        sections = extract_sections(lang_content, lang_code, docs_prefix)
        generate_pdf(lang_code, sections, output_dir)

    # Clean up TOML file
    if os.path.exists(toml_file):
        os.remove(toml_file)

    print("\n🎉 **Generation complete!**")
    print(f"📂 **Output directory**: {os.path.abspath(output_dir)}")

if __name__ == "__main__":
    main()
PYTHON_EOF

echo "✅ **Script completed successfully.**"
