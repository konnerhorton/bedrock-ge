<p align="center">
  <img src="https://bedrock.engineer/public/Bedrock_TextRight.png" alt="Bedrock logo" width="75%"/>
</p>

<h3 align="center">Bedrock, the Open Source Foundation for Geotechnical Engineering</h3>

---

📃 **Documentation:** <https://bedrock.engineer/docs>

🖥️ **Source Code:** <https://github.com/bedrock-engineer/bedrock-ge>

🐍 **`bedrock-ge` on PyPI:** <https://pypi.org/project/bedrock-ge/>

🌐 **Website:** <https://bedrock.engineer/>

🔗 **LinkedIn:** <https://www.linkedin.com/company/bedrock-engineer>

---

## 🌟 Highlights

### 📖 Read / write Ground Investigation (GI) data in different formats

| Data Format | Read | Write |
|-------------|------|-------|
| AGS 3       | ✅  | ❌    |
| AGS 4       | Soon | [python-ags4](https://pypi.org/project/python-AGS4/) |
| Excel       | ✅  | ✅    |
| CSV         | ✅  | ✅    |
| JSON        | ✅  | ✅    |
| GeoJSON     | ✅  | ✅    |

What do you need? [DIGGS](https://diggsml.org/)? [NADAG](https://www.ngu.no/geologisk-kartlegging/om-nadag-nasjonal-database-grunnundersokelser)? [GEF](https://publicwiki.deltares.nl/display/STREAM/Dutch+National+GEF+Standards)?  Something else?  
Let us know by creating an [issue](https://github.com/bedrock-engineer/bedrock-ge/issues) or starting a [discussion](https://github.com/orgs/bedrock-engineer/discussions) 💭

Also, if you have a project with publicly available GI data, please share that in a [discussion](https://github.com/orgs/bedrock-engineer/discussions), such that we can create a tutorial from it 🤩

### ✅ Validate your GI data

`bedrock-ge` comes with data validation to make sure that you can combine Ground Investigation data from multiple files into a single GIS database with consistent relationships between GI locations, samples, in-situ measurements and lab tests.

This data validation mechanism (based on [`pandera`](https://pandera.readthedocs.io/en/stable/)) is easily extensible, giving you the power to add your own data validation criteria 💪

### 🗺️ Put your GI data from multiple files into a single 3D GIS database

For example, you can take GI data from 100 AGS files and combine them into a single a [GeoPackage](https://en.wikipedia.org/wiki/GeoPackage) ([like a Shapefile, but then waaay better](http://switchfromshapefile.org/)). Such a GeoPackage can then be loaded into ArcGIS, such that you can visualize your GI data in 3D:

<p align="center">
  <img src="https://bedrock.engineer/public/images/KaiTak_BrGI_ArcGIS.gif" alt="GI data visualization .gif in 3D in ArcGIS" width="90%"/>
</p>

### 🟦 Put your GI data into Speckle

Once you have your GI data inside [Speckle](https://speckle.systems/), it's super easy to visualize GI data together with civil engineering designs:

<p align="center">
  <img src="https://bedrock.engineer/public/images/KaiTak_BrGI_Speckle.png" alt="Kai Tak, Hong Kong, data from many sources." width="56%" />
  <img src="https://bedrock.engineer/public/images/BPFoundation.png" alt="Bored Pile foundation design." width="40%" />
  <a href="https://app.speckle.systems/projects/013aaf06e7/models/0fa0287ba8@dfbec71408,1cbe68ed69@d3c4a34cff,44c8d1ecae@b962e2f29d,7f9d99cae2@bbed7cf165,9535541c2b@fafe06f9c0,a739490298@e858cc8cb3,ff81bfa02b@dda7c2f981" target="_blank">Click here to go to the Kai Tak Speckle project from the left image</a>
</p>

Moreover, your GI data becomes available in all the software that [Speckle has connectors for](https://app.speckle.systems/downloads).

### 🔓 Free and Open Source Software

Free and Open Source Software (FOSS) gives you full access to the code, which means you can customize `bedrock-ge` to integrate with other tools and fit your workflows & project needs.

As the name implies, FOSS is free to use, so you're not tied to expensive software licenses or locked into a specific software vendor ⛓️‍💥

You can give [feedback](#-feedback) and [contribute](#-contributing), such that together we together can build the tools we've always wanted and needed 🤝

## ℹ️ Overview

> **Definition of Bedrock**
>
> In an abstract sense, the main principles on which something is based. [1]
>
> In the real world, the bedrock is the hard area of rock in the ground that holds up the loose soil above. [1]
>
> In many civil engineering projects, the identification of the bedrock through digging, drilling or geophysical methods is an important task, which greatly influences (foundation) design. [2]  
>
> Sources: [[1] Bedrock | Cambridge Dictionary](https://dictionary.cambridge.org/us/dictionary/english/bedrock), [[2] Bedrock | Wikipedia](https://en.wikipedia.org/wiki/Bedrock)

Bedrock, this open source software project, forms the foundation for for ground investigation data, subsurface modelling and Geo-BIM.

With Bedrock you can get your data from any Ground Investigation data format into a GIS database 🗺️, from a GIS database into Speckle 🟦, and from Speckle into all the software we work with in the AEC industry 🏗️.

The purpose of Bedrock is NOT to become THE standard for geotechnical data, because we don't need 15 instead of 14 competing standards:

<p align="center">
  <img src="https://bedrock.engineer/public/images/14Become15Standards.png" alt="14 competing standards become 15 competing standards | xkcd.com/927" width="60%"/>
  <br>
  Source: <a href="https://xkcd.com/927/" target="_blank">https://xkcd.com/927</a>
</p>  

For example, us geotechnical engineers who are used to working with AGS data know that the "ISPT group" is a table that describes an In-Situ Standard Penetration Test and we know what headings, i.e. columns that AGS group, i.e. table has. Therefore, Bedrock doesn't change that the naming of those columns. Bedrock just makes sure that the data is structured in a sensible way, such that Ground Investigation data from multiple sources can be converted into a GIS database.

A GIS database with Ground Investigation data contains tables that describe the Ground Investigation `'Project'`, the `'Location'`s where GI data was collected, the `'Sample'`s and `'InSitu'` measurements taken at these `'Location'`s, and the `'Lab'` tests that were performed on the collected `'Sample'`s.

The `'Project'`, `'Location'`, `'Sample'`, `'InSitu'` measurement and `'Lab'` test tables are related to each other: each lab test belongs to a sample, which belongs to a GI location, which belongs to a project. These relationships can be visualized in a hierarchy like this:

```bash
'Project'
 └───'Location'
     ├───'InSitu'
     └───'Sample'
          └───'Lab'
```

These relationships are represented in the database tables with so-called "foreign keys". For example, the results of an Atterberg Limits Lab test, i.e. Liquid Limit and Plastic Limit tests, that originated from an AGS file would be in stored in the `'Lab_LLPL'` table. Each row in this table represents the Atterberg Limit test results performed on a specific sample. Each row knows to which project, GI location and sample it belongs through its `project_uid`, `location_uid` and `sample_uid` respectively.

This relational database ([linked tables](https://en.wikipedia.org/wiki/Relational_database)) with Ground Investigation data becomes a GIS database by assigning a (3D) GIS geometry to each of the rows in each of the database tables (except for the `'Project'` table).

## ⬇️ Installation

In case you're using `uv`, you can add `bedrock-ge` to your Python project and install it in your project's virtual environment by running:

```bash
uv add bedrock-ge
```

I would highly recommend anyone to start using [`uv`](https://docs.astral.sh/uv/) (Unified Virtual Environment Manager) if you're not already doing so. Some of the advantages (Source: [`uv`](https://docs.astral.sh/uv/)):

- 🖥️ `uv` Python projects will work on Windows, macOS and Linux.
- 🐍 `uv` [installs and manages](https://docs.astral.sh/uv/#python-management) Python versions.
- 🗂️ `uv` provides [comprehensive project management](https://docs.astral.sh/uv/#project-management), with a [universal lockfile](https://docs.astral.sh/uv/concepts/projects/#project-lockfile). This means no more headaches about virtual environments (or having to explain what on earth a virtual env is), or people running different versions of Python or Python packages on the same project, causing errors and other problems.
- In short, 🚀 `uv` is a single tool to replace `pip`, `pip-tools`, `pipx`, `poetry`, `pyenv`, `virtualenv`, `conda` and more...

It's of course also possible to install `bedrock-ge` from [PyPI](https://pypi.org/project/bedrock-ge/) (Python Packaging Index) using `pip`:

```bash
pip install bedrock-ge
```

## 💭 Feedback

Got some feedback, a great idea, running into problems when working with Bedrock or just want to ask some questions?

Please feel free to:

1. open an issue for feature requests or bug reports: [`bedrock-ge` issues](https://github.com/bedrock-engineer/bedrock-ge/issues),
2. start a discussion in this GitHub repo: [Bedrock discussions](https://github.com/orgs/bedrock-engineer/discussions),
3. or start a discussion on the Speckle community forum if that's more appropriate: [Speckle community forum](https://speckle.community/)

All feedback and engagement with the Bedrock community is welcome 🤗

## 👷 Contributing

🛑 Wait, please read this too!

Contributing isn't scary 😄

Contributing isn't just about writing code:

- Use Bedrock and provide [feedback](#-feedback) 🪲
- Share how you use Bedrock 🏗️
- Help each other out, e.g. by replying to questions in the [discussions](https://github.com/orgs/bedrock-engineer/discussions) or [`bedrock-ge` issues](https://github.com/bedrock-engineer/bedrock-ge/issues) 🤝
- Spread the word about Bedrock 🤩
- Documentation and tutorials 📃
- Most pages on the [bedrock.engineer](https://bedrock.engineer/) website can be edited, so if you see a spelling mistake or have a suggestion on how to explain something better, please smash that button! 🖱️💥
  
<p align="center">
  <img src="https://bedrock.engineer/public/images/EditThisPage.png" alt="Edit this page on GitHub button on bedrock.engineer" width="20%"/>
</p>

- If you would like to contribute code, AWESOME! 💖  
  Please create an issue for what you'd like to contribute. If you don't know how to get started, please indicate this in your issue, and we'll help you out.

## 🤔 Things to Consider

### GIS Data, Projected vs Geodetic CRS's and Heights / Elevations

Ground investigation data is initially measured in Easting, Northing, z-coordinate, i.e. in a projected Coordinate Reference System (CRS).

If you want your ground investigation data to go into a GIS database, all GIS geometry needs to use the same CRS.

Therefore, if you are dealing with GI data collected using different projected CRS's, you'll have to convert the Easting, Northing, z-coordinates to global longitude, latitude, ellipsoidal height coordinates in a geodetic CRS. ([Further reading](https://clover-animantarx-a3a.notion.site/Geomatics-36dfece2dece4358b44c44d08c9cded6))

Please start a [discussion](https://github.com/orgs/bedrock-engineer/discussions) or create an issue if want to be able to put data that were collected in different projected CRS's into a single GIS database. This is pretty easy with [`geopandas`](https://geopandas.org/en/stable/) / [`pyproj`](https://pyproj4.github.io/pyproj/stable/) transformations, but hasn't been necessary yet.

## ✍️ Author

Hi, I'm Joost Gevaert 👋

I studied geotechnical engineering and applied geophysics and then worked for [Arup](https://www.arup.com/) for 4 years as a geotechnical engineer and computational designer.

During my time at Arup I worked a lot on bringing computational design into the world of geotechnical engineering, and on [bridging the gaps between geotechnical engineering and structural engineering](https://www.linkedin.com/posts/joost-gevaert_lightbim-lightbim-lightbim-activity-7234726439835549697-3xdO).

Bedrock is the Free and Open Source Software (FOSS) that I wish existed when I worked as a geotechnical engineer at Arup.

> Computational design is a field that involves the use of computer algorithms, simulations, and data analysis to support and enhance the design process. It enables designers to explore vast design spaces, to find solutions to complex design problems, and to make informed decisions based on data-driven insights.  
> Source: [Computational design | Arup](https://www.arup.com/services/computational-and-parametric-design/)
