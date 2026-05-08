"""Document parsing utilities built on Docling."""

import os
import sys

# pylint: disable=import-error
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions, RapidOcrOptions
from docling.document_converter import DocumentConverter, PdfFormatOption, HTMLFormatOption

from rfpilot.config.constants import PROJECT_ROOT
from rfpilot.exception.exception import RfpilotException
from rfpilot.logging.logger import logging
from rfpilot.utils.file_utils import save_file


def get_converter():
    """Create a Docling converter configured for OCR-enabled PDF and HTML parsing."""
    # PDF Configuration (OCR Enabled)
    pdf_options = PdfPipelineOptions()
    pdf_options.do_ocr = True
    pdf_options.ocr_options = RapidOcrOptions(
        force_full_page_ocr=False,
        lang=["en"]
    )

    # Converter Initialization
    return DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(pipeline_options=pdf_options),
            InputFormat.HTML: HTMLFormatOption()
        }
    )


# Initialize once
converter = get_converter()


def perform_intelligent_parsing(file_path):
    """
    Universal function for PDF and HTML.
    Automatically detects file type and applies the correct pipeline.
    """
    logging.info("Starting Intelligent Parsing for: %s", os.path.basename(file_path))

    if not os.path.exists(file_path):
        raise FileNotFoundError(file_path)

    try:

        result = converter.convert(file_path)
        doc = result.document

        markdown_data = doc.export_to_markdown()
        logging.info("Document successfully converted to structured markdown.")
        return markdown_data

    except Exception as exc:
        logging.error("Docling conversion failed: %s", exc)
        raise RfpilotException(exc, sys) from exc


if __name__ == "__main__":
    input_file = os.path.join(
        PROJECT_ROOT,
        "docs/test_docs/Bid1/JA-207652 Student and Staff Computing Devices FINAL.pdf",
    )

    try:
        data = perform_intelligent_parsing(input_file)
        output_file = save_file(content=data, input_file=input_file, extension=".md")
        print(f"Extraction Complete! Saved at: {output_file}")

    except Exception as err:  # pylint: disable=broad-exception-caught
        print(f"Error in workflow: {err}")
