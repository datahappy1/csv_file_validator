import logging
import csv
import datetime
from csv_file_validator import validations

# logger = logging.Logger(name=__name__)

config = {
    'file_metadata': {
        'file_value_separator': ',',
        'file_has_header': True,
    },
    'file_validation_rules': {
        'file_name_file_mask': 'SalesJ',
        'file_extension': 'csv',
        'file_size_range': [0, 1],
        'file_row_count_range': [0, 1000],
        'file_header_column_names': ['Transaction_date', 'Product', 'Price', 'Payment_Type', 'Name', 'City', 'State', 'Country', 'Account_Created', 'Last_Login', 'Latitude', 'Longitude']
    },
    'column_validation_rules': {
        'Transaction_date': {
            'allow_data_type': 'datetime',
        },
        'Country': {
            'allow_fixed_value_list': ['yyy', 'www'],
            'allow_regex': '$#%@%^@',
            'allow_data_type': 'str'
        },
        'Price': {
            'allow_numeric_value_range': [0, 100000],
            'allow_substring': 'xxzerw',
            'allow_fixed_value': 'xxx',
            'allow_data_type': 'int'
        }
    }
}


class Validate:
    @staticmethod
    def function_caller(attribute, **kwargs):
        attribute_func_map = {
            "file_name_file_mask": validations.check_filemask,
            "file_extension": validations.check_file_extension,
            "file_size_range": validations.check_file_size_range,
            "file_row_count_range": validations.check_file_row_count_range,
            "file_header_column_names": validations.check_file_header_column_names,
            "allow_data_type": validations.check_column_allow_data_type,
            "allow_numeric_value_range": validations.check_column_allow_numeric_value_range,
            "allow_fixed_value_list": validations.check_column_allow_fixed_value_list,
            "allow_regex": validations.check_column_allow_regex,
            "allow_substring": validations.check_column_allow_substring,
            "allow_fixed_value": validations.check_column_allow_fixed_value,
        }

        for func_name, func in attribute_func_map.items():
            if func_name == attribute:
                return func(**kwargs)
        else:
            return None

    def _get_file_header(self):
        self.file_header = open(file, mode='r', encoding='utf8').readline().split(self._get_file_metadata_value('file_value_separator'))

    def file_read_generator(self, file):
        self._get_file_header()
        for row in open(file, mode='r', encoding='utf8'):
            if ','.join(self.file_header) != row:
                yield dict(zip(self.file_header, row.split(self._get_file_metadata_value('file_value_separator'))))

    def __init__(self, config):
        self.config = config

    # TODO
    def _validate_config_file(self):
        if not isinstance(self.config, dict):
            raise Exception

    def _get_file_level_validations(self):
        return {k: v for k, v in self.config.get('file_validation_rules').items()}

    def _get_column_level_validations(self, column):
        return {k: v for k, v in self.config.get('column_validation_rules').items() if k==column}

    def _get_file_metadata_value(self, metavalue):
        return [v for k, v in self.config.get('file_metadata').items() if k == metavalue][0]

    def validate_file(self, file):
        file_level_validations = self._get_file_level_validations()
        for validation, value in file_level_validations.items():
            self.function_caller(validation, **{'file': file, 'arg1': value})

    def validate_line(self, line):
        for k, v in line.items():
            column_level_validations = self._get_column_level_validations(column=k)
            for column, validations in column_level_validations.items():
                for validation, value in validations.items():
                    self.function_caller(validation, **{'column': column, 'arg1': value, 'arg2': v})


files_list = ["SalesJan2009.csv"]

vobj = Validate(config)
for file in files_list:
    vobj.validate_file(file)
    for line in vobj.file_read_generator(file):
        vobj.validate_line(line)
