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
    type=str,
    help="Filepath to client list CSV."
)

load.add_argument(
    "items",
    type=str,
    help="Filepath to item list CSV."
)

load.add_argument(
    "batch file",
    type=str,
    help="Filepath to invoice batch CSV."
)
