# Main file to run CLI and interface options
__author__ = "Matteo Golin"

# Imports
import datetime as dt
from utils import Item, Issuer, Client, Template

# Params
terms = "Here is a super long and ridiculous paragraph representing the terms and conditions of my company. This is " \
        "all MIT licensed anyways so it's not like it matters."

company = Issuer("GolinDev Inc.", "GolinDev", "Tangerine", "golindev@gmail.com", 3432622690)

client = Client("Jennifer Kathleen Nuth", "201 Tewsley Dr", "Ottawa, ON, Canada")

example_item = Item("Auto invoice software", "Creates invoices automatically.", 1500.00, 3)

due = dt.date.fromisoformat("2022-09-14")

template = Template(company, client, example_item, terms, due)

print(template)

# Main
template.fill_out()
template.save(pdf=True)
