import json
import logging
import os

import pytest

from csv_file_validator.__main__ import process_file, ValidationResultEnum
from csv_file_validator.config import Config, \
    get_validated_config
from csv_file_validator.exceptions import InvalidConfigException
from csv_file_validator.settings_parser import Settings


class TestsFunctionalConfig:
    def test_correct_config_model1(self):
        correct_config = {
            "file_metadata": {"file_value_separator": ",",
                              "file_row_terminator": "\n",
                              "file_value_quote_char": "\"",
                              "file_has_header": True},
            "file_validation_rules": {"file_name_file_mask": ".+\\d+"},
            "column_validation_rules": {}
        }
        config = Config(**correct_config)

        assert config

        assert get_validated_config(correct_config)

    def test_correct_config_model2(self):
        correct_config = {
            "file_metadata": {"file_value_separator": ",",
                              "file_row_terminator": "\n",
                              "file_value_quote_char": "\"",
                              "file_has_header": True},
            "file_validation_rules": {"file_name_file_mask": ".+\\d+"},
        }

        assert get_validated_config(correct_config)

    def test_incorrect_config_model1(self):
        incorrect_config = {
            "file_metadata": {"some_invalid_key": True,
                              "file_row_terminator": "\n"},
            "file_validation_rules": {"file_name_file_mask": ".+\\d+"},
            "column_validation_rules": []
        }

        with pytest.raises(TypeError):
            Config(**incorrect_config)

        with pytest.raises(InvalidConfigException):
            get_validated_config(incorrect_config)

    def test_incorrect_config_model2(self):
        incorrect_config = {
            "file_metadata": {"file_row_terminator": "\n"},
            "file_validation_rules": {"file_name_file_mask": ".+\\d+"},
            "column_validation_rules": []
        }

        with pytest.raises(TypeError):
            Config(**incorrect_config)

        with pytest.raises(InvalidConfigException):
            get_validated_config(incorrect_config)

    def test_incorrect_config_model3(self):
        incorrect_config = {
            "file_metadata": {"file_value_separator": ",",
                              "file_row_terminator": "\n",
                              "file_value_quote_char": "\"",
                              "file_has_header": "yes"},
            "file_validation_rules": {"file_name_file_mask": ".+\\d+"},
            "column_validation_rules": []
        }

        with pytest.raises(ValueError):
            Config(**incorrect_config)

        with pytest.raises(InvalidConfigException):
            get_validated_config(incorrect_config)

    def test_empty_config_model(self):
        empty_config = {
            "file_metadata": {},
            "file_validation_rules": {},
            "column_validation_rules": {}
        }

        with pytest.raises(TypeError):
            Config(**empty_config)

        with pytest.raises(InvalidConfigException):
            get_validated_config(empty_config)


