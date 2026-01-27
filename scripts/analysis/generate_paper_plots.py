"""Generar visualizaciones para el Research Paper.

Este script ahora utiliza la clase centralizada Plot para generar las figuras.
"""

from scripts.analysis.plot import Plot


def main():
    plotter = Plot()
    # Generar solo figuras del paper
    plotter.plot_fig1_global_timeseries()
    plotter.plot_fig2_heatmap()
    plotter.plot_fig3_coquimbo_paradox()
    plotter.plot_fig4_arica_redenor()
    plotter.plot_fig5_company_ranking()


if __name__ == "__main__":
    main()
