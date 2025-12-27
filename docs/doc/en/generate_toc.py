""" 
This helper script generates a table of contents listing all the files of the wiki. 
The resulting file "_Sidebar.md" will be written to the same folder. 
On GitHub, this is shown as the sidebar of the wiki, allowing navigation.

(c) Kai Droege, Colin Curtain 2024 
"""

import os

# Define the GitHub wiki base URL
base_url = "https://github.com/ccbogel/QualCoder/wiki/"

def generate_sidebar_section(section_title: str) -> str:
    section_level = section_title[:2]
    filenames = os.listdir()
    sidebar_entries = []

    for filename in filenames:
        # Use only files belonging to this section
        if filename.startswith(section_level) and filename.endswith(".md"):
            # Extract the number and the name from the filename
            number, name_md = filename.split('-', 1)
            # Remove the '.md' extension and replace '-' with spaces to get the name
            name = name_md[:-3].replace('-', ' ')
            # Format the entry
            #sidebar_entry = f"     {number} [{name}]({base_url}{number}-{name})\n"
            sidebar_entry = f"     {number} [{name}]({base_url}{filename[:-3]})\n"
            
            sidebar_entries.append(sidebar_entry)

    # Sort entries by the numerical prefix for ordered display
    sidebar_entries.sort()

    # Collect entries in section string with empty lines in between
    res = section_title + '\n\n'
    for entry in sidebar_entries:
        res += entry + '\n'
    
    return res

# Main script

# 1) Add the Titel and the entry for "1. Introduction" (= Home.md)
sidebar_text = """
# Contents

1. __[Introduction](https://github.com/ccbogel/QualCoder/wiki)__

"""

# 2) Add the sections
sidebar_text += generate_sidebar_section("2. __Setup__")
sidebar_text += generate_sidebar_section("3. __Managing Data__")
sidebar_text += generate_sidebar_section("4. __Coding__")
sidebar_text += generate_sidebar_section("5. __Analyzing the Results__")
sidebar_text += generate_sidebar_section("6. __Advanced Options__")
sidebar_text += generate_sidebar_section("7. __Other Information__")

# 3) Write it to "_Sidebar.md"
with open('_Sidebar.md', 'w', encoding='utf-8') as outfile:
    outfile.write(sidebar_text)