class TestsFunctionalValidation:
    @staticmethod
    def open_config_file(config):
        with open(config, mode='r') as json_file:
            parsed_config = json.load(json_file)
            return Config(**parsed_config)

    def test_correct_file_with_header(self, caplog):
        args = {'file_loc': os.getcwd() + '/files/csv/with_header/SalesJan2009_with_header_correct_file.csv',
                'config': os.getcwd() + '/files/configs/config_with_header.json'}

        parsed_config = TestsFunctionalValidation.open_config_file(args['config'])

        settings = Settings(**{'skip_column_validations_on_empty_file': True,
                               'raise_exception_and_halt_on_failed_validation': False})

        caplog.set_level(logging.INFO)

        assert ValidationResultEnum.SUCCESS == process_file(parsed_config, settings, args['file_loc'])

        assert f"Validation of {args['file_loc']} finished without any errors" in caplog.text

    def test_correct_file_without_header(self, caplog):
        args = {'file_loc': os.getcwd() + '/files/csv/without_header/SalesJan2009_without_header_correct_file.csv',
                'config': os.getcwd() + '/files/configs/config_without_header.json'}

        parsed_config = TestsFunctionalValidation.open_config_file(args['config'])

        settings = Settings(**{'skip_column_validations_on_empty_file': True,
                               'raise_exception_and_halt_on_failed_validation': False})

        caplog.set_level(logging.INFO)

        assert ValidationResultEnum.SUCCESS == process_file(parsed_config, settings, args['file_loc'])

        assert f"Validation of {args['file_loc']} finished without any errors" in caplog.text

    def test_incorrect_file_with_header(self, caplog):
        args = {'file_loc': os.getcwd() + '/files/csv/with_header/SalesJan2009_with_header_incorrect_file.csv',
                'config': os.getcwd() + '/files/configs/config_with_header.json'}

        parsed_config = TestsFunctionalValidation.open_config_file(args['config'])

        settings = Settings(**{'skip_column_validations_on_empty_file': True,
                               'raise_exception_and_halt_on_failed_validation': False})

        caplog.set_level(logging.ERROR)

        assert ValidationResultEnum.FAILURE == process_file(parsed_config, settings, args['file_loc'])

        assert 'check_column_allow_int_value_range - failed to meet this value' in caplog.text

    def test_incorrect_file_without_header(self, caplog):
        args = {'file_loc': os.getcwd() + '/files/csv/without_header/SalesJan2009_without_header_incorrect_file.csv',
                'config': os.getcwd() + '/files/configs/config_without_header.json'}

        parsed_config = TestsFunctionalValidation.open_config_file(args['config'])

        settings = Settings(**{'skip_column_validations_on_empty_file': True,
                               'raise_exception_and_halt_on_failed_validation': False})

        caplog.set_level(logging.ERROR)

        assert ValidationResultEnum.FAILURE == process_file(parsed_config, settings, args['file_loc'])

        assert 'failed to meet this value' in caplog.text

    def test_missing_file(self, caplog):
        args = {'file_loc': os.getcwd() + '/files/csv/MISSING_FILE.csv',
                'config': os.getcwd() + '/files/configs/config_with_header.json'}

        parsed_config = TestsFunctionalValidation.open_config_file(args['config'])

        settings = Settings(**{'skip_column_validations_on_empty_file': True,
                               'raise_exception_and_halt_on_failed_validation': False})

        caplog.set_level(logging.ERROR)

        assert ValidationResultEnum.COULD_NOT_PROCESS == process_file(parsed_config, settings, args['file_loc'])

        assert f'File {args["file_loc"]} setup raised issues, [Errno 2] No such file or directory:' in caplog.text

    def test_empty_file_skip_column_validations_with_header(self, caplog):
        args = {'file_loc': os.getcwd() + '/files/csv/with_header/SalesJan2009_with_header_empty_file.csv',
                'config': os.getcwd() + '/files/configs/config_with_header.json'}

        parsed_config = TestsFunctionalValidation.open_config_file(args['config'])

        settings = Settings(**{'skip_column_validations_on_empty_file': True,
                               'raise_exception_and_halt_on_failed_validation': False})

        caplog.set_level(logging.INFO)

        assert ValidationResultEnum.SUCCESS == process_file(parsed_config, settings, args['file_loc'])

        assert 'File has no rows to validate, skipping column level validations' in caplog.text

    def test_empty_file_dont_skip_column_validations_with_header(self, caplog):
        args = {'file_loc': os.getcwd() + '/files/csv/with_header/SalesJan2009_with_header_empty_file.csv',
                'config': os.getcwd() + '/files/configs/config_with_header.json'}

        parsed_config = TestsFunctionalValidation.open_config_file(args['config'])

        settings = Settings(**{'skip_column_validations_on_empty_file': False,
                               'raise_exception_and_halt_on_failed_validation': False})

        caplog.set_level(logging.INFO)

        assert ValidationResultEnum.SUCCESS == process_file(parsed_config, settings, args['file_loc'])

        assert 'Found 4 column validations' in caplog.text

    def test_empty_file_skip_column_validations_without_header(self, caplog):
        args = {'file_loc': os.getcwd() + '/files/csv/without_header/SalesJan2009_without_header_empty_file.csv',
                'config': os.getcwd() + '/files/configs/config_without_header.json'}

        parsed_config = TestsFunctionalValidation.open_config_file(args['config'])

        settings = Settings(**{'skip_column_validations_on_empty_file': True,
                               'raise_exception_and_halt_on_failed_validation': False})

        caplog.set_level(logging.INFO)

        assert ValidationResultEnum.SUCCESS == process_file(parsed_config, settings, args['file_loc'])

        assert 'File has no rows to validate, skipping column level validations' in caplog.text

    def test_config_without_header_file_with_header(self, caplog):
        args = {'file_loc': os.getcwd() + '/files/csv/with_header/SalesJan2009_with_header_correct_file.csv',
                'config': os.getcwd() + '/files/configs/config_without_header.json'}

        parsed_config = TestsFunctionalValidation.open_config_file(args['config'])

        settings = Settings(**{'skip_column_validations_on_empty_file': True,
                               'raise_exception_and_halt_on_failed_validation': False})

        caplog.set_level(logging.ERROR)

        assert ValidationResultEnum.FAILURE == process_file(parsed_config, settings, args['file_loc'])

        assert 'check_column_allow_data_type - failed to meet this value' in caplog.text

    def test_config_with_header_file_without_header(self, caplog):
        args = {'file_loc': os.getcwd() + '/files/csv/without_header/SalesJan2009_without_header_correct_file.csv',
                'config': os.getcwd() + '/files/configs/config_with_header.json'}

        parsed_config = TestsFunctionalValidation.open_config_file(args['config'])

        settings = Settings(**{'skip_column_validations_on_empty_file': True,
                               'raise_exception_and_halt_on_failed_validation': False})

        caplog.set_level(logging.ERROR)

        assert ValidationResultEnum.FAILURE == process_file(parsed_config, settings, args['file_loc'])

        assert "check_file_header_column_names - failed to meet this value : ['Transaction_date', 'Product', 'Price', 'Payment_Type', 'Name', 'City', 'State', 'Country', 'Account_Created', 'Last_Login', 'Latitude', 'Longitude']" in caplog.text

    def test_empty_file_dont_skip_column_validations_without_header(self, caplog):
        args = {'file_loc': os.getcwd() + '/files/csv/without_header/SalesJan2009_without_header_empty_file.csv',
                'config': os.getcwd() + '/files/configs/config_without_header.json'}

        parsed_config = TestsFunctionalValidation.open_config_file(args['config'])

        settings = Settings(**{'skip_column_validations_on_empty_file': False,
                               'raise_exception_and_halt_on_failed_validation': False})

        caplog.set_level(logging.INFO)

        assert ValidationResultEnum.FAILURE == process_file(parsed_config, settings, args['file_loc'])

        assert "Column validations set in the config, but none of the expected columns found in the file" in caplog.text

    def test_inconsistent_file_with_header(self, caplog):
        args = {
            'file_loc': os.getcwd() + '/files/csv/without_header/SalesJan2009_without_header_inconsistent_columns_file.csv',
            'config': os.getcwd() + '/files/configs/config_without_header.json'}

        parsed_config = TestsFunctionalValidation.open_config_file(args['config'])

        settings = Settings(**{'skip_column_validations_on_empty_file': True,
                               'raise_exception_and_halt_on_failed_validation': False})

        caplog.set_level(logging.ERROR)

        assert ValidationResultEnum.FAILURE == process_file(parsed_config, settings, args['file_loc'])

        assert 'SalesJan2009_without_header_inconsistent_columns_file.csv cannot be validated, column count is not consistent, row' in caplog.text

    def test_inconsistent_file_without_header(self, caplog):
        args = {
            'file_loc': os.getcwd() + '/files/csv/without_header/SalesJan2009_without_header_inconsistent_columns_file.csv',
            'config': os.getcwd() + '/files/configs/config_without_header.json'}

        parsed_config = TestsFunctionalValidation.open_config_file(args['config'])

        settings = Settings(**{'skip_column_validations_on_empty_file': True,
                               'raise_exception_and_halt_on_failed_validation': False})

        caplog.set_level(logging.ERROR)

        assert ValidationResultEnum.FAILURE == process_file(parsed_config, settings, args['file_loc'])

        assert 'SalesJan2009_without_header_inconsistent_columns_file.csv cannot be validated, column count is not consistent, row' in caplog.text
