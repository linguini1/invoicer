# Invoicer
### Matteo Golin

## Usage
This software creates invoices from a set of input parameters. Invoices are created in an HTML template and then 
converted to PDF format.

### Batch Processing
CLI tool allows for batch invoice generation using the subcommand `batch`. It takes three positional arguments for the
CSV files containing client data, item data and the invoice combinations. The CSV files must follow a specified format
described below.

#### Clients CSV file
Will contain one column for the client name, one for their address and another for their location. Order does not 
matter.
```
name, address, location
John Doe, 1344 Example Street, "City, State/Province, Country"
...
```

#### Items CSV file
Will contain a column for the item name, price per unit and the item description. Order does not matter. Prices should be plain numbers in $. Do not include the $ sign.
```
name, description, price
Garden Gnome, "A very well-known, small, porcelain lawn ornament.", 12.99
...
```

#### Batches CSV file
The batches CSV file will contain as many rows as needed, where the first row is client name, second row is the invoice
due date in ISO date format, and the following rows contain items that will be charge on the invoice + their quantity.

Essentially, each column represents one invoice. Items and their quantities must be comma separated in a string format
(i.e. both values are in the same cell). Columns may vary in length.
```
John Doe, Jane Doe, ...
2022-01-01, 2023-09-16, ...
"Garden Gnome, 3", "USB stick, 16", ...
"Another item, 2", <this cell is empty>, ...
"A third item, 9", <this cell is empty>, ...
...
```

#### Issuer
The user will also be prompted to include issuer information via the commandline. Type `batch -h` to view all required
commands. The issuer is used for all invoices in the batch.

#### Terms and Agreements
The terms and agreements can be entered via commandline as a string or as a filepath to a text file. They will be used
on every invoice in the batch.

### Console Interface
You may choose to enter your data via inputs given to the console interface. To select this option, run the program with
commandline argument `-interface` or `-i`.

## Installation
Python 3.10.0 or later is required

- Beautiful Soup (bs4)
- pdfkit
- pdfkit's dependency wkhtmltopdf
- Pandas

## Module Usage
