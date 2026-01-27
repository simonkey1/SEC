"""Generar visualizaciones EDA para el Informe Técnico.

Este script utiliza la clase centralizada Plot para generar figuras de calidad de datos
y distribución de proyectos.
"""

from scripts.analysis.plot import Plot


def main():
    plotter = Plot()
    # Generar solo figuras EDA
    plotter.plot_eda_missing_values()
    plotter.plot_eda_projects_distribution()


if __name__ == "__main__":
    main()
