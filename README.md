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
#### how to install & run:


#### how to add custom validation rule: