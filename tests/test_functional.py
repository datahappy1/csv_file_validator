import os
import json
import logging
from csv_file_validator.__main__ import ValidationRunner


class TestsFunctional:
    @staticmethod
    def open_config_file(config):
        with open(config, mode='r') as json_file:
            parsed_config = json.load(json_file)
            return parsed_config

    def test_success_fixed_file_with_header(self):
        args = {'file_loc': os.getcwd()+'/files/csv/with_header/SalesJan2009_with_header_fixed.csv',
                'config': os.getcwd()+'/files/configs/config_with_header.json'}

        parsed_config = TestsFunctional.open_config_file(args['config'])

        settings = {'skip_column_validations_on_empty_file': True}

        obj = ValidationRunner(parsed_config, settings)
        obj.setup_file(args['file_loc'])
        obj.process_file_level_validations()
        obj.process_column_level_validations()
        result = obj.teardown_file()

        assert result == 0

    def test_success_invalid_file_with_header(self, caplog):
        args = {'file_loc': os.getcwd()+'/files/csv/with_header/SalesJan2009_with_header_invalid_file.csv',
                'config': os.getcwd()+'/files/configs/config_with_header.json'}

        parsed_config = TestsFunctional.open_config_file(args['config'])

        settings = {'skip_column_validations_on_empty_file': True}

        caplog.set_level(logging.ERROR)

        obj = ValidationRunner(parsed_config, settings)
        obj.setup_file(args['file_loc'])
        obj.process_file_level_validations()
        obj.process_column_level_validations()
        result = obj.teardown_file()

        assert 'check_column_allow_numeric_value_range - failed to meet this value' in caplog.text
        assert result == 0

    def test_success_empty_file_skip_column_validations_with_header(self, caplog):
        args = {'file_loc': os.getcwd()+'/files/csv/with_header/SalesJan2009_with_header_empty.csv',
                'config': os.getcwd()+'/files/configs/config_with_header.json'}

        parsed_config = TestsFunctional.open_config_file(args['config'])

        settings = {'skip_column_validations_on_empty_file': True}

        caplog.set_level(logging.INFO)

        obj = ValidationRunner(parsed_config, settings)
        obj.setup_file(args['file_loc'])
        obj.process_file_level_validations()
        obj.process_column_level_validations()
        result = obj.teardown_file()

        assert 'File has no rows to validate, skipping column level validations' in caplog.text
        assert result == 0

    def test_fail_empty_file_dont_skip_column_validations_with_header(self, caplog):
        args = {'file_loc': os.getcwd()+'/files/csv/with_header/SalesJan2009_with_header_empty.csv',
                'config': os.getcwd()+'/files/configs/config_with_header.json'}

        parsed_config = TestsFunctional.open_config_file(args['config'])

        settings = {'skip_column_validations_on_empty_file': False}

        caplog.set_level(logging.ERROR)

        obj = ValidationRunner(parsed_config, settings)
        obj.setup_file(args['file_loc'])
        obj.process_file_level_validations()
        obj.process_column_level_validations()
        result = obj.teardown_file()

        assert 'column count is not consistent, row #: 1, expected column count: 0, actual column count: 12' in caplog.text
        assert result == 1

    def test_success_file_without_header(self):
        args = {'file_loc': os.getcwd()+'/files/csv/without_header/SalesJan2009_without_header_fixed.csv',
                'config': os.getcwd()+'/files/configs/config_without_header.json'}

        parsed_config = TestsFunctional.open_config_file(args['config'])

        settings = {'skip_column_validations_on_empty_file': True}

        obj = ValidationRunner(parsed_config, settings)
        obj.setup_file(args['file_loc'])
        obj.process_file_level_validations()
        obj.process_column_level_validations()
        result = obj.teardown_file()

        assert result == 0

    def test_success_empty_file_skip_column_validations_without_header(self, caplog):
        args = {'file_loc': os.getcwd()+'/files/csv/without_header/SalesJan2009_without_header_empty.csv',
                'config': os.getcwd()+'/files/configs/config_without_header.json'}

        parsed_config = TestsFunctional.open_config_file(args['config'])

        settings = {'skip_column_validations_on_empty_file': True}

        caplog.set_level(logging.INFO)

        obj = ValidationRunner(parsed_config, settings)
        obj.setup_file(args['file_loc'])
        obj.process_file_level_validations()
        obj.process_column_level_validations()
        result = obj.teardown_file()

        assert 'File has no rows to validate, skipping column level validations' in caplog.text
        assert result == 0

    def test_fail_empty_file_dont_skip_column_validations_without_header(self, caplog):
        args = {'file_loc': os.getcwd()+'/files/csv/without_header/SalesJan2009_without_header_empty.csv',
                'config': os.getcwd()+'/files/configs/config_without_header.json'}

        parsed_config = TestsFunctional.open_config_file(args['config'])

        settings = {'skip_column_validations_on_empty_file': False}

        caplog.set_level(logging.INFO)

        obj = ValidationRunner(parsed_config, settings)
        obj.setup_file(args['file_loc'])
        obj.process_file_level_validations()
        obj.process_column_level_validations()
        result = obj.teardown_file()

        assert 'Found 3 column level validations' in caplog.text
        assert result == 1

    def test_fail_inconsistent_file_without_header(self, caplog):
        args = {'file_loc': os.getcwd()+'/files/csv/without_header/SalesJan2009_without_header_invalid_file.csv',
                'config': os.getcwd()+'/files/configs/config_without_header.json'}

        parsed_config = TestsFunctional.open_config_file(args['config'])

        settings = {'skip_column_validations_on_empty_file': True}

        caplog.set_level(logging.ERROR)

        obj = ValidationRunner(parsed_config, settings)
        obj.setup_file(args['file_loc'])
        obj.process_file_level_validations()
        obj.process_column_level_validations()
        result = obj.teardown_file()

        assert 'SalesJan2009_without_header_invalid_file.csv cannot be validated, column count is not consistent, row' in caplog.text
        assert result == 1
