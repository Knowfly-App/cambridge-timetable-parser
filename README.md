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
usage: main.py [-h] [--file_path FILE_PATH] [--output_path OUTPUT_PATH] [--start-page START_PAGE]

options:
  -h, --help            show this help message and exit
  --file_path FILE_PATH
                        path to the pdf file for the cambridge timetable
  --output_path OUTPUT_PATH
                        The path for the output CSV file (default: timetable.csv)
  --start-page START_PAGE
                        First page from where the "Syllabus view(A–Z)" section starts
```


## Example:

> Note: Use `python3` instead of `python` if you do not have python aliased to python3


### Usage with default values

```bash
python main.py
```

### Usage with all arguments

```bash
python main.py --file_path "timetable.pdf" --output_path "output.csv" --start-page 10
```

