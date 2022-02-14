"""
validation module
"""

from typing import List

from csv_file_validator.config import Config
from csv_file_validator.exceptions import InvalidConfigException
from csv_file_validator.file import File
from csv_file_validator.validation_functions import execute_mapped_validation_function


def validate_file(file_level_validations: dict, file: File) -> int:
    """
    function for validating a file, for every file level validation, call
    the mapped validation function and process it
    :return:
    """
    file_level_validations_fail_count: int = 0

    for validation, validation_value in file_level_validations.items():
        file_level_validations_fail_count += execute_mapped_validation_function(
            validation,
            **{
                "file_name": file.file_name,
                "file_header": file.file_header,
                "file_row_count": file.file_data_row_count,
                "file_size": file.file_size,
                "validation_value": validation_value,
            },
        )

    return file_level_validations_fail_count


def validate_column_validation_rules(config: Config, file: File) -> None:
    """
    function to validate column level validation rules with the file content
    :param config:
    :param file:
    :return:
    """
    if file.file_header:
        _column_level_validations_from_file: List = file.file_header
    else:
        _column_level_validations_from_file: List = [
            str(val) for val in range(0, file.get_first_row_column_count())
        ]

    _column_validation_rule_names_from_config: List = list(
        config.column_validation_rules.keys()
    )

    if not _column_level_validations_from_file:
        raise InvalidConfigException(
            "Column validations set in the config, "
            "but none of the expected columns found in the file"
        )

    if not all(
            item in _column_level_validations_from_file
            for item in _column_validation_rule_names_from_config
    ):
        raise InvalidConfigException(
            "Column validations set in the config, "
            "but not all expected columns found in the file"
        )


def validate_line_values(column_level_validations: dict, line: dict, idx: int) -> int:
    """
    function for validating a line in a file, for every column level validation, call
    the mapped validation function and process it
    :param column_level_validations:
    :param line:
    :param idx:
    :return:
    """
    column_level_validations_fail_count: int = 0

    # looping through column names and column values in the line items
    for column_name, column_value in line.items():
        if column_name in column_level_validations:
            # looping through validation items
            for validation, validation_value in column_level_validations[
                column_name
            ].items():
                column_level_validations_fail_count += execute_mapped_validation_function(
                    validation,
                    **{
                        "column": column_name,
                        "validation_value": validation_value,
                        "column_value": column_value,
                        "row_number": idx,
                    },
                )

    return column_level_validations_fail_count
