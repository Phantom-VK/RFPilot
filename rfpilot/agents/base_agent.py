from agents import ModelSettings

from rfpilot.config.settings import settings


AGENT_DEFAULTS = {"model": settings.DEEPSEEK_MODEL}

JSON_MODE_RESPONSE_FORMAT = {"response_format": {"type": "json_object"}}

EXTRACTION_MODEL_SETTINGS = ModelSettings(
    temperature=0,
    top_p=1,
    max_tokens=2500,
    extra_body=JSON_MODE_RESPONSE_FORMAT,
)

MERGE_MODEL_SETTINGS = ModelSettings(
    temperature=0,
    top_p=1,
    max_tokens=4000,
    extra_body=JSON_MODE_RESPONSE_FORMAT,
)
