import os
import sys

from rfpilot.config.constants import PROJECT_ROOT
from rfpilot.exception.exception import RfpilotException
from rfpilot.logging.logger import logging


def save_output(content, file_name, extension="txt"):
    """
    Saves content to a specified folder within the project path.
    """
    try:
        # Define and create the 'output' directory
        output_dir = os.path.join(PROJECT_ROOT, "output")
        os.makedirs(output_dir, exist_ok=True)

        # Prepare final file path (handles file name with or without extension)
        base_name = os.path.splitext(os.path.basename(file_name))[0]
        final_path = os.path.join(output_dir, f"{base_name}.{extension.strip('.')}")

        # Write the content
        with open(final_path, "w", encoding="utf-8") as f:
            f.write(content)

        logging.info(f"File saved successfully at: {final_path}")
        return final_path
    except Exception as e:
        logging.error(f"Failed to save file: {e}")
        raise RfpilotException(e, sys)
