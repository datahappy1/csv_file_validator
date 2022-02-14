"""
config.py
"""
from dataclasses import dataclass
from typing import Optional, Union

from csv_file_validator.exceptions import InvalidConfigException

MANDATORY_METADATA_KEYS = [
    "file_value_separator",
    "file_row_terminator",
    "file_has_header",
]
OPTIONAL_METADATA_KEYS = ["file_value_quote_char"]


class FileMetadata:
    """
    file metadata class
    """

    file_value_separator: str
    file_value_quote_char: str
    file_row_terminator: str
    file_has_header: str


@dataclass
class Config:
    """
    config class
    """

    file_metadata: FileMetadata
    file_validation_rules: dict
    column_validation_rules: dict


def get_validated_config(config: dict) -> Config:
    """
    get validated config function
    :param config:
    :return:
    """
    if not config.get("file_metadata"):
        raise InvalidConfigException("config file missing metadata object")

    if (
            not config.get("file_metadata").get("file_value_separator")
            or not config.get("file_metadata").get("file_row_terminator")
            or not config.get("file_metadata").get("file_has_header") in [True, False]
    ):
        raise InvalidConfigException(
            "config file metadata object not containing all mandatory keys"
        )

    if not config.get("file_validation_rules") and not config.get(
            "column_validation_rules"
    ):
        raise InvalidConfigException(
            "config file missing file_validation_rules object and "
            "column_validation_rules object"
        )

    return Config(**config)


def get_config_file_metadata_value(config, metadata_key) -> Optional[Union[str, bool]]:
    """
    get_config_file_metadata configuration item function
    :param config:
    :param metadata_key:
    :return:
    """
    metadata_item: Optional[Union[str, bool]] = None
    try:
        metadata_item = config.file_metadata[metadata_key]
    except KeyError:
        if metadata_key in MANDATORY_METADATA_KEYS:
            raise InvalidConfigException(
                f"config file missing file_metadata key {metadata_key}"
            )
    return metadata_item
