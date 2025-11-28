import markdown
from xhtml2pdf import pisa
import os

def convert_md_to_pdf(source_md, output_pdf):
    # 1. Read Markdown
    with open(source_md, 'r', encoding='utf-8') as f:
        md_content = f.read()

    # 2. Convert to HTML
    # We need to add some basic CSS for better formatting
    html_content = markdown.markdown(md_content, extensions=['tables', 'fenced_code'])
    
    full_html = f"""
    <html>
    <head>
    <style>
        body {{ font-family: Helvetica, sans-serif; font-size: 12px; }}
        h1 {{ color: #333; font-size: 24px; border-bottom: 1px solid #ccc; padding-bottom: 10px; }}
        h2 {{ color: #444; font-size: 18px; margin-top: 20px; }}
        h3 {{ color: #555; font-size: 14px; margin-top: 15px; }}
        pre {{ background-color: #f5f5f5; padding: 10px; border: 1px solid #ddd; }}
        code {{ font-family: Courier, monospace; }}
        img {{ max-width: 100%; height: auto; margin: 20px 0; }}
        table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
    </style>
    </head>
    <body>
    {html_content}
    </body>
    </html>
    """

    # 3. Write to PDF
    with open(output_pdf, "wb") as result_file:
        pisa_status = pisa.CreatePDF(
            full_html,                # the HTML to convert
            dest=result_file          # the file handle to recieve result
        )

    if pisa_status.err:
        print(f"Error converting {source_md} to PDF")
    else:
        print(f"Successfully created {output_pdf}")

if __name__ == "__main__":
    source = r"C:\Users\Administrator\.gemini\antigravity\brain\e5d121e2-d559-4f3d-bf10-dc80789a864d\architecture.md"
    output = r"C:\Users\Administrator\.gemini\antigravity\brain\e5d121e2-d559-4f3d-bf10-dc80789a864d\architecture.pdf"
    
    if os.path.exists(source):
        convert_md_to_pdf(source, output)
    else:
        print(f"Source file not found: {source}")
