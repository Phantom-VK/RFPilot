import os
import sys

from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions, RapidOcrOptions

from rfpilot.config.constants import PROJECT_ROOT
from rfpilot.exception.exception import RfpilotException
from rfpilot.logging.logger import logging
from rfpilot.utils.file_utils import save_output


def get_converter():
    """
    Proper Docling configuration using RapidOCR (ONNX).
    """

    # Configure pipeline
    pipeline_options = PdfPipelineOptions()
    pipeline_options.do_ocr = True

    # set RapidOCR
    pipeline_options.ocr_options = RapidOcrOptions(
        force_full_page_ocr=False,
        lang=["en"]
    )

    # Attach pipeline to PDF format
    return DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(
                pipeline_options=pipeline_options
            )
        }
    )

converter = get_converter()


def perform_intelligent_ocr(file_path):
    logging.info(f"Starting Intelligent Parsing for: {os.path.basename(file_path)}")

    if not os.path.exists(file_path):
        raise FileNotFoundError(file_path)

    try:
        result = converter.convert(file_path)
        markdown_output = result.document.export_to_markdown()

        logging.info("Document successfully converted to Markdown.")
        return markdown_output

    except Exception as e:
        logging.error(f"Docling conversion failed: {str(e)}")
        raise RfpilotException(e, sys)


# if __name__ == "__main__":
#     input_file = os.path.join(
#         PROJECT_ROOT,
#         "docs/test_docs/Bid1/JA-207652 Student and Staff Computing Devices FINAL.pdf"
#     )
#
#     try:
#         structured_text = perform_intelligent_ocr(input_file)
#         output_file = save_output(structured_text, input_file, extension=".md")
#
#         print(f"Extraction Complete! Check the output folder: {output_file}")
#
#     except Exception as e:
#         print(f"Error in workflow: {e}")