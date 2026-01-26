import os


def create_mega_view():
    reports_dir = "outputs/event_reports"
    files = [
        f
        for f in os.listdir(reports_dir)
        if f.endswith(".html") and f != "index.html" and f != "mega_view.html"
    ]

    # Ordenar por fecha (extraída del nombre de archivo YYYY-MM-DD...)
    files.sort(reverse=True)

    output_path = os.path.join(reports_dir, "mega_view.html")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("<html><head><title>Visualización Completa: 53 Eventos</title>")
        f.write("<style>")
        f.write(
            "body { background-color: #1a1a1a; color: white; font-family: sans-serif; padding: 20px; }"
        )
        f.write(
            ".grid-container { display: grid; grid-template-columns: repeat(auto-fill, minmax(600px, 1fr)); gap: 20px; }"
        )
        f.write(
            ".card { background: #2a2a2a; border-radius: 8px; overflow: hidden; border: 1px solid #444; height: 600px; }"
        )
        f.write("iframe { width: 100%; height: 100%; border: none; }")
        f.write("h1 { text-align: center; color: #00d4ff; }")
        f.write("</style></head><body>")

        f.write(f"<h1>⚡ Monitor de Desastres: {len(files)} Eventos Históricos</h1>")
        f.write("<div class='grid-container'>")

        for filename in files:
            # Clean title
            title = filename.replace(".html", "").replace("_", " ")
            f.write(f"<div class='card'>")
            # Lazy load iframes to prevent browser crash
            f.write(
                f"<iframe src='{filename}' loading='lazy' title='{title}'></iframe>"
            )
            f.write("</div>")

        f.write("</div></body></html>")

    print(f"✅ Mega Reporte generado en: {output_path}")


if __name__ == "__main__":
    create_mega_view()
