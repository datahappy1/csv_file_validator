import logging
from typing import Union
from csv_file_validator import validation_functions as validation_funcs

logger = logging.getLogger(__name__)


class InvalidLineColumnCountException(Exception):
    """
    Invalid Line Column Count Exception custom exception type
    """

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
        if not isinstance(self.config, dict):
            raise Exception('config file not dict')

        if not self.config.get('file_metadata'):
            raise Exception('config file missing metadata object')

        if not self.config.get('file_validation_rules') and \
                not self.config.get('column_validation_rules'):
            raise Exception('config file missing file_validation_rules object and '
                            'column_validation_rules object')
        return True

    def get_validated_config(self) -> dict:
        """
        method for returning a validated configuration
        :return:
        """
        self._validate_config_file()
        return self.config

    def _get_config_file_metadata_items(self) -> dict:
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
        return [v for k, v in self._get_config_file_metadata_items() if k == metadata_value][0]

    def get_config_file_validation_rules_items(self) -> dict:
        """
        method for returning file validation rules configuration items
        :return:
        """
        return {k: v for k, v in self.config.get('file_validation_rules').items()}

    def get_config_column_validation_rules_items(self, column) -> dict:
        """
        method for returning column validation rules configuration items
        :param column:
        :return:
        """
        return {k: v for k, v in self.config.get('column_validation_rules').items() if k == column}


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

        self.file_header = None
        if self._get_config_file_metadata_value('file_has_header'):
            self.file_header = self.file_handler.readline().rstrip(self.file_row_terminator). \
                split(self.file_value_separator)

        self.file_row_count = sum(1 for line in self.file_handler)
        # seek the file back to the file beginning after counting the lines in the opened file handler
        self.file_handler.seek(0)

        self.first_row_control_length = len(self.file_handler.readline().split(self.file_value_separator))
        # seek the file back to the file beginning after counting the lines in the opened file handler
        self.file_handler.seek(0)

    def file_read_generator(self) -> dict:
        """
        file reading generator method
        :return:
        """
        for _row_index, _row in enumerate(self.file_handler):

            if len(_row.split(self.file_value_separator)) != self.first_row_control_length:
                raise InvalidLineColumnCountException(f'row #:{_row_index} , row line: {_row}')

            row = _row.rstrip(self.file_row_terminator)
            if self.file_header:
                # if file contains header, yield {(column name 1, value),(column name 2),..}
                if self.file_value_separator.join(self.file_header) != row:
                    yield dict(zip(self.file_header, row.split(self.file_value_separator)))

            else:
                # if file is without header, yield {(column index, value), (column index2, value),..}
                yield dict(zip([x for x in range(0, len(row.split(self.file_value_separator)))],
                               row.split(self.file_value_separator)))

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
        file_level_validations = self.get_config_file_validation_rules_items()
        file_level_validations_count = len(file_level_validations)
        for validation, validation_value in file_level_validations.items():
            file_level_validations_fail_count += self.function_caller(validation,
                                                                      **{'file_name': self.file_name,
                                                                         'file_handler': self.file_handler,
                                                                         'file_header': self.file_header,
                                                                         'file_row_count': self.file_row_count,
                                                                         'validation_value': validation_value}
                                                                      )
        return file_level_validations_count, file_level_validations_fail_count

    def validate_line(self, line, idx):
        """
        method for validating a line in a file, for every column level validation, call
        the mapped validation function and process it
        :param line:
        :param idx:
        :return:
        """
        column_level_validations_count = 0
        column_level_validations_fail_count = 0
        for k, v in line.items():
            column_level_validations = self.get_config_column_validation_rules_items(column=k)
            for column, validations in column_level_validations.items():
                column_level_validations_count += 1
                for validation, value in validations.items():
                    column_level_validations_fail_count += self.function_caller(validation,
                                                                                **{'column': column,
                                                                                   'validation_value': value,
                                                                                   'column_value': v,
                                                                                   'row_number': idx}
                                                                                )
        return column_level_validations_count, column_level_validations_fail_count
