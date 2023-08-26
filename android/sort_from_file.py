"""
Sort files based on an already existing proprietary-files.txt with proper sections
"""

from sys import exit as sysexit, argv
from re import sub as regsub

MISC_SECTION = "Misc"

def extract_path(full_line: str) -> str:
    """
    Removes all kind of extra arguments in the file name (-, ; and :)
    """
    # Remove the "-" that specifies the file should be treated as a build target
    cleaned_line = regsub("^-", "", full_line)
    # Remove all extra arguments after ";" like "MODULE="
    cleaned_line = cleaned_line.split(";")[0]
    # Always use the real vendor path to compare files, this should help handling renames
    cleaned_line = cleaned_line.split(":")[0]
    # Remove whitespaces and \n
    cleaned_line = cleaned_line.strip()

    return cleaned_line


if __name__ == "__main__":
    proprietary_files = []
    sections = {}
    sorted_sections = { MISC_SECTION: [] }

    if len(argv) < 3:
        print("Not enough arguments")
        sysexit(1)

    sort_source_file = argv[1]
    file_to_sort = argv[2]

    # Start by retrieving the list of proprietary files
    with open(file_to_sort, "r", encoding="UTF-8") as sortfile:
        for line in sortfile.readlines():
            if not line.startswith("#") and line.strip() != "":
                proprietary_files.append(line.strip()) # Remove suffixes like \n or extra spaces

    # Next, extract each section from the source file
    with open(sort_source_file, "r", encoding="UTF-8") as sourcefile:
        current_section = "Unknown"
        previous_line = ""
        for line in sourcefile.readlines():
            line = extract_path(line)
            # A section is delimited by an empty line followed by a comment (the section name)
            if line.startswith("#") and previous_line.strip() == "":
                current_section = line.removeprefix("#").strip()
            elif not line.startswith("#") and line.strip() != "":
                sections[line] = current_section
            previous_line = line

    # Compare both files and sort
    for blob in proprietary_files:
        blob_path = extract_path(blob)
        if blob_path in sections:
            section = sections[blob_path]
            if section in sorted_sections:
                sorted_sections[section].append(blob)
            else:
                sorted_sections[section] = [blob]
        else:
            sorted_sections[MISC_SECTION].append(blob)

    if len(sorted_sections[MISC_SECTION]) == 0:
        del sorted_sections[MISC_SECTION]

    # Finish by printing all sections in sorted order
    sections_names = list(sorted_sections.keys())
    sections_names.sort()

    for name in sections_names:
        print(f"# {name}")
        for blob in sorted_sections[name]:
            print(blob)
        print("")
