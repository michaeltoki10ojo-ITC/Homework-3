import os
import webbrowser

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots


# =========================================================
# 1. FILE + TAX INFORMATION
# =========================================================

DATA_FILE = "taxData2021.txt"

tax_names = {
    "T10": "Alcoholic Beverages Sales Tax",
    "T12": "Insurance Premiums Sales Tax",
    "T13": "Motor Fuels Sales Tax",
    "T16": "Tobacco Products Sales Tax",
    "T19": "Other Selective Sales and Gross Receipts Taxes",
    "T23": "Hunting and Fishing License",
    "T24": "Motor Vehicles License",
    "T28": "Occupation and Businesses License, NEC",
}

left_codes = ["T10", "T12", "T13", "T16"]
right_codes = ["T19", "T23", "T24", "T28"]


# =========================================================
# 2. LOAD DATA
# =========================================================

df = pd.read_csv(
    DATA_FILE,
    sep="\t",
    dtype=str
)

# Use state columns only.
# "US" is a national total, not a state.
state_columns = [
    column
    for column in df.columns
    if column not in ["item", "US"]
]


# =========================================================
# 3. GET AND CLEAN ONE TAX ROW
# =========================================================

def get_tax_data(code):
    matching_row = df[df["item"] == code]

    if matching_row.empty:
        raise ValueError(
            f"Tax code {code} was not found in {DATA_FILE}."
        )

    row = matching_row.iloc[0]

    available_values = []

    # Collect valid values first.
    for state in state_columns:
        value = row[state]

        if value != "X":
            available_values.append(float(value))

    if not available_values:
        raise ValueError(
            f"{code} has no usable state values."
        )

    # Homework instructions say missing values can be
    # replaced with the average for that tax row.
    row_average = (
        sum(available_values) /
        len(available_values)
    )

    locations = []
    values = []
    missing_states = []

    for state in state_columns:
        value = row[state]

        locations.append(state)

        if value == "X":
            values.append(row_average)
            missing_states.append(state)
        else:
            values.append(float(value))

    return {
        "locations": locations,
        "values": values,
        "average": row_average,
        "missing_states": missing_states,
    }


# =========================================================
# 4. PRELOAD ALL 8 TAX VIEWS
# =========================================================

tax_data = {}

for code in left_codes + right_codes:
    tax_data[code] = get_tax_data(code)


# =========================================================
# 5. PRINT DATA CHECK
# =========================================================

print()
print("DATA CHECK")
print("-" * 65)

for code in left_codes + right_codes:
    missing = tax_data[code]["missing_states"]

    if missing:
        print(
            f"{code}: replaced X for "
            f"{', '.join(missing)} "
            f"with row average "
            f"{tax_data[code]['average']:,.2f}"
        )
    else:
        print(
            f"{code}: no missing state values"
        )

print("-" * 65)


# =========================================================
# 6. CREATE TWO SIDE-BY-SIDE MAPS
# =========================================================

fig = make_subplots(
    rows=1,
    cols=2,

    specs=[
        [
            {"type": "choropleth"},
            {"type": "choropleth"},
        ]
    ],

    column_widths=[0.5, 0.5],

    # Equal spacing between maps.
    horizontal_spacing=0.10,
)


# =========================================================
# 7. INITIAL LEFT MAP
# =========================================================

initial_left = left_codes[0]

fig.add_trace(
    go.Choropleth(
        locations=tax_data[initial_left]["locations"],
        z=tax_data[initial_left]["values"],

        locationmode="USA-states",

        colorscale="Viridis",

        showscale=True,

        colorbar=dict(
            title=dict(
                text="Tax Value",
                side="top"
            ),

            # Just outside left map.
            x=0.465,

            # Vertically centered.
            y=0.50,

            len=0.53,
            thickness=18,

            xanchor="left",
            yanchor="middle",
        ),

        marker_line_color="white",
        marker_line_width=0.6,

        hovertemplate=(
            "<b>%{location}</b><br>"
            + tax_names[initial_left]
            + "<br>"
            + "Value: %{z:,.0f}"
            + "<extra></extra>"
        ),

        name=initial_left,
    ),

    row=1,
    col=1,
)


# =========================================================
# 8. INITIAL RIGHT MAP
# =========================================================

initial_right = right_codes[0]

