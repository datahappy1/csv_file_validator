"""
main module
"""
import os
import sys
import json
import logging
from argparse import ArgumentParser
from configparser import ConfigParser
from csv_file_validator.validation import SetupValidation, SetupFile, \
    ValidateFileLevel, ValidateColumnLevel
from csv_file_validator.exceptions import InvalidSettingsException, \
    InvalidConfigException, InvalidLineColumnCountException, \
    InvalidFileLocationException, ValidationErrorException

# set logging
LOGGING_LEVEL = logging.DEBUG
logging.basicConfig(level=LOGGING_LEVEL)
LOGGER = logging.getLogger(__name__)
# mute traceback
sys.tracebacklimit = 0


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
    if not parser.has_option('project_scoped_settings', 'RAISE_EXCEPTION_AND_HALT_ON_FOUND_VALIDATION_ERROR'):
        raise InvalidSettingsException("missing RAISE_EXCEPTION_AND_HALT_ON_FOUND_VALIDATION_ERROR option "
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
    args = dict()

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
        if not parsed_file_loc_list:
            raise InvalidFileLocationException(f"Folder {_parsed_file_loc} is empty")

    elif os.path.isfile(_parsed_file_loc):
        parsed_file_loc_list = [_parsed_file_loc]
    else:
        raise InvalidFileLocationException(f"Could not load file(s) {_parsed_file_loc} "
                                           f"for validation")
    args['file_loc'] = parsed_file_loc_list

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

    args['config'] = parsed_config

    return args


class ValidationRunner:
    """
    validation runner class
    """

    def __init__(self, config, settings):
        self.config = self._validate_config(config)
        self.settings = settings
        self.file_obj = None
        self.file_name = None
        self.file_level_failed_validations_counter = 0
        self.column_level_failed_validations_counter = 0

    @staticmethod
    def _validate_config(config):
        validation_obj = SetupValidation(config)

        try:
            return validation_obj.get_validated_config()
        except InvalidConfigException as conf_err:
            LOGGER.error('Validation of config json file raised issued, %s', conf_err)
            raise conf_err

    def setup_file(self, file_name):
        """
        setup file method
        :param file_name:
        :return:
        """
        self.file_name = file_name

        try:
            self.file_obj = SetupFile(self.config, self.file_name)
        except Exception as err:
            LOGGER.error('File %s setup raised issues, %s', self.file_name, err)
            raise err

        LOGGER.info('Validation of %s started', self.file_name)

        if self.settings.get('skip_column_validations_on_empty_file') not in (True, False):
            LOGGER.info('SKIP_COLUMN_VALIDATIONS_ON_EMPTY_FILE in settings.conf invalid, '
                        'setting value to False and continuing')
            self.settings['skip_column_validations_on_empty_file'] = False

        if self.settings.get('raise_exception_and_halt_on_found_validation_error') not in (True, False):
            LOGGER.info('RAISE_EXCEPTION_AND_HALT_ON_FOUND_VALIDATION_ERROR in settings.conf invalid, '
                        'setting value to False and continuing')
            self.settings['raise_exception_and_halt_on_found_validation_error'] = False

        return 0

    def process_file_level_validations(self):
        """
        process file level validations method
        :return:
        """
        validation_file_obj = ValidateFileLevel(self.config, self.file_name)

        if self.file_obj.file_with_configured_header_has_empty_header:
            raise InvalidConfigException('File with header set to true in the '
                                         'config has no header row')

        file_level_validations_count = validation_file_obj.get_file_level_validations_count()

        LOGGER.info('Found %s file level validations', file_level_validations_count)

        if file_level_validations_count > 0:
            LOGGER.info('Evaluation of file validation rules starting')
            try:
                ret = validation_file_obj.validate_file()
                self.file_level_failed_validations_counter = ret
                if self.settings['raise_exception_and_halt_on_found_validation_error'] \
                        and ret == 1:
                    raise ValidationErrorException('Evaluation of a validation rule failed')
                LOGGER.info('Evaluation of all file validation rules finished')

            except InvalidConfigException as conf_err:
                LOGGER.error('File %s cannot be validated, '
                             'config file has issues, %s',
                             self.file_name, conf_err)
                raise conf_err

        if self.file_level_failed_validations_counter > 0:
            raise ValidationErrorException('Evaluation of a validation rule failed')

        return 0

    def process_column_level_validations(self):
        """
        process column level validations method
        :return:
        """
        if self.file_obj.file_has_no_data_rows and \
                self.settings['skip_column_validations_on_empty_file']:
            LOGGER.info('File has no rows to validate, skipping column level validations')
            return 0

        validation_column_obj = ValidateColumnLevel(self.config, self.file_name)

        column_level_validations_count = \
            validation_column_obj.get_column_level_validations_count()

        LOGGER.info('Found %s column level validations', column_level_validations_count)

        if column_level_validations_count > 0:
            LOGGER.info('Evaluation of column validation rules starting')

            try:
                for idx, line in validation_column_obj.file_read_generator():
                    ret = validation_column_obj.validate_line_values(line, idx)
                    self.column_level_failed_validations_counter += ret
                    if self.settings['raise_exception_and_halt_on_found_validation_error'] \
                            and ret == 1:
                        raise ValidationErrorException('Evaluation of a validation rule failed')
                LOGGER.info('Evaluation of all column validation rules finished')

            except InvalidConfigException as conf_err:
                LOGGER.error('File %s cannot be validated, '
                             'config file has issues, %s',
                             self.file_name, conf_err)
                raise conf_err
            except InvalidLineColumnCountException as col_count_err:
                LOGGER.error('File %s cannot be validated, '
                             'column count is not consistent, %s',
                             self.file_name, col_count_err)
                raise col_count_err

        if self.column_level_failed_validations_counter > 0:
            raise ValidationErrorException('Evaluation of a validation rule failed')

        return 0

    def report_success(self):
        """
        report success method
        :return:
        """
        LOGGER.info('Validation of %s finished with no errors ',
                    self.file_name)

    def report_failure(self, val_err):
        """
        report failure method
        :return:
        """
        LOGGER.info('Failed to validate file %s because of %s',
                    self.file_name, val_err.__repr__())
        LOGGER.info('Validation of %s finished with: '
                    '%s failed file level validations ,'
                    '%s failed column level validations',
                    self.file_name,
                    self.file_level_failed_validations_counter,
                    self.column_level_failed_validations_counter)

    def close_file(self):
        """
        close file method
        :return:
        """
        self.file_obj.close_file_handler()

    def run(self, file_name):
        """
        validation orchestration runner
        :param file_name:
        :return:
        """
        try:
            self.setup_file(file_name)
            self.process_file_level_validations()
            self.process_column_level_validations()
            self.report_success()
            return 0
        except Exception as val_err:
            self.report_failure(val_err)
            return 1
        finally:
            self.close_file()


if __name__ == '__main__':
    SETTINGS = prepare_settings()
    PREPARED_ARGS = prepare_args()
    CONFIG = PREPARED_ARGS['config']
    FILE_LOCATION = PREPARED_ARGS['file_loc']

    VALIDATION_RUNNER = ValidationRunner(CONFIG, SETTINGS)
    for file in FILE_LOCATION:
        VALIDATION_RUNNER.run(file)
