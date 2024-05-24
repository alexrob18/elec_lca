# elec_lca

[![PyPI](https://img.shields.io/pypi/v/elec_lca.svg)][pypi status]
[![Status](https://img.shields.io/pypi/status/elec_lca.svg)][pypi status]
[![Python Version](https://img.shields.io/pypi/pyversions/elec_lca)][pypi status]
[![License](https://img.shields.io/pypi/l/elec_lca)][license]

[![Read the documentation at https://elec_lca.readthedocs.io/](https://img.shields.io/readthedocs/elec_lca/latest.svg?label=Read%20the%20Docs)][read the docs]
[![Tests](https://github.com/alexrob18/elec_lca/actions/workflows/python-test.yml/badge.svg)][tests]
[![Codecov](https://codecov.io/gh/alexrob18/elec_lca/branch/main/graph/badge.svg)][codecov]

[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)][pre-commit]
[![Black](https://img.shields.io/badge/code%20style-black-000000.svg)][black]

[pypi status]: https://pypi.org/project/elec_lca/
[read the docs]: https://elec_lca.readthedocs.io/
[tests]: https://github.com/alexrob18/elec_lca/actions?workflow=Tests
[codecov]: https://app.codecov.io/gh/alexrob18/elec_lca
[pre-commit]: https://github.com/pre-commit/pre-commit
[black]: https://github.com/psf/black

## Installation

You can install _elec_lca_ via [pip] from [PyPI]:

```console
$ pip install elec_lca
```

## Objective
To transform a whole background ecoinvent database (tested with v3.9.1 cutoff) through user-specified electricity market mix for a certain location, for user-defined scenario(s) and periods.

## Documentation
https://elec_lca.readthedocs.io/en/latest/

## Requirement
<li>Users need to provide their own background database, the ecoinvent database is not included in this package.</li>
<li>Required packages are given in <i>requirements.txt </i> Run the following commands to install the package: </li>

```
git clone https://github.com/alexrob18/elec_lca.git
cd elec_lca (or your local repo path)
pip install -r requirements.txt
``` 


## How to use it
The best way is to follow the example notebook in the example folder.

## Contributing

Contributions are very welcome.
To learn more, see the [Contributor Guide][Contributor Guide].

## License

Distributed under the terms of the [Apache 2.0 license][License],
_elec_lca_ is free and open source software.

## Issues

If you encounter any problems,
please [file an issue][Issue Tracker] along with a detailed description.


<!-- github-only -->

[command-line reference]: https://elec_lca.readthedocs.io/en/latest/usage.html
[License]: https://github.com/alexrob18/elec_lca/blob/main/LICENSE
[Contributor Guide]: https://github.com/alexrob18/elec_lca/blob/main/CONTRIBUTING.md
[Issue Tracker]: https://github.com/alexrob18/elec_lca/issues


## Building the Documentation

You can build the documentation locally by installing the documentation Conda environment:

```bash
conda env create -f docs/environment.yml
```

activating the environment

```bash
conda activate sphinx_elec_lca
```

and [running the build command](https://www.sphinx-doc.org/en/master/man/sphinx-build.html#sphinx-build):

```bash
sphinx-build docs _build/html --builder=html --jobs=auto --write-all; open _build/html/index.html
```