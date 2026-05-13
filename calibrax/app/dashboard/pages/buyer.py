import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output
import pandas as pd
import requests
import plotly.express as px

dash.register_page(__name__,title="Buyer",name="Buyer",path="/buyer",order=2)

API_BASE = "http://localhost:8080"

color_seq = ["#DAD7CD","#A3B18A","#588157","#3A5A40","#344E41"]

# Fetch initial filter options
filters = requests.get(f"{API_BASE}/filters").json()

def to_options(lst):
    opts = [{"label": "All", "value": ""}]
    opts += [{"label": v, "value": v} for v in lst]
    return opts

layout = html.Div([

    html.H1("Buyer Product Explorer"),

    # Search
    dcc.Input(
        id="buyer-search",
        type="text",
        placeholder="Search product...",
        style={"width": "100%", "padding": "10px"}
    ),

    html.Br(), html.Br(),

    # Filters

    html.Div([
        html.Div([
            dbc.Label("Category"),
            dcc.Dropdown(id='buyer-category', options=to_options(filters["categorys"]), value="", multi=False)
        ]),
        html.Div([
            dbc.Label("Segment"),
            dcc.Dropdown(id='buyer-segment', options=to_options(filters["segments"]), value="", multi=False)
        ]),
        html.Div([
            dbc.Label("Collection"),
            dcc.Dropdown(id='buyer-collection', options=to_options(filters["collections"]), value="", multi=False)
        ]),
        html.Div([
            dbc.Label("buyer Type"),
            dcc.Dropdown(id='buyer-product_type', options=to_options(filters["product_types"]), value="", multi=False)
        ]),
    ], style={"display": "grid", "gridTemplateColumns": "repeat(4, 1fr)", "gap": "10px"}),

    html.Hr(),

    # Cards
    html.Div(id="buyer-product-cards")
])


@dash.callback(
    Output("buyer-product-cards", "children"),
    Input("buyer-search", "value"),
    Input("buyer-category", "value"),
    Input("buyer-segment", "value"),
    Input("buyer-collection", "value"),
    Input("buyer-product_type", "value")
)
def update_buyer_page(search, category, segment, collection, product_type):

    params = {
        "search": search,
        "category": category,
        "segment": segment,
        "collection": collection,
        "product_type": product_type
    }

    data = requests.get(f"{API_BASE}/buyer-products", params=params).json()
    df = pd.DataFrame(data)

    if df.empty:
        return html.Div("No products found")

    cards = []

    for product_id, group in df.groupby("product_id_diy"):

        row = group.iloc[0]
        competitors = group.sort_values("competitor_price_per_unit").head(5)

        competitor_list = []

        for _, comp in competitors.iterrows():
            if pd.isna(comp["competitor_title"]):
                continue

            competitor_list.append(html.Div([
                html.Img(src=comp["competitor_image"], style={"width": "80px"}),
                html.A(comp["competitor_title"], href=comp["competitor_url"], target="_blank"),
                html.P(f"Price/unit: {round(comp['competitor_price_per_unit'],2)}")
            ], style={"display": "flex", "gap": "10px"}))

        card = html.Div([
            html.Div([                
                html.A(row["title"], href=row["product_url"], target="_blank"),                
            ], className='card-header'),
            html.Img(src=row["image_url"], style={"width": "120px"}),
            html.P(f"Price/unit: {round(row['price_per_unit'],2)}"),
            html.Details([
                html.Summary("View Competitors"),
                html.Div(competitor_list)
            ])

        ], style={
            "border": "1px solid #ccc",
            "padding": "15px",
            "marginBottom": "10px",
            "borderRadius": "10px"
        },className="card")

        cards.append(card)

    return cards


@dash.callback(
    Output("buyer-category", "options"),
    Output("buyer-segment", "options"),
    Output("buyer-collection", "options"),
    Output("buyer-product_type", "options"),
    Input("buyer-category", "value"),
    Input("buyer-segment", "value"),
    Input("buyer-collection", "value"),
    Input("buyer-product_type", "value"),
)
def update_filters(category, segment, collection, product_type):

    params = {
        "category": category or None,
        "segment": segment or None,
        "collection": collection or None,
        "product_type": product_type or None
    }

    data = requests.get(f"{API_BASE}/filters", params=params).json()

    return to_options(data["categorys"]), \
           to_options(data["segments"]), \
           to_options(data["collections"]), \
           to_options(data["product_types"])