fig.add_trace(
    go.Choropleth(
        locations=tax_data[initial_right]["locations"],
        z=tax_data[initial_right]["values"],

        locationmode="USA-states",

        colorscale="Viridis",

        showscale=True,

        colorbar=dict(
            title=dict(
                text="Tax Value",
                side="top"
            ),

            # Just outside right map.
            x=0.985,

            y=0.50,

            len=0.53,
            thickness=18,

            xanchor="left",
            yanchor="middle",
        ),

        marker_line_color="white",
        marker_line_width=0.6,

        hovertemplate=(
            "<b>%{location}</b><br>"
            + tax_names[initial_right]
            + "<br>"
            + "Value: %{z:,.0f}"
            + "<extra></extra>"
        ),

        name=initial_right,
    ),

    row=1,
    col=2,
)


# =========================================================
# 9. LEFT MAP BUTTONS
# =========================================================

left_buttons = []

for code in left_codes:

    new_hover = (
        "<b>%{location}</b><br>"
        + tax_names[code]
        + "<br>"
        + "Value: %{z:,.0f}"
        + "<extra></extra>"
    )

    left_buttons.append(
        dict(
            label=code,

            method="update",

            args=[
                {
                    "z": [
                        tax_data[code]["values"]
                    ],

                    "hovertemplate": [
                        new_hover
                    ],

                    "name": [
                        code
                    ],
                },

                {
                    "annotations[0].text":
                        (
                            f"<b>"
                            f"{tax_names[code]} "
                            f"({code})"
                            f"</b>"
                        )
                },

                # Update LEFT trace only.
                [0],
            ],
        )
    )


# =========================================================
# 10. RIGHT MAP BUTTONS
# =========================================================

right_buttons = []

for code in right_codes:

    new_hover = (
        "<b>%{location}</b><br>"
        + tax_names[code]
        + "<br>"
        + "Value: %{z:,.0f}"
        + "<extra></extra>"
    )

    right_buttons.append(
        dict(
            label=code,

            method="update",

            args=[
                {
                    "z": [
                        tax_data[code]["values"]
                    ],

                    "hovertemplate": [
                        new_hover
                    ],

                    "name": [
                        code
                    ],
                },

                {
                    "annotations[1].text":
                        (
                            f"<b>"
                            f"{tax_names[code]} "
                            f"({code})"
                            f"</b>"
                        )
                },

                # Update RIGHT trace only.
                [1],
            ],
        )
    )


# =========================================================
# 11. MAP STYLE
# =========================================================

fig.update_geos(
    scope="usa",

    showlakes=True,
    lakecolor="white",

    showland=True,

    bgcolor="rgba(0,0,0,0)",
)


# =========================================================
# 12. FORCE SYMMETRICAL MAP DOMAINS
# =========================================================
#
# Left map:
# 0.03 to 0.43
#
# Right map:
# 0.57 to 0.97
#
# These are mirror images around x = 0.50.
# =========================================================

fig.update_geos(
    domain_x=[0.03, 0.43],
    domain_y=[0.10, 0.87],

    row=1,
    col=1,
)

fig.update_geos(
    domain_x=[0.57, 0.97],
    domain_y=[0.10, 0.87],

    row=1,
    col=2,
)


# =========================================================
# 13. PAGE LAYOUT
# =========================================================

fig.update_layout(

    # Let browser determine width.
    autosize=True,

    height=720,

    title=dict(
        text=(
            "<b>"
            "2021 State Tax Choropleth Maps"
            "</b>"
        ),

        # Exact center of figure.
        x=0.50,

        y=0.98,

        xanchor="center",
        yanchor="top",

        font=dict(
            size=27,
            color="#203864",
        ),
    ),

    margin=dict(
        l=20,
        r=35,
        t=170,
        b=25,
    ),

    paper_bgcolor="white",
    plot_bgcolor="white",

    font=dict(
        family="Arial",
        color="#203864",
    ),

    # =====================================================
    # MAP TITLES
    # =====================================================

    annotations=[

        # LEFT MAP TITLE
        dict(
            text=(
                f"<b>"
                f"{tax_names[initial_left]} "
                f"({initial_left})"
                f"</b>"
            ),

            # Exact center of left half.
            x=0.23,

            y=1.01,

            xref="paper",
            yref="paper",

            xanchor="center",
            yanchor="bottom",

            showarrow=False,

            font=dict(
                size=16,
                color="#203864",
            ),
        ),

        # RIGHT MAP TITLE
        dict(
            text=(
                f"<b>"
                f"{tax_names[initial_right]} "
                f"({initial_right})"
                f"</b>"
            ),

            # Exact center of right half.
            x=0.77,

            y=1.01,

            xref="paper",
            yref="paper",

            xanchor="center",
            yanchor="bottom",

            showarrow=False,

            font=dict(
                size=16,
                color="#203864",
            ),
        ),
    ],


    # =====================================================
    # BUTTON GROUPS
    # =====================================================

    updatemenus=[

        # LEFT BUTTON GROUP
        dict(
            type="buttons",

            direction="right",

            buttons=left_buttons,

            # Center buttons over left map.
            x=0.23,
            y=1.13,

            xanchor="center",
            yanchor="middle",

            showactive=True,
            active=0,

            bgcolor="white",
            bordercolor="#808080",
            borderwidth=1,

            font=dict(
                size=13,
                color="#203864",
            ),

            pad=dict(
                r=2,
                t=2,
                l=2,
                b=2,
            ),
        ),

        # RIGHT BUTTON GROUP
        dict(
            type="buttons",

            direction="right",

            buttons=right_buttons,

            # Center buttons over right map.
            x=0.77,
            y=1.13,

            xanchor="center",
            yanchor="middle",

            showactive=True,
            active=0,

            bgcolor="white",
            bordercolor="#808080",
            borderwidth=1,

            font=dict(
                size=13,
                color="#203864",
            ),

            pad=dict(
                r=2,
                t=2,
                l=2,
                b=2,
            ),
        ),
    ],
)


# =========================================================
# 14. BUILD RESPONSIVE HTML
# =========================================================

OUTPUT_FILE = "homework3_choropleth.html"

plot_html = fig.to_html(
    full_html=False,

    include_plotlyjs=True,

    config={
        "responsive": True,
        "displaylogo": False,
    },

    # Makes Plotly fill the centered container.
    default_width="100%",
    default_height="720px",
)


# =========================================================
# 15. CENTER THE WHOLE VISUALIZATION IN HTML
# =========================================================

full_html = f"""
<!DOCTYPE html>

<html>

<head>

    <meta charset="UTF-8">

    <meta
        name="viewport"
        content="width=device-width, initial-scale=1.0"
    >

    <title>
        2021 State Tax Choropleth Maps
    </title>

    <style>

        * {{
            box-sizing: border-box;
        }}

        html {{
            width: 100%;
            margin: 0;
            padding: 0;
        }}

        body {{
            width: 100%;
            margin: 0;
            padding: 0;
            background: white;
            font-family: Arial, sans-serif;
        }}

        .page-wrapper {{
            width: 100%;
            display: flex;
            justify-content: center;
            align-items: flex-start;
        }}

        .chart-wrapper {{
            width: 96%;
            max-width: 1500px;
            margin-left: auto;
            margin-right: auto;
        }}

        .plotly-graph-div {{
            width: 100% !important;
            margin-left: auto !important;
            margin-right: auto !important;
        }}

    </style>

</head>


<body>

    <div class="page-wrapper">

        <div class="chart-wrapper">

            {plot_html}

        </div>

    </div>


    <script>

        // Resize Plotly when the browser window changes.
        window.addEventListener(
            "resize",
            function() {{

                const plot =
                    document.querySelector(
                        ".plotly-graph-div"
                    );

                if (plot) {{
                    Plotly.Plots.resize(plot);
                }}
            }}
        );

    </script>

</body>

</html>
"""


# =========================================================
# 16. SAVE HTML FILE
# =========================================================

with open(
    OUTPUT_FILE,
    "w",
    encoding="utf-8"
) as file:

    file.write(full_html)


# =========================================================
# 17. TERMINAL SUMMARY
# =========================================================

print()
print("PROGRAM CREATED SUCCESSFULLY")
print("=" * 65)

print()
print("LEFT MAP")

for code in left_codes:
    print(
        f"  {code} - {tax_names[code]}"
    )


print()
print("RIGHT MAP")

for code in right_codes:
    print(
        f"  {code} - {tax_names[code]}"
    )


print()
print(
    f"Saved interactive file: "
    f"{OUTPUT_FILE}"
)

print()
print(
    "Each map can be changed "
    "independently using its four buttons."
)

print("=" * 65)


# =========================================================
# 18. OPEN FINAL PAGE
# =========================================================

absolute_path = os.path.abspath(
    OUTPUT_FILE
)

webbrowser.open(
    "file:///" +
    absolute_path.replace("\\", "/")
)