import os
import json
import logging
import argparse
from csv_file_validator.validation import SetupValidation, ValidateFile
from csv_file_validator.exceptions import InvalidConfigException, InvalidLineColumnCountException, \
    InvalidFileLocationException

# set logging levels for main function console output
logging_level = logging.DEBUG
logging.basicConfig(level=logging_level)
logger = logging.getLogger(__name__)


def validation_runner(file, config):
    logger.info(f'Validation of {file} started')

    validation_obj = SetupValidation(config)
    validation_obj.get_validated_config()

    logger.info(f'Validation config initiated and validated')

    validation_file_obj = ValidateFile(config, file)

    logger.info(f'Evaluation of file validation rules starting')

    file_level_validations_counter, file_level_failed_validations_counter = validation_file_obj.validate_file()

    logger.info(f'Evaluation of {file_level_validations_counter} file validation rules finished')

    logger.info(f'Evaluation of column validation rules starting')

    column_level_validated_items_counter = 0
    column_level_failed_validations_counter = 0
    try:
        for idx, line in enumerate(validation_file_obj.file_read_generator()):
            _all_validations_count, _all_failed_validations_counter = ValidateFile.validate_line(validation_file_obj,
                                                                                                 line, idx)

            column_level_validated_items_counter += _all_validations_count
            column_level_failed_validations_counter += _all_failed_validations_counter

        logger.info(f'Evaluation of {column_level_validated_items_counter} column validation rules finished')
        logger.info(f'Validation of {file} finished with: '
                    f'{file_level_failed_validations_counter} failed file level validations ,'
                    f'{column_level_failed_validations_counter} failed column level validations')

    except InvalidLineColumnCountException as ColCountErr:
        logger.error(f'File {file} cannot be validated, column count is not consistent {ColCountErr}')

    ValidateFile.close_file_handler(validation_file_obj)

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

    if os.path.isdir(_parsed_file_loc):
        parsed_file_loc = []
        for path in os.listdir(_parsed_file_loc):
            full_path = os.path.join(_parsed_file_loc, path)
            if os.path.isfile(full_path):
                parsed_file_loc.append(full_path)

    elif os.path.isfile(_parsed_file_loc):
        parsed_file_loc = [_parsed_file_loc]
    else:
        raise InvalidFileLocationException(f"Could not load file(s) {_parsed_file_loc} for validation")

    _parsed_config = parsed.configfile

    if os.path.isfile(_parsed_config):
        with open(_parsed_config, mode='r') as json_file:
            try:
                parsed_config = json.load(json_file)
            except json.JSONDecodeError as jsonDecodeErr:
                raise InvalidConfigException(f"Could not load config - valid file, JSON decode error {jsonDecodeErr}")
            except Exception as Exc:
                raise InvalidConfigException(f"Could not load config - valid file, general exception {Exc}")
    else:
        try:
            json.loads(_parsed_config)
            parsed_config = _parsed_config
        except json.JSONDecodeError as jsonDecodeErr:
            raise InvalidConfigException(f"Could not load config - not a valid file, JSON decode error {jsonDecodeErr}")
        except Exception as Exc:
            raise InvalidConfigException(f"Could not load config - not a valid file, general exception {Exc}")

    return {'file_loc': parsed_file_loc,
            'config': parsed_config}


if __name__ == '__main__':
    prepared_args = prepare_args()
    for file in prepared_args['file_loc']:
        validation_runner(file, prepared_args['config'])
