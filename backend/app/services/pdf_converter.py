import os
import subprocess
import shutil

PDF_AVAILABLE = False
PDF_ENGINE = None

if shutil.which('libreoffice'):
    PDF_AVAILABLE = True
    PDF_ENGINE = 'libreoffice'
elif shutil.which('soffice'):
    PDF_AVAILABLE = True
    PDF_ENGINE = 'libreoffice'


def convert_to_pdf(docx_path):
    if not PDF_AVAILABLE:
        return None

    pdf_path = docx_path.rsplit('.', 1)[0] + '.pdf'
    out_dir = os.path.dirname(docx_path)

    try:
        if PDF_ENGINE == 'libreoffice':
            subprocess.run(
                ['libreoffice', '--headless', '--convert-to', 'pdf',
                 '--outdir', out_dir, docx_path],
                capture_output=True, timeout=60, check=True,
                env={**os.environ, 'HOME': '/tmp'},
            )
        elif PDF_ENGINE == 'docx2pdf':
            from docx2pdf import convert
            convert(docx_path, pdf_path)

        if os.path.exists(pdf_path):
            return pdf_path
    except Exception:
        pass
    return None
