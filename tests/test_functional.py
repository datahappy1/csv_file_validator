import os
import json
import logging
from csv_file_validator.__main__ import ValidationRunner


class TestsFunctionalPositive:
    @staticmethod
    def open_config_file(config):
        with open(config, mode='r') as json_file:
            parsed_config = json.load(json_file)
            return parsed_config

    def test_correct_file_with_header(self):
        args = {'file_loc': os.getcwd()+'/files/csv/with_header/SalesJan2009_with_header_correct_file.csv',
                'config': os.getcwd()+'/files/configs/config_with_header.json'}

        parsed_config = TestsFunctionalPositive.open_config_file(args['config'])

        settings = {'skip_column_validations_on_empty_file': True,
                    'raise_exception_and_halt_on_found_validation_error': False}

        obj = ValidationRunner(parsed_config, settings)
        result = obj.run(args['file_loc'])

        assert result == 0

    def test_correct_file_without_header(self):
        args = {'file_loc': os.getcwd()+'/files/csv/without_header/SalesJan2009_without_header_correct_file.csv',
                'config': os.getcwd()+'/files/configs/config_without_header.json'}

        parsed_config = TestsFunctionalPositive.open_config_file(args['config'])

        settings = {'skip_column_validations_on_empty_file': True,
                    'raise_exception_and_halt_on_found_validation_error': False}

        obj = ValidationRunner(parsed_config, settings)
        result = obj.run(args['file_loc'])

        assert result == 0

    def test_incorrect_file_with_header(self, caplog):
        args = {'file_loc': os.getcwd()+'/files/csv/with_header/SalesJan2009_with_header_incorrect_file.csv',
                'config': os.getcwd()+'/files/configs/config_with_header.json'}

        parsed_config = TestsFunctionalPositive.open_config_file(args['config'])

        settings = {'skip_column_validations_on_empty_file': True,
                    'raise_exception_and_halt_on_found_validation_error': False}

        caplog.set_level(logging.ERROR)

        obj = ValidationRunner(parsed_config, settings)
        result = obj.run(args['file_loc'])

        assert 'check_column_allow_numeric_value_range - failed to meet this value' in caplog.text
        assert result == 0

    def test_incorrect_file_without_header(self, caplog):
        args = {'file_loc': os.getcwd()+'/files/csv/without_header/SalesJan2009_without_header_incorrect_file.csv',
                'config': os.getcwd()+'/files/configs/config_without_header.json'}

        parsed_config = TestsFunctionalPositive.open_config_file(args['config'])

        settings = {'skip_column_validations_on_empty_file': True,
                    'raise_exception_and_halt_on_found_validation_error': False}

        caplog.set_level(logging.ERROR)

        obj = ValidationRunner(parsed_config, settings)
        result = obj.run(args['file_loc'])

        assert 'failed to meet this value' in caplog.text
        assert result == 0

    def test_empty_file_skip_column_validations_with_header(self, caplog):
        args = {'file_loc': os.getcwd()+'/files/csv/with_header/SalesJan2009_with_header_empty_file.csv',
                'config': os.getcwd()+'/files/configs/config_with_header.json'}

        parsed_config = TestsFunctionalPositive.open_config_file(args['config'])

        settings = {'skip_column_validations_on_empty_file': True,
                    'raise_exception_and_halt_on_found_validation_error': False}

        caplog.set_level(logging.INFO)

        obj = ValidationRunner(parsed_config, settings)
        result = obj.run(args['file_loc'])

        assert 'File has no rows to validate, skipping column level validations' in caplog.text
        assert result == 0

    def test_empty_file_dont_skip_column_validations_with_header(self, caplog):
        args = {'file_loc': os.getcwd()+'/files/csv/with_header/SalesJan2009_with_header_empty_file.csv',
                'config': os.getcwd()+'/files/configs/config_with_header.json'}

        parsed_config = TestsFunctionalPositive.open_config_file(args['config'])

        settings = {'skip_column_validations_on_empty_file': False,
                    'raise_exception_and_halt_on_found_validation_error': False}

        caplog.set_level(logging.INFO)

        obj = ValidationRunner(parsed_config, settings)
        result = obj.run(args['file_loc'])

        assert 'Found 3 column level validations' in caplog.text
        assert result == 0

    def test_empty_file_skip_column_validations_without_header(self, caplog):
        args = {'file_loc': os.getcwd()+'/files/csv/without_header/SalesJan2009_without_header_empty_file.csv',
                'config': os.getcwd()+'/files/configs/config_without_header.json'}

        parsed_config = TestsFunctionalPositive.open_config_file(args['config'])

        settings = {'skip_column_validations_on_empty_file': True,
                    'raise_exception_and_halt_on_found_validation_error': False}

        caplog.set_level(logging.INFO)

        obj = ValidationRunner(parsed_config, settings)
        result = obj.run(args['file_loc'])

        assert 'File has no rows to validate, skipping column level validations' in caplog.text
        assert result == 0

    def test_config_without_header_file_with_header(self, caplog):
        args = {'file_loc': os.getcwd()+'/files/csv/with_header/SalesJan2009_with_header_correct_file.csv',
                'config': os.getcwd()+'/files/configs/config_without_header.json'}

        parsed_config = TestsFunctionalPositive.open_config_file(args['config'])

        settings = {'skip_column_validations_on_empty_file': True,
                    'raise_exception_and_halt_on_found_validation_error': False}

        caplog.set_level(logging.ERROR)

        obj = ValidationRunner(parsed_config, settings)
        result = obj.run(args['file_loc'])

        assert 'check_column_allow_data_type - failed to meet this value' in caplog.text
        assert result == 0

