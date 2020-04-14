"""
validation module
"""
import logging
import csv
import os
from typing import Union
from csv_file_validator import validation_functions as validation_funcs
from csv_file_validator.exceptions import InvalidConfigException, InvalidLineColumnCountException

LOGGER = logging.getLogger(__name__)


class SetupValidation:
    """
    Setup Validation class
    """

    @staticmethod
    def function_caller(attribute, **kwargs) -> [classmethod, None]:
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
                return func(**kwargs)
        else:
            raise InvalidConfigException(f'function {attribute} not found in '
                                         f'function_caller attribute_func_map')

    def __init__(self, config):
        self.config = config

    def _validate_config_file(self) -> Union[Exception, bool]:
        """
        config file validation method
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

        return True

    def get_validated_config(self) -> Union[dict, None]:
        """
        method for returning a validated configuration
        :return:
        """
        if self._validate_config_file():
            return self.config
        return None

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

        if metadata_item:
            return metadata_item[0]
        return None

    def get_config_file_validation_rules_all_items(self) -> Union[dict, None]:
        """
        method for returning file validation rules configuration items
        :return:
        """
        try:
            return self.config.get('file_validation_rules')
        except AttributeError:
            return None

    def get_config_column_validation_rules_all_items(self) -> Union[dict, None]:
        """
        method for returning column validation rules configuration items
        :param column:
        :return:
        """
        try:
            return self.config.get('column_validation_rules')
        except AttributeError:
            return None

    def get_validated_config_column_validation_rules_items(self, columns) -> Union[dict, None]:
        """
        method for returning column validation rules configuration items
        that are verified to be in the column names of the validated file
        :param columns:
        :return:
        """
        try:
            return {k: v for k, v in self.get_config_column_validation_rules_all_items().items()
                    if k in columns}
        except AttributeError:
            return None


class ValidateFile(SetupValidation):
    """
    Validate file class
    """

    def __init__(self, config, file):
        super().__init__(config)
        self.file_name = file
        self.file_handler = open(file, mode='r', encoding='utf8')
        self.file_row_terminator = self._get_config_file_metadata_value('file_row_terminator')
        self.file_value_separator = self._get_config_file_metadata_value('file_value_separator')
        self.file_value_quote_char = self._get_config_file_metadata_value('file_value_quote_char')
        self.file_size = os.path.getsize(self.file_name) / 1024 / 1024
        self.file_row_count = sum(1 for line in self.file_handler)
        self._reset_file_handler()

        if self._get_config_file_metadata_value('file_has_header'):
            self.file_header = self.file_handler.readline().rstrip(self.file_row_terminator) \
                .split(self.file_value_separator)
            if self.file_header != ['']:
                # we subtract 1 from the file_row_count because of the header row
                self.file_row_count -= 1

            _first_row = self.file_handler.readline().rstrip(self.file_row_terminator) \
                .split(self.file_value_separator)
            if _first_row != ['']:
                self.first_data_row_control_length = len(_first_row)
            else:
                self.first_data_row_control_length = 0

            self.column_level_validations_from_file = self.file_header

        else:
            self.file_header = None

            _first_row = self.file_handler.readline().rstrip(self.file_row_terminator) \
                .split(self.file_value_separator)
            if _first_row != ['']:
                self.first_data_row_control_length = len(_first_row)
            else:
                self.first_data_row_control_length = 0

            self.column_level_validations_from_file = \
                [str(x) for x in range(0, self.first_data_row_control_length)]

        self._reset_file_handler()

        self.file_level_validations = self.get_config_file_validation_rules_all_items()
        self.column_level_validations = self.get_validated_config_column_validation_rules_items(
            columns=self.column_level_validations_from_file)

    def get_number_of_file_level_validations(self):
        """
        function returning the count of the file level validations
        :return:
        """
        if self.file_level_validations:
            return len(self.file_level_validations)
        return 0

    def get_number_of_column_level_validations(self):
        """
        function returning the count of the column level validations
        :return:
        """
        if self.column_level_validations:
            return len(self.column_level_validations)
        return 0

    def _get_column_level_validation_items(self, col):
        """
        function returning for each column the validations found
        :param col:
        :return:
        """
        return {k: v for k, v in self.column_level_validations.items() if k == str(col)}

    def _reset_file_handler(self):
        """
        method to reset the file handler using seek back to file beginning
        :return:
        """
        self.file_handler.seek(0)

    def file_has_empty_header(self) -> bool:
        """
        method checking if we can validate the file based on its content
        :return:
        """
        if self.file_header == ['']:
            return True
        return False

    def file_has_no_rows(self) -> bool:
        """
        method checking if the file has any rows (besides header row if configured)
        :return:
        """
        if self.file_row_count == 0:
            return True
        return False

    def file_read_generator(self) -> dict:
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
            if len(row) != self.first_data_row_control_length:

                raise InvalidLineColumnCountException(f'row #: {_int_row_counter}, '
                                                      f'expected column count: '
                                                      f'{self.first_data_row_control_length}, '
                                                      f'actual column count: '
                                                      f'{len(row)}')

            if self.file_header:
                # if file contains header, yield row number and column names with values
                # row number,{(column name 1, value), (column name 2),..}
                # or if the file header already passed through the generator,
                # yield such row value to the validations to capture erroneous
                # files having multiple headers as these header values
                # should not pass the validations
                if self.file_header != row or _int_row_counter > 1:
                    yield _int_row_counter, dict(zip(self.file_header, row))
                else:
                    pass

            else:
                # if file is without header, yield row number column indexes with values
                # row number,{(0, value), (1, value),..}
                yield _int_row_counter, dict(zip(self.column_level_validations_from_file, row))

    def close_file_handler(self):
        """
        method for closing the file handler after validations finished
        :return:
        """
        self.file_handler.close()

    def validate_file(self):
        """
        method for validating a file, for every file level validation, call
        the mapped validation function and process it
        :return:
        """
        file_level_validations_fail_count = 0

        for validation, validation_value in self.file_level_validations.items():

            file_level_validations_fail_count += \
                self.function_caller(validation, **{'file_name': self.file_name,
                                                    'file_handler': self.file_handler,
                                                    'file_header': self.file_header,
                                                    'file_row_count': self.file_row_count,
                                                    'file_size': self.file_size,
                                                    'validation_value': validation_value})

        return file_level_validations_fail_count

    def validate_line_values(self, line, idx):
        """
        method for validating a line in a file, for every column level validation, call
        the mapped validation function and process it
        :param line:
        :param idx:
        :return:
        """
        column_level_validations_fail_count = 0

        if not self.column_level_validations:
            raise InvalidConfigException('Column validations set in the config, '
                                         'but none of the related columns found in the file')

        if len(self.column_level_validations) < \
                len(self.get_config_column_validation_rules_all_items()):
            raise InvalidConfigException('Column validations set in the config, '
                                         'but not all related columns found in the file')

        # looping through column names and column values in the line items
        for column_name, column_value in line.items():

            column_level_validations = self._get_column_level_validation_items(col=column_name)
            # looping through validations for each column
            for column, validations in column_level_validations.items():

                # looping through validation items
                for validation, validation_value in validations.items():

                    column_level_validations_fail_count += \
                        self.function_caller(validation, **{'column': column,
                                                            'validation_value': validation_value,
                                                            'column_value': column_value,
                                                            'row_number': idx})

        return column_level_validations_fail_count
