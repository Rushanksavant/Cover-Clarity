import os
from pathlib import Path
import pdfplumber
from docling.document_converter import DocumentConverter

# Operational Directories relative to root/
RAW_BASE_DIR = Path("./data-collection/raw")
PROCESSED_BASE_DIR = Path("./data-collection/processed")

def parse_pdf_with_plumber(source_path: Path, output_path: Path):
    """Fallback text extraction for PDFs to bypass local OCR/Torch driver conflicts."""
    md_lines = []
    with pdfplumber.open(source_path) as pdf:
        for i, page in enumerate(pdf.pages, 1):
            text = page.extract_text() or ""
            md_lines.append(f"\n\n")
            md_lines.append(text)
            
    markdown_content = "\n".join(md_lines)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(markdown_content)

def run_hybrid_ingestion():
    if not RAW_BASE_DIR.exists():
        print(f"❌ Base raw directory '{RAW_BASE_DIR}' does not exist.")
        return

    print("🚀 Initializing Hybrid Processing Engine (Docling + pdfplumber)...")
    docling_converter = DocumentConverter()
    processed_count = 0

    all_files = list(RAW_BASE_DIR.rglob("*"))
    
    for raw_file_path in all_files:
        if raw_file_path.is_dir():
            continue

        clean_suffix = raw_file_path.suffix.lower().strip()
        if not clean_suffix.endswith((".html", ".htm", ".pdf")):
            continue

        relative_path = raw_file_path.relative_to(RAW_BASE_DIR)
        output_filepath = PROCESSED_BASE_DIR / relative_path.with_suffix(".md")
        output_filepath.parent.mkdir(parents=True, exist_ok=True)

        print(f"⚙️ Routing: [{raw_file_path.name}] -> [{output_filepath.name}]")
        try:
            if clean_suffix == ".pdf":
                # Route PDF processing to pdfplumber to avoid the RapidOCR torch bug
                print("  📄 Format identified as PDF. Executing vector text extraction...")
                parse_pdf_with_plumber(raw_file_path, output_filepath)
            else:
                # Route HTML pages to Docling to extract structured web tables
                print("  🌐 Format identified as HTML. Executing Docling layout parsing...")
                conversion_result = docling_converter.convert(raw_file_path)
                markdown_content = conversion_result.document.export_to_markdown()
                with open(output_filepath, "w", encoding="utf-8") as f:
                    f.write(markdown_content)
            
            processed_count += 1
            print(f"  ✅ Saved markdown safely.")
            

        except Exception as e:
            print(f"  💥 Error processing {raw_file_path.name}: {str(e)}")
            print(f"  🛡️ Preserving original file to avoid data loss.")

    print(f"\n🏁 Process complete. Generated {processed_count} Markdown files in '{PROCESSED_BASE_DIR}'.")

if __name__ == "__main__":
    run_hybrid_ingestion()