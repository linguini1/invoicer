# CLI parsing tools
__author__ = "Matteo Golin"

"""
Required parameters:

- Brand name

- Company being billed
- Company address
- Company location

- Invoice payment date
- Invoice number

- Items
- Their description
- Their name
- Their price per unit
- Their quantity

- Tax percentage

- Payment information
- Account name / payable to
- Bank name
- Email address

- Terms and conditions

"""

# Imports
import argparse

# Constants
DESCRIPTION = """Takes inputs for invoice generation."""
FILE_TYPE = argparse.FileType()  # Ensures passed file paths are in fact files

# Starting with issuer and terms and agreements first because they are constant
parser = argparse.ArgumentParser(DESCRIPTION)
subparsers = parser.add_subparsers(dest="command")

# Interface command
parser.add_argument(
    "-i",
    action="store_true",
    help="Triggers console interface launch on runtime."
)

# From file command
load = subparsers.add_parser("batch", help="Performs batch invoicing using data from CSV files.")

load.add_argument(
    "clients",
    type=FILE_TYPE,
    help="Filepath to client list CSV."
)

load.add_argument(
    "items",
    type=FILE_TYPE,
    help="Filepath to item list CSV."
)

load.add_argument(
    "batch",
    type=FILE_TYPE,
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
    required=True,
    type=str,
    help="The email of the issuer."
)

load.add_argument(
    "-phone", "-p",
    required=True,
    type=int,
    help="The phone number of the issuer."
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
    help="The text file containing the terms and agreements."
)
