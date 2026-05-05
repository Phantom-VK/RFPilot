import os
import sys
import json
from typing import Union

from rfpilot.config.constants import PROJECT_ROOT
from rfpilot.exception.exception import RfpilotException
from rfpilot.logging.logger import logging


def save_file(
    content: Union[str, dict, list, bytes],
    input_file: str,
    extension: str = "txt",
    subdir: str = "output"
) -> str:
    """
    Generic file saver supporting text, JSON, and binary content.

    Args:
        content: str | dict | list | bytes
        input_file: original file path (used for naming)
        extension: desired output extension (e.g., 'txt', 'json', 'md', 'bin')
        subdir: output folder inside project

    Returns:
        str: full path of saved file
    """

    try:
        # Normalize extension
        extension = extension.strip().lower().lstrip(".")

        # Prepare output directory
        output_dir = os.path.join(PROJECT_ROOT, subdir)
        os.makedirs(output_dir, exist_ok=True)

        # Prepare file name
        base_name = os.path.splitext(os.path.basename(input_file))[0]
        final_path = os.path.join(output_dir, f"{base_name}.{extension}")

        # Decide write mode
        is_binary = isinstance(content, (bytes, bytearray))
        mode = "wb" if is_binary else "w"

        with open(final_path, mode, encoding=None if is_binary else "utf-8") as f:

            # JSON handling
            if extension == "json":
                if not isinstance(content, (dict, list)):
                    raise ValueError("JSON extension requires dict or list content")

                json.dump(content, f, indent=2, ensure_ascii=False)

            # Binary handling
            elif is_binary:
                f.write(content)

            # Default text handling
            else:
                if not isinstance(content, str):
                    content = str(content)

                f.write(content)

        logging.info(f"File saved successfully at: {final_path}")
        return final_path

    except Exception as e:
        logging.error(f"Failed to save file: {str(e)}")
        raise RfpilotException(e, sys)