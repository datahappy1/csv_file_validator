# csv_file_validator
### Python 3+ CSV file validation tool 

#### what this tool can do:
The purpose of this tool is to validate comma separated value files. This tool needs the user to provide a validation schema and a file path of the file to be validated, or a folder path to validate multiple files in one run against one provided validation schema.  

##### validation schema:
Validation schema is a json file. Let's have a closer look at a example file.
```json
{
   "file_metadata":{
      "file_value_separator":",",
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
         "allow_regex":"$#%@%^@",
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
Mandatory objects in the validation schema json are:
- `file_metadata` with these 3 keys: 
```json
   "file_metadata":{
      "file_value_separator":",",
      "file_row_terminator":"\n",
      "file_has_header":true
   },
```
- atleast one of the validation types: `file_validation_rules` and `column_validation_rules`

##### Validation schema for a file with a header:


##### Validation schema for a file without a header:

#### how to install & run:
- ideally create and activate a `virtual environment` or `pipenv`
- install dependencies from `requirements.txt`
- run using a command `python3 -xxxx`

#### how to add custom validation rule:
- prepare your function in `/csv_file_validator/validation_functions.py` module
- this function has to return 0 on successful validation, 1 on a failed validation
- add your function to the registered validation keys - functions mapping in `/csv_file_validator/validation.py` in the `function_caller` static method like:

        attribute_func_map = {
            "my_new_function": validation_funcs.my_new_function
        }
 
 - now you can use `my_new_function` in your config json file for validations
 
 