from csv_file_validator import validations

config = {
    'file_name_file_mask': 'test*',
    'file_extension': 'csv',
    'file_size_range': [0, 1],
    'file_row_count_range': [0, 50],
    'file_value_separator': ',',
    'file_has_header': True,
    'file_header_column_names': ['col1', 'col2', 'col3'],
    'column_validation_rules': {
        'col1': {
            'allow_numeric_value_range': [0, 100],
            'allow_data_type': 'str',
        },
        'col2': {
            'allow_fixed_value_list': ['yyy', 'www'],
            'allow_regex': '$#%@%^@',
        },
        'col3': {
            'allow_substring': 'xxzerw',
            'allow_fixed_value': 'xxx',
            'allow_data_type': 'str'
        }
    }
}


class Validate:
    @staticmethod
    def function_caller(attribute, **kwargs):
        attribute_func_map = {
            "file_name_file_mask": validations.check_filemask,
            "file_extension": validations.check_file_extension,
            # "file_size_range": validations.check_file_size_range,
            # "file_row_count_range": validations.check_file_row_count_range,
            # "file_value_separator": validations.check_file_value_separator,
            # "file_has_header": validations.check_file_has_header,
            # "file_header_column_names": validations.check_file_header_column_names,
            # "file_column_datatypes": validations.check_file_column_datatypes,
            # "column_allow_numeric_value_range": validations.check_column_allow_numeric_value_range,
            # "column_allow_fixed_value_list": validations.check_column_allow_fixed_value_list,
            # "column_allow_regex": validations.check_column_allow_regex,
            # "column_allow_substring": validations.check_column_allow_substring,
            # "column_allow_fixed_value": validations.check_column_allow_fixed_value,
        }

        for func_name, func in attribute_func_map.items():
            if func_name == attribute:
                return func(**kwargs)
        else:
            return None

    @staticmethod
    def file_read_generator(file):
        for row in open(file, encoding="utf8", mode='r'):
            yield row

    def __init__(self, config):
        self.config = config

    def _validate_config_file(self):
        pass

    def _get_file_level_validations(self):
        return {k: v for k, v in self.config.items() if k.startswith('file')}

    def _get_column_level_validations(self):
        return {k: v for k, v in self.config.get('column_validation_rules').items()}

    def _get_all_validations(self):
        return {**self._get_file_level_validations(), **self._get_column_level_validations()}

    def _get_validation(self, validation_rule):
        return {k: v for k, v in self._get_all_validations().items() if k == validation_rule}

    def validate_file(self, file):
        file_level_validations = self._get_file_level_validations()
        for validation, value in file_level_validations.items():
            self.function_caller(validation, **{'file': file, 'arg1': value})

    def validate_line(self, line):
        column_level_validations = self._get_column_level_validations()
        for validation, value in column_level_validations.items():
            self.function_caller(validation, **{'line': line, 'arg1': value})


files_list = ["SalesJan2009.csv"]

vobj = Validate(config)
for file in files_list:
    vobj.validate_file(file)
    for line in vobj.file_read_generator(file):
        vobj.validate_line(line)

# print(Validate._get_file_level_validations(vobj))
# print(Validate._get_column_level_validations(vobj))
# print(Validate._get_all_validations(vobj))
# print(Validate.function_caller('file_extension', **{'arg1': "csv"}))
# print(Validate.function_caller('file_mask', **{'arg1': "xqw"}))
