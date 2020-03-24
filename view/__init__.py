import hashlib
import logging

import dash_html_components as html

from .line_graph import line_graph_panel
from .scatter_plot import scatter_panel
from .table import table_panel
from .title import title_panel

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Gray hex color with and without transparency
GRAY = "#d9d9d9"
GRAY_TRANSP = GRAY + "80"

# enum for mapping variables to views
title_mapping = {
    "confirmed": "Confirmed Cases",
    "deaths": "Deaths",
    "recovered": "Recovered",
    "growth": "Growth Factor",
    "daily_increase": "Daily Increase",
    "cumulative": "Cumulative",
    "log": "Logarithmic",
    "linear": "Linear",
    "case_fatality": "Case Fatality Ratio",
    "since_100": "Growth Since 100 Cases",
    "since_10": "Growth Since 10 Cases",
}


layout_parent = dict(
    autosize=True,
    automargin=True,
    hovermode="closest",
    legend=dict(font=dict(size=10), orientation="v"),
)

app_layout = html.Div(
    [
        html.Div(
            id="output-clientside"
        ),  # empty Div to trigger javascript file for graph resizing
        title_panel,
        line_graph_panel,
        scatter_panel,
        table_panel,
    ],
    id="mainContainer",
    style={"display": "flex", "flex-direction": "column"},
)


def get_color(country: str) -> str:
    """Return a unique color hex code based on the country name."""
    if "double" in country:
        return GRAY

    def _get_unique_int_from_str(s):
        return int.from_bytes(hashlib.sha256(s.encode()).digest(), "big") % 255

    return "#%02X%02X%02X" % (
        _get_unique_int_from_str(country[0]),
        _get_unique_int_from_str(country[1]),
        _get_unique_int_from_str(country[2]) if len(country) > 2 else 128,
    )
