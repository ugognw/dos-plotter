import argparse
import pathlib

from pymatgen.electronic_structure.plotter import DosPlotter
from pymatgen.io.vasp import Vasprun

from dos_plotter.__about__ import __version__


def create_plot(
    *,
    input_file: pathlib.Path,
    elements: list[str],
    orbitals: list[int]
    ) -> DosPlotter:
    vasprun = Vasprun(input_file, parse_dos=True)
    cdos = vasprun.complete_dos
    plot = DosPlotter()
    if elements:
        element_dos = cdos.get_element_dos()
        for element in elements:
            if orbitals:
                spd_dos_atom = cdos.get_element_spd_dos(element.capitalize())
                for orbital in orbitals:
                    plot.add_dos(spd_dos_atom[orbital])
            else:
                plot.add_dos(element_dos[element])
    elif orbitals:
            spd_dos_atom = cdos.get_element_spd_dos(element.capitalize())
            for orbital in orbitals:
                plot.add_dos(spd_dos_atom[orbital])
    else:
        tdos = vasprun.tdos
        plot.add_dos("Total DOS", tdos)
    return plot


def _create_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="dos-plotter",
        description="""
Create a Density of States plot from a VASP calculation
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples
--------

# Basic
dos-plotter --element Co --orbital d --total --input-file vasprun.xml --output-file co-dos.svg
""",
    )
    parser.add_argument(
        "-e",
        "--element",
        default=[],
        dest="elements",
        metavar="ELEMENTS",
        action="append",
        help="Include the density of states from the given elements. "
        "This flag may be repeated multiple times. If not included, "
        "The DOS from all elements will be included.",
    )
    parser.add_argument(
        "--orbital",
        default=[],
        dest="orbitals",
        metavar="ORBITALS",
        action="append",
        help="Include the density of states from the given orbitals "
        "specified by azimuthal quantum number (e.g., 0 = s, 1 = p, "
        "2 = d, 3 = f). This flag may be repeated multiple times. If "
        "not included, the DOS from all orbitals will be included.",
    )
    parser.add_argument(
        "-t",
        "--total",
        default=False,
        action="store_const",
        const=True,
        help="""
        Whether to plot the total DOS alongside all other selected DOS.
        """,
    )
    parser.add_argument(
        "--input-file",
        default=pathlib.Path("vasprun.xml"),
        type=pathlib.Path,
        help="""
        The path to the 'vasprun.xml' file from the calculation".
        """,
    )
    parser.add_argument(
        "--output-file",
        default="dos.png",
        help="""
        The output file for the DOS figure. The file type will be inferred "
        from the extension. If no extension is provided, the figure will be 
        saved as a .png.
        """,
    )
    parser.add_argument(
        "-V",
        "--version",
        default=False,
        action="store_const",
        const=True,
        help="Print the version.",
    )
    return parser


def save_plot(plot: DosPlotter,
              savename: str,
              xlim: list[float],
              ylim: list[float]):
    img_format = savename.split(".")[-1] if savename.index(".") >= 0 else "png"
    plot.save_plot(savename, img_format=img_format, xlim=xlim, ylim=ylim)


def main():
    parser = _create_argument_parser()
    args = parser.parse_args()
    if args.version:
        print(f"dos-plotter {__version__}")  # noqa: T201
        return

    plot = create_plot(input_file=args.input_file,
                       elements=args.elements,
                       orbitals=args.orbitals)
    save_plot(plot=plot,
              savename=args.output_file,
              xlim=args.xlim,
              ylim=args.ylim)
