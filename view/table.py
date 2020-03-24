import dash_html_components as html
import dash_table

from model import corona_table_data

# the datatable
table_panel = html.Div(
    [
        html.Div(
            [
                dash_table.DataTable(
                    id="data_table",
                    columns=[{"name": i, "id": i} for i in corona_table_data.columns],
                    data=corona_table_data.to_dict("records"),
                    selected_rows=[],
                    page_size=500,
                    row_selectable="multi",
                    filter_action="native",
                    sort_action="native",
                    fixed_columns={"headers": True, "data": 1},
                    fixed_rows={"headers": True, "data": 0},
                    style_table={"overflowX": "scroll"},
                    style_cell={"fontSize": 12, "minWidth": "150px"},
                    style_data_conditional=[
                        {
                            "if": {"row_index": "odd"},
                            "backgroundColor": "rgb(248, 248, 248)",
                        },
                        {
                            "if": {"column_id": "New Cases"},
                            "backgroundColor": "#ffeeaa",
                            "color": "black",
                        },
                        {
                            "if": {"column_id": "New Deaths"},
                            "backgroundColor": "#ff0000",
                            "color": "white",
                        },
                    ],
                    style_header={"fontWeight": "bold"},
                )
            ],
            className="pretty_container twelve columns",
        ),
    ],
    className="row flex-display",
)
