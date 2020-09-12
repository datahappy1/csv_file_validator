"""
main module
"""
import os
import json
import logging
from argparse import ArgumentParser
from configparser import ConfigParser
from csv_file_validator.validation import SetupValidation, SetupFile, \
    ValidateFileLevel, ValidateColumnLevel
from csv_file_validator.exceptions import InvalidSettingsException, \
    InvalidConfigException, InvalidLineColumnCountException, \
    InvalidFileLocationException, FoundValidationErrorException, \
    FoundValidationErrorsException

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
        raise InvalidSettingsException(
            "missing project_scoped_settings section in settings.conf")

    if not parser.has_option('project_scoped_settings',
                             'SKIP_COLUMN_VALIDATIONS_ON_EMPTY_FILE'):
        raise InvalidSettingsException(
            "missing SKIP_COLUMN_VALIDATIONS_ON_EMPTY_FILE option "
            "in the section project_scoped_settings in settings.conf")

    if not parser.has_option('project_scoped_settings',
                             'RAISE_EXCEPTION_AND_HALT_ON_FAILED_VALIDATION'):
        raise InvalidSettingsException(
            "missing RAISE_EXCEPTION_AND_HALT_ON_FAILED_VALIDATION option "
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
    @staticmethod
    def validate_config(config):
        """
        validate config method
        :param config:
        :return:
        """
        validation_obj = SetupValidation(config)

        try:
            return validation_obj.get_validated_config()
        except InvalidConfigException as conf_err:
            LOGGER.error('Validation of config json file raised issued, %s', conf_err)
            raise conf_err

    @staticmethod
    def report_success(file_name):
        """
        report success method
        :param file_name:
        :return:
        """
        LOGGER.info('Validation of %s finished without any errors',
                    file_name)

    @staticmethod
    def report_failure(file_name, val_err):
        """
        report failure method
        :param file_name:
        :param val_err:
        :return:
        """
        LOGGER.info('Failed to validate file %s , reason: %s',
                    file_name, val_err.__str__())

    @staticmethod
    def close_file(file_obj):
        """
        close file method
        :param file_obj:
        :return:
        """
        file_obj.close_file_handler()

    @staticmethod
    def close_file_report_failure(file_name, file_obj, exc):
        """
        close file and report failure method
        :param file_name:
        :param file_obj:
        :param exc:
        :return:
        """
        ValidationRunner.close_file(file_obj)
        ValidationRunner.report_failure(file_name, exc)

    def __init__(self, config, settings):
        self.config = self.validate_config(config)
        self.settings = settings

    def setup_file_run(self, file_name):
        """
        setup file run method
        :param file_name:
        :return:
        """
        try:
            file_obj = SetupFile(self.config, file_name)
        except Exception as exc:
            LOGGER.error('File %s setup raised issues, %s', file_name, exc)
            raise exc

        LOGGER.info('Validation of %s started', file_name)

        if self.settings.get('skip_column_validations_on_empty_file') \
                not in (True, False):
            LOGGER.info('SKIP_COLUMN_VALIDATIONS_ON_EMPTY_FILE in settings.conf invalid, '
                        'setting value to False and continuing')
            self.settings['skip_column_validations_on_empty_file'] = False

        if self.settings.get('raise_exception_and_halt_on_failed_validation') \
                not in (True, False):
            LOGGER.info('RAISE_EXCEPTION_AND_HALT_ON_FAILED_VALIDATION '
                        'in settings.conf invalid, setting value to False and continuing')
            self.settings['raise_exception_and_halt_on_failed_validation'] = False

        return file_obj

    def process_file_level_validations(self, file_name, file_obj):
        """
        process file level validations method
        :param file_name:
        :param file_obj:
        :return:
        """
        file_level_failed_validations_counter = 0

        validation_file_obj = ValidateFileLevel(self.config, file_name)

        if file_obj.file_with_configured_header_has_empty_header:
            raise InvalidConfigException('File with header set to true in the '
                                         'config has no header row')

        file_level_validations_count = validation_file_obj.get_file_level_validations_count()

        LOGGER.info('Found %s file level validations', file_level_validations_count)

        if file_level_validations_count > 0:
            LOGGER.info('Evaluation of file validation rules starting')
            try:
                ret = validation_file_obj.validate_file()
                file_level_failed_validations_counter = ret
                if self.settings['raise_exception_and_halt_on_failed_validation'] \
                        and ret > 0:
                    raise FoundValidationErrorException('Evaluation of a '
                                                        'file level validation rule failed')
                LOGGER.info('Evaluation of all file validation rules finished')

            except InvalidConfigException as conf_err:
                LOGGER.error('File %s cannot be validated, config file has issues, %s',
                             file_name, conf_err)
                raise conf_err

        if file_level_failed_validations_counter > 0:
            raise FoundValidationErrorsException(f'Evaluation of '
                                                 f'{file_level_failed_validations_counter} '
                                                 f'file validation rule(s) failed')

        return 0

    def process_column_level_validations(self, file_name, file_obj):
        """
        process column level validations method
        :param file_name:
        :param file_obj:
        :return:
        """
        if file_obj.file_has_no_data_rows and \
                self.settings['skip_column_validations_on_empty_file']:
            LOGGER.info('File has no rows to validate, skipping column level validations')
            return 0

        column_level_failed_validations_counter = 0

        validation_column_obj = ValidateColumnLevel(self.config, file_name)

        column_level_validations_count = \
            validation_column_obj.get_column_level_validations_count()

        LOGGER.info('Found %s column level validations', column_level_validations_count)

        if column_level_validations_count > 0:
            LOGGER.info('Evaluation of column validation rules starting')

            try:
                for idx, line in validation_column_obj.file_read_generator():
                    ret = validation_column_obj.validate_line_values(line, idx)
                    column_level_failed_validations_counter += ret
                    if self.settings['raise_exception_and_halt_on_failed_validation'] \
                            and ret > 0:
                        raise FoundValidationErrorException('Evaluation of a '
                                                            'column level validation rule failed')
                LOGGER.info('Evaluation of all column validation rules finished')

            except InvalidConfigException as conf_err:
                LOGGER.error('File %s cannot be validated, config file has issues, %s',
                             file_name, conf_err)
                raise conf_err
            except InvalidLineColumnCountException as col_count_err:
                LOGGER.error('File %s cannot be validated, '
                             'column count is not consistent, %s',
                             file_name, col_count_err)
                raise col_count_err

        if column_level_failed_validations_counter > 0:
            raise FoundValidationErrorsException(f'Evaluation of '
                                                 f'{column_level_failed_validations_counter} '
                                                 f'column validation rule(s) failed')

        return 0

    def run(self, file_name):
        """
        validation orchestration runner
        :param file_name:
        :return:
        """
        try:
            file_obj = self.setup_file_run(file_name)
        except InvalidConfigException as invalid_config_exc:
            self.report_failure(file_name, invalid_config_exc)
            return 1

        _runner_accumulated_errors = str()

        try:
            self.process_file_level_validations(file_name, file_obj)
        except (FoundValidationErrorException, InvalidConfigException) as halt_flow_exc:
            self.close_file_report_failure(file_name, file_obj, halt_flow_exc)
            return 1
        except FoundValidationErrorsException as found_validation_errors_continue_flow_exc:
            _runner_accumulated_errors += str(found_validation_errors_continue_flow_exc) + '; '

        try:
            self.process_column_level_validations(file_name, file_obj)
        except (FoundValidationErrorException, InvalidConfigException,
                InvalidLineColumnCountException) as halt_flow_exc:
            self.close_file_report_failure(file_name, file_obj, halt_flow_exc)
            return 1
        except FoundValidationErrorsException as found_validation_errors_continue_flow_exc:
            _runner_accumulated_errors += str(found_validation_errors_continue_flow_exc)

        if _runner_accumulated_errors:
            self.close_file_report_failure(file_name, file_obj, _runner_accumulated_errors)
            return 1

        self.close_file(file_obj)
        self.report_success(file_name)

        return 0


if __name__ == '__main__':
    SETTINGS = prepare_settings()
    PREPARED_ARGS = prepare_args()
    CONFIG = PREPARED_ARGS['config']
    FILE_LOCATION = PREPARED_ARGS['file_loc']
    VALIDATION_RUNNER = ValidationRunner(CONFIG, SETTINGS)
    for file in FILE_LOCATION:
        VALIDATION_RUNNER.run(file)
