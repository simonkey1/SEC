"""Generar visualizaciones para el Informe Técnico.

Este script ahora utiliza la clase centralizada Plot para generar las figuras.
"""

from scripts.analysis.plot import Plot


def main():
    plotter = Plot()
    # Generar solo figuras técnicas
    plotter.plot_technical_volume()
    plotter.plot_technical_coverage()


if __name__ == "__main__":
    main()
