import argparse
import re

import pandas as pd
import PyPDF2


def parse_timetable(file_path, output_path, format):
    # read your file
    pdf = PyPDF2.PdfReader(open(file_path, "rb"))

    # strings to clenup
    replace = [
        "Cambridge Final Exam Timetable",
        "Syllabus/Component Code Duration Date Session",
        "IG Cambridge IGCSE        ",
        "Sessions:  AM morning        PM afternoon  ",
        "Sessions:  AM morning        PM afternoon        \nIG Cambridge IGCSE       \nAS Cambridge International AS Level    AL Cambridge International A Level    \nCambridge Final Exam Timetable ",
        "Syllabus view (A–Z)",
        "Sessions:  AM morning        PM afternoon        \nIG Cambridge IGCSE    \nAS Cambridge International AS Level    AL Cambridge International A Level    \nCambridge Final Exam Timetable ",
        "AS Cambridge International AS Level    AL Cambridge International A Level    ",
        "Cambridge Final Exam Timetable ",
        "Sessions:  AM morning        PM afternoon        EV evening\nIG Cambridge IGCSE    OL Cambridge O Level    \nAS Cambridge International AS Level    AL Cambridge International A Level    \nCambridge Final Exam Timetable ",
        "Cambridge IGCSE Continued",
    ]

    data = []

    syllabus_found_count = 0

    for i in range(len(pdf.pages)):
        text = pdf.pages[i].extract_text()

        if "Syllabus view (A–Z)" in text:
            syllabus_found_count += 1

        if syllabus_found_count < 2:
            continue

        # ? replace all "November" that are not preceded by a number with ""
        text = re.sub(r"(?<!\d) November", "", text)
        text = re.sub(r"(?<!\d) June", "", text)
        text = re.sub(r"(?<!\d) March", "", text)
        for replace_line in replace:
            text = text.replace(replace_line, "")

        text = (
            text.replace("\n2024", "2024")
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

    # titles = re.findall(r"Cambridge[a-zA-Z ]*\n", data_string)

    whitelist = [
        "Cambridge IGCSE",
        "Cambridge International AS Level",
        "Cambridge International A Level",
        "Cambridge O Level",
    ]

    titles = re.findall("|".join(whitelist), data_string)

    data = re.split("|".join(titles), data_string)[1:]

    data = [
        [
            [
                titles[i].strip(),
                x,
                *re.findall(
                    r"(.*)[ ]?([0-9]{4}\/[0-9]{2}) ([0-9]?h?[ ]?[0-9]?[0-9]?m?)[ ]*(.*) (AM|PM|EV)",
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
    
    # for each string in flat_data, replace multiple spaces with a single space
    flat_data = [[re.sub(r" +", " ", x) for x in d] for d in flat_data]

    # remove whitespace from the start and end of each string in flat_data
    flat_data = [[x.strip() for x in d] for d in flat_data]

    # convert the data_map to a dataframe
    df = pd.DataFrame(flat_data)
    df.columns = ["type", "subject", "code", "duration", "date", "session"]

    # replace the leading digits in subject with empty string
    df["subject"] = df["subject"].str.replace(r"^[\d ]+", "", regex=True)

    # if format == "json":
    #     df.to_json(output_path, orient="records")
    # else:
    #     df.to_csv(output_path, index=False)

    grouped_data = df.groupby(df["code"].str[:4])

    # make a list of the grouped data
    grouped_data_list = [grouped_data.get_group(x) for x in grouped_data.groups]

    grouped_data = []

    for group in grouped_data_list:
        # get the common substring of the subjects
        # get a list of the subjects in the group
        subjects = group["subject"].tolist()

        # get the common substring of the subjects
        commonSubstring = ""

        # get the shortest subject
        shortestSubject = min(subjects, key=len)

        # iterate through the characters of the shortest subject
        for i in range(len(shortestSubject)):
            # get the current character
            currentChar = shortestSubject[i]
            # check if the current character is the same in all the subjects
            if all([subject[i] == currentChar for subject in subjects]) and (
                currentChar.isalpha() or currentChar == " "
            ):
                # add the current character to the common substring
                commonSubstring += currentChar
            else:
                # break the loop if the current character is not the same in all the subjects
                break

        # convert the group to a dictionary
        group = group.sort_values(by=["code"]).to_dict("records")
        # add the group to the output data
        grouped_data.append(
            {
                "code": group[0]["code"][:4],
                "commonSubstring": commonSubstring.strip(),
                "group": group,
            }
        )

    # save the output data to a json file
    # json.dump(grouped_data, open(f"json/zone{idx}.json", "w"), indent=2)

    grouped_df = pd.DataFrame(grouped_data)

    if format == "json":
        grouped_df.to_json(output_path, orient="records")
    else:
        grouped_df.to_csv(output_path, index=False)

    return grouped_df, df


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
        "--format",
        type=str,
        default="json",
        help="Export format: csv or json (default: json)",
    )
    args = parser.parse_args()

    # call the function
    parse_timetable(
        file_path=args.file_path,
        output_path=args.output_path,
        format=args.format,
    )
