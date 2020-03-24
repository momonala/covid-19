import dash_core_components as dcc
import dash_html_components as html

from model import corona_country_data, corona_table_data
from .utils import create_popover

# use a default number of countries on first page load
FIRST_N_COUNTRIES = 12

# extract out because we dont want to show "Development X" in case_fatality view
line_graph_view_options = [
    {"label": "Cumulative ", "value": "cumulative"},
    {"label": "Daily Increase  ", "value": "daily_increase"},
    {"label": "Trajectory ", "value": "trajectory"},
    {"label": "Development 100 ", "value": "since_100"},
    {"label": "Development 10 ", "value": "since_10"},
    # {"label": "Growth Factor  ", "value": "growth"},
]

# just an example of the data we expect, so we can build the controls around it
ts_df_example = corona_country_data["confirmed"]["cumulative"].copy()

# just the controls for the graph
_line_graph_control_panel = html.Div(
    [
        create_popover("assets/about_line.md", "line-graph"),
        html.P("Data Source:", className="control_label"),
        dcc.Dropdown(
            id="data_source",
            options=[
                {"label": "Confirmed Cases ", "value": "confirmed"},
                {"label": "Deaths  ", "value": "deaths"},
                {"label": "Recovered  ", "value": "recovered"},
                {"label": "Case Fatality Ratio ", "value": "case_fatality"},
            ],
            value="confirmed",
            multi=False,
            className="dcc_control",
        ),
        html.P("View:", className="control_label"),
        dcc.Dropdown(
            id="line_graph_view",
            options=line_graph_view_options,
            value="trajectory",
            multi=False,
            className="dcc_control",
        ),
        html.P("Scaling:", className="control_label"),
        dcc.RadioItems(
            id="line_graph_scaler",
            options=[
                {"label": "  Log  ", "value": "log"},
                {"label": "  Linear  ", "value": "linear"},
            ],
            value="log",
            labelStyle={"display": "inline-block"},
            className="dcc_control",
        ),
        html.P("Countries:", className="control_label"),
        dcc.Dropdown(
            id="countries",
            options=[{"label": c, "value": c} for c in ts_df_example.index],
            multi=True,
            value=list(corona_table_data["Country"].iloc[:FIRST_N_COUNTRIES]),
            className="dcc_control",
        ),
        # date slider wrapped in another div so we can hide it when trajectory not set
        html.Div(
            [
                html.P("Date:", id="current_date", className="control_label",),
                dcc.Slider(
                    id="date_slider",
                    min=0,
                    max=len(ts_df_example.columns) - 1,
                    step=1,
                    value=len(ts_df_example.columns) - 1,
                ),
            ],
            id="date_slider_div",
            style={"display": "none"},
        ),
    ],
    className="pretty_container three columns",
)


# just the graph
_line_graph_panel = html.Div(
    [
        html.Div(
            [
                dcc.Graph(
                    id="count_graph",
                    config={"editable": True, "displayModeBar": False},
                ),
            ],
            className="pretty_container",
        ),
    ],
    className="nine columns",
)

line_graph_panel = html.Div(
    [_line_graph_control_panel, _line_graph_panel], className="row flex-display",
)
