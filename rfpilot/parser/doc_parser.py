import os
import sys

from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions, RapidOcrOptions
from docling.document_converter import DocumentConverter, PdfFormatOption, HTMLFormatOption

from rfpilot.config.constants import PROJECT_ROOT
from rfpilot.exception.exception import RfpilotException
from rfpilot.logging.logger import logging
from rfpilot.utils.file_utils import save_file


def get_converter():
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
    logging.info(f"Starting Intelligent Parsing for: {os.path.basename(file_path)}")

    if not os.path.exists(file_path):
        raise FileNotFoundError(file_path)

    try:

        result = converter.convert(file_path)
        doc = result.document

        markdown_data = doc.export_to_markdown()
        logging.info("Document successfully converted to structured markdown.")
        return markdown_data

    except Exception as e:
        logging.error(f"Docling conversion failed: {str(e)}")
        raise RfpilotException(e, sys)


if __name__ == "__main__":
    input_file = os.path.join(
        PROJECT_ROOT,
        "docs/test_docs/Bid2/Dell Laptops w_Extended Warranty - Bid Information - {3} _ BidNet Direct.html"
    )

    try:
        data = perform_intelligent_parsing(input_file)
        output_file = save_file(content=data, input_file=input_file, extension=".md")
        print(f"Extraction Complete! Saved at: {output_file}")

    except Exception as e:
        print(f"Error in workflow: {e}")
