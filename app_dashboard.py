import pandas as pd
import numpy as np
from pathlib import Path

import plotly.express as px
import plotly.graph_objects as go

from dash import Dash, dcc, html

# =========================
# 1. Load & preprocess data
# =========================

DATA_PATH = Path("./data/WA_Fn-UseC_-Telco-Customer-Churn.csv")
df = pd.read_csv(DATA_PATH)

# Clean / convert
df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce")
df["TotalCharges"] = df["TotalCharges"].fillna(df["TotalCharges"].median())

df["ChurnFlag"] = df["Churn"].map({"Yes": 1, "No": 0})

# Create some helper columns
bins_tenure = [0, 12, 24, 48, 72, np.inf]
labels_tenure = ["0–12", "13–24", "25–48", "49–72", "73+"]
df["TenureGroup"] = pd.cut(df["tenure"], bins=bins_tenure, labels=labels_tenure, right=True)

bins_charges = [0, 25, 50, 75, 100, np.inf]
labels_charges = ["0–25", "26–50", "51–75", "76–100", "100+"]
df["MonthlyChargesGroup"] = pd.cut(df["MonthlyCharges"], bins=bins_charges, labels=labels_charges, right=True)

# =========================
# 2. Precompute figures
# =========================

# 2.1 High-level KPIs
churn_rate = df["ChurnFlag"].mean()
total_customers = len(df)
churn_yes = (df["Churn"] == "Yes").sum()
churn_no = (df["Churn"] == "No").sum()

fig_churn_pie = px.pie(
    df,
    names="Churn",
    title="Overall Churn Distribution",
    hole=0.4
)

# 2.2 Churn rate by contract type
churn_by_contract = (
    df.groupby("Contract")["ChurnFlag"]
    .mean()
    .reset_index()
    .sort_values("ChurnFlag", ascending=False)
)

fig_churn_contract = px.bar(
    churn_by_contract,
    x="Contract",
    y="ChurnFlag",
    title="Churn Rate by Contract Type",
    labels={"ChurnFlag": "Churn Rate"},
    text_auto=".0%"
)
fig_churn_contract.update_yaxes(tickformat=".0%")

# 2.3 Tenure distribution by churn
fig_tenure_hist = px.histogram(
    df,
    x="tenure",
    color="Churn",
    barmode="overlay",
    nbins=40,
    title="Tenure Distribution (Churn vs Non-Churn)",
    labels={"tenure": "Tenure (months)"}
)
fig_tenure_hist.update_traces(opacity=0.7)

# 2.4 Monthly Charges by Churn
fig_monthly_box = px.box(
    df,
    x="Churn",
    y="MonthlyCharges",
    title="Monthly Charges by Churn Status",
    labels={"MonthlyCharges": "Monthly Charges (£)"}
)

# 2.5 Correlation heatmap of numeric features
numeric_cols = ["tenure", "MonthlyCharges", "TotalCharges", "ChurnFlag"]
corr = df[numeric_cols].corr()

fig_corr_heatmap = px.imshow(
    corr,
    x=numeric_cols,
    y=numeric_cols,
    text_auto=".2f",
    title="Correlation Heatmap (Numeric Features)",
    aspect="auto",
)

# 2.6 Churn rate heatmap: tenure group vs monthly charge group
pivot_churn = df.pivot_table(
    index="TenureGroup",
    columns="MonthlyChargesGroup",
    values="ChurnFlag",
    aggfunc="mean"
)

fig_churn_heatmap = px.imshow(
    pivot_churn,
    text_auto=".0%",
    title="Churn Rate Heatmap: Tenure vs Monthly Charges",
    aspect="auto",
    labels=dict(x="Monthly Charges Group (£)", y="Tenure Group (months)", color="Churn Rate"),
)
fig_churn_heatmap.update_coloraxes(colorbar_tickformat=".0%")

# 2.7 Churn by internet service
if "InternetService" in df.columns:
    churn_by_internet = (
        df.groupby("InternetService")["ChurnFlag"]
        .mean()
        .reset_index()
        .sort_values("ChurnFlag", ascending=False)
    )

    fig_churn_internet = px.bar(
        churn_by_internet,
        x="InternetService",
        y="ChurnFlag",
        title="Churn Rate by Internet Service Type",
        labels={"ChurnFlag": "Churn Rate"},
        text_auto=".0%"
    )
    fig_churn_internet.update_yaxes(tickformat=".0%")
else:
    fig_churn_internet = go.Figure()

