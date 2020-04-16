import os
import json
import logging
from pathlib import Path
from unittest.mock import patch
from csv_file_validator.__main__ import validation_runner, get_project_scope_settings


class TestsFunctional:
    @staticmethod
    def open_config_file(config):
        with open(config, mode='r') as json_file:
            parsed_config = json.load(json_file)
            return parsed_config

    # def test_mock(self):
    #     with patch('csv_file_validator.__main__.get_project_scope_settings') as mock:
    #         instance = mock.return_value
    #         instance.method.return_value = False
    #         print(str(Path(os.getcwd()).parents[0]) + 'csv_file_validator\\settings.conf')
    #         #result = get_project_scope_settings('C:\\Users\\pavel.prudky\\PycharmProjects\\file_validator\\csv_file_validator\\settings.conf')
    #         result = get_project_scope_settings(str(Path(os.getcwd()).parents[0]) + '\\csv_file_validator\\settings.conf')
    #         print('xxx')
    #         print(result)

    def test_success_file_with_header(self):
        args = {'file_loc': os.getcwd()+'/files/csv/with_header/SalesJan2009_with_header_fixed.csv',
                'config': os.getcwd()+'/files/configs/config_with_header.json'}

        parsed_config = TestsFunctional.open_config_file(args['config'])

        result = validation_runner(args['file_loc'], parsed_config)

        assert result == 0

    def test_fail_file_with_header(self, caplog):
        args = {'file_loc': os.getcwd()+'/files/csv/with_header/SalesJan2009_with_header_invalid_file.csv',
                'config': os.getcwd()+'/files/configs/config_with_header.json'}

        parsed_config = TestsFunctional.open_config_file(args['config'])

        caplog.set_level(logging.ERROR)
        result = validation_runner(args['file_loc'], parsed_config)

        assert 'check_column_allow_numeric_value_range - failed to meet this value' in caplog.text
        assert result == 0

    def test_success_file_without_header(self):
        args = {'file_loc': os.getcwd()+'/files/csv/without_header/SalesJan2009_without_header_fixed.csv',
                'config': os.getcwd()+'/files/configs/config_without_header.json'}

        parsed_config = TestsFunctional.open_config_file(args['config'])

        result = validation_runner(args['file_loc'], parsed_config)

        assert result == 0

    def test_fail_inconsistent_file_without_header(self, caplog):
        args = {'file_loc': os.getcwd()+'/files/csv/without_header/SalesJan2009_without_header_invalid_file.csv',
                'config': os.getcwd()+'/files/configs/config_without_header.json'}

        parsed_config = TestsFunctional.open_config_file(args['config'])

        caplog.set_level(logging.ERROR)
        result = validation_runner(args['file_loc'], parsed_config)

        assert 'SalesJan2009_without_header_invalid_file.csv cannot be validated, column count is not consistent, row' in caplog.text
        assert result == 1
