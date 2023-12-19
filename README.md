# Cambridge Timetable Parser

> A simple script to parse the timetable from the pdf file for the Timetable provided by the Cambridge.

## Installing dependencies

```bash
pip install -r requirements.txt
```

or 

```bash
pip3 install -r requirements.txt
```

## Usage 

```bash
usage: main.py [-h] [--file-path FILE_PATH] [--output-path OUTPUT_PATH] [--format FORMAT]

options:
  -h, --help            show this help message and exit
  --file-path FILE_PATH
                        path to the pdf file for the cambridge timetable
  --output-path OUTPUT_PATH
                        The path for the output CSV file (default: timetable.csv)
  --format FORMAT       Export format: csv or json (default: json)
```


## Example:

> Note: Use `python3` instead of `python` if you do not have python aliased to python3


### Usage with default values

```bash
python main.py
```

### Usage with all arguments

```bash
python main.py --file_path "timetable.pdf" --output_path "output.csv" --format "csv"
```

>
> Note the CSV format only extracts the timetable as a normal table, it does not group the subjects by code.
> If you wish to group the subjects by code, try using the JSON format.
>