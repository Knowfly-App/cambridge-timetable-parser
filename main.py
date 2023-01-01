import PyPDF2
import re
import pandas as pd
import argparse


def parse_timetable(file_path, output_path, start_page, format):
    # read your file
    pdf = PyPDF2.PdfReader(open(file_path, 'rb'))

    # strings to clenup
    replace = ["Syllabus/Component Code Duration Date Session",
               "Sessions:  AM morning        PM afternoon        EV evening\nIG Cambridge IGCSE    OL Cambridge O Level    \nAS Cambridge International AS Level    AL Cambridge International A Level    \nCambridge Final Exam Timetable June 2023", "Syllabus view (A–Z)"]

    data = []

    for i in range(start_page, len(pdf.pages)):
        text = pdf.pages[i].extract_text()
        for replace_line in replace:
            text = text.replace(replace_line, '')
        temp = list(filter(None, text[:-3].splitlines()))

        text = []

        def dontJoin(x): return x.split()[0] == 'Cambridge' or len(
            x) == 1 or x[-2:] in ['AM', 'PM', 'EV']

        flag = False
        for i in range(len(temp)):
            if dontJoin(temp[i]):
                if flag or len(temp[i]) == 1 or temp[i][-9:] == 'Continued':
                    flag = False
                    continue
                text.append(temp[i])
            else:
                text.append(temp[i] + " " + temp[i+1])
                flag = True
                i += 1

        data.extend(text)

    data_string = "\n".join(data)

    titles = re.findall(r'Cambridge[a-zA-Z ]*\n', data_string)

    # split the data_string based on the titles
    data = re.split(r'Cambridge[a-zA-Z ]*\n', data_string)[1:]

    data = [[[titles[i].strip(), x, *re.findall(
            r'(.*)[ ]?([0-9]{4}\/[0-9]{2}) ([0-9]*?h?[ ]?[0-9]*?m?) (.*)', x)] for x in sorted(d.splitlines())]
            for i, d in enumerate(data)]

    # flatten data
    def flatten(l): return [item for sublist in l for item in sublist]

    flat_data = flatten(data)

    flat_data = [[i[0], *i[2]] for i in flat_data]

    # convert the data_map to a dataframe
    df = pd.DataFrame(flat_data)
    df.columns = ['type', 'subject', 'code', 'duration', 'date']
    
    if format == 'json':
        df.to_json(output_path, orient='records')
    else:
        df.to_csv(output_path, index=False)


if __name__ == '__main__':
    # read arguments from the command line
    parser = argparse.ArgumentParser()
    parser.add_argument('--file-path', type=str, default='file.pdf',
                        help='path to the pdf file for the cambridge timetable')
    parser.add_argument('--output-path', type=str, default='timetable.csv',
                        help='The path for the output CSV file (default: timetable.csv)')
    parser.add_argument('--start-page', type=int, default=10,
                        help='First page from where the "Syllabus view(A–Z)" section starts')
    parser.add_argument('--format', type=str, default="csv",
                        help='Export format: csv or json (default: csv)')
    args = parser.parse_args()

    # call the function
    parse_timetable(file_path=args.file_path,
                    output_path=args.output_path, start_page=args.start_page-1, format=args.format)
