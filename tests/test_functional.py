import os
import json
import logging
from csv_file_validator.__main__ import validation_runner


def test_success_file_with_header():
    args = {'file_loc': os.getcwd()+'/files/csv/with_header/SalesJan2009_with_header_fixed.csv',
            'config': os.getcwd()+'/files/configs/config_with_header.json'}

    with open(args['config'], mode='r') as json_file:
        parsed_config = json.load(json_file)

    res = validation_runner(args['file_loc'], parsed_config)

    assert res == 0


def test_fail_file_with_header(caplog):
    args = {'file_loc': os.getcwd()+'/files/csv/with_header/SalesJan2009_with_header_invalid_file.csv',
            'config': os.getcwd()+'/files/configs/config_with_header.json'}

    with open(args['config'], mode='r') as json_file:
        parsed_config = json.load(json_file)

    caplog.set_level(logging.ERROR)
    validation_runner(args['file_loc'], parsed_config)

    assert 'check_column_allow_numeric_value_range - failed to meet this value' in caplog.text


def test_success_file_without_header():
    args = {'file_loc': os.getcwd()+'/files/csv/without_header/SalesJan2009_without_header_fixed.csv',
            'config': os.getcwd()+'/files/configs/config_without_header.json'}

    with open(args['config'], mode='r') as json_file:
        parsed_config = json.load(json_file)

    res = validation_runner(args['file_loc'], parsed_config)

    assert res == 0


def test_fail_inconsistent_file_without_header(caplog):
    args = {'file_loc': os.getcwd()+'/files/csv/without_header/SalesJan2009_without_header_invalid_file.csv',
            'config': os.getcwd()+'/files/configs/config_without_header.json'}

    with open(args['config'], mode='r') as json_file:
        parsed_config = json.load(json_file)

    caplog.set_level(logging.ERROR)
    validation_runner(args['file_loc'], parsed_config)

    assert 'SalesJan2009_without_header_invalid_file.csv cannot be validated, column count is not consistent, row' in caplog.text
