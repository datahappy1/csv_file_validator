import json
import logging
import os

from csv_file_validator.__main__ import process_file, ValidationResultEnum
from csv_file_validator.config import Config
from csv_file_validator.settings_parser import Settings


class TestsFunctional:
    @staticmethod
    def open_config_file(config):
        with open(config, mode='r') as json_file:
            parsed_config = json.load(json_file)
            return Config(**parsed_config)

    def test_correct_file_with_header(self, caplog):
        args = {'file_loc': os.getcwd() + '/files/csv/with_header/SalesJan2009_with_header_correct_file.csv',
                'config': os.getcwd() + '/files/configs/config_with_header.json'}

        parsed_config = TestsFunctional.open_config_file(args['config'])

        settings = Settings(**{'skip_column_validations_on_empty_file': True,
                               'raise_exception_and_halt_on_failed_validation': False})

        caplog.set_level(logging.INFO)

        assert ValidationResultEnum.SUCCESS == process_file(parsed_config, settings, args['file_loc'])

        assert f"Validation of {args['file_loc']} finished without any errors" in caplog.text

    def test_correct_file_without_header(self, caplog):
        args = {'file_loc': os.getcwd() + '/files/csv/without_header/SalesJan2009_without_header_correct_file.csv',
                'config': os.getcwd() + '/files/configs/config_without_header.json'}

        parsed_config = TestsFunctional.open_config_file(args['config'])

        settings = Settings(**{'skip_column_validations_on_empty_file': True,
                               'raise_exception_and_halt_on_failed_validation': False})

        caplog.set_level(logging.INFO)

        assert ValidationResultEnum.SUCCESS == process_file(parsed_config, settings, args['file_loc'])

        assert f"Validation of {args['file_loc']} finished without any errors" in caplog.text

    def test_incorrect_file_with_header(self, caplog):
        args = {'file_loc': os.getcwd() + '/files/csv/with_header/SalesJan2009_with_header_incorrect_file.csv',
                'config': os.getcwd() + '/files/configs/config_with_header.json'}

        parsed_config = TestsFunctional.open_config_file(args['config'])

        settings = Settings(**{'skip_column_validations_on_empty_file': True,
                               'raise_exception_and_halt_on_failed_validation': False})

        caplog.set_level(logging.ERROR)

        assert ValidationResultEnum.FAILURE == process_file(parsed_config, settings, args['file_loc'])

        assert 'check_column_allow_int_value_range - failed to meet this value' in caplog.text

    def test_incorrect_file_without_header(self, caplog):
        args = {'file_loc': os.getcwd() + '/files/csv/without_header/SalesJan2009_without_header_incorrect_file.csv',
                'config': os.getcwd() + '/files/configs/config_without_header.json'}

        parsed_config = TestsFunctional.open_config_file(args['config'])

        settings = Settings(**{'skip_column_validations_on_empty_file': True,
                               'raise_exception_and_halt_on_failed_validation': False})

        caplog.set_level(logging.ERROR)

        assert ValidationResultEnum.FAILURE == process_file(parsed_config, settings, args['file_loc'])

        assert 'failed to meet this value' in caplog.text

    def test_missing_file(self, caplog):
        args = {'file_loc': os.getcwd() + '/files/csv/MISSING_FILE.csv',
                'config': os.getcwd() + '/files/configs/config_with_header.json'}

        parsed_config = TestsFunctional.open_config_file(args['config'])

        settings = Settings(**{'skip_column_validations_on_empty_file': True,
                               'raise_exception_and_halt_on_failed_validation': False})

        caplog.set_level(logging.ERROR)

        assert ValidationResultEnum.COULD_NOT_PROCESS == process_file(parsed_config, settings, args['file_loc'])

        assert f'File {args["file_loc"]} setup raised issues, [Errno 2] No such file or directory:' in caplog.text

    def test_empty_file_skip_column_validations_with_header(self, caplog):
        args = {'file_loc': os.getcwd() + '/files/csv/with_header/SalesJan2009_with_header_empty_file.csv',
                'config': os.getcwd() + '/files/configs/config_with_header.json'}

        parsed_config = TestsFunctional.open_config_file(args['config'])

        settings = Settings(**{'skip_column_validations_on_empty_file': True,
                               'raise_exception_and_halt_on_failed_validation': False})

        caplog.set_level(logging.INFO)

        assert ValidationResultEnum.SUCCESS == process_file(parsed_config, settings, args['file_loc'])

        assert 'File has no rows to validate, skipping column level validations' in caplog.text

    def test_empty_file_dont_skip_column_validations_with_header(self, caplog):
        args = {'file_loc': os.getcwd() + '/files/csv/with_header/SalesJan2009_with_header_empty_file.csv',
                'config': os.getcwd() + '/files/configs/config_with_header.json'}

        parsed_config = TestsFunctional.open_config_file(args['config'])

        settings = Settings(**{'skip_column_validations_on_empty_file': False,
                               'raise_exception_and_halt_on_failed_validation': False})

        caplog.set_level(logging.INFO)

        assert ValidationResultEnum.SUCCESS == process_file(parsed_config, settings, args['file_loc'])

        assert 'Found 4 column level validations' in caplog.text

    def test_empty_file_skip_column_validations_without_header(self, caplog):
        args = {'file_loc': os.getcwd() + '/files/csv/without_header/SalesJan2009_without_header_empty_file.csv',
                'config': os.getcwd() + '/files/configs/config_without_header.json'}

        parsed_config = TestsFunctional.open_config_file(args['config'])

        settings = Settings(**{'skip_column_validations_on_empty_file': True,
                               'raise_exception_and_halt_on_failed_validation': False})

        caplog.set_level(logging.INFO)

        assert ValidationResultEnum.SUCCESS == process_file(parsed_config, settings, args['file_loc'])

        assert 'File has no rows to validate, skipping column level validations' in caplog.text

    def test_config_without_header_file_with_header(self, caplog):
        args = {'file_loc': os.getcwd() + '/files/csv/with_header/SalesJan2009_with_header_correct_file.csv',
                'config': os.getcwd() + '/files/configs/config_without_header.json'}

        parsed_config = TestsFunctional.open_config_file(args['config'])

        settings = Settings(**{'skip_column_validations_on_empty_file': True,
                               'raise_exception_and_halt_on_failed_validation': False})

        caplog.set_level(logging.ERROR)

        assert ValidationResultEnum.FAILURE == process_file(parsed_config, settings, args['file_loc'])

        assert 'check_column_allow_data_type - failed to meet this value' in caplog.text

    def test_config_with_header_file_without_header(self, caplog):
        args = {'file_loc': os.getcwd() + '/files/csv/without_header/SalesJan2009_without_header_correct_file.csv',
                'config': os.getcwd() + '/files/configs/config_with_header.json'}

        parsed_config = TestsFunctional.open_config_file(args['config'])

        settings = Settings(**{'skip_column_validations_on_empty_file': True,
                               'raise_exception_and_halt_on_failed_validation': False})

        caplog.set_level(logging.ERROR)

        assert ValidationResultEnum.FAILURE == process_file(parsed_config, settings, args['file_loc'])

        assert "check_file_header_column_names - failed to meet this value : ['Transaction_date', 'Product', 'Price', 'Payment_Type', 'Name', 'City', 'State', 'Country', 'Account_Created', 'Last_Login', 'Latitude', 'Longitude']" in caplog.text

    def test_empty_file_dont_skip_column_validations_without_header(self, caplog):
        args = {'file_loc': os.getcwd() + '/files/csv/without_header/SalesJan2009_without_header_empty_file.csv',
                'config': os.getcwd() + '/files/configs/config_without_header.json'}

        parsed_config = TestsFunctional.open_config_file(args['config'])

        settings = Settings(**{'skip_column_validations_on_empty_file': False,
                               'raise_exception_and_halt_on_failed_validation': False})

        caplog.set_level(logging.INFO)

        assert ValidationResultEnum.FAILURE == process_file(parsed_config, settings, args['file_loc'])

        assert "Column validations set in the config, but none of the expected columns found in the file" in caplog.text

    def test_inconsistent_file_with_header(self, caplog):
        args = {
            'file_loc': os.getcwd() + '/files/csv/without_header/SalesJan2009_without_header_inconsistent_columns_file.csv',
            'config': os.getcwd() + '/files/configs/config_without_header.json'}

        parsed_config = TestsFunctional.open_config_file(args['config'])

        settings = Settings(**{'skip_column_validations_on_empty_file': True,
                               'raise_exception_and_halt_on_failed_validation': False})

        caplog.set_level(logging.ERROR)

        assert ValidationResultEnum.FAILURE == process_file(parsed_config, settings, args['file_loc'])

        assert 'SalesJan2009_without_header_inconsistent_columns_file.csv cannot be validated, column count is not consistent, row' in caplog.text

    def test_inconsistent_file_without_header(self, caplog):
        args = {
            'file_loc': os.getcwd() + '/files/csv/without_header/SalesJan2009_without_header_inconsistent_columns_file.csv',
            'config': os.getcwd() + '/files/configs/config_without_header.json'}

        parsed_config = TestsFunctional.open_config_file(args['config'])

        settings = Settings(**{'skip_column_validations_on_empty_file': True,
                               'raise_exception_and_halt_on_failed_validation': False})

        caplog.set_level(logging.ERROR)

        assert ValidationResultEnum.FAILURE == process_file(parsed_config, settings, args['file_loc'])

        assert 'SalesJan2009_without_header_inconsistent_columns_file.csv cannot be validated, column count is not consistent, row' in caplog.text
