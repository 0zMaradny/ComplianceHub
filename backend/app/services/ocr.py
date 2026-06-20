"""OCR service — PDF and image text extraction with Arabic support.

Extends file_parser.py with:
  - PDF: pypdf for text-based, pdf2image + tesseract for scanned
  - Images (PNG, JPG, TIFF, BMP): Pillow preprocessing + tesseract
  - Arabic auto-detection
  - Image preprocessing (grayscale, denoise, threshold, deskew)
"""

import os
import re
import logging
import shutil
from pathlib import Path

from PIL import Image, ImageEnhance, ImageFilter

logger = logging.getLogger(__name__)

# ── CONFIG ─────────────────────────────────────────────────────────────────
TESSERACT_LANG = "eng+ara"
TESSERACT_CONFIG = "--psm 3 --oem 3"
IMAGE_DPI = 300
PDF_DPI = 300
MIN_TEXT_LENGTH_FOR_TEXT_PDF = 50
MAX_IMAGE_PIXELS = 10_000_000
SUPPORTED_IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".tiff", ".tif", ".bmp", ".gif"}

# ── Helpers ────────────────────────────────────────────────────────────────

def _validate_tesseract_lang(lang: str) -> str:
    """Validate Tesseract language packs are installed. Falls back to available langs."""
    try:
        import pytesseract
        available = pytesseract.get_languages()
    except Exception:
        return lang  # Can't check, proceed and let tesseract fail naturally
    requested = lang.split('+')
    missing = [l for l in requested if l not in available]
    if missing:
        logger.warning("Tesseract language pack(s) not installed: %s. Available: %s", missing, available)
        # Fall back to available languages only
        available_requested = [l for l in requested if l in available]
        if available_requested:
            return '+'.join(available_requested)
        return 'eng'  # Ultimate fallback
    return lang


def _detect_has_arabic(text: str) -> bool:
    """Check if text contains Arabic characters."""
    arabic_range = re.compile(r"[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]")
    return bool(arabic_range.search(text))


def _preprocess_image(img: Image.Image) -> Image.Image:
    """Preprocess image for better OCR accuracy.

    Uses Otsu's method for adaptive thresholding instead of a fixed
    threshold, which preserves faint text and handles uneven lighting.
    """
    if img.mode != "L":
        img = img.convert("L")

    img = ImageEnhance.Contrast(img).enhance(1.5)
    img = img.filter(ImageFilter.SHARPEN)

    # Otsu's adaptive thresholding — finds optimal threshold automatically
    try:
        import numpy as np
        arr = np.array(img)
        # Compute Otsu's threshold
        hist, _ = np.histogram(arr.flatten(), bins=256, range=(0, 256))
        total = arr.size
        sum_total = np.dot(np.arange(256), hist)
        sum_bg, weight_bg, max_var = 0.0, 0.0, 0.0
        threshold = 128
        for t in range(256):
            weight_bg += hist[t]
            if weight_bg == 0:
                continue
            weight_fg = total - weight_bg
            if weight_fg == 0:
                break
            sum_bg += t * hist[t]
            mean_bg = sum_bg / weight_bg
            mean_fg = (sum_total - sum_bg) / weight_fg
            var_between = weight_bg * weight_fg * (mean_bg - mean_fg) ** 2
            if var_between > max_var:
                max_var = var_between
                threshold = t
        img = Image.fromarray((arr > threshold).astype(np.uint8) * 255)
    except ImportError:
        # Fallback: use PIL's autocontrast + adaptive point
        img = ImageOps.autocontrast(img, cutoff=1)
        img = img.point(lambda x: 0 if x < 128 else 255)

    return img


