from pypdf import PdfReader


class PDFExtractionError(Exception):
    pass


def extract_text_from_pdf(file_stream):
    """
    Extract text from an in-memory PDF file stream.
    Raises PDFExtractionError if the file cannot be read or contains no text.
    """
    try:
        reader = PdfReader(file_stream)
    except Exception as exc:
        raise PDFExtractionError(f"Could not read PDF file: {exc}")

    if reader.is_encrypted:
        try:
            reader.decrypt("")
        except Exception:
            raise PDFExtractionError("The PDF is password protected.")

    text_parts = []
    for page in reader.pages:
        try:
            page_text = page.extract_text() or ""
        except Exception:
            page_text = ""
        text_parts.append(page_text)

    full_text = "\n".join(text_parts).strip()

    if not full_text:
        raise PDFExtractionError(
            "No readable text was found in this PDF. It may be a scanned image."
        )

    return full_text
