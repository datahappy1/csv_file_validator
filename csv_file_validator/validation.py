"""
validation module
"""
import csv
import os
from typing import Union
from collections.abc import Generator
from csv_file_validator import validation_functions as validation_funcs
from csv_file_validator.exceptions import InvalidConfigException, \
    InvalidLineColumnCountException


def get_validation_function(attribute, **kwargs):
    """
    mapping method between config rules and validation functions
    :param attribute:
    :param kwargs:
    :return:
    """
    attribute_func_map = {
        "file_name_file_mask": validation_funcs.check_file_mask,
        "file_extension": validation_funcs.check_file_extension,
        "file_size_range": validation_funcs.check_file_size_range,
        "file_row_count_range": validation_funcs.check_file_row_count_range,
        "file_header_column_names": validation_funcs.check_file_header_column_names,
        "allow_data_type": validation_funcs.check_column_allow_data_type,
        "allow_numeric_value_range": validation_funcs.check_column_allow_numeric_value_range,
        "allow_fixed_value_list": validation_funcs.check_column_allow_fixed_value_list,
        "allow_regex": validation_funcs.check_column_allow_regex,
        "allow_substring": validation_funcs.check_column_allow_substring,
        "allow_fixed_value": validation_funcs.check_column_allow_fixed_value,
    }

    for func_name, func in attribute_func_map.items():
        if func_name == attribute:
            return_value = func(**kwargs)
            break
    else:
        raise InvalidConfigException(f'function {attribute} not found in '
                                     f'function_caller attribute_func_map')
    return return_value


def open_file_handler(file_name):
    """
    function returning opened file handler
    :param file_name:
    :return:
    """
    return open(file_name, mode='r', encoding='utf8')


class SetupValidation:
    """
    Setup Validation class
    """

    def __init__(self, config):
        self.config = config

    def __str__(self):
        return str(self.config)

    def get_validated_config(self) -> Union[dict, InvalidConfigException]:
        """
        method for returning a validated configuration
        :return:
        """
        if not self.config.get('file_metadata'):
            raise InvalidConfigException('config file missing metadata object')

        if not self.config.get('file_metadata').get('file_value_separator') or \
                not self.config.get('file_metadata').get('file_row_terminator') or \
                not self.config.get('file_metadata').get('file_has_header') in [True, False]:
            raise InvalidConfigException('config file metadata object not containing '
                                         'all mandatory keys')

        if not self.config.get('file_validation_rules') and \
                not self.config.get('column_validation_rules'):
            raise InvalidConfigException('config file missing file_validation_rules object and '
                                         'column_validation_rules object')

        return self.config


class SetupFile(SetupValidation):
    """
    Setup File class
    """
    def __init__(self, config, file):
        super().__init__(config)
        self.file_name = file
        self.file_handler = open_file_handler(self.file_name)
        self.file_row_terminator = self._get_config_file_metadata_value('file_row_terminator')
        self.file_value_separator = self._get_config_file_metadata_value('file_value_separator')
        self.file_value_quote_char = self._get_config_file_metadata_value('file_value_quote_char')
        self.file_size = os.path.getsize(self.file_name) / 1024 / 1024
        self.file_header = self._get_file_header()

    @property
    def file_with_configured_header_has_empty_header(self) -> bool:
        """
        method checking if we can validate the file based on its content
        :return:
        """
        if self.file_header == ['']:
            return True
        return False

    @property
    def file_data_row_count(self) -> int:
        """
        file data row count property
        :return:
        """
        file_data_row_count = self._get_count_of_rows_from_gen()
        if self.file_header and self.file_header != ['']:
            # we subtract 1 from the file_row_count because of the header row
            file_data_row_count -= 1
        return file_data_row_count

    @property
    def file_has_no_data_rows(self) -> bool:
        """
        method checking if the file has any rows (besides header row if configured)
        :return:
        """
        if self.file_data_row_count == 0:
            return True
        return False

    def _get_config_file_metadata_all_items(self) -> dict:
        """
        method for returning file_metadata configuration items
        :return:
        """
        return self.config.get('file_metadata').items()

    def _get_config_file_metadata_value(self, metadata_value) -> Union[None, str, bool]:
        """
        method for returning file_metadata configuration item
        :param metadata_value:
        :return:
        """
        metadata_item = [v for k, v in self._get_config_file_metadata_all_items()
                         if k == metadata_value]

        return metadata_item[0] if metadata_item else None

    def _file_rowcount_generator(self) -> Generator:
        """
        file row counting generator method
        :return:
        """
        reader = csv.reader(self.file_handler,
                            delimiter=self.file_value_separator,
                            quotechar=self.file_value_quote_char)
        for _ in reader:
            yield

    def _get_count_of_rows_from_gen(self) -> int:
        """
        method to get count of rows from _file_rowcount_generator
        :return:
        """
        row_count = len(list(self._file_rowcount_generator()))

        self.reset_file_handler()

        return row_count

    def _get_file_header(self) -> list:
        """
        method to get file header row
        :return:
        """
        if self._get_config_file_metadata_value('file_has_header'):
            file_header = self.file_handler.readline().rstrip(self.file_row_terminator) \
                .split(self.file_value_separator)
        else:
            file_header = None

        self.reset_file_handler()

        return file_header

    def reset_file_handler(self) -> None:
        """
        method to reset the file handler using seek back to file beginning
        :return:
        """
        self.file_handler.seek(0)

    def close_file_handler(self) -> None:
        """
        method for closing the file handler after validations finished
        :return:
        """
        self.file_handler.close()


