"""Interactive entry point for the GENOME event analysis.

Run from the project root:

    python app.py            # prints a note about the notebook UI

The ipywidgets interface is designed to run inside Jupyter/Colab. Import and
call `main()` from a notebook cell for the interactive experience, or use the
functions in the `genome` package directly in your own script.
"""

import io
import sys

import ipywidgets as widgets
from IPython.display import display, HTML, clear_output

from genome.api import scrape_api_data
from genome.processing import process_event_data
from genome.analysis import calculate_stats_and_ma, run_cointegration_test
from genome.viz import render_blue_html_window, plot_data


def main():
    """Build and display the interactive GENOME scraper/analysis UI."""
    # Force the dark-blue background and white text for the UI panel.
    display(HTML("""
    <style>
        .custom-bg {
            background-color: #081424 !important;
            padding: 20px;
            border-radius: 8px;
            border: 1px solid #1a365d;
        }
    </style>
    """))

    def create_input_row(label_text, widget):
        label = widgets.HTML(
            f"<span style='color:white; font-size:14px; "
            f"font-weight:bold;'>{label_text}</span>"
        )
        label.layout.width = "200px"
        return widgets.HBox([label, widget])

    title = widgets.HTML(
        "<h2 style='color: white; margin-top:0;'>GENOME Events API Scraper</h2>"
    )

    actor_widget = widgets.Text(placeholder="e.g. Poland,Germany")
    recipient_widget = widgets.Text(placeholder="single match, blank=any")
    dfrom_widget = widgets.Text(placeholder="YYYY-MM-DD")
    dto_widget = widgets.Text(placeholder="YYYY-MM-DD")

    btn_go = widgets.Button(description="GO", button_style="primary")
    btn_go.style.font_weight = "bold"

    ui = widgets.VBox([
        title,
        create_input_row("Actor country/countries:", actor_widget),
        create_input_row("Recipient country:", recipient_widget),
        create_input_row("Date from (Optional):", dfrom_widget),
        create_input_row("Date to (Optional):", dto_widget),
        widgets.HTML("<br>"),
        btn_go,
    ])
    ui.add_class("custom-bg")

    out = widgets.Output()

    def on_go_clicked(b):
        with out:
            clear_output(wait=True)

            # Parse inputs.
            actors_raw = actor_widget.value.strip()
            actor_countries = (
                [c.strip() for c in actors_raw.split(",")] if actors_raw else []
            )
            recip = recipient_widget.value.strip()
            dfrom = dfrom_widget.value.strip()
            dto = dto_widget.value.strip()

            # Capture printed pipeline output so it can be shown in the panel.
            captured_output = io.StringIO()
            original_stdout = sys.stdout
            sys.stdout = captured_output
            try:
                raw_df = scrape_api_data(actor_countries, recip, dfrom, dto)

                if raw_df is not None:
                    processed_df = process_event_data(raw_df)
                    if processed_df is not None:
                        final_df = calculate_stats_and_ma(
                            processed_df, actor_countries
                        )
                        run_cointegration_test(final_df, actor_countries)
                        results_text = captured_output.getvalue()
                    else:
                        results_text = captured_output.getvalue()
                        final_df = None
                else:
                    results_text = captured_output.getvalue()
                    final_df = None
            finally:
                # Always restore stdout, even if something raised.
                sys.stdout = original_stdout

            render_blue_html_window(results_text)
            if raw_df is not None and 'final_df' in dir() and final_df is not None:
                plot_data(final_df, actor_countries)
            elif raw_df is None:
                display(HTML(
                    "<p style='color:#ff6666; font-weight:bold;'>"
                    "No data was retrieved. Exiting analysis.</p>"
                ))

    btn_go.on_click(on_go_clicked)
    display(ui, out)


if __name__ == "__main__":
    print(
        "This project's UI is built with ipywidgets and is meant to run in a "
        "notebook.\nOpen notebooks/demo.ipynb (or any Jupyter/Colab cell) and "
        "run:\n\n    from app import main; main()\n"
    )
