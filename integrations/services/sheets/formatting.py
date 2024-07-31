def color_cell(value, color, type="stringValue", is_link=False):
    return (
        {
            "userEnteredValue": {type: value},
            "userEnteredFormat": {
                "backgroundColorStyle": {"rgbColor": color},
                "textFormat": {"link": {"uri": value}} if is_link else {},
            },
        },
    )


def title_cell(value: str):
    return (
        {
            "userEnteredValue": {"stringValue": value},
            "userEnteredFormat": {"textFormat": {"bold": True, "fontSize": 10}, "padding": {"right": 20}},
        },
    )


def wrap_row(row):
    return {"values": row}
