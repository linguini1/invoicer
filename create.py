# Main file to run CLI and interface options
__author__ = "Matteo Golin"

# Imports
import datetime as dt
from utils import Item, Issuer, Client, Template

# Params
company = Issuer("GolinDev Inc.", "GolinDev", "Tangerine", "golindev@gmail.com", 3432622690)
due = dt.date.fromisoformat("2022-09-14")

# Load items and clients
Item.from_csv("itemList.csv")
Client.from_csv("clientList.csv")

template = Template(company, Client.find_client("Mauro Golin"), Item.all(), due=due)
template.terms_from_file("terms.txt")

# Main
template.populate()
template.save(pdf=True)
