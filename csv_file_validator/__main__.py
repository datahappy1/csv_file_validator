"""
main module
"""
import os
import json
import logging
from argparse import ArgumentParser
from configparser import ConfigParser
from csv_file_validator.validation import SetupValidation, ValidateFileLevel, ValidateColumnLevel
from csv_file_validator.exceptions import InvalidSettingsException, \
    InvalidConfigException, InvalidLineColumnCountException, InvalidFileLocationException

# set logging
LOGGING_LEVEL = logging.DEBUG
logging.basicConfig(level=LOGGING_LEVEL)
LOGGER = logging.getLogger(__name__)


def prepare_settings(conf_file_loc='settings.conf') -> dict:
    """
    function for parsing values from settings.conf
    :param conf_file_loc:
    :return:
    """
    settings = dict()
    parser = ConfigParser()
    parser.read(conf_file_loc)

    if not parser.has_section('project_scoped_settings'):
        raise InvalidSettingsException("missing project_scoped_settings section in settings.conf")
    if not parser.has_option('project_scoped_settings', 'SKIP_COLUMN_VALIDATIONS_ON_EMPTY_FILE'):
        raise InvalidSettingsException("missing SKIP_COLUMN_VALIDATIONS_ON_EMPTY_FILE option "
                                       "in the section project_scoped_settings in settings.conf")

    for name, value in parser.items('project_scoped_settings'):
        if value in ('True', 'true'):
            settings[name] = True
        elif value in ('False', 'false'):
            settings[name] = False
        else:
            settings[name] = value

    return settings


def prepare_args() -> dict:
    """
    function for preparation of the CLI arguments
    :return:
    """
    parser = ArgumentParser()
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


class Runner:
    """

    """
    def __init__(self, file_name, config, settings):
        self.file_name = file_name,
        self.file_name = self.file_name[0]
        self.config = config,
        self.config = self.config[0]
        self.settings = settings
        self.validation_file_obj = None
        self.file_level_failed_validations_counter = 0
        self.column_level_failed_validations_counter = 0

    def setup_config(self):
        """

        :return:
        """
        LOGGER.info(f'Validation of {self.file_name} started')

        validation_obj = SetupValidation(self.config)
        validation_obj.get_validated_config()

        LOGGER.info('Validation config validated')
        return 0

    def process_file_level_validations(self):
        """

        :return:
        """
        self.validation_file_obj = ValidateFileLevel(self.config, self.file_name)

        if self.validation_file_obj.file_with_configured_header_has_empty_header():
            LOGGER.error('file with header set to true in config has no header row')
            return 1

        file_level_validations_count = self.validation_file_obj.get_number_of_file_level_validations()

        LOGGER.info(f'Found {file_level_validations_count} file level validations')

        if file_level_validations_count > 0:
            LOGGER.info('Evaluation of file validation rules starting')
            try:
                self.file_level_failed_validations_counter = self.validation_file_obj.validate_file()
                LOGGER.info('Evaluation of file validation rules finished')
            except InvalidConfigException as conf_err:
                LOGGER.error(f'File {self.file_name} cannot be validated, '
                             f'config file has issues, {conf_err}')
                return 1

        return 0

    def process_column_level_validations(self):
        """

        :return:
        """
        validation_column_obj = ValidateColumnLevel(self.config, self.file_name)

        if self.settings.get('skip_column_validations_on_empty_file') not in (True, False):
            LOGGER.info('SKIP_COLUMN_VALIDATIONS_ON_EMPTY_FILE in settings.conf invalid, '
                        'setting value to False and continuing')
            self.settings['skip_column_validations_on_empty_file'] = False

        if validation_column_obj.file_has_no_data_rows() and \
                self.settings['skip_column_validations_on_empty_file']:
            LOGGER.info('File has no rows to validate, skipping column level validations')
            LOGGER.info(f'Validation of {self.file_name} finished with: '
                        f'{self.file_level_failed_validations_counter} '
                        f'failed file level validations')

        column_level_validations_count_from_config = \
            validation_column_obj.get_config_column_validation_rules_all_items_length()

        LOGGER.info(f'Found {column_level_validations_count_from_config} column level validations')

        if column_level_validations_count_from_config > 0:
            LOGGER.info('Evaluation of column validation rules starting')

            try:
                validation_column_obj.validate_config_file_columns_aligned_with_file_content()
            except InvalidConfigException as conf_err:
                LOGGER.error(f'File {self.file_name} cannot be validated, '
                             f'config is not consistent with the file content, {conf_err}')
                return 1

            try:
                for idx, line in validation_column_obj.file_read_generator():
                    self.column_level_failed_validations_counter += \
                        ValidateColumnLevel.validate_line_values(validation_column_obj, line, idx)

                LOGGER.info('Evaluation of column validation rules finished')
            except InvalidConfigException as conf_err:
                LOGGER.error(f'File {self.file_name} cannot be validated, '
                             f'config file has issues, {conf_err}')
                return 1
            except InvalidLineColumnCountException as col_count_err:
                LOGGER.error(f'File {self.file_name} cannot be validated, '
                             f'column count is not consistent, {col_count_err}')
                return 1

        return 0

    def complete(self):
        """

        :return:
        """
        self.validation_file_obj.close_file_handler()

        LOGGER.info(f'Validation of {self.file_name} finished with: '
                    f'{self.file_level_failed_validations_counter} '
                    f'failed file level validations ,'
                    f'{self.column_level_failed_validations_counter} '
                    f'failed column level validations')
        return 0

    def run(self):
        """

        :return:
        """
        self.setup_config()
        self.process_file_level_validations()
        self.process_column_level_validations()
        self.complete()


if __name__ == '__main__':
    SETTINGS = prepare_settings()
    PREPARED_ARGS = prepare_args()

    for file in PREPARED_ARGS['file_loc']:
        r = Runner(file, PREPARED_ARGS['config'], SETTINGS)
        r.run()
