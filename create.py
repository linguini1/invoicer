# Main file to run CLI and interface options
__author__ = "Matteo Golin"

# Imports
import datetime as dt
from utils import Item, Issuer, Client, Template

# Params
terms = "Here is a super long and ridiculous paragraph representing the terms and conditions of my company. This is " \
        "all MIT licensed anyways so it's not like it matters."

company = Issuer("GolinDev Inc.", "GolinDev", "Tangerine", "golindev@gmail.com", 3432622690)
due = dt.date.fromisoformat("2022-09-14")

# Load items and clients
Item.from_csv("itemList.csv")
Client.from_csv("clientList.csv")

template = Template(company, Client.instances[0], Item.instances, terms, due)

# Main
template.fill_out()
template.save(pdf=True)
