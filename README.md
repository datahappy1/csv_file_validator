# csv_file_validator
## Python CSV file validation tool 

This tool is written with type hints introduced in Python 3.5

- [What this tool can do](#what-this-tool-can-do)
- [Validation schema](#validation-schema)
  - [Validation schema for a file with a header](#validation-schema-for-a-file-with-a-header)
  - [Validation schema for a file without a header](#validation-schema-for-a-file-without-a-header)
- [Validation rules](#validation-rules)
- [How to install & run](#how-to-install--run)
  - [Arguments needed](#arguments-needed)
- [How to add a custom column validation rule](#how-to-add-a-custom-column-validation-rule)

### What this tool can do:
The purpose of this tool is to validate comma separated value files. This tool needs the user to provide a validation schema as a json file and a file path of the file to be validated, or a folder path to validate multiple files in one run against the provided validation schema.  

### Validation schema:
Validation schema is a json file. Let's have a closer look at a real life example file.
```json
{
   "file_metadata":{
      "file_value_separator":",",
      "file_value_quote_char": "\"",
      "file_row_terminator":"\n",
      "file_has_header":true
   },
   "file_validation_rules":{
      "file_name_file_mask":"SalesJ",
      "file_extension":"csv",
      "file_size_range":[0,1],
      "file_row_count_range":[0,1000],
      "file_header_column_names":[
         "Transaction_date",
         "Product",
         "Price",
         "Payment_Type",
         "Name",
         "City",
         "State",
         "Country",
         "Account_Created",
         "Last_Login",
         "Latitude",
         "Longitude"
      ]
   },
   "column_validation_rules":{
      "Transaction_date":{
         "allow_data_type": "datetime.%M/%d/%y %H:%S"
      },
      "Country":{
         "allow_fixed_value_list":[
            "Norway",
            "United States"
         ],
         "allow_regex":"[a-zA-Z].+",
         "allow_substring":"sub",
         "allow_data_type":"str"
      },
      "Price":{
         "allow_int_value_range":[0, 100000],
         "allow_fixed_value":1000,
         "allow_data_type":"int"
      },
      "Latitude":{
        "allow_float_value_range": [-42.5, 90.5]
      }
   }
}
```
**Mandatory** objects in the validation schema json are:
- `file_metadata` object containing these 4 keys: 
```json
   "file_metadata":{
      "file_value_separator":",",
      "file_value_quote_char": "\"",
      "file_row_terminator":"\n",
      "file_has_header":true
   },
```
- at least one defined rule

#### Validation schema for a file with a header:
If validating a file that has a header, we have to set the `file_has_header` key to `true` and define the column names in the `column validation rules`.

```json
{
   "file_metadata":{
      "file_value_separator":",",
      "file_value_quote_char": "\"",
      "file_row_terminator":"\n",
      "file_has_header":true
   },
   "file_validation_rules":{
      "file_name_file_mask":"SalesJ",
      "file_extension":"csv",
      "file_size_range":[0,1],
      "file_row_count_range":[0,1000],
      "file_header_column_names":[
         "Transaction_date",
         "Product",
         "Price",
         "Payment_Type",
         "Name",
         "City",
         "State",
         "Country",
         "Account_Created",
         "Last_Login",
         "Latitude",
         "Longitude"
      ]
   },
   "column_validation_rules":{
      "Transaction_date":{
         "allow_data_type": "datetime.%M/%d/%y %H:%S"
      },
      "Country":{
         "allow_fixed_value_list":[
            "Norway",
            "United States"
         ],
         "allow_regex":"[a-zA-Z].+",
         "allow_substring":"Norwayz",
         "allow_data_type":"str",
         "allow_fixed_value":"value"
      },
      "Price":{
         "allow_int_value_range":[0, 100000],
         "allow_fixed_value":1000,
         "allow_data_type":"int"
      },
      "Latitude":{
        "allow_float_value_range": [-42.5, 90.5]
      }
   }
}
```

#### Validation schema for a file without a header:
If validating a file that has no header, we have to set the `file_has_header` key to `false` and define the column indexes in the `column validation rules` so they're starting from 0 for the first column.
```json
{
   "file_metadata":{
      "file_value_separator":",",
      "file_value_quote_char": "\"",
      "file_row_terminator":"\n",
      "file_has_header":false
   },
   "file_validation_rules":{
      "file_name_file_mask":"SalesJ",
      "file_extension":"csv",
      "file_size_range":[0,1],
      "file_row_count_range":[0,1000]
   },
   "column_validation_rules":{
      "0":{
         "allow_data_type": "datetime.%M/%d/%y %H:%S"
      },
      "1":{
         "allow_fixed_value_list":[
            "Norway",
            "United States"
         ],
         "allow_regex":"[a-zA-Z].+",
         "allow_substring":"xzy",
         "allow_data_type":"str"
      },
      "2":{
         "allow_int_value_range":[0, 100000],
         "allow_fixed_value":1000,
         "allow_data_type":"int"
      },
      "10":{
        "allow_float_value_range": [-42.5, 90.5]
      }
   }
}
```
### Validation rules:
- File level validation rules:
    - file_name_file_mask : checks file name matches the file mask regex pattern
    - file_extension : checks file extension is an exact match with the provided value
    - file_size_range : checks file size in MB is in the range of the provided values
    - file_row_count_range : checks file row count is in the range of the provided values
    - file_header_column_names : checks file header is an exact match with the provided value
- Column level validation rules:
    - allow_data_type : checks column values are of the allowed data type ( allowed options: `str` , `int` , `float`, `datetime`, `datetime.<<format>>`)
    - allow_int_value_range : checks integer column values are in the range of the provided values
    - allow_float_value_range : checks float column values are in the range of the provided values
    - allow_fixed_value_list : checks column values are in the provided value list
    - allow_regex : checks column values match the provided regex pattern
    - allow_substring : checks column values are a substring of the provided value 
    - allow_fixed_value : checks column values are an exact match with the provided value


### How to install & run:
- ideally create and activate a `virtual environment` or `pipenv` in order to safely install dependencies from `requirements.txt` using `pip install -r requirements.txt`
- Set PYTHONPATH , from Windows CMD for example `set PYTHONPATH=%PYTHONPATH%;C:\csv_file_validator`
- run using a command for example: `python C:\csv_file_validator\csv_file_validator -fl C:\csv_file_validator\tests\files\csv\with_header\SalesJan2009_with_header_correct_file.csv -cfg C:\csv_file_validator\tests\files\configs\config_with_header.json`

- in `settings.conf` file 
    - you can set the variable `RAISE_EXCEPTION_AND_HALT_ON_FAILED_VALIDATION` to `True` or `False`, this variable drives the behavior whether the tool stops validations after it hits a failed validation or not
    - you can set the variable `SKIP_COLUMN_VALIDATIONS_ON_EMPTY_FILE` to `True` or `False`, this variable drives the behavior whether the tool bypass the column level validations on a file that has no rows or not

#### arguments needed:
- `-fl` <string: mandatory> single file absolute path or absolute folder location (in case you need to validate multiple files from a directory in one app run)
- `-cfg` <string: mandatory> configuration json file location absolute path

### How to add a custom column validation rule:
Column validation rule interface: ![](/docs/img/my_new_validation_function_interface_diagram.png)
>The keyword argument `validation_value` is the value in the config.json file, describing the allowed values for the validation rule

>The keyword argument `column_value` is the value in the corresponding column in the .csv file being validated

- Create a function in `/csv_file_validator/validation_functions.py` module and decorate it with `@logging_decorator` like this:

    ```python
    @logging_decorator 
    def my_new_validation_function(kwargs):
        # example condition that validates the exact match of a validation_value and a column_value:
        if kwargs.get('validation_value') == kwargs.get('column_value'): 
            # your validation condition success returns 0
            return 0
        # your validation condition fail returns 1     
        return 1
    ```
- Add your function name to the registered validation name key - function mapping dictionary `_ATTRIBUTE_FUNC_MAP`. 
This dictionary is located at the end of the file `/csv_file_validator/validation_functions.py`.

    ```python
    "my_new_validation_function": my_new_validation_function
    ```
- For a column you wish to evaluate using this new validation rule, setup a validation function to validation value mapping in `config.json`

    ```json
    "my_column_name": {
        "my_new_validation_function": "some_validation_value"
    }
    ```
- If you need to define regex patterns in regex validation rules, check https://regex101.com/
