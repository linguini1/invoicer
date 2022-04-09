# Main file to run CLI and interface options
__author__ = "Matteo Golin"

# Imports
from utils import Item, Issuer, Client, Template
from interface import Interface
from inputs import parser

# Get command line arguments
arguments = parser.parse_args()
print(arguments)

# Get template from user input
if arguments.i:
    interface = Interface()
    template = interface.invoice_from_input()

if arguments.command == "batch":
    Item.from_csv(arguments.items)
    Client.from_csv(arguments.clients)

Item.from_csv("itemList.csv")
Client.from_csv("clientList.csv")

golinDev = Issuer("Golin Dev Inc.", "Golin Dev", "Royal Bank of Canada", "golindev@gmail.com", 5555556666)

Template.set_issuer(golinDev)
Template.terms_from_file("terms.txt")
Template.batch_from_file("combos.csv", pdf=True)
