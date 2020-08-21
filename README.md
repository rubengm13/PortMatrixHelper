# PortMatrixHelper
 PortMatrixHelper is a simple configuration Generator. It parses a typical Port Matrix data into Configuration Templates for each Interface. The Configuration Templates can be modified an expanded on as needed.

# Getting Started
## Software Prerequisites
* Microsoft Excel XLSX Editor
* Python Module - openpyxl

## Work Book Setup
PortMatrixHelper utilizes a Port Matrix Excel Work Book, within this Spreadsheet a few requirements need to be Met so that the script runs without issue. Below is a list of requirements for the Work Book and Setup information.
* Port Matrix Work Book must have a "Settings" Sheet, Please utilize the provided Sample Spreadsheet and build from that, or copy the "Settings" sheet to your new WorkBook
* When you start your Table, the Headers must be defined in ROW 6, the Script will ignore the first 5 rows.
  * This is to Ensure Some Space is available for any Notes that need to be added about the Switch
* One Network Device per Sheet
* "Template" and "Configuration" need to be added to ROW 6, these names will be used as Headers to identify template to be used and where to post the configuration
  * The Name of the Configuration Template you wish to use for a particular row must be defined under that rows "Template"
* Any Sheets you wan the program to ignore, you can add them in the Settings Sheet. One per cell in the Column labeled "Sheets to ignore"
* Ensure the Configruation Template Names are Unique
* Ensure the Table Headers are Unique

## Template Setup
For the Configuration Template, the keys that will be substituted with values are wrapped in curly braces "{}". The key within the curly braces has to match the exact Column Header Value you want to replace it with.
### Example
Configuration Template:
```
interface {Interface}
description {description}
switchport
switchport mode trunk
```
With this template, the 'Interface' and 'description' keys will map to a value as long as the key exist as a header. It is case sensitive.


### CLI Options
   -h, --help            show this help message and exit
   -v, --verbose         Enable Verbose Output
   -i INPUT_FILE, --input_file=INPUT_FILE
                         Input file name of excel sheet
   -o OUTPUT_FILE, --output=OUTPUT_FILE
                         Output file name of excel sheet
