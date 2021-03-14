"""Download and format the LSP specification."""
import argparse
import requests
import subprocess


def get_argument_parser():
    """Return the Argument Parser."""
    parser = argparse.ArgumentParser(
        description="Download and format the LSP specification."
    )

    parser.add_argument("--version", choices=(["3-14", "3-15", "3-16", "3-17", "current"]), help="the version of the protocol", default="current")

    parser.add_argument("-o", "--output", help="the name of the resulting file (excluding extension)", default="specification")


    return parser

url_part = "https://raw.githubusercontent.com/microsoft/language-server-protocol/gh-pages/_specifications/specification-{0}.md"
arguments = get_argument_parser().parse_args()

# replace current with its actual name
if arguments.version == "current":
    arguments.version = requests.get(url_part.format(arguments.version)).content.decode()
    arguments.version = arguments.version.strip(".md")
    arguments.version = arguments.version.strip("specification-")

specification = requests.get(url_part.format(arguments.version)).content.decode()

# Pandoc has issues with \n and \r
specification = specification.replace("\\n", "\\\\n")
specification = specification.replace("\\r", "\\\\r")

specification_lines = specification.splitlines()

# insert various Panroc options
specification_lines.insert(1, 'geometry: "left=3cm,right=3cm,top=2cm,bottom=2cm"')

specification = "\n".join(specification_lines)

with open(arguments.output + ".md", "w") as f:
    f.write(specification)

subprocess.Popen(["pandoc", "-i", arguments.output + ".md", "-o", arguments.output + ".pdf", "--pdf-engine=lualatex"]).communicate()
