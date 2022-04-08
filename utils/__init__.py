# Invoice creation utilities

# Imports
import datetime as dt
import bs4.element
from bs4 import BeautifulSoup
import pdfkit
import os
import re

# Constants
EMAIL_RE = "^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*$"
ISO_DATE_RE = "^\d{4}-([0]\d|1[0-2])-([0-2]\d|3[01])$"


# Classes
class Item:

    def __init__(self, name: str, description: str, price: float, quantity: int):

        # Validation
        assert price >= 0, f"Price {price} is not greater than or equal to $0."
        assert quantity >= 0, f"Quantity {quantity} is not greater than or equal to 0."
        assert type(quantity) is int, f"Quantity {quantity} is not an integer value."

        # Properties
        self.name = name
        self.description = description
        self.price = price
        self.quantity = quantity

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


class Client:

    def __init__(self, name: str, address: str, location: str):
        self.name = name
        self.address = address
        self.location = location


class Template:

    invoices_created = 0

    def __init__(
            self,
            issuer: Issuer,
            client: Client,
            items: list[Item] | Item,
            terms_and_conditions: str,
            due: str | dt.date,
            offset: int = 0,
            tax_percentage: float = 13.0
    ):

        # Validation
        assert type(offset) is int, f"Starting number of {offset} is not an integer."
        assert 0 <= tax_percentage <= 100, f"Tax percentage of {tax_percentage} is not between 0 and 100."

        if type(due) is str:
            assert re.match(ISO_DATE_RE, due), f"Due date of {due} is not in ISO format (yyyy-mm-dd)."
        else:
            assert type(due) is dt.date, f"Due date must be in ISO date format as a string or be a datetime.date object."

        Template.invoices_created += 1  # Track instances

        # Properties
        self.invoice = self.__get_template()
        self.issuer = issuer
        self.client = client
        self.terms = terms_and_conditions
        self.items = items if type(items) is list else [items]
        self.__due = due
        self._id = self.invoices_created + offset  # So numbering can start from specified number
        self.tax_percentage = tax_percentage / 100

    # Properties
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

        return self.__get_element(class_name).string.replace_with(text)

    # Functions for filling out template

    def invoice_details(self):

        """Updates invoice details."""

        today = dt.date.today()  # Today's date

        self.__replace_text("invoice-date", f"Date of issue: {str(today)}")
        self.__replace_text("payment-date", f"Due by: {str(self.due)}")
        self.__replace_text("invoice-number", f"Invoice #{str(self._id)}")

    def add_items(self):

        """Adds items to the item list on the invoice."""

        # Get the item table
        table = self.__get_element("item-table")

        for item in self.items:
            table.append(item.html)

    def totals(self):

        """Update totals."""

        # Calculations
        subtotal = 0
        for item in self.items:
            subtotal += item.subtotal

        tax = subtotal * self.tax_percentage
        grand_total = subtotal + tax

        # Replacing
        self.__replace_text("actual-subtotal", format_price(subtotal))
        self.__replace_text("grandtotal", format_price(grand_total))
        self.__replace_text("tax", format_price(tax))
        self.__replace_text("tax-percentage", f"Tax {int(self.tax_percentage * 100)}%")

    def brand_name(self):

        """Fills in brand name."""

        self.__replace_text("brand-name", self.issuer.name)

    def payment_info(self):

        """Updates payment information."""

        self.__replace_text("pay-to", f"Pay to: {self.issuer.name}")
        self.__replace_text("account", f"Account: {self.issuer.account_name}")
        self.__replace_text("bank", self.issuer.bank)
        self.__replace_text("email", self.issuer.email)
        self.__replace_text("phone", format_phone(self.issuer.phone))

    def billing_details(self):
        """Updates billing information."""

        self.__replace_text("company-name", self.client.name)
        self.__replace_text("address", self.client.address)
        self.__replace_text("location", self.client.location)

    def terms_and_conditions(self):

        """Updates terms and conditions."""

        self.__replace_text("terms-and-conditions", self.terms)

    def add_styling(self):

        """Adds the CSS styling inline in the invoice."""

        with open("resources/invoice.css") as file:
            style = f"<style>{file.read()}</style>"

        style_tag = BeautifulSoup(style, features='html.parser')

        self.invoice.find("html").append(style_tag)

    def fill_out(self):

        """Fills out the invoice in its entirety."""

        self.invoice_details()
        self.add_items()
        self.totals()
        self.brand_name()
        self.payment_info()
        self.billing_details()
        self.terms_and_conditions()
        self.add_styling()

        self.invoice.find("title").string.replace_with(f"Invoice {self._id}")

    def save(self, pdf=False):

        """Saves the template as an HTML file."""

        # Make output directory
        try:
            os.mkdir("output")
        except FileExistsError:
            pass

        with open(f"output/invoice_{self._id}.html", "w") as file:
            file.write(str(self.invoice))

        if pdf:
            self.__save_pdf()

    def __save_pdf(self):

        """Saves the template as a PDF file."""

        project_dir = os.getcwd() + "\\output\\"  # Requires absolute path for some reason

        try:
            pdfkit.from_file(f"{project_dir}invoice_{self._id}.html", f"{project_dir}/invoice_{self._id}.pdf")
        except OSError:  # For some reason this is always thrown, but PDF is successfully made anyway
            pass


# Functions
def format_price(price: float) -> str:

    """Returns price as a string formatted to two decimal places."""

    return f"{round(price, 2):.2f}"


def format_phone(phone: int) -> str:

    """Returns phone number as a string formatted with hyphens."""

    phone = str(phone)

    return f"{phone[:3]}-{phone[3:6]}-{phone[6:]}"
