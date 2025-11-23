"""
Generic data-visualisation web app using pandas + Plotly + Dash.

How to use:
1. Put your CSV under ./data and update DATA_PATH.
2. Adjust `preprocess_data()` to clean / engineer features.
3. Add / change figures in `build_static_figures()` and the callback.
"""

from pathlib import Path
import numpy as np
import pandas as pd

import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output

# =========================
# 1. Load & preprocess data
# =========================

# DATA_PATH = Path("data/your_dataset.csv")   # 👈 change this
DATA_PATH = Path("./data/WA_Fn-UseC_-Telco-Customer-Churn.csv")



def preprocess_data(path: Path) -> pd.DataFrame:
    """Read CSV and do all cleaning / type conversion here."""
    df = pd.read_csv(path)

    # Example clean-up (adapt to your own data)
    # ------------------------------------------------
    # Numeric conversion with NaN handling
    for col in df.columns:
        if df[col].dtype == "object":
            try:
                df[col] = pd.to_numeric(df[col], errors="ignore")
            except Exception:
                pass

    # Example: fill numeric NaNs with median
    num_cols = df.select_dtypes(include="number").columns
    for col in num_cols:
        df[col] = df[col].fillna(df[col].median())

    return df


df = preprocess_data(DATA_PATH)

numeric_cols = df.select_dtypes(include="number").columns.tolist()
categorical_cols = [c for c in df.columns if c not in numeric_cols]

# Guard against empty lists
if len(numeric_cols) < 2:
    raise ValueError("Need at least 2 numeric columns for this template.")
if len(categorical_cols) == 0:
    categorical_cols = [None]  # colour disabled


# =========================
# 2. Precompute static figs
# =========================

def build_static_figures(data: pd.DataFrame):
    """Figures that do not change with user interaction."""
    # 2.1 Summary stats bar chart (mean with std)
    desc = data[numeric_cols].describe().T.reset_index()
    desc = desc.rename(columns={"index": "feature"})
    fig_summary = px.bar(
        desc,
        x="feature",
        y="mean",
        error_y="std",
        title="Numeric Features: Mean ± Std",
        labels={"mean": "Mean value", "feature": "Feature"},
    )

    # 2.2 Correlation heatmap
    corr = data[numeric_cols].corr()
    fig_corr = go.Figure(
        data=go.Heatmap(
            z=corr.values,
            x=corr.columns,
            y=corr.index,
            colorscale="Viridis",
            zmin=-1,
            zmax=1,
            colorbar=dict(title="Correlation"),
            text=np.round(corr.values, 2),
            texttemplate="%{text}",
        )
    )
    fig_corr.update_layout(
        title="Correlation Heatmap (numeric features)",
        xaxis_title="",
        yaxis_title="",
    )

    return fig_summary, fig_corr


fig_summary, fig_corr = build_static_figures(df)

# =========================
# 3. Build Dash layout
# =========================

app = Dash(__name__)

app.layout = html.Div(
    style={
        "fontFamily": "Arial, sans-serif",
        "margin": "0 auto",
        "maxWidth": "1200px",
        "padding": "20px",
        "backgroundColor": "#f7f7f7",
    },
    children=[
        html.H1("Data Dashboard Template", style={"textAlign": "center"}),

        # Row 0 – dataset info
        html.Div(
            style={"marginBottom": "20px"},
            children=[
                html.P(f"Rows: {len(df):,}"),
                html.P(f"Numeric columns: {', '.join(numeric_cols)}"),
            ],
        ),

        # Row 1 – interactive scatter
        html.Div(
            style={"display": "flex", "gap": "20px", "flexWrap": "wrap"},
            children=[
                html.Div(
                    style={"flex": "1", "minWidth": "260px"},
                    children=[
                        html.Label("X axis"),
                        dcc.Dropdown(
                            id="x-col",
                            options=[{"label": c, "value": c} for c in numeric_cols],
                            value=numeric_cols[0],
                            clearable=False,
                        ),
                        html.Br(),
                        html.Label("Y axis"),
                        dcc.Dropdown(
                            id="y-col",
                            options=[{"label": c, "value": c} for c in numeric_cols],
                            value=numeric_cols[1],
                            clearable=False,
                        ),
                        html.Br(),
                        html.Label("Colour by (optional)"),
                        dcc.Dropdown(
                            id="colour-col",
                            options=[
                                {"label": "None", "value": "None"}
                            ]
                            + [
                                {"label": c, "value": c}
                                for c in categorical_cols
                                if c is not None
                            ],
                            value="None",
                            clearable=False,
                        ),
                    ],
                ),
                html.Div(
                    style={
                        "flex": "3",
                        "minWidth": "300px",
                        "backgroundColor": "white",
                        "padding": "10px",
                        "borderRadius": "8px",
                    },
                    children=[dcc.Graph(id="scatter-fig")],
                ),
            ],
        ),

        html.Br(),

        # Row 2 – summary stats + correlation
        html.Div(
            style={"display": "flex", "gap": "20px", "flexWrap": "wrap"},
            children=[
                html.Div(
                    style={
                        "flex": "1",
                        "minWidth": "300px",
                        "backgroundColor": "white",
                        "padding": "10px",
                        "borderRadius": "8px",
                    },
                    children=[dcc.Graph(figure=fig_summary)],
                ),
                html.Div(
                    style={
                        "flex": "1",
                        "minWidth": "300px",
                        "backgroundColor": "white",
                        "padding": "10px",
                        "borderRadius": "8px",
                    },
                    children=[dcc.Graph(figure=fig_corr)],
                ),
            ],
        ),
    ],
)

# =========================
# 4. Callbacks (interaction)
# =========================

@app.callback(
    Output("scatter-fig", "figure"),
    Input("x-col", "value"),
    Input("y-col", "value"),
    Input("colour-col", "value"),
)
def update_scatter(x_col, y_col, colour_col):
    """Interactive scatter plot driven by dropdowns."""
    if colour_col == "None":
        fig = px.scatter(
            df,
            x=x_col,
            y=y_col,
            title=f"{y_col} vs {x_col}",
        )
    else:
        fig = px.scatter(
            df,
            x=x_col,
            y=y_col,
            color=colour_col,
            title=f"{y_col} vs {x_col} coloured by {colour_col}",
        )

    fig.update_layout(margin=dict(l=40, r=20, t=60, b=40), height=450)
    return fig


if __name__ == "__main__":
    # Set debug=True while developing, False when finished.
    app.run(debug=True)