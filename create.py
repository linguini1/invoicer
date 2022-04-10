# Main file to run CLI and interface options
__author__ = "Matteo Golin"

# Imports
from utils import Item, Issuer, Client, Template
from interface import Interface
from inputs import parser

# Get command line arguments
arg = parser.parse_args()
print(arg)

# Get template from user input
if arg.i:
    interface = Interface()
    template = interface.invoice_from_input()

if arg.command == "batch":
    Item.from_csv(arg.items.name)
    Client.from_csv(arg.clients.name)

    issuer = Issuer(
        name=arg.name,
        account_name=arg.acc,
        bank=arg.bank,
        email=arg.email,
        phone=arg.phone
    )

    Template.set_issuer(issuer)

    if arg.terms:
        Template.set_terms(arg.terms)
    else:
        Template.terms_from_file(arg.terms_file.name)

    Template.batch_from_file(arg.batch.name, pdf=True)
