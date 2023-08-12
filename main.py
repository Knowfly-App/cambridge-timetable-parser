import argparse
import re

import pandas as pd
import PyPDF2


def parse_timetable(file_path, output_path, start_page, format):
    # read your file
    pdf = PyPDF2.PdfReader(open(file_path, "rb"))

    # strings to clenup
    replace = [
        "Syllabus/Component Code Duration Date Session",
        "November",
        "June"
        "Sessions:  AM morning        PM afternoon        EV evening\nIG Cambridge IGCSE    OL Cambridge O Level    \nAS Cambridge International AS Level    AL Cambridge International A Level    \nCambridge Final Exam Timetable ",
        " 2023",
        "Syllabus view (A–Z)",
        "Sessions:  AM morning        PM afternoon        \nIG Cambridge IGCSE    \nAS Cambridge International AS Level    AL Cambridge International A Level    \nCambridge Final Exam Timetable ",
        " 2023",
        "Sessions:  AM morning        PM afternoon        \nIG Cambridge IGCSE       \nAS Cambridge International AS Level    AL Cambridge International A Level    \nCambridge Final Exam Timetable ",
        " 2023",
        "Sessions:  AM morning        PM afternoon        \nIG Cambridge IGCSE    9–1 Cambridge IGCSE (9–1)    OL Cambridge O Level    \nAS Cambridge International AS Level    AL Cambridge International A Level    \nCambridge Final Exam Timetable ",
        " 2023",
        "Sessions:  AM morning        PM afternoon        EV evening\nIG Cambridge IGCSE    OL Cambridge O Level    \nAS Cambridge International AS Level    AL Cambridge International A Level    \nCambridge Final Exam Timetable ",
        " 2023",
        "Sessions:  AM morning        PM afternoon        EV evening\nIG Cambridge IGCSE    OL Cambridge O Level    \nAS Cambridge International AS Level    AL Cambridge International A Level    \nCambridge Final Exam Timetable ",
        " 2023",
        "Sessions:  AM morning        PM afternoon        \nIG Cambridge IGCSE    \nAS Cambridge International AS Level    AL Cambridge International A Level    \nCambridge Final Exam Timetable ",
        " 2023",
        "Sessions:  AM morning        PM afternoon  ",
        "IG Cambridge IGCSE        ",
        "AS Cambridge International AS Level    AL Cambridge International A Level    ",
        "Cambridge Final Exam Timetable ",
        " 2023Cambridge IGCSE",
        "Cambridge Final Exam Timetable ",
        " 2023",
        "Cambridge IGCSE Continued",
    ]

    data = []

    for i in range(start_page, len(pdf.pages)):
        text = pdf.pages[i].extract_text()
        for replace_line in replace:
            text = text.replace(replace_line, "")

        text = (
            text.replace("\n2023", "2023")
            .replace("AM", " AM\n")
            .replace("PM", " PM\n")
            .replace("EV", " EV\n")
        )
        temp = list(filter(None, text[:-3].splitlines()))

        # temp = [x for x in temp if x != 'IG Cambridge IGCSE   ']

        text = []

        def dontJoin(x):
            return (
                x.split()[0] == "Cambridge"
                or len(x) == 1
                or x[-2:] in ["AM", "PM", "EV"]
            )

        flag = False
        for i in range(len(temp)):
            if len(temp[i].strip()) == 0:
                continue
            if dontJoin(temp[i]):
                if flag or len(temp[i]) == 1 or temp[i][-9:] == "Continued":
                    flag = False
                    continue
                text.append(temp[i])
            else:
                text.append(temp[i] + " " + temp[i + 1])
                flag = True
                i += 1

        data.extend(text)

    data_string = "\n".join(data)

    titles = re.findall(r"Cambridge[a-zA-Z ]*\n", data_string)

    # split the data_string based on the titles
    data = re.split(r"Cambridge[a-zA-Z ]*\n", data_string)[1:]

    data = [
        [
            [
                titles[i].strip(),
                x,
                *re.findall(
                    r"(.*)[ ]?([0-9]{4}\/[0-9]{2}) ([0-9]?h?[ ]?[0-9]?[0-9]?m?)[ ]*(.*)",
                    x,
                ),
            ]
            for x in sorted(d.splitlines())
        ]
        for i, d in enumerate(data)
    ]

    # flatten data
    def flatten(l):
        return [item for sublist in l for item in sublist]

    flat_data = flatten(data)

    flat_data = [[i[0], *i[2]] for i in flat_data if len(i) == 3]

    # for the last string of each sublist in flat_data, replace AM with AM and PM with PM
    # flat_data = [
    #     [*d[:-1], d[-1]]
    #     for d in flat_data
    # ]

    # for each string in flat_data, replace multiple spaces with a single space
    flat_data = [[re.sub(r" +", " ", x) for x in d] for d in flat_data]

    # remove whitespace from the start and end of each string in flat_data
    flat_data = [[x.strip() for x in d] for d in flat_data]

    # convert the data_map to a dataframe
    df = pd.DataFrame(flat_data)
    df.columns = ["type", "subject", "code", "duration", "date"]

    if format == "json":
        df.to_json(output_path, orient="records")
    else:
        df.to_csv(output_path, index=False)
        
    return df

if __name__ == "__main__":
    # read arguments from the command line
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--file-path",
        type=str,
        default="file.pdf",
        help="path to the pdf file for the cambridge timetable",
    )
    parser.add_argument(
        "--output-path",
        type=str,
        default="timetable.csv",
        help="The path for the output CSV file (default: timetable.csv)",
    )
    parser.add_argument(
        "--start-page",
        type=int,
        default=10,
        help='First page from where the "Syllabus view(A–Z)" section starts',
    )
    parser.add_argument(
        "--format",
        type=str,
        default="csv",
        help="Export format: csv or json (default: csv)",
    )
    args = parser.parse_args()

    # call the function
    parse_timetable(
        file_path=args.file_path,
        output_path=args.output_path,
        start_page=args.start_page - 1,
        format=args.format,
    )