class ValidateFileLevel(SetupFile):
    """
    Validate file class
    """
    def __init__(self, config, file):
        super().__init__(config, file)
        self.file_level_validations = self.config.get('file_validation_rules')

    def get_file_level_validations_count(self) -> int:
        """
        function returning the count of the file level validations
        :return:
        """
        if self.file_level_validations:
            return len(self.file_level_validations)
        return 0

    def validate_file(self) -> int:
        """
        method for validating a file, for every file level validation, call
        the mapped validation function and process it
        :return:
        """
        file_level_validations_fail_count = 0

        for validation, validation_value in self.file_level_validations.items():
            file_level_validations_fail_count += \
                get_validation_function(validation, **{'file_name': self.file_name,
                                                       'file_handler': self.file_handler,
                                                       'file_header': self.file_header,
                                                       'file_row_count': self.file_data_row_count,
                                                       'file_size': self.file_size,
                                                       'validation_value': validation_value})

        return file_level_validations_fail_count


class ValidateColumnLevel(SetupFile):
    """
    Validate column level class
    """
    def __init__(self, config, file):
        super().__init__(config, file)
        self.first_row_control_length = self._get_first_row_column_count()
        self.column_level_validations = self._get_column_level_validations()

    def _get_first_row_column_count(self) -> int:
        """
        method to get the first data row item length for file
        column count integrity check in the file_read_generator method
        :return:
        """
        first_row = self.file_handler.readline().rstrip(self.file_row_terminator) \
            .split(self.file_value_separator)

        self.reset_file_handler()

        return len(first_row) if first_row != [''] else 0

    def _get_column_level_validations(self) -> dict:
        """
        method to get column level validation rules from the file content
        if the file has header, return header rows, if no header in the file,
        return each column index from the first data row in the file
        :return:
        """
        if self.file_header:
            _column_level_validations_from_file = self.file_header
        else:
            _column_level_validations_from_file = \
                [str(x) for x in range(0, self.first_row_control_length)]

        _column_validation_rule_names_from_config = \
            list(self.config['column_validation_rules'].keys())

        if not _column_level_validations_from_file:
            raise InvalidConfigException('Column validations set in the config, '
                                         'but none of the expected columns found in the file')

        if not all(item in _column_level_validations_from_file for item
                   in _column_validation_rule_names_from_config):
            raise InvalidConfigException('Column validations set in the config, '
                                         'but not all expected columns found in the file')

        return self.config['column_validation_rules']

    def get_column_level_validations_count(self) -> int:
        """
        function returning the count of the column level validations
        :return:
        """
        if self.column_level_validations:
            return len(self.column_level_validations)
        return 0

    def file_read_generator(self) -> Union[Exception, Generator]:
        """
        file reading generator method
        :return:
        """
        _int_row_counter = 0
        reader = csv.reader(self.file_handler,
                            delimiter=self.file_value_separator,
                            quotechar=self.file_value_quote_char)
        for row in reader:
            _int_row_counter += 1
            if len(row) != self.first_row_control_length:
                raise InvalidLineColumnCountException(f'row #: {_int_row_counter}, '
                                                      f'expected column count: '
                                                      f'{self.first_row_control_length}, '
                                                      f'actual column count: '
                                                      f'{len(row)}')

            if self.file_header and _int_row_counter > 1:
                # if file contains header, yield row number and column names with values
                # row number,{(column name 1, value), (column name 2),..}
                yield _int_row_counter, dict(zip(self.file_header, row))
            elif not self.file_header:
                # if file is without header, yield row number column indexes with values
                # row number,{(0, value), (1, value),..}
                yield _int_row_counter, dict(zip(self.column_level_validations, row))
            else:
                # file header row so continue, header should be checked separately in
                # file_validation_rules.file_header_column_names
                continue

    def validate_line_values(self, line, idx) -> int:
        """
        method for validating a line in a file, for every column level validation, call
        the mapped validation function and process it
        :param line:
        :param idx:
        :return:
        """
        column_level_validations_fail_count = 0

        # looping through column names and column values in the line items
        for column_name, column_value in line.items():

            if column_name in self.column_level_validations:

                # looping through validation items
                for validation, validation_value in \
                        self.column_level_validations[column_name].items():
                    column_level_validations_fail_count += \
                        get_validation_function(validation, **{'column': column_name,
                                                               'validation_value': validation_value,
                                                               'column_value': column_value,
                                                               'row_number': idx})

        return column_level_validations_fail_count