class TestsFunctionalNegative:

    def test_empty_file_dont_skip_column_validations_without_header(self, caplog):
        args = {'file_loc': os.getcwd()+'/files/csv/without_header/SalesJan2009_without_header_empty_file.csv',
                'config': os.getcwd()+'/files/configs/config_without_header.json'}

        parsed_config = TestsFunctionalPositive.open_config_file(args['config'])

        settings = {'skip_column_validations_on_empty_file': False,
                    'raise_exception_and_halt_on_found_validation_error': False}

        caplog.set_level(logging.INFO)

        obj = ValidationRunner(parsed_config, settings)
        result = obj.run(args['file_loc'])

        assert "InvalidConfigException('Column validations set in the config, but none of the expected columns found in the file')" in caplog.text
        assert result == 1

    def test_inconsistent_file_with_header(self, caplog):
        args = {'file_loc': os.getcwd()+'/files/csv/without_header/SalesJan2009_without_header_inconsistent_columns_file.csv',
                'config': os.getcwd()+'/files/configs/config_without_header.json'}

        parsed_config = TestsFunctionalPositive.open_config_file(args['config'])

        settings = {'skip_column_validations_on_empty_file': True,
                    'raise_exception_and_halt_on_found_validation_error': False}

        caplog.set_level(logging.ERROR)

        obj = ValidationRunner(parsed_config, settings)
        result = obj.run(args['file_loc'])

        assert 'SalesJan2009_without_header_inconsistent_columns_file.csv cannot be validated, column count is not consistent, row' in caplog.text
        assert result == 1

    def test_inconsistent_file_without_header(self, caplog):
        args = {'file_loc': os.getcwd()+'/files/csv/without_header/SalesJan2009_without_header_inconsistent_columns_file.csv',
                'config': os.getcwd()+'/files/configs/config_without_header.json'}

        parsed_config = TestsFunctionalPositive.open_config_file(args['config'])

        settings = {'skip_column_validations_on_empty_file': True,
                    'raise_exception_and_halt_on_found_validation_error': False}

        caplog.set_level(logging.ERROR)

        obj = ValidationRunner(parsed_config, settings)
        result = obj.run(args['file_loc'])

        assert 'SalesJan2009_without_header_inconsistent_columns_file.csv cannot be validated, column count is not consistent, row' in caplog.text
        assert result == 1

    def test_config_with_header_file_without_header(self, caplog):
        args = {'file_loc': os.getcwd()+'/files/csv/without_header/SalesJan2009_without_header_correct_file.csv',
                'config': os.getcwd()+'/files/configs/config_with_header.json'}

        parsed_config = TestsFunctionalPositive.open_config_file(args['config'])

        settings = {'skip_column_validations_on_empty_file': True,
                    'raise_exception_and_halt_on_found_validation_error': False}

        caplog.set_level(logging.INFO)

        obj = ValidationRunner(parsed_config, settings)
        result = obj.run(args['file_loc'])

        assert "SalesJan2009_without_header_correct_file.csv because of InvalidConfigException('Column validations set in the config, but not all expected columns found in the file')" in caplog.text
        assert result == 1