# 2.8 Save figures as HTML
# fig_churn_pie.write_html("churn_pie.html")
# fig_churn_contract.write_html("churn_by_contract.html")
# fig_tenure_hist.write_html("tenure_hist.html")
# fig_monthly_box.write_html("monthly_box.html")
# fig_corr_heatmap.write_html("corr_heatmap.html")
# fig_churn_heatmap.write_html("churn_heatmap.html")
# fig_churn_internet.write_html("churn_internet.html")

# =========================
# 3. Build Dash app layout
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
        html.H1("Customer Churn Dashboard", style={"textAlign": "center"}),

        # KPI cards
        html.Div(
            style={
                "display": "flex",
                "gap": "20px",
                "justifyContent": "space-between",
                "marginBottom": "20px",
                "flexWrap": "wrap",
            },
            children=[
                html.Div(
                    style={
                        "flex": "1",
                        "minWidth": "200px",
                        "backgroundColor": "white",
                        "padding": "15px",
                        "borderRadius": "8px",
                        "boxShadow": "0 2px 4px rgba(0,0,0,0.1)",
                    },
                    children=[
                        html.H3("Total Customers"),
                        html.H2(f"{total_customers:,}")
                    ],
                ),
                html.Div(
                    style={
                        "flex": "1",
                        "minWidth": "200px",
                        "backgroundColor": "white",
                        "padding": "15px",
                        "borderRadius": "8px",
                        "boxShadow": "0 2px 4px rgba(0,0,0,0.1)",
                    },
                    children=[
                        html.H3("Churn Rate"),
                        html.H2(f"{churn_rate:.1%}")
                    ],
                ),
                html.Div(
                    style={
                        "flex": "1",
                        "minWidth": "200px",
                        "backgroundColor": "white",
                        "padding": "15px",
                        "borderRadius": "8px",
                        "boxShadow": "0 2px 4px rgba(0,0,0,0.1)",
                    },
                    children=[
                        html.H3("Churned / Retained"),
                        html.P(f"Churned: {churn_yes:,}"),
                        html.P(f"Retained: {churn_no:,}"),
                    ],
                ),
            ],
        ),

        # Row 1: Overall churn + by contract
        html.Div(
            style={"display": "flex", "gap": "20px", "flexWrap": "wrap"},
            children=[
                html.Div(
                    style={"flex": "1", "minWidth": "300px", "backgroundColor": "white",
                           "padding": "10px", "borderRadius": "8px"},
                    children=[dcc.Graph(figure=fig_churn_pie)]
                ),
                html.Div(
                    style={"flex": "1", "minWidth": "300px", "backgroundColor": "white",
                           "padding": "10px", "borderRadius": "8px"},
                    children=[dcc.Graph(figure=fig_churn_contract)]
                ),
            ],
        ),

        html.Br(),

        # Row 2: Tenure + Monthly charges
        html.Div(
            style={"display": "flex", "gap": "20px", "flexWrap": "wrap"},
            children=[
                html.Div(
                    style={"flex": "1", "minWidth": "300px", "backgroundColor": "white",
                           "padding": "10px", "borderRadius": "8px"},
                    children=[dcc.Graph(figure=fig_tenure_hist)]
                ),
                html.Div(
                    style={"flex": "1", "minWidth": "300px", "backgroundColor": "white",
                           "padding": "10px", "borderRadius": "8px"},
                    children=[dcc.Graph(figure=fig_monthly_box)]
                ),
            ],
        ),

        html.Br(),

        # Row 3: Heatmaps
        html.Div(
            style={"display": "flex", "gap": "20px", "flexWrap": "wrap"},
            children=[
                html.Div(
                    style={"flex": "1", "minWidth": "300px", "backgroundColor": "white",
                           "padding": "10px", "borderRadius": "8px"},
                    children=[dcc.Graph(figure=fig_corr_heatmap)]
                ),
                html.Div(
                    style={"flex": "1", "minWidth": "300px", "backgroundColor": "white",
                           "padding": "10px", "borderRadius": "8px"},
                    children=[dcc.Graph(figure=fig_churn_heatmap)]
                ),
            ],
        ),

        html.Br(),

        # Row 4: Churn by Internet service
        html.Div(
            style={"backgroundColor": "white", "padding": "10px", "borderRadius": "8px"},
            children=[dcc.Graph(figure=fig_churn_internet)],
        ),
    ],
)

if __name__ == "__main__":
    # debug=False avoids constant live-reload noise
    app.run(debug=False)