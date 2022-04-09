# Invoice creation utilities

# Imports
import datetime as dt
import bs4.element
from bs4 import BeautifulSoup
import pdfkit
import os
import re
import pandas as pd
from typing import Iterable

# Constants
EMAIL_RE = "^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*$"
ISO_DATE_RE = "^\d{4}-([0]\d|1[0-2])-([0-2]\d|3[01])$"

OPTIONS = {
    "dpi": 300,
    "page-size": "A5",
    "margin-top": "0",
    "margin-bottom": "0",
    "margin-left": "0",
    "margin-right": "0",
    "encoding": "UTF-8",
    "no-outline": None,
}


# Classes
class Item:

    _instances = []

    def __init__(self, name: str, description: str, price: float, quantity: int):

        # Validation
        assert price >= 0, f"Price {price} is not greater than or equal to $0."
        assert quantity >= 0, f"Quantity {quantity} is not greater than or equal to 0."
        assert type(quantity) is int, f"Quantity {quantity} is not an integer value."

        self._instances.append(self)

        # Properties
        self.name = name
        self.description = description
        self.price = round(price, 2)
        self.__quantity = quantity

    # Class methods

    @classmethod
    def from_csv(cls, filename: str):

        """Creates a bunch of item instances from a CSV file."""

        for index, row in dataframe_from_csv(filename):

            Item(
                name=row["name"],
                description=row["description"],
                price=float(row["price"]),
                quantity=0  # Quantity is 0 by default until set
            )

    @classmethod
    def find_items(cls, names: str | list[str]) -> list:

        """Returns the Item object with the corresponding name."""

        names = [names] if type(names) is str else names  # Make sure names is iterable

        return [item for item in cls._instances if item.name in names]

    @classmethod
    def all(cls) -> list:
        return cls._instances

    # Instance methods

    # Properties
    @property
    def subtotal(self) -> float:
        return round(self.price * self.quantity, 2)

    @property
    def html(self) -> BeautifulSoup:

        representation = f"""<tr>
            <td>
              <div class="product-desc">
                <h4>{self.name}</h4>
                <p>{self.description}</p>
              </div>
            </td>
            <td>{format_price(self.price)}</td>
            <td>{self.quantity}</td>
            <td>{format_price(self.subtotal)}</td>
          </tr>"""

        return BeautifulSoup(representation, features='html.parser')

    @property
    def quantity(self):
        return self.__quantity

    @quantity.setter
    def quantity(self, value: int):

        if type(value) is not int:
            raise ValueError(f"Quantity {value} is not an integer.")
        elif value < 0:
            raise ValueError(f"Quantity {value} is not greater than or equal to 0.")

        self.__quantity = value

    # Built in methods

    def __repr__(self):
        return f"#{self._id} {self.name} (x{self.quantity})\n${self.price:.2f} each\n{self.description[:25]}..."


class Issuer:

    def __init__(self, name: str, account_name: str, bank: str, email: str, phone: int):

        # Validations
        assert type(phone) is int, f"Phone number {phone} was not entered as an integer."
        assert len(str(phone)) == 10, f"Phone number {phone} is not 10 digits long."
        assert re.match(EMAIL_RE, email), f"The email address {email} is invalid."

        # Properties
        self.name = name
        self.account_name = account_name
        self.bank = bank
        self.email = email
        self.phone = phone

    def __repr__(self):

        return f"{self.name}"


class Client:

    _instances = []

    def __init__(self, name: str, address: str, location: str):

        self._instances.append(self)

        # Properties
        self.name = name
        self.address = address
        self.location = location

    @classmethod
    def from_csv(cls, filename: str):
        """Creates a bunch of item instances from a CSV file."""

        # Create client instances
        for index, row in dataframe_from_csv(filename):

            Client(
                name=row["name"],
                address=row["address"],
                location=row["location"]
            )

    @classmethod
    def find_client(cls, name: str):

        """Returns the Item object with the corresponding name."""

        return [client for client in cls._instances if client.name == name][0]

    def __repr__(self):
        return f"{self.name}"


