import os
import sys

from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions, RapidOcrOptions
from docling.document_converter import DocumentConverter, PdfFormatOption

from rfpilot.config.constants import PROJECT_ROOT
from rfpilot.exception.exception import RfpilotException
from rfpilot.logging.logger import logging
from rfpilot.utils.file_utils import save_file


def get_converter():
    pipeline_options = PdfPipelineOptions()
    pipeline_options.do_ocr = True

    pipeline_options.ocr_options = RapidOcrOptions(
        force_full_page_ocr=False,
        lang=["en"]
    )

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
        doc = result.document
        markdown_data = doc.export_to_markdown()
        logging.info("Document successfully converted to structured markdown.")
        return markdown_data

    except Exception as e:
        logging.error(f"Docling conversion failed: {str(e)}")
        raise RfpilotException(e, sys)


# # --- Execution ---
# if __name__ == "__main__":
#     input_file = os.path.join(
#         PROJECT_ROOT,
#         "docs/test_docs/Bid1/JA-207652 Student and Staff Computing Devices FINAL.pdf"
#     )
#
#     try:
#         data = perform_intelligent_ocr(input_file)
#
#         output_file = save_file(content=data, input_file=input_file, extension=".md")
#
#         print(f"Extraction Complete! JSON saved at: {output_file}")
#
#     except Exception as e:
#         print(f"Error in workflow: {e}")