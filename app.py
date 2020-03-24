from typing import List, Dict

import dash
import dash_bootstrap_components as dbc
import pandas as pd
from dash.dependencies import ClientsideFunction, Input, Output, State

from model import get_doubling_time_ts_df, corona_country_data, corona_table_data
from view import (
    layout_parent,
    app_layout,
    line_graph,
    GRAY,
    GRAY_TRANSP,
    get_color,
    title_mapping,
)
from view.utils import registered_popovers


# this is the application/server
app = dash.Dash(
    __name__,
    meta_tags=[{"name": "viewport", "content": "width=device-width"}],
    external_stylesheets=[dbc.themes.LUX],
)
server = app.server
app.layout = app_layout

# Create callback for resizing the charts
app.clientside_callback(
    ClientsideFunction(namespace="clientside", function_name="resize"),
    Output("output-clientside", "children"),
    [Input("count_graph", "figure")],
)


@app.callback(
    Output("count_graph", "figure"),
    [
        Input("countries", "value"),
        Input("data_source", "value"),
        Input("line_graph_view", "value"),
        Input("line_graph_scaler", "value"),
        Input("date_slider", "value"),
        Input("count_graph", "hoverData"),
    ],
)
def update_time_series(
    countries: List[str],
    data_source: str,
    line_graph_view: str,
    line_graph_scaler: str,
    date_slider: int,
    hover_data: dict,
) -> Dict[str, List]:

    if line_graph_view == "trajectory":
        return update_trajectory_chart(
            countries, data_source, line_graph_scaler, date_slider, hover_data,
        )

    # special filtering for viewing "from n days setting"
    if line_graph_view in ["since_100", "since_10"]:
        df = get_doubling_time_ts_df(countries, line_graph_view, data_source)
        countries += list(filter(lambda x: "double" in x, df.index))
        x_vals = df.columns
    else:
        df = corona_country_data[data_source][line_graph_view].copy()
        x_vals = [x[:-3] for x in df.columns]

    # popualte the data output field
    data = []
    for country in countries:
        if country in df.index:
            data.append(
                dict(
                    type="scatter",
                    mode="lines",
                    name=country,
                    showlegend=True if "double" not in country else False,
                    y=df.loc[country],
                    x=x_vals,
                    line=dict(shape="spline", smoothing="2", color=get_color(country),),
                )
            )

    title = f"{title_mapping[data_source]} - {title_mapping[line_graph_view]}"
    layout_count = {
        **layout_parent,
        "title": title,
        "xaxis": {
            "title": "Development Time (days)",
            "showspikes": True,
            "spikethickness": 1,
        },
        "yaxis": {
            "title": f"Count - {title_mapping[line_graph_scaler]}",
            "type": line_graph_scaler,
            "showspikes": True,
            "spikethickness": 1,
        },
        "margin": {"l": 70, "b": 70, "r": 10, "t": 50},
    }

    return dict(data=data, layout=layout_count)


def update_trajectory_chart(
    countries: List[str],
    data_source: str,
    line_graph_scaler: str,
    date_slider: int,
    hover_data,
) -> Dict[str, List]:

    country_on_hover = None
    if hover_data:
        # divide by two because we are graphing two traces at at time (line and scatter)
        idx = hover_data["points"][0]["curveNumber"] // 2
        country_on_hover = countries[idx]

    # ts data to operate on
    df_cumulative = corona_country_data[data_source]["cumulative"]
    df_daily = corona_country_data[data_source]["daily_increase"]
    date = pd.to_datetime(df_cumulative.columns[date_slider])

    # popualte the time series data output field.
    # if the date and minimum number of cases is exceeded, then plot the scatter and line trace.
    data = []
    for country in countries:
        if country in df_cumulative.index:
            x = df_cumulative.loc[country]
            y = df_daily.loc[country]
            index = (pd.to_datetime(x.index) <= date) & (x > 50)
            trace_color = (
                get_color(country) if country == country_on_hover else GRAY_TRANSP
            )
            if True in list(index):
                data.append(
                    dict(
                        type="scatter",
                        mode="lines",
                        name=country,
                        y=y[index],
                        x=x[index],
                        customdata=country,
                        line=dict(shape="spline", smoothing="2", color=trace_color),
                        showlegend=False,
                    )
                )
                data.append(
                    dict(
                        type="scatter",
                        y=[y[index].iloc[-1]],
                        x=[x[index].iloc[-1]],
                        text=country,
                        name=country,
                        mode="markers+text",
                        textposition="top center",
                        showlegend=False,
                        marker={"size": 8, "color": get_color(country),},
                    ),
                )

    title = f"Trajectory of Covid {title_mapping[data_source]} {df_cumulative.columns[date_slider - 1]}"
    layout_count = {
        **layout_parent,
        "autosize": False,
        "title": title,
        "xaxis": {
            "title": "Total Count",
            "type": line_graph_scaler,
            "showspikes": True,
            "spikethickness": 1,
        },
        "yaxis": {
            "title": "Daily Increase",
            "type": line_graph_scaler,
            "showspikes": True,
            "spikethickness": 1,
        },
        "margin": {"l": 70, "b": 70, "r": 10, "t": 50},
    }

    return dict(data=data, layout=layout_count)


@app.callback(
    Output("scatter_plot", "figure"),
    [
        Input("countries", "value"),
        Input("scatter_x_data", "value"),
        Input("scatter_y_data", "value"),
        Input("scatter_x_scaler", "value"),
        Input("scatter_y_scaler", "value"),
        Input("min_cases_thresh", "value"),
        Input("show_labels", "value"),
    ],
)
def update_scatter_plot(
    countries: List[str],
    x_axis: str,
    y_axis: str,
    x_scaler: str,
    y_scaler: str,
    min_cases_thresh: str,
    show_labels: str,
):
    df = corona_table_data[corona_table_data["Total Cases"] > int(min_cases_thresh)]
    names = df["Country"] if show_labels else countries
    colors = list(
        map(lambda x: get_color(x) if x in countries else GRAY, df["Country"])
    )
    data = [
        dict(
            type="scatter",
            y=df[y_axis],
            x=df[x_axis],
            text=names,
            name=df["Country"],
            mode="markers+text",
            textposition="top center",
            showlegend=False,
            marker={
                "size": 8,
                "opacity": 1,
                "line": {"width": 0.5, "color": "white"},
                "color": colors,
            },
        )
    ]

    layout_scatter = {
        **layout_parent,
        "title": f"{y_axis} vs. {x_axis}",
        "xaxis": {
            "title": f"{x_axis} {title_mapping[x_scaler]}",
            "type": x_scaler,
            "showspikes": True,
            "spikethickness": 1,
        },
        "yaxis": {
            "title": f"{y_axis} {title_mapping[y_scaler]}",
            "type": y_scaler,
            "showspikes": True,
            "spikethickness": 1,
        },
        "margin": {"l": 70, "b": 70, "r": 10, "t": 50},
        "textposition": "top center",
    }
    return dict(data=data, layout=layout_scatter)


@app.callback(
    [Output("data_table", "selected_rows"), Output("data_table", "data")],
    [Input("countries", "value")],
)
def update_table_selection_from_country_dropdown(countries: List[str]):
    """Update the Data Table selection and sorting, based on the country dropdown."""

    # move selected countries to top of table
    df = corona_table_data.copy()
    df["new"] = list(range(1, len(df) + 1))
    df.loc[df[df.Country.isin(countries)].index, "new"] = 0
    df = df.sort_values(["new", "Total Cases"], ascending=[True, False])
    df = df.drop("new", axis=1)
    return [
        list(range(len(countries))),
        df.to_dict("records"),
    ]


@app.callback(
    dash.dependencies.Output("line_graph_view", "options"),
    [dash.dependencies.Input("data_source", "value")],
)
def hide_cases_since_dropdowns_if_case_fatalit_set(value: str):
    if value == "case_fatality":
        return line_graph.line_graph_view_options[:3]
    else:
        return line_graph.line_graph_view_options


@app.callback(
    dash.dependencies.Output("date_slider_div", "style"),
    [dash.dependencies.Input("line_graph_view", "value")],
)
def hide_date_slider_if_trajectory_not_set(value: str):
    if value == "trajectory":
        return {"display": "block"}
    else:
        return {"display": "none"}


# dynamically create callbacks for each about-info popover we created
def _toggle_popover(n, is_open):
    if n:
        return not is_open
    return is_open


for p in registered_popovers:
    app.callback(
        Output(f"popover-{p}", "is_open"),
        [Input(f"popover-target-{p}", "n_clicks")],
        [State(f"popover-{p}", "is_open")],
    )(_toggle_popover)

if __name__ == "__main__":
    app.run_server(debug=True, port=8001)
