"""
__main__.py
"""
import logging
from enum import Enum
from typing import List, Optional

from csv_file_validator.argument_parser import prepare_args
from csv_file_validator.config import get_validated_config, Config
from csv_file_validator.exceptions import (
    InvalidConfigException,
    InvalidLineColumnCountException,
    FoundValidationErrorException,
    FoundValidationErrorsException,
    InvalidSettingsException,
    InvalidFileLocationException,
)
from csv_file_validator.file import File
from csv_file_validator.settings_parser import prepare_settings, Settings
from csv_file_validator.validation import (
    validate_file,
    check_column_validation_rules_align_with_file_content,
    validate_line_values,
)

logging_level = logging.DEBUG
logging.basicConfig(level=logging_level)
logger = logging.getLogger(__name__)


class ValidationResultEnum(Enum):
    SUCCESS = 0
    FAILURE = 1
    COULD_NOT_PROCESS = 2


class ValidationResultItem:
    def __init__(self, file_name: str, result: ValidationResultEnum):
        self.file_name: str = file_name
        self.result: ValidationResultEnum = result

    def __repr__(self):
        return f"{self.file_name} -> {self.result.name}"


def process_file_validations(config: Config, settings: Settings, file: File) -> None:
    """
    process file level validations function
    :param config:
    :param settings:
    :param file:
    :return:
    """
    failed_file_validations_counter: int = 0

    file_validations: dict = config.file_validation_rules
    file_validations_count: int = (len(file_validations) if file_validations else 0)

    if file.with_configured_header_has_empty_header:
        raise InvalidConfigException(
            "File with header set to true in the config has no header row"
        )

    logger.info("Found %s file validations", file_validations_count)

    if file_validations_count > 0:
        try:
            failed_file_validations_counter = validate_file(file_validations, file)
            if (
                settings.raise_exception_and_halt_on_failed_validation
                and failed_file_validations_counter > 0
            ):
                raise FoundValidationErrorException(
                    "Evaluation of a file validation rule failed"
                )

        except InvalidConfigException as conf_err:
            logger.error(
                "File %s cannot be validated, config file has issues, %s",
                file.name,
                conf_err,
            )
            raise conf_err

    if failed_file_validations_counter > 0:
        raise FoundValidationErrorsException(
            f"Evaluation of "
            f"{failed_file_validations_counter} "
            f"file validation rule(s) failed"
        )


def process_column_validations(config: Config, settings: Settings, file: File) -> None:
    """
    process column level validations function
    :param config:
    :param settings:
    :param file:
    :return:
    """
    if file.has_no_data_rows and settings.skip_column_validations_on_empty_file:
        logger.info("File has no rows to validate, skipping column level validations")
        return

    failed_column_validations_counter: int = 0

    check_column_validation_rules_align_with_file_content(config, file)

    column_validations: dict = config.column_validation_rules
    column_validations_count: int = (
        len(column_validations) if column_validations else 0
    )

    logger.info("Found %s column validations", column_validations_count)

    if column_validations_count > 0:
        try:
            for idx, line in file.file_read_generator():
                validation_result: int = validate_line_values(
                    column_validations, line, idx
                )
                failed_column_validations_counter += validation_result
                if (
                    settings.raise_exception_and_halt_on_failed_validation
                    and validation_result > 0
                ):
                    raise FoundValidationErrorException(
                        "Evaluation of a column validation rule failed"
                    )

        except InvalidConfigException as conf_err:
            logger.error(
                "File %s cannot be validated, config file has issues, %s",
                file.name,
                conf_err,
            )
            raise conf_err
        except InvalidLineColumnCountException as col_count_err:
            logger.error(
                "File %s cannot be validated, column count is not consistent, %s",
                file.name,
                col_count_err,
            )
            raise col_count_err

    if failed_column_validations_counter > 0:
        raise FoundValidationErrorsException(
            f"Evaluation of "
            f"{failed_column_validations_counter} "
            f"column validation rule(s) failed"
        )


def process_file(
    config: Config, settings: Settings, file_name: str
) -> ValidationResultEnum:
    """
    process_file function
    :param config:
    :param settings:
    :param file_name:
    :return:
    """
    try:
        file: File = File(config, file_name)
        logger.info("Validation of %s started", file_name)
    except Exception as exc:
        logger.error("File %s setup raised issues, %s", file_name, exc)
        return ValidationResultEnum.COULD_NOT_PROCESS

    accumulated_errors: str = str()

    try:
        process_file_validations(config=config, settings=settings, file=file)
    except (FoundValidationErrorException, InvalidConfigException) as halt_flow_exc:
        logger.info(
            "Failed to validate file %s , reason: %s", file_name, str(halt_flow_exc),
        )
        file.close_file_handler()
        return ValidationResultEnum.FAILURE
    except FoundValidationErrorsException as found_validation_errors_continue_flow_exc:
        accumulated_errors += str(found_validation_errors_continue_flow_exc)

    try:
        process_column_validations(config=config, settings=settings, file=file)
    except (
        FoundValidationErrorException,
        InvalidConfigException,
        InvalidLineColumnCountException,
    ) as halt_flow_exc:
        logger.info(
            "Failed to validate file %s , reason: %s", file_name, str(halt_flow_exc),
        )
        file.close_file_handler()
        return ValidationResultEnum.FAILURE
    except FoundValidationErrorsException as found_validation_errors_continue_flow_exc:
        accumulated_errors += str(found_validation_errors_continue_flow_exc)

    file.close_file_handler()

    if accumulated_errors:
        logger.info(
            "Failed to validate file %s , reason: %s", file_name, accumulated_errors,
        )
        return ValidationResultEnum.FAILURE

    logger.info("Validation of %s finished without any errors", file_name)
    return ValidationResultEnum.SUCCESS


def main() -> Optional[List[ValidationResultItem]]:
    """
    main function
    :return:
    """
    try:
        prepared_args: dict = prepare_args()
    except (InvalidConfigException, InvalidFileLocationException) as invalid_args_exc:
        logger.error(invalid_args_exc)
        return None

    try:
        config: Config = get_validated_config(prepared_args["config"])
    except InvalidConfigException as invalid_config_exc:
        logger.error(invalid_config_exc)
        return None

    try:
        settings: Settings = prepare_settings()
    except InvalidSettingsException as invalid_settings_exc:
        logger.error(invalid_settings_exc)
        return None

    validation_results: List[ValidationResultItem] = []

    for file_name in prepared_args["file_loc"]:
        validation_result_item: ValidationResultItem = ValidationResultItem(
            file_name=file_name,
            result=process_file(config=config, settings=settings, file_name=file_name),
        )

        validation_results.append(validation_result_item)

    return validation_results


if __name__ == "__main__":
    main()