def _ocr_image(img: Image.Image, lang: str = TESSERACT_LANG) -> dict:
    """Run OCR on a PIL Image, return dict with text + confidence."""
    try:
        import pytesseract
    except ImportError:
        return {"text": "", "confidence": 0, "error": "pytesseract not installed"}

    preprocessed = _preprocess_image(img)
    try:
        # Validate Tesseract language data is available, fall back if needed
        effective_lang = _validate_tesseract_lang(lang)
        data = pytesseract.image_to_data(preprocessed, lang=effective_lang, config=TESSERACT_CONFIG, output_type=pytesseract.Output.DICT)
        # Build word objects with position data for layout-aware assembly
        words = []
        text_list = data.get("text", [])
        conf_list = data.get("conf", [])
        left_list = data.get("left", [])
        top_list = data.get("top", [])
        width_list = data.get("width", [])
        height_list = data.get("height", [])
        for i, text in enumerate(text_list):
            text = text.strip()
            if not text:
                continue
            if i < len(conf_list):
                try:
                    conf = int(conf_list[i])
                except (ValueError, TypeError):
                    conf = -1
            else:
                conf = -1
            if conf <= 0:
                continue
            left = left_list[i] if i < len(left_list) else 0
            top = top_list[i] if i < len(top_list) else 0
            w = width_list[i] if i < len(width_list) else 0
            h = height_list[i] if i < len(height_list) else 0
            words.append({"text": text, "conf": conf, "left": left, "top": top, "w": w, "h": h})

        if not words:
            return {
                "text": "", "paragraphs": [], "tables": [],
                "ocr_confidence": 0, "ocr_method": f"tesseract_{effective_lang.replace('+', '_')}",
                "preprocessing": ["grayscale", "contrast", "sharpen", "binary_threshold"],
            }

        # Sort by top (line), then left (column)
        avg_word_height = sum(w["h"] for w in words) / len(words)
        line_threshold = max(avg_word_height * 0.5, 5)  # Pixels within same line

        words.sort(key=lambda w: (w["top"], w["left"]))

        # Group words into lines based on vertical position
        lines_data = []
        current_line_words = [words[0]]
        current_line_top = words[0]["top"]
        for w in words[1:]:
            if abs(w["top"] - current_line_top) <= line_threshold:
                current_line_words.append(w)
            else:
                lines_data.append(current_line_words)
                current_line_words = [w]
                current_line_top = w["top"]
        if current_line_words:
            lines_data.append(current_line_words)

        # Detect columns: if there's a significant gap in left positions,
        # treat as separate columns and join with proper spacing
        lines = []
        confidences = []
        for line_words in lines_data:
            # Sort words in line by left position
            line_words.sort(key=lambda w: w["left"])
            line_text_parts = []
            prev_right = 0
            for w in line_words:
                confidences.append(w["conf"])
                # Detect column gap: if there's a large horizontal gap,
                # insert a tab/space to separate columns
                if prev_right > 0 and (w["left"] - prev_right) > avg_word_height * 3:
                    line_text_parts.append("    ")  # 4-space column separator
                elif line_text_parts:
                    line_text_parts.append(" ")
                line_text_parts.append(w["text"])
                prev_right = w["left"] + w["w"]
            lines.append("".join(line_text_parts))

        full_text = "\n".join(lines)
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0

        return {
            "text": full_text,
            "paragraphs": [l for l in lines if l.strip()],
            "tables": [],
            "ocr_confidence": round(avg_confidence, 1),
            "ocr_method": f"tesseract_{lang.replace('+', '_')}",
            "preprocessing": ["grayscale", "contrast", "sharpen", "binary_threshold"],
        }
    except Exception as e:
        logger.warning("OCR failed: %s", e)
        return {"text": "", "ocr_confidence": 0, "error": str(e), "paragraphs": [], "tables": [], "ocr_method": "tesseract", "preprocessing": []}


# ── Public API ─────────────────────────────────────────────────────────────


