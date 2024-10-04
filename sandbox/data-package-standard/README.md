# Data Package Standard

[Data Package Standard Introduction | datapackage.org](https://datapackage.org/overview/introduction/)

The data package standard is a specification designed to simplify the sharing, validation, and use of data. It defines a consistent structure for organizing datasets, typically using metadata files (like datapackage.json) to describe the contents, formats, and sources of the data.

The data package standard makes datasets FAIR:

>**FAIR Data Exchange**  
>The Data Package standard facilitates findability, accessibility, interoperability, and reusability of data making it perfect for FAIR Data Exchange.

It's possible to describe relational database (RDB) schema with the Data Package Standard, which is what Bedrock uses the Data Package Standard for.

This can by done in 2 ways:

1. A single Data Package JSON with a Data Resource for each RDB table. The [`path` or `data`](https://datapackage.org/standard/data-resource/#path-or-data) properties of the Data Resource are then left empty, and the `schema` property then contains a Table Schema:
2. A Table Schema for each RDB table in a separate JSON. These JSON's then refer to each other to establish the relationships between the tables in the RDB.

Option 2. is probably better, because a data resource is supposed to contain data.

The Data Package, Data Resource, Table Schema hierarchy:

[Data Package](https://datapackage.org/standard/data-package/)  
└─[Data Resource](https://datapackage.org/standard/data-resource/)  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─[Table Schema](https://datapackage.org/standard/table-schema)

An example Data Package JSON with data originating from a relational database:
[Schleswig-Holstein outdoor swimming waters | opendata.schleswig-holstein.de/data/frictionless/badegewaesser.json](https://opendata.schleswig-holstein.de/data/frictionless/badegewaesser.json)

## Why I like the Data Package Standard

- Open
- Active community and backed by the [Open Knowledge Foundation](https://okfn.org/en/)
- JSON → much more readable than XML-based standards
- Ecosystem of [Open Source Software compatible with the Data Package Standard](https://datapackage.org/overview/software/)
  - [Open Data Editor](https://opendataeditor.okfn.org/): The Open Data Editor (ODE) is an open source tool for non-technical data practitioners to explore and detect errors in tables.
  - Python package: [`frictionless-py](https://framework.frictionlessdata.io/)
