# PortMatrixHelper
 PortMatrixHelper is a simple configuration Generator. It parses a typical Port Matrix data into Configuration Templates for each Interface. The Configuration Templates can be modified an expanded on as needed.

 It also Logs in to the devices and check the CDP and LLDP neighbors to check your connections, and ensure they are connected as defined.

# Getting Started
## Software Prerequisites
* Microsoft Excel XLSX Editor
* Python Module - openpyxl
A .EXE file can be provided to simplify the need of library requirements.

## Work Book Setup
PortMatrixHelper utilizes a Port Matrix Excel Work Book, within this Spreadsheet a few requirements need to be Met so that the script runs without issue.
Below is a list of requirements for the Work Book and Setup information.
* Port Matrix Work Book must have a "Settings" Sheet, Please utilize the provided Sample Spreadsheet and build from that, or copy the "Settings" sheet to your new WorkBook
### Network Device Sheets
* The First 8 Rows are reserved, within these 8 rows Columns 'A-D' are reserved for the script.
  * The necessary credentials can be added within these row (in Green) to allow the script to login to the devices.
  * Any Column after F within these first 8 rows can be utilized for any necessary notes.
* When you start your Table, the Headers must be defined in ROW 9.
  * The Script utilizes Columns 'A-F' (in Orange), the title of these Columns should not be renamed.
  * Columns can be added or deleted starting Column G, any title can be given to these Columns
  * Ensure the column names are unique
* Template name should be added under the 'Template' column
* Configuration will be overwritten if there is any match with a template
* One Network Device per Sheet

### Settings Sheet
* Any Sheets you wan the program to ignore, you can add them in the Settings Sheet. One per cell in the Column labeled "Sheets to ignore"
 * i.e. ignoring a vlan sheet, ip sheet, or management documentation.
* Ensure the Configuration Template Names are Unique
* Add the configuration next to each template name
* Template names and Keys utilized in the configuration are Case Sensitive

## Template Configuration Setup
For the Configuration Template, the keys that will be substituted with values are wrapped in curly braces "{}". The key within the curly braces has to match the exact Column Header Value you want to replace it with.
### Example
Configuration Template:
```
interface {Local Interface}
description {Description}
switchport
switchport mode trunk
```
With this template, the 'Local Interface' and 'Description' keys will map to a value as long as the key exist as a header. It is case sensitive.


# Running the Script
The script will not do anything unless a CLI option is selected. Please see below for available CLI options.

### CLI Options
```
Options:
  -h, --help            show this help message and exit
  -v, --verbose         Enable Verbose Output.
  -i INPUT_FILE, --input_file=INPUT_FILE
                        Input file name of excel sheet.
  -o OUTPUT_FILE, --output=OUTPUT_FILE
                        Output file name of excel sheet, if not output file is
                        specified it will overwrite the input file.
  -g, --generate_config
                        Generate Configuration based on the matching template.
  -c, --check_connections
                        Logs in to the devices, checks if connection matches
                        the outline connection in the spreadsheet. Will check
                        via CDP and LLDP. Will also gather SN information and
                        other basic info from 'show version'.
```
### Sample CLI Command
```
python PortMatrixHelper.py -i PortMatrix1.xlsx -o test -gcv
```
This Command will read the 'PortMatrix1.xlsx' workbook. After reading the device information and ignoring the sheets identified it will run the script with Config Generator, utilizing the templates, and will also login to the devices and check connections via lldp and cdp. Some show version information will be gathered. After completing the script it will output the information to a new spreadsheet, 'test.xlsx'.