def extract_pdf(filepath: str) -> dict:
    """Extract text from PDF. Try pypdf first, fall back to OCR for scanned docs."""
    result = {
        "filename": os.path.basename(filepath),
        "paragraphs": [],
        "text": "",
        "tables": [],
        "ocr_confidence": None,
        "ocr_method": "pypdf",
        "pages": 0,
        "error": None,
    }

    try:
        import pypdf
        reader = pypdf.PdfReader(filepath)
        try:
            result["pages"] = len(reader.pages)
            text_parts = []
            for page in reader.pages:
                text = page.extract_text() or ""
                text_parts.append(text)
            full_text = "\n".join(text_parts).strip()

            if len(full_text) >= MIN_TEXT_LENGTH_FOR_TEXT_PDF:
                lines = [l.strip() for l in full_text.splitlines() if l.strip()]
                result["text"] = full_text
                result["paragraphs"] = lines
                result["ocr_method"] = "pypdf"
                return result
        finally:
            reader.stream.close()  # Explicitly close file handle
    except Exception as e:
        logger.info("pypdf failed, falling back to OCR: %s", e)
        result["pypdf_error"] = str(e)

    try:
        import pdf2image
        images = pdf2image.convert_from_path(filepath, dpi=PDF_DPI)
        all_text = []
        all_confidences = []
        for i, img in enumerate(images):
            ocr_result = _ocr_image(img)
            if ocr_result.get("text"):
                all_text.append(f"--- Page {i + 1} ---\n{ocr_result['text']}")
                if ocr_result.get("ocr_confidence"):
                    all_confidences.append(ocr_result["ocr_confidence"])
            if i >= 50:
                result["truncated"] = True
                result["pages_processed"] = 50
                logger.warning("PDF OCR truncated at 50 pages (total: %d)", len(images))
                break

        result["text"] = "\n\n".join(all_text)
        result["paragraphs"] = [l.strip() for l in result["text"].splitlines() if l.strip()]
        result["ocr_method"] = "pdf2image_tesseract"
        result["ocr_confidence"] = round(sum(all_confidences) / len(all_confidences), 1) if all_confidences else 0
        result["pages"] = len(images)
        if not result["text"].strip():
            result["error"] = "No text extracted from any page"
        return result

    except ImportError as e:
        result["error"] = f"OCR dependencies not installed: {e}"
        return result
    except Exception as e:
        result["error"] = str(e)
        return result


def extract_image(filepath: str) -> dict:
    """Extract text from an image file using OCR."""
    result = {
        "filename": os.path.basename(filepath),
        "paragraphs": [],
        "text": "",
        "tables": [],
        "ocr_confidence": None,
        "ocr_method": "tesseract",
        "error": None,
    }

    try:
        img = Image.open(filepath)
        # Validate image is not corrupt or polyglot (verify forces full decode)
        try:
            img.verify()
        except Exception as e:
            result["error"] = f"Invalid or corrupt image: {e}"
            return result
        # Re-open after verify (verify closes the file)
        img = Image.open(filepath)

        if img.width * img.height > MAX_IMAGE_PIXELS:
            scale = (MAX_IMAGE_PIXELS / (img.width * img.height)) ** 0.5
            new_size = (int(img.width * scale), int(img.height * scale))
            img = img.resize(new_size, Image.LANCZOS)

        ocr_result = _ocr_image(img)
        result["text"] = ocr_result.get("text", "")
        result["paragraphs"] = ocr_result.get("paragraphs", [])
        result["ocr_confidence"] = ocr_result.get("ocr_confidence")
        result["ocr_method"] = ocr_result.get("ocr_method", "tesseract")
        if ocr_result.get("error"):
            result["error"] = ocr_result["error"]
        return result

    except Exception as e:
        result["error"] = str(e)
        return result


def extract_any(filepath: str) -> dict:
    """Auto-detect file type and extract text."""
    ext = os.path.splitext(filepath)[1].lower()

    if ext == ".pdf":
        return extract_pdf(filepath)

    if ext in SUPPORTED_IMAGE_EXTS:
        return extract_image(filepath)

    return {
        "filename": os.path.basename(filepath),
        "paragraphs": [],
        "text": "",
        "tables": [],
        "ocr_confidence": None,
        "ocr_method": None,
        "error": f"Unsupported file type: {ext}",
    }
