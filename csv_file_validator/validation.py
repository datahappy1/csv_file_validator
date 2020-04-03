from csv_file_validator import validation_functions as validation_funcs


class Validate:
    @staticmethod
    def function_caller(attribute, **kwargs):
        attribute_func_map = {
            "file_name_file_mask": validation_funcs.check_filemask,
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

    #TODO
    def _validate_config_file(self):
        if not isinstance(self.config, dict):
            raise Exception

    def _get_file_level_validations(self):
        print(type(self.config))
        print(self.config)
        return {k: v for k, v in self.config.get('file_validation_rules').items()}

    def _get_column_level_validations(self, column):
        return {k: v for k, v in self.config.get('column_validation_rules').items() if k==column}

#https://pybit.es/python-subclasses.html
class ValidateFile(Validate):
    def __init__(self, file):
        super().__init__(file)
        self.file = file

    def _get_file_header(self):
        self.file_header = open(self.file, mode='r', encoding='utf8').readline().split(self._get_file_metadata_value('file_value_separator'))

    def file_read_generator(self):
        self._get_file_header()
        for row in open(self.file, mode='r', encoding='utf8'):
            if ','.join(self.file_header) != row:
                yield dict(zip(self.file_header, row.split(self._get_file_metadata_value('file_value_separator'))))

    def _get_file_metadata_value(self, metavalue):
        return [v for k, v in self.config.get('file_metadata').items() if k == metavalue][0]

    def validate_file(self):
        file_level_validations = self._get_file_level_validations()
        for validation, value in file_level_validations.items():
            self.function_caller(validation, **{'file': self.file, 'arg1': value})


# class ValidateLine(Validate):
#     def __init__(self, line, config):
#         super().__init__(config)
#         self.line = line
#
#     def validate_line(self):
#         for k, v in self.line.items():
#             column_level_validations = self._get_column_level_validations(column=k)
#             for column, validations in column_level_validations.items():
#                 for validation, value in validations.items():
#                     self.function_caller(validation, **{'column': column, 'arg1': value, 'arg2': v})
