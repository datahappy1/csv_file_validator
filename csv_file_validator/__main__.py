"""
main module
"""
import os
import sys
import json
import logging
import argparse
from csv_file_validator.settings import SKIP_COLUMN_VALIDATIONS_ON_EMPTY_FILE
from csv_file_validator.validation import SetupValidation, ValidateFile
from csv_file_validator.exceptions import InvalidConfigException, InvalidLineColumnCountException, \
    InvalidFileLocationException, FileContentException

# set logging
LOGGING_LEVEL = logging.DEBUG
logging.basicConfig(level=LOGGING_LEVEL)
LOGGER = logging.getLogger(__name__)
# mute traceback
sys.tracebacklimit = 0


def validation_runner(file_name, config):
    """
    function for the validation run
    :param file_name:
    :param config:
    :return:
    """
    LOGGER.info(f'Validation of {file_name} started')

    validation_obj = SetupValidation(config)
    validation_obj.get_validated_config()

    LOGGER.info('Validation config initiated and validated')

    validation_file_obj = ValidateFile(config, file_name)

    file_level_failed_validations_counter = 0
    file_level_validations_count = validation_file_obj.get_number_of_file_level_validations()

    LOGGER.info(f'Found {file_level_validations_count} file level validations')

    if file_level_validations_count:
        LOGGER.info('Evaluation of file validation rules starting')
        try:
            file_level_failed_validations_counter = validation_file_obj.validate_file()
            LOGGER.info('Evaluation of file validation rules finished')
        except InvalidConfigException as conf_err:
            LOGGER.error(f'File {file_name} cannot be fully validated, '
                         f'config file has issues, {conf_err}')

    try:
        validation_file_obj.file_content_checker()
    except FileContentException as file_cont_exc:
        if str(file_cont_exc) == "File has header set to true in config but has no header row":
            LOGGER.error(file_cont_exc)
            return 1
        elif str(file_cont_exc) == "File has no rows to validate" \
                and SKIP_COLUMN_VALIDATIONS_ON_EMPTY_FILE:
            LOGGER.info(file_cont_exc)
            return 1
        else:
            pass

    column_level_failed_validations_counter = 0
    column_level_validations_count = validation_file_obj.get_number_of_column_level_validations()

    LOGGER.info(f'Found {column_level_validations_count} column level validations')

    if column_level_validations_count:
        LOGGER.info('Evaluation of column validation rules starting')
        try:
            for idx, line in validation_file_obj.file_read_generator():
                column_level_failed_validations_counter += \
                    ValidateFile.validate_line_values(validation_file_obj, line, idx)

            LOGGER.info('Evaluation of column validation rules finished')

        except InvalidLineColumnCountException as col_count_err:
            LOGGER.error(f'File {file_name} cannot be validated, '
                         f'column count is not consistent, {col_count_err}')
        except InvalidConfigException as conf_err:
            LOGGER.error(f'File {file_name} cannot be validated, '
                         f'config is not consistent with the file content, {conf_err}')

    ValidateFile.close_file_handler(validation_file_obj)

    LOGGER.info(f'Validation of {file_name} finished with: '
                f'{file_level_failed_validations_counter} '
                f'failed file level validations ,'
                f'{column_level_failed_validations_counter} '
                f'failed column level validations')

    return 0


def prepare_args():
    """
    function for preparation of the CLI arguments
    :return:
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-fl', '--filelocation', type=str, required=True)
    parser.add_argument('-cfg', '--configfile', type=str, required=True)
    parsed = parser.parse_args()

    _parsed_file_loc = parsed.filelocation
    parsed_file_loc_list = []

    if os.path.isdir(_parsed_file_loc):
        for path in os.listdir(_parsed_file_loc):
            full_path = os.path.join(_parsed_file_loc, path)
            if os.path.isfile(full_path):
                parsed_file_loc_list.append(full_path)

    elif os.path.isfile(_parsed_file_loc):
        parsed_file_loc_list = [_parsed_file_loc]
    else:
        raise InvalidFileLocationException(f"Could not load file(s) {_parsed_file_loc} "
                                           f"for validation")

    _parsed_config = parsed.configfile
    parsed_config = None

    if os.path.isfile(_parsed_config):
        with open(_parsed_config, mode='r') as json_file:
            try:
                parsed_config = json.load(json_file)
            except json.JSONDecodeError as json_decode_err:
                raise InvalidConfigException(f"Could not load config - valid file, "
                                             f"JSON decode error: {json_decode_err}")
            except Exception as exc:
                raise InvalidConfigException(f"Could not load config - valid file, "
                                             f"general exception: {exc}")
    else:
        raise InvalidConfigException("Could not load config file - not a valid file")

    return {'file_loc': parsed_file_loc_list,
            'config': parsed_config}


if __name__ == '__main__':
    PREPARED_ARGS = prepare_args()
    for file in PREPARED_ARGS['file_loc']:
        validation_runner(file, PREPARED_ARGS['config'])
