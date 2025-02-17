"""
Upload a new version to Zenodo
"""

from __future__ import annotations

import json
import os
import shutil
import sys
from pathlib import Path
from typing import Annotated

import numpy as np
import pandas as pd
import typer
from dotenv import load_dotenv
from loguru import logger
from openscm_zenodo.zenodo import ZenodoInteractor

pd.set_option("display.max_rows", 100)


def main(  # noqa: PLR0913, PLR0915
    file_to_process: Annotated[
        Path, typer.Argument(help="Core variables definition file from which to start")
    ],
    publish: Annotated[
        bool,
        typer.Option(
            help=(
                "Should we publish the new Zenodo record? "
                "If we don't publish, "
                "you can check/tweak the deposition before hitting publish manually."
            )
        ),
    ] = False,
    metadata_file: Annotated[
        Path,
        typer.Option(help="File from which to load the metadata"),
    ] = Path("METADATA.json"),
    generated_dir: Annotated[
        Path,
        typer.Option(help="Directory in which to place the generated files"),
    ] = Path("generated"),
    sheet_to_read: Annotated[
        str,
        typer.Option(help="Sheet to read from `file_to_process`"),
    ] = "ScenarioMIP core variables NEW",
    verbose: Annotated[
        bool,
        typer.Option(help="Show information about the number of variables included"),
    ] = False,
    any_deposition_id: Annotated[
        int,
        typer.Option(
            help="Any deposition ID related to the Zenodo record you want to update"
        ),
    ] = 14870678,
    logging_level: Annotated[str, typer.Option(help="Logging level to use")] = "INFO",
) -> None:
    """
    Process a file and upload the processed files to Zenodo
    """
    logger.configure(handlers=[dict(sink=sys.stderr, level=logging_level)])
    logger.enable("openscm_zenodo")

    load_dotenv()

    if "ZENODO_TOKEN" not in os.environ:
        msg = (
            "Please copy the `.env.sample` file to `.env` "
            "and ensure you have set your ZENODO_TOKEN."
        )
        raise KeyError(msg)

    with open(metadata_file) as fh:
        metadata = json.load(fh)

    version = metadata["metadata"]["version"]
    version_filename = version.replace(".", "-")

    # Too lazy to split out functions, just use the comments
    # Set up the file names
    full_definition_file_name = (
        f"ScenarioMIP_coreVariables_full_{version_filename}.xlsx"
    )
    full_definition_file = generated_dir / full_definition_file_name
    core_variables_file = (
        generated_dir / f"ScenarioMIP_coreVariables_only-core_{version_filename}.csv"
    )
    readme_file = generated_dir / f"README_{version_filename}.md"
    files_to_upload = [full_definition_file, core_variables_file, readme_file]

    # Get just the core variables
    core_indicator_cols = ["land", "emissions", "energy", "cdr", "macro"]
    full_definition = pd.read_excel(
        file_to_process,
        sheet_name=sheet_to_read,
        dtype={c: str for c in core_indicator_cols},
    )
    is_core = np.full(full_definition.shape[0], False)
    for c in core_indicator_cols:
        is_core = is_core | ~full_definition[c].isnull()

    core_variables = full_definition[is_core]
    # Sort values before continuing
    core_variables = core_variables.sort_values(by="variable")

    if verbose:
        print(f"There are {full_definition.shape[0]} variables in total.")
        print(f"Of these, {core_variables.shape[0]} are core variables.")
        print()
        top_level_breakdown = (
            core_variables["variable"].apply(lambda x: x.split("|")[0]).value_counts()
        )
        print(f"Breakdown by top-level key:\n{top_level_breakdown}")
        print()
        second_level_breakdown = (
            core_variables["variable"]
            .apply(lambda x: "|".join(x.split("|")[:2]))
            .value_counts()
        )
        print(f"Breakdown by second-level key:\n{second_level_breakdown}")

    # Write the README
    with open(readme_file, "w") as fh:
        fh.write("# ScenarioMIP core variables\n")
        fh.write("\n")
        fh.write("There are two files here:\n")
        fh.write("\n")
        fh.write(
            f"1. `{full_definition_file.name}`: "
            "This contains all the defined variables\n"
        )
        fh.write(
            f"1. `{core_variables_file.name}`: This contains only the core variables\n"
        )
        fh.write("\n")
        fh.write(
            f"Start with `{core_variables_file.name}`, "
            "these are the key variables we need in submissions.\n"
        )
        fh.write(
            "Then, if you have time and energy, "
            f"move onto including the variables in `{full_definition_file.name}`.\n"
        )
        fh.write("\n")
        fh.write(
            f"In this version ({version}), "
            f"there are {full_definition.shape[0]} variables in the full set "
            f"and {core_variables.shape[0]} variables in the core set.\n"
        )

        fh.write(
            "The core variables are broken down "
            "in the following top-level categories:\n\n"
        )
        top_level_breakdown = (
            core_variables["variable"].apply(lambda x: x.split("|")[0]).value_counts()
        )
        top_level_breakdown.name = "Number of variables"
        top_level_breakdown.index.name = "Top-level element"
        for category, count in top_level_breakdown.to_dict().items():
            fh.write(f"1. {category}: {count}\n")

    # Write the full defintions with a name that includes version information
    full_definition_file.parent.mkdir(exist_ok=True, parents=True)
    shutil.copy2(file_to_process, full_definition_file)

    # Write the core variables (as CSV, so you get sensible previews)
    core_variables.to_csv(core_variables_file, index=False)

    # Do the upload to Zenodo
    zenodo_interactor = ZenodoInteractor(token=os.environ["ZENODO_TOKEN"])

    latest_deposition_id = zenodo_interactor.get_latest_deposition_id(
        any_deposition_id=any_deposition_id,
    )
    draft_deposition_id = zenodo_interactor.get_draft_deposition_id(
        latest_deposition_id=latest_deposition_id
    )

    zenodo_interactor.update_metadata(
        deposition_id=draft_deposition_id, metadata=metadata
    )

    # Remove the previous version's files from the new deposition
    zenodo_interactor.remove_all_files(deposition_id=draft_deposition_id)

    # Upload files
    bucket_url = zenodo_interactor.get_bucket_url(deposition_id=draft_deposition_id)
    for file in files_to_upload:
        zenodo_interactor.upload_file_to_bucket_url(
            file,
            bucket_url=bucket_url,
        )

    if publish:
        zenodo_interactor.publish(deposition_id=draft_deposition_id)
        print(
            f"Published the new record at https://zenodo.org/records/{draft_deposition_id}"
        )

    else:
        print(
            f"You can preview the draft upload at https://zenodo.org/uploads/{draft_deposition_id}"
        )


if __name__ == "__main__":
    typer.run(main)
