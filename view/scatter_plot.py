import dash_core_components as dcc
import dash_html_components as html

from model import corona_table_data
from .utils import create_popover


# just the controls for the graph
_scatter_control_panel = html.Div(
    [
        create_popover("assets/about_scatter.md", "scatter"),
        html.P("x data:", className="control_label"),
        dcc.Dropdown(
            id="scatter_x_data",
            options=[{"label": c, "value": c} for c in corona_table_data.columns],
            multi=False,
            value="Total Cases",
            className="dcc_control",
        ),
        html.P("y data:", className="control_label"),
        dcc.Dropdown(
            id="scatter_y_data",
            options=[{"label": c, "value": c} for c in corona_table_data.columns],
            multi=False,
            value="Total Deaths",
            className="dcc_control",
        ),
        html.P("x scaling:", className="control_label"),
        dcc.RadioItems(
            id="scatter_x_scaler",
            options=[
                {"label": "  Log  ", "value": "log"},
                {"label": "  Linear  ", "value": "linear"},
            ],
            value="log",
            labelStyle={"display": "inline-block"},
            className="dcc_control",
        ),
        html.P("y scaling:", className="control_label"),
        dcc.RadioItems(
            id="scatter_y_scaler",
            options=[
                {"label": "  Log  ", "value": "log"},
                {"label": "  Linear  ", "value": "linear"},
            ],
            value="log",
            labelStyle={"display": "inline-block"},
            className="dcc_control",
        ),
        html.P("Min # Cases Threshold", className="control_label"),
        dcc.Dropdown(
            id="min_cases_thresh",
            options=[
                {"label": str(x), "value": x} for x in [0, 10, 100, 200, 500, 1000]
            ],
            multi=False,
            value="100",
            className="dcc_control",
        ),
        dcc.Checklist(
            id="show_labels",
            options=[{"label": " Show All Labels", "value": "all_labels"},],
            value=[],
        ),
    ],
    className="pretty_container three columns",
)

# just the graph
_scatter_graph_panel = html.Div(
    [
        html.Div(
            [
                dcc.Graph(
                    id="scatter_plot",
                    config={"editable": True, "displayModeBar": False},
                ),
            ],
            className="pretty_container",
        ),
    ],
    className="nine columns",
)

scatter_panel = html.Div(
    [_scatter_control_panel, _scatter_graph_panel], className="row flex-display",
)
