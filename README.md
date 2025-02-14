# ScenarioMIP core variables zenodo upload

A simple repo to get the ScenarioMIP core variable definitions onto zenodo.
This repo is unlikely to be needed for long
and is really just a chance to test out
[openscm-zenodo](https://github.com/openscm/openscm-zenodo).
<!---

We recommend having a status line in your repo to tell anyone who stumbles
on your repository where you're up to. Some suggested options:

- prototype: the project is just starting up and the code is all prototype
- development: the project is actively being worked on
- finished: the project has achieved what it wanted and is no longer being
  worked on, we won't reply to any issues
- dormant: the project is no longer worked on but we might come back to it, if
  you have questions, feel free to raise an issue
- abandoned: this project is no longer worked on and we won't reply to any
  issues

-->

## Status

- development: the project is actively being worked on

## Installation

### Setting up the virtual environment

We do all our environment management using [uv](https://docs.astral.sh/uv/).
To get started, you will need to make sure that uv is installed
([instructions here](https://docs.astral.sh/uv/getting-started/installation/),
we found that using uv's standalone installer was best on a Mac).

To create the virtual environment, run

```sh
uv install
uv run pre-commit install
```

These steps are also captured in the `Makefile` so if you want a single
command, you can instead simply run `make virtual-enviroment`.

### Joining the Zenodo record

We are working on this zenodo record.
To enable access to edit this record,
you will need to ask someone who already has access to give you access.
Once they have given you access,
you will be able to create a Zenodo token and use this repository to edit the records.

### Setting up your Zenodo token

Firstly, make sure you have copied `.env.sample` to `.env`.
You will also need to create a Zenodo token (if you don't have one already)
and put it into your `.env` file
(do not put it in `.env.sample`, this will leak your credentials to the world!).
For full details on creating zenodo tokens, see the instructions in `.env.sample`.

## Uploading a new version to Zenodo

Having done the installation/setup steps, you can now make uploads.
Step 1 is to update the version in `METADATA.json` to whatever version you would like to use next.
Then you can upload the data to Zenodo.

```sh
uv run python upload.py <file-to-process>
# For example
uv run python upload.py ScenarioMIP_coreVariables.xlsx
```

By default, this will just set up the deposition.
You can then go to Zenodo and press publish.
If you want to just publish directly, then add the `--publish` flag, i.e.

```sh
uv run python upload.py <file-to-process> --publish
```

## Development

Install and run instructions are the same as the above (this is a simple
repository, without tests etc. so there are no development-only dependencies).

### Contributing

This is a very thin repository.
There aren't any strict guidelines for contributing.
If you would like to contribute and don't know how, it is best to raise an issue
to discuss what you want to do (without a discussion, we can't guarantee that
any contribution can actually be used).

### Repository structure

The repository is very basic.
There is a single driver script, `upload.py`.
The metadata to associate with a deposit is by default loaded from `METADATA.json`.
Help for the upload script can be shown by running:

```sh
uv run python upload.py --help
```

### Tools

In this repository, we use the following tools:

- git for version-control (for more on version control, see
  [general principles: version control](https://gitlab.com/znicholls/mullet-rse/-/blob/main/book/theory/version-control.md))
    - for these purposes, git is a great version-control system so we don't
      complicate things any further. For an introduction to Git, see
      [this introduction from Software Carpentry](http://swcarpentry.github.io/git-novice/).
- [uv](https://docs.astral.sh/uv/) for environment management
  (for more on environment management, see
  [general principles: environment management](https://gitlab.com/znicholls/mullet-rse/-/blob/main/book/theory/environment-management.md))
    - there are lots of environment management systems.
      uv works well in our experience.
    - we track the `uv.lock` file so that the environment
      is completely reproducible on other machines or by other people
      (e.g. if you want a colleague to take a look at what you've done)
- [pre-commit](https://pre-commit.com/) with some very basic settings to get some
  easy wins in terms of maintenance, specifically:
    - code formatting with [ruff](https://docs.astral.sh/ruff/formatter/)
    - basic file checks (removing unneeded whitespace, not committing large
      files etc.)
    - (for more thoughts on the usefulness of pre-commit, see
      [general principles: automation](https://gitlab.com/znicholls/mullet-rse/-/blob/main/book/general-principles/automation.md)

## Original template

This project was generated from this template:
[basic python repository](https://gitlab.com/znicholls/copier-basic-python-repository).
[copier](https://copier.readthedocs.io/en/stable/) is used to manage and
distribute this template.
