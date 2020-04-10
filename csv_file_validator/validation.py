import logging
import csv
from typing import Union
from csv_file_validator import validation_functions as validation_funcs
from csv_file_validator.exceptions import InvalidConfigException, InvalidLineColumnCountException

logger = logging.getLogger(__name__)


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
            return None

    def __init__(self, config):
        self.config = config

    def _validate_config_file(self) -> Union[Exception, bool]:
        """
        config file validation method
        :return:
        """
        if not self.config.get('file_metadata'):
            raise InvalidConfigException('config file missing metadata object')

        if not self.config.get('file_validation_rules') and \
                not self.config.get('column_validation_rules'):
            raise InvalidConfigException('config file missing file_validation_rules object and '
                                         'column_validation_rules object')
        return True

    def get_validated_config(self) -> dict:
        """
        method for returning a validated configuration
        :return:
        """
        self._validate_config_file()
        return self.config

    def _get_config_file_metadata_all_items(self) -> dict:
        """
        method for returning file_metadata configuration items
        :return:
        """
        return self.config.get('file_metadata').items()

    def _get_config_file_metadata_value(self, metadata_value) -> Union[str, list]:
        """
        method for returning file_metadata configuration item
        :param metadata_value:
        :return:
        """
        return [v for k, v in self._get_config_file_metadata_all_items() if k == metadata_value][0]

    def get_config_file_validation_rules_all_items(self) -> dict:
        """
        method for returning file validation rules configuration items
        :return:
        """
        return {k: v for k, v in self.config.get('file_validation_rules').items()}

    def get_config_column_validation_rules_all_items(self) -> dict:
        """
        method for returning column validation rules configuration items
        :param column:
        :return:
        """
        return {k: v for k, v in self.config.get('column_validation_rules').items()}

    def get_validated_config_column_validation_rules_items(self, columns) -> dict:
        """
        method for returning column validation rules configuration items
        that are verified to be in the column names of the validated file
        :param columns:
        :return:
        """
        return {k: v for k, v in self.get_config_column_validation_rules_all_items().items()
                if k in columns}


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

        if self._get_config_file_metadata_value('file_has_header'):
            self.file_header = self.file_handler.readline().rstrip(self.file_row_terminator)\
                .split(self.file_value_separator)

            self.first_data_row_control_length = len(self.file_handler.readline()
                                                     .split(self.file_value_separator))

            self.column_level_validations_from_file = self.file_header
        else:
            self.file_header = None

            self.first_data_row_control_length = len(self.file_handler.readline()
                                                     .split(self.file_value_separator))
            self.column_level_validations_from_file = \
                [x for x in range(0, self.first_data_row_control_length)]

        # adding +1 because we already read the first file row while setting
        # the self.first_data_row_control_length
        self.file_row_count = sum(1 for line in self.file_handler) + 1
        self._reset_file_handler()

        self.file_level_validations = self.get_config_file_validation_rules_all_items()
        self.column_level_validations = self.get_validated_config_column_validation_rules_items(
            columns=self.column_level_validations_from_file)

    def get_number_of_file_level_validations(self):
        """
        function returning the count of the file level validations
        :return:
        """
        return len(self.file_level_validations)

    def get_number_of_column_level_validations(self):
        """
        function returning the count of the column level validations
        :return:
        """
        return len(self.column_level_validations)

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

    def file_read_generator(self) -> dict:
        """
        file reading generator method
        :return:
        """
        reader = csv.reader(self.file_handler, delimiter=self.file_value_separator, quotechar=None)
        for row_index, row in enumerate(reader):
            if len(row) != self.first_data_row_control_length:
                raise InvalidLineColumnCountException(f'row #:{row_index} , row line: {row}')

            if self.file_header:
                # if file contains header, yield column names with values
                # {(column name 1, value),(column name 2),..}
                if [x for x in self.file_header] != row:
                    yield dict(zip(self.file_header, row))

            else:
                # if file is without header, yield column indexes with values
                # {(0, value), (1, value),..}
                yield dict(zip(self.column_level_validations_from_file, row))

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
            file_level_validations_fail_count += self.function_caller(validation,
                                                                      **{'file_name': self.file_name,
                                                                         'file_handler': self.file_handler,
                                                                         'file_header': self.file_header,
                                                                         'file_row_count': self.file_row_count,
                                                                         'validation_value': validation_value}
                                                                      )
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
                                         'but none of the related columns found the file')

        if len(self.column_level_validations) < len(self.get_config_column_validation_rules_all_items()):
            raise InvalidConfigException('Column validations set in the config, '
                                         'but not all related columns found the file')

        # looping through column names and column values in the line items
        for column_name, column_value in line.items():

            column_level_validations = self._get_column_level_validation_items(col=column_name)
            # looping through validations for each column
            for column, validations in column_level_validations.items():

                # looping through validation items
                for validation, validation_value in validations.items():

                    column_level_validations_fail_count += self.function_caller(validation,
                                                                                **{'column': column,
                                                                                   'validation_value': validation_value,
                                                                                   'column_value': column_value,
                                                                                   'row_number': idx}
                                                                                )

        return column_level_validations_fail_count
