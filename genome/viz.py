"""Presentation helpers: styled HTML summary and moving-average plots."""

import matplotlib.pyplot as plt

try:
    from IPython.display import display, HTML
    _HAS_IPYTHON = True
except ImportError:  # allows the module to import outside a notebook
    _HAS_IPYTHON = False


def render_blue_html_window(captured_text):
    """Render captured pipeline text inside a styled dark-blue panel."""
    if not captured_text.strip():
        return
    if not _HAS_IPYTHON:
        print(captured_text)
        return

    html_window = f"""
    <div style="background-color: #0b1f38; color: #f0f0f0; padding: 20px;
                border-radius: 10px; font-family: 'Consolas', monospace;
                white-space: pre-wrap; max-height: 400px; overflow-y: auto;
                border: 2px solid #4a90e2; box-shadow: 0 4px 8px rgba(0,0,0,0.3);
                font-size: 14px; margin-top: 20px;">
        <h3 style="color: #66b2ff; margin-top: 0; border-bottom: 1px solid #66b2ff;
                   padding-bottom: 5px;">Analysis Results</h3>
    {captured_text}
    </div>
    """
    display(HTML(html_window))


def plot_data(df, actor_countries):
    """Plot the 7-day moving average of event weight for each actor."""
    plt.figure(figsize=(12, 6))
    plot_df = df.sort_values("event_date")

    for actor in actor_countries:
        col_name = f"ma_weight_{actor}"
        if col_name in plot_df.columns:
            country_df = plot_df.dropna(subset=[col_name])
            if not country_df.empty:
                plt.plot(
                    country_df["event_date"],
                    country_df[col_name],
                    label=actor,
                )

    plt.axhline(y=0, color="black", linestyle="--", linewidth=0.8, alpha=0.7)
    plt.title("7-Day Moving Average of Event Weight by Country")
    plt.xlabel("Event Date")
    plt.ylabel("Moving Average of Weight")
    plt.xticks(rotation=45)
    plt.legend(title="Country")
    plt.tight_layout()
    plt.show()
