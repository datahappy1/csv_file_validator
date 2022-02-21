"""
config.py
"""
from dataclasses import dataclass

from csv_file_validator.exceptions import InvalidConfigException


@dataclass
class FileMetadata:
    """
    file metadata class
    """

    file_value_separator: str
    file_value_quote_char: str
    file_row_terminator: str
    file_has_header: bool


class Config:
    """
    config class
    """

    def __init__(self, file_metadata, file_validation_rules, column_validation_rules):
        self.file_metadata: FileMetadata = FileMetadata(**file_metadata)
        self.file_validation_rules: dict = file_validation_rules
        self.column_validation_rules: dict = column_validation_rules
        self._check_data_types()

    def _check_data_types(self):
        if any(
            x is not str
            for x in [
                type(self.file_metadata.file_value_separator),
                type(self.file_metadata.file_value_quote_char),
                type(self.file_metadata.file_row_terminator),
            ]
        ):
            raise ValueError
        if type(self.file_metadata.file_has_header) is not bool:
            raise ValueError

        if any(
            x is not dict
            for x in [
                type(self.column_validation_rules),
                type(self.file_validation_rules),
            ]
        ):
            raise ValueError


def get_validated_config(config: dict) -> Config:
    """
    get validated config function
    :param config:
    :return:
    """
    if not config.get("file_metadata"):
        raise InvalidConfigException("config file missing metadata object")

    if not config.get("file_validation_rules") and not config.get(
        "column_validation_rules"
    ):
        raise InvalidConfigException(
            "config file missing file_validation_rules object and "
            "column_validation_rules object"
        )

    config.setdefault("file_validation_rules", dict())
    config.setdefault("column_validation_rules", dict())

    try:
        return Config(**config)
    except (ValueError, TypeError) as config_err:
        raise InvalidConfigException(config_err)
