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

# Starting with issuer and terms and agreements first because they are constant
parser = argparse.ArgumentParser()
