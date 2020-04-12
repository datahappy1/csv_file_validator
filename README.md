# csv_file_validator
### Python 3+ CSV file validation tool 

#### what this tool can do:
The purpose of this tool is to validate comma separated value files. This tool needs the user to provide a validation schema and a file path of the file to be validated, or a folder path to validate multiple files in one run against one provided validation schema.  

##### validation schema:
Validation schema is a json file. Let's have a closer look at a real life example file.
```json
{
   "file_metadata":{
      "file_value_separator":",",
      "file_value_quoting":"",
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
         "allow_data_type":"datetime"
      },
      "Country":{
         "allow_fixed_value_list":[
            "Norway",
            "USA"
         ],
         "allow_regex":"[a-zA-Z].+",
         "allow_substring":"sub",
         "allow_data_type":"str"
      },
      "Price":{
         "allow_numeric_value_range":[0, 100000],
         "allow_fixed_value":"1000",
         "allow_data_type":"int"
      }
   }
}
```
Mandatory objects in the validation schema json are:
- `file_metadata` with these 3 keys: 
```json
   "file_metadata":{
      "file_value_separator":",",
      "file_row_terminator":"\n",
      "file_has_header":true
   },
```
- and at least one defined rule for at least one of the validation types: `file_validation_rules` and `column_validation_rules`

Optional objects in the validation schema json are:
- optional key in the file_metadata object is for csv quote character:
  - for doublequotes example:
    ```json
    "file_value_quote_char": '"'
    ```


##### Validation schema for a file with a header:
If validating a file that has a header, we have to set the `file_has_header` key to `true` and define the column names in the `column validation rules`.

```json
{
   "file_metadata":{
      "file_value_separator":",",
      "file_value_quoting":"",
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
         "allow_data_type":"datetime"
      },
      "Country":{
         "allow_fixed_value_list":[
            "Norway",
            "www"
         ],
         "allow_regex":"[a-zA-Z].+",
         "allow_substring":"",
         "allow_data_type":"str"
      },
      "Price":{
         "allow_numeric_value_range":[0, 100000],
         "allow_fixed_value":"1000",
         "allow_data_type":"int"
      }
   }
}
```

##### Validation schema for a file without a header:
If validating a file that has no header, we have to set the `file_has_header` key to `false` and define the column indexes in the `column validation rules` so they're starting from 0 for the first column.
```json
{
   "file_metadata":{
      "file_value_separator":",",
      "file_value_quoting":"",
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
         "allow_data_type":"datetime"
      },
      "1":{
         "allow_fixed_value_list":[
            "Norway",
            "www"
         ],
         "allow_regex":"[a-zA-Z].+",
         "allow_substring":"",
         "allow_data_type":"str"
      },
      "2":{
         "allow_numeric_value_range":[0, 100000],
         "allow_fixed_value":"1000",
         "allow_data_type":"int"
      }
   }
}
```

#### how to install & run:
- ideally create and activate a `virtual environment` or `pipenv`
- install dependencies from `requirements.txt`
- Set PYTHONPATH , from Windows CMD for example set PYTHONPATH=%PYTHONPATH%;C:\csv_file_validator
- run using a command `python3 C:\csv_file_validator\csv_file_validator\__main__.py`

- for defining regex patterns in regex validation rules, check https://regex101.com/

#### how to add custom validation rule:
- prepare your function in `/csv_file_validator/validation_functions.py` module and decorate it with `logging_decorator` like 
```python
@logging_decorator 
def my_validation_function(kwargs):
    if kwargs.get('validation_value') == 'a': # your validation condition
        return 0
    else:
        return 1
```
- this function has to return 0 on successful validation, 1 on a failed validation
- add your function to the registered validation keys - functions mapping in `/csv_file_validator/validation.py` in the `function_caller` static method like:

        attribute_func_map = {
            "my_new_function": validation_funcs.my_new_function
        }
 
 - now you can use `my_new_function` in your config json file for validations
 
 