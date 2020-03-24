import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html

# for info buttons, see fn create_popover below
registered_popovers = []


def create_popover(
    info_file: str, html_id: str, button_title: str = "About This Chart"
) -> html.Div:
    """Create a HTMl button which provides a popover giving information about the chart of its parent div.

    Registers the popover to a list which dynamically creates callbacks in the main application.

    Args:
         info_file: relative link to text file containing information about the popover in question.
         html_id: specification of the HTMl id to toggle in click of the button
         button_title: text to display on button

    Returns: a html.Div containing a list of the button and popover dash HTML Component Objects.
    """
    registered_popovers.append(html_id)
    return html.Div(
        [
            dbc.Button(
                button_title,
                id=f"popover-target-{html_id}",
                style={"fontSize": 14},
                outline=True,
            ),
            dbc.Popover(
                [
                    dbc.PopoverBody(
                        dcc.Markdown(open(info_file, "r").readlines()),
                        style={"fontSize": 14},
                    ),
                ],
                id=f"popover-{html_id}",
                is_open=False,
                target=f"popover-target-{html_id}",
                container="body",
                placement="right-start",
            ),
        ]
    )
