# -*- coding: utf-8 -*-
"""
Run PyMERRY.

PyMERRY can be run either:

1. From Spyder:
   Edit PARAMETER_FILE below and run this script.

2. From a terminal:
   python run_pymerry.py <parameter_file>

Examples:
    python run_pymerry.py parameters.txt
    python run_pymerry.py parameters_with_topo.txt
"""


# =============================================================================
# IMPORTS
# =============================================================================

import argparse
import os
import warnings
import numpy as np
import pygimli as pg
from time import time
import tools.PyMERRY as PM
from datetime import timedelta
import matplotlib.pyplot as plt


warnings.filterwarnings("ignore")


# =============================================================================
# SPYDER CONFIGURATION
# =============================================================================
#
# When running the script from Spyder, edit the value below to select the
# desired parameter file.
#
# Example:
#     PARAMETER_FILE = "parameters.txt"
#
#     PARAMETER_FILE = "parameters_with_topo.txt"
#
# When a parameter file is provided through the terminal, it takes priority
# over this value.
# =============================================================================

PARAMETER_FILE = os.path.join("examples", "example_without_topography",
                              "parameters.txt")


# =============================================================================
# FUNCTIONS
# =============================================================================

def get_parameter_file():
    """
    Get the PyMERRY parameter file.

    When the script is run from Spyder without command-line arguments,
    PARAMETER_FILE is used.

    When the script is run from a terminal, a parameter file must be
    provided as a command-line argument.

    Returns
    -------
    str
        Path to the parameter file.
    """

    parser = argparse.ArgumentParser(
        description="Run PyMERRY using a parameter file."
    )

    parser.add_argument(
        "parameter_file",
        nargs="?",
        help="Path to the PyMERRY parameter file."
    )

    args = parser.parse_args()

    # -------------------------------------------------------------------------
    # Detect whether the script is running from Spyder
    # -------------------------------------------------------------------------

    running_in_spyder = "SPYDER_ARGS" in os.environ

    # -------------------------------------------------------------------------
    # Terminal execution
    # -------------------------------------------------------------------------

    if not running_in_spyder:

        if args.parameter_file is None:
            print("\nERROR: No parameter file was provided.")
            print("\nPyMERRY must be run from the terminal as:")
            print("    python run_pymerry.py <parameter_file>")
            print("\nExamples:")
            print("    python run_pymerry.py parameters.txt")
            print("    python run_pymerry.py parameters_with_topo.txt")
            print("\nUse --help for more information.\n")

            raise SystemExit(1)

        parameter_file_name = args.parameter_file

    # -------------------------------------------------------------------------
    # Spyder execution
    # -------------------------------------------------------------------------

    else:

        if args.parameter_file is not None:
            parameter_file_name = args.parameter_file
        else:
            parameter_file_name = PARAMETER_FILE

    # -------------------------------------------------------------------------
    # Check that the parameter file exists
    # -------------------------------------------------------------------------

    if not os.path.isfile(parameter_file_name):
        print(f"\nERROR: Parameter file not found:")
        print(f"    {parameter_file_name}\n")

        raise SystemExit(1)

    return parameter_file_name


# =============================================================================
# MAIN PROGRAM
# =============================================================================

if __name__ == "__main__":

    # Turn off the automatic figure display from PyGIMLi:
    pg.viewer.mpl.noShow(on=True)

    # =========================================================================
    # 1 - LOAD INPUT DATA FOR PyMERRY FROM PARAMETER FILE
    # =========================================================================

    parameter_file_name = get_parameter_file()

    print("\n" + "=" * 70)
    print("PyMERRY")
    print("=" * 70)
    print(f"Parameter file: {parameter_file_name}")
    print("=" * 70 + "\n")

    # =========================================================================
    # 2 - INSTANTIATE PyMERRY
    # =========================================================================

    # 2.1 - Initialize:
    inputs = PM.InputTools.load_parameters(parameter_file_name)

    data = inputs["data"]
    model = inputs["model"]
    mesh = inputs["mesh"]

    # 2.2 - Create saving directory:
    save_dir = PM.InputTools.normalize_path(inputs["save_dir"])
    os.makedirs(save_dir, exist_ok=True)

    PM.InputTools.save_parameters_file(inputs)

    # =========================================================================
    # 3 - RUN PyMERRY
    # =========================================================================

    to = time()

    # 3.1 - Set input data:
    pm = PM.MERRY(
        data=inputs["data"],
        model=inputs["model"],
        mesh=inputs["mesh"],
        DOI_DD=inputs["doi_DD"],
        DOI_W=inputs["doi_W"],
        DOI_WS=inputs["doi_WS"],
        alpha=inputs["alpha"],
        beta=inputs["beta"]
    )

    # 3.2 - Compute masks and coverage:
    pm.create_masks(verbose=True)

    # 3.3 - Compute errors
    # "__name__" is required for parallel runs:
    pm.error_assesment(__name__, verbose=True)

    tf = time()

    print(f"Total runtime {timedelta(seconds=tf - to)}\n")

    # =========================================================================
    # 4 - SAVE RESULTS AND PLOTS
    # =========================================================================

    # 4.1 - Display PyMERRY status in console:
    print(pm)

    # 4.2 - Save results as .csv files:
    pm.save("quadrupoles", path=save_dir)
    pm.save("u", path=save_dir)
    pm.save("j", path=save_dir)
    pm.save("frechet", path=save_dir)
    pm.save("masks", path=save_dir)
    pm.save("coverage", path=save_dir)
    pm.save("profile_mask", path=save_dir)
    pm.save("rhoa_th", path=save_dir)
    pm.save("error_absolute", path=save_dir)
    pm.save("error_relative", path=save_dir)
    pm.save("error_min", path=save_dir)

    np.savetxt(
        os.path.join(save_dir, "py_merry_run_time_s.txt"),
        np.array([tf - to]),
        delimiter=";"
    )

    # =========================================================================
    # 5 - FIGURES
    # =========================================================================

    # 5.1 - Coverage plot:
    fig1, ax1 = plt.subplots(figsize=(16, 9))

    pg.show(
        mesh,
        data=pm.coverage,
        ax=ax1,
        cMin=0,
        cMax=1,
        cMap="Greys",
        label="Coverage"
    )

    fig1.savefig(
        os.path.join(save_dir, "coverage.png"),
        bbox_inches="tight"
    )

    plt.close(fig1)

    # 5.2 - Error plot:
    #      low resistivity / model / high resistivity

    fig2, ax2 = plt.subplots(3, figsize=(16, 9))

    PM.Plots.plot_error_bars(
        pm.model_mask,
        pm.profile_mask,
        pm.error_absolute,
        pm.mesh,
        inputs["cmin"],
        inputs["cmax"],
        inputs["gamma"],
        inputs["logscale"],
        fig2,
        ax2[0],
        ax2[1],
        ax2[2]
    )

    fig2.savefig(
        os.path.join(save_dir, "errors.png"),
        bbox_inches="tight"
    )

    plt.close(fig2)

    # Turn on the automatic figure display from PyGIMLi:
    pg.viewer.mpl.noShow(on=False)

    print("\n" + "=" * 70)
    print("PyMERRY run completed successfully.")
    print(f"Results saved in: {save_dir}")
    print("=" * 70 + "\n")