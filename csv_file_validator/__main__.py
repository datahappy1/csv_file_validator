import platform
import os, re
from types import SimpleNamespace, FunctionType
from csv_file_validator import validations

pf = platform.system()

if pf == 'linux':
    import modin.pandas as pd
else:
    import pandas as pd

# basicdtypes  float, int, bool, timedelta64[ns] and datetime64[ns], string
# https://pandas.pydata.org/pandas-docs/stable/getting_started/basics.html#basics-dtypes

type_to_pd_dtype = {
    "string": "object",
    "integer": "int64",
    "float": "float64",
    "bool": "bool",
    "datetime": "datetime64",
}

# config
config = {
    'high_severity_validations': {
        'file_name_filemask': 'test*',
        'file_extension': 'csv',
        'file_size_range': [0, 1],
        'file_row_count_range': [0, 50],
    },
    'low_severity_validations': {
        'file_value_separator': ',',
        'file_has_header': True,
        'file_header_column_names': ['col1', 'col2', 'col3'],
        'column_datatypes': {
            'col1': 'str',
            'col2': 'str',
            'col3': 'str'
        },
        'column_validation_rules': {
            'col1': {
                'allow_numeric_value_range': [0, 100]
            },
            'col2': {
                'allow_fixed_value_list': ['yyy', 'www'],
                'allow_regex': '$#%@%^@',
            },
            'col3': {
                'allow_substring': 'xxzerw',
                'allow_fixed_value': 'xxx'
            }
        }
    }
}


class Validate:
    def __init__(self, config):
        self.config = config


    def _function_caller(self, attribute, **kwargs):
        attribute_func_map = {
            "file_extension": validations.check_file_extension,
            "file_mask": validations.check_filemask,
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

    def _get_config(self):
        if isinstance(self.config, dict):
            return SimpleNamespace(**self.config)
        else:
            raise Exception

    def _get_high_severity_validations(self):
        return {k: v for k, v in self.config.get('high_severity_validations').items()}

    def _get_low_severity_validations(self):
        return {k: v for k, v in self.config.get('low_severity_validations').items()}

    def _get_all_severity_validations(self):
        return {**self._get_high_severity_validations(), **self._get_low_severity_validations()}

    def _get_validation(self, validation_rule):
        return {k: v for k, v in self._get_all_severity_validations().items() if k == validation_rule}

    def _file_read_generator(self, file):
        for row in open(file, encoding="utf8", mode='r'):
            yield row

files_list = ["test1.csv"]

vobj = Validate(config)
for f in files_list:
    for l in vobj._file_read_generator(f):
        print(l)

#Validate.read_file(vobj)
# print(Validate._get_high_severity_validations(vobj))
# print(Validate._get_low_severity_validations(vobj))
# print(Validate._get_all_severity_validations(vobj))
#print(Validate._get_validation(vobj, validation_rule="file_has_header"))
print(Validate._function_caller(vobj, 'file_extension', **{'arg1': "csv"}))
print(Validate._function_caller(vobj, 'file_mask', **{'arg1': "xqw"}))
