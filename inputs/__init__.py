# CLI parsing tools
__author__ = "Matteo Golin"

# Imports
import argparse
import re
from utils import EMAIL_RE

# Constants
DESCRIPTION = """Takes inputs for invoice generation."""
FILE_TYPE = argparse.FileType()  # Ensures passed file paths are in fact files


def file_path_metavar(filename: str, ext: str) -> str:

    """File path example."""

    return f"path/to/{filename}.{ext}"


# Starting with issuer and terms and agreements first because they are constant
parser = argparse.ArgumentParser(DESCRIPTION)
subparsers = parser.add_subparsers(dest="command")


# Validation types
def Email(email: str) -> str:

    """Email type validation."""

    if re.match(EMAIL_RE, email):
        return email
    else:
        raise ValueError(f"The passed email {email} is not valid.")


def Phone(number: str) -> int:

    """Phone validation type."""

    if len(number) == 10:

        try:
            number = int(number)
            return number
        except ValueError:
            raise ValueError(f"The phone number {number} is not a valid integer.")

    else:
        raise ValueError("Phone number must be 10 digits long.")


# Interface command
parser.add_argument(
    "-i", "-interface",
    action="store_true",
    help="Triggers console interface launch on runtime."
)

# From file command
load = subparsers.add_parser("batch", help="Performs batch invoicing using data from CSV files.")

load.add_argument(
    "clients",
    type=FILE_TYPE,
    metavar=file_path_metavar("clientsFile", "csv"),
    help="Filepath to client list CSV."
)

load.add_argument(
    "items",
    type=FILE_TYPE,
    metavar=file_path_metavar("itemsFile", "csv"),
    help="Filepath to item list CSV."
)

load.add_argument(
    "batch",
    type=FILE_TYPE,
    metavar=file_path_metavar("batchFile", "csv"),
    help="Filepath to invoice batch CSV."
)

load.add_argument(
    "-name", "-n",
    required=True,
    type=str,
    help="The name of the issuer."
)

load.add_argument(
    "-acc", "-a",
    required=True,
    metavar="ACCOUNT NAME",
    type=str,
    help="The account name of the issuer."
)

load.add_argument(
    "-bank", "-b",
    required=True,
    type=str,
    help="The bank of the issuer."
)

load.add_argument(
    "-email", "-e",
    metavar="example@domain.net",
    required=True,
    type=Email,
    help="The email of the issuer."
)

load.add_argument(
    "-phone", "-p",
    metavar="5555555555",
    required=True,
    type=Phone,
    help="The phone number of the issuer, with no spaces or hyphens."
)

# Terms and agreements should be mutually exclusive (either file or string)
terms_group = load.add_mutually_exclusive_group(required=True)

terms_group.add_argument(
    "-terms", "-t",
    type=str,
    help="The terms and agreements as a string."
)

terms_group.add_argument(
    "-terms-file", "-tf",
    type=FILE_TYPE,
    metavar=file_path_metavar("termsAndAgreements", "txt"),
    help="The text file containing the terms and agreements."
)