class Template:

    invoices_created = 0
    __terms_and_conditions = None
    __issuer = None

    def __init__(
            self,
            client: Client,
            items: list[Item] | Item,
            due: str | dt.date | None = None,
            offset: int = 0,
            tax_percentage: float = 13.0
    ):

        # Validation
        assert type(offset) is int, f"Starting number of {offset} is not an integer."
        assert 0 <= tax_percentage <= 100, f"Tax percentage of {tax_percentage} is not between 0 and 100."

        if type(due) is str:
            assert re.match(ISO_DATE_RE, due), f"Due date of {due} is not in ISO format (yyyy-mm-dd)."
            self.__due = dt.date.fromisoformat(due)
        else:
            assert type(due) is dt.date, f"Due date must be in ISO date format as a string or be a datetime.date object."
            self.__due = due

        Template.invoices_created += 1  # Track instances

        # Properties
        self.invoice = self.__get_template()
        self.client = client
        self.items = items if type(items) is list else [items]
        self._id = self.invoices_created + offset  # So numbering can start from specified number
        self.tax_percentage = tax_percentage / 100
        self._created = dt.date.today()

    # Class functions

    @classmethod
    def batch_from_file(cls, filename: str, pdf=False):

        """Creates a batch of invoices from a batch CSV file."""

        if not cls.__issuer:
            raise ValueError("Please define an issuer first.")

        if not cls.__terms_and_conditions:
            raise ValueError("Please define the terms and agreements first.")

        batches = pd.read_csv(filename)  # Read batches

        # Create templates from batches
        for client in batches:
            column = batches[client]

            current_items = []  # Items charged on current invoice

            # Parse client header (duplicate headers get numbers added on and that prevents lookup)
            client = client.split(".")[0]

            # Getting client
            client = Client.find_client(client)

            for row in column.iteritems():
                index, value = row  # Unpack

                # As soon as NaN is reached, break (no more items)
                if pd.isna(value):
                    break

                # Get date
                if index == 0:
                    due_date = value

                # It's an item
                else:
                    name, quantity = value.split(",")
                    quantity = int(quantity)

                    item = Item.find_items(name)[0]
                    item.quantity = quantity

                    current_items.append(item)

            # Create the template and save it
            template = Template(client, current_items, due=due_date)
            template.save(pdf=pdf)

    @classmethod
    def terms_from_file(cls, filename: str):

        """Sets the class terms and agreements to the terms and agreements read from a text file."""

        if ".txt" not in filename:
            raise ValueError("File must be .txt file.")

        with open(filename, "r") as file:
            terms = file.read()

        cls.__terms_and_conditions = terms

    @classmethod
    def set_terms(cls, terms: str):
        cls.__terms_and_conditions = terms

    @classmethod
    def set_issuer(cls, issuer: Issuer):
        cls.__issuer = issuer

    # Properties

    @property
    def terms_and_conditions(self):
        return self.__class__.terms_and_conditions

    @property
    def issuer(self):
        return self.__class__.__issuer

    @property
    def due(self):
        return self.__due

    @due.setter
    def due(self, value: str | dt.date):

        if type(value) is str:

            if re.match(ISO_DATE_RE, value):
                self.__due = dt.date.fromisoformat(value)
            else:
                raise ValueError("Due date string not in ISO format (yyyy-mm-dd).")

        elif type(value) == dt.date:
            self.__due = value
        else:
            raise ValueError("Due date must be an ISO date string or a datetime.date object.")

    @property
    def subtotal(self) -> float:

        """Returns pre-tax subtotal as a float."""

        subtotal = 0
        for item in self.items:
            subtotal += item.subtotal

        return subtotal

    @property
    def tax(self) -> float:

        """Returns tax total as a float."""

        return self.subtotal * self.tax_percentage

    @property
    def grand_total(self) -> float:

        """Returns sum of subtotal and tax as a float."""

        return self.subtotal + self.tax

    # Utility functions

    @staticmethod
    def __get_template() -> BeautifulSoup:

        """Returns the invoice template."""

        with open("resources/invoice.html") as file:
            raw_text = file.read()
            template = BeautifulSoup(raw_text, features='html.parser')

        return template

    def __get_element(self, class_name: str) -> bs4.element.Tag:

        """Returns an element of the template given its class name."""

        return self.invoice.find(class_=class_name)

    def __replace_text(self, class_name: str, text: str):

        """Replaces the tag text using passed text."""

        self.__get_element(class_name).string.replace_with(text)

    # Functions for filling out template

    def __invoice_details(self):

        """Updates invoice details."""
        self.__replace_text("invoice-date", f"Date of issue: {str(self._created)}")
        self.__replace_text("payment-date", f"Due by: {str(self.due)}")
        self.__replace_text("invoice-number", f"Invoice #{str(self._id)}")

    def __add_items(self):

        """Adds items to the item list on the invoice."""

        # Get the item table
        table = self.__get_element("item-table")

        for item in self.items:
            table.append(item.html)

    def __totals(self):

        """Update totals."""

        # Replacing
        self.__replace_text("actual-subtotal", format_price(self.subtotal))
        self.__replace_text("grandtotal", format_price(self.grand_total))
        self.__replace_text("tax", format_price(self.tax))
        self.__replace_text("tax-percentage", f"Tax {int(self.tax_percentage * 100)}%")

    def __brand_name(self):

        """Fills in brand name."""

        self.__replace_text("brand-name", self.__issuer.name)

    def __payment_info(self):

        """Updates payment information."""

        self.__replace_text("pay-to", f"Pay to: {self.__issuer.name}")
        self.__replace_text("account", f"Account: {self.__issuer.account_name}")
        self.__replace_text("bank", self.__issuer.bank)
        self.__replace_text("email", self.__issuer.email)
        self.__replace_text("phone", format_phone(self.__issuer.phone))

    def __billing_details(self):
        """Updates billing information."""

        self.__replace_text("company-name", self.client.name)
        self.__replace_text("address", self.client.address)
        self.__replace_text("location", self.client.location)

    def __fill_terms_and_conditions(self):

        """Updates terms and conditions."""

        self.__replace_text("terms-and-conditions", self.__terms_and_conditions)

    def __add_styling(self):

        """Adds the CSS styling inline in the invoice."""

        with open("resources/invoice.css") as file:
            style = f"<style>{file.read()}</style>"

        style_tag = BeautifulSoup(style, features='html.parser')

        self.invoice.find("html").append(style_tag)

    def populate(self):

        """Fills out the invoice in its entirety."""

        if not self.__terms_and_conditions:
            raise ValueError("Please define the terms and conditions of the invoice.")

        if not self.due:
            raise ValueError("Please define the due date of the invoice.")

        self.__invoice_details()
        self.__add_items()
        self.__totals()
        self.__brand_name()
        self.__payment_info()
        self.__billing_details()
        self.__fill_terms_and_conditions()
        self.__add_styling()

        self.invoice.find("title").string.replace_with(f"Invoice {self._id}")

    def save(self, pdf=False):

        """Saves the template as an HTML file."""

        # Make output directory
        try:
            os.mkdir("output")
        except FileExistsError:
            pass

        # Ensure population of field
        self.populate()

        with open(f"output/invoice_{self._id}.html", "w") as file:
            file.write(str(self.invoice))

        if pdf:
            self.__save_pdf()

    def __save_pdf(self):

        """Saves the template as a PDF file."""

        project_dir = os.getcwd() + "\\output\\"  # Requires absolute path for some reason

        filepath = f"{project_dir}invoice_{self._id}"

        try:
            pdfkit.from_file(f"{filepath}.html", f"{filepath}.pdf", options=OPTIONS)
        except OSError:  # For some reason this is always thrown, but PDF is successfully made anyway
            pass

    # Built in methods
    def __repr__(self):
        return f"Issued by: {self.__issuer}\nIssued to: {self.client}\nTotal: {self.grand_total}\nDue: {self.due}"


# Functions
def format_price(price: float) -> str:

    """Returns price as a string formatted to two decimal places."""

    return f"{round(price, 2):.2f}"


def format_phone(phone: int) -> str:

    """Returns phone number as a string formatted with hyphens."""

    phone = str(phone)

    return f"{phone[:3]}-{phone[3:6]}-{phone[6:]}"


def dataframe_from_csv(filename: str) -> Iterable:

    """Returns the CSV as a Pandas dataframe."""

    if ".csv" not in filename:
        raise ValueError("File must be a .csv file.")

    data = pd.read_csv(filename)  # Read in data

    return data.iterrows()
