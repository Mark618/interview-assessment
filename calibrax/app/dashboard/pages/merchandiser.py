import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output
import pandas as pd
import requests
import plotly.express as px

dash.register_page(__name__,title="Merchandiser",name="Merchandiser",path="/",order=1)

API_BASE = "http://localhost:8080"

color_seq = ["#3A5A40","#DAD7CD","#A3B18A","#588157","#344E41"]

# Fetch initial filter options
filters = requests.get(f"{API_BASE}/filters").json()

def to_options(lst):
    opts = [{"label": "All", "value": ""}]
    opts += [{"label": v, "value": v} for v in lst]
    return opts

layout = html.Div([
    # html.H1("Technical Assessment"),

    # Filters
    html.Div([
        html.Div([
            dbc.Label("Category"),
            dcc.Dropdown(id='filter-category', options=to_options(filters["categorys"]), value="", multi=False)
        ]),
        html.Div([
            dbc.Label("Segment"),
            dcc.Dropdown(id='filter-segment', options=to_options(filters["segments"]), value="", multi=False)
        ]),
        html.Div([
            dbc.Label("Collection"),
            dcc.Dropdown(id='filter-collection', options=to_options(filters["collections"]), value="", multi=False)
        ]),
        html.Div([
            dbc.Label("Product Type"),
            dcc.Dropdown(id='filter-product_type', options=to_options(filters["product_types"]), value="", multi=False)
        ]),
    ], style={"display": "grid", "gridTemplateColumns": "repeat(4, 1fr)", "gap": "10px"}),

    html.Hr(),

    # KPI Cards
    html.Div(id='kpi-cards', style={"display": "flex", "gap": "20px"}),

    html.Hr(),

    # Top Overpriced Products Table
    
    html.Div(children=[
        html.H2("Top Overpriced Products"),
        dash_table.DataTable(
        id='overpriced-table',
        columns=[
            {"name": "Title", "id": "title"},
            {"name": "Brand", "id": "brand"},
            {"name": "Category", "id": "category"},
            {"name": "Our Price", "id": "our_price"},
            {"name": "Competitor", "id": "competitor_vendor"},
            {"name": "Competitor Price", "id": "competitor_price"},
            {"name": "Price Index", "id": "price_index"},
        ],
        markdown_options={"html": True},
        page_size=10,
        style_table={'overflowX': 'auto'},
        ),
    ]),    

    html.Hr(),

    # Charts
    html.Div([
        html.Div([dcc.Graph(id='price-index-hist',config={"displayModeBar": False})], style={"width": "48%", "display": "inline-block"}),
        html.Div([dcc.Graph(id='competitor-bar',config={"displayModeBar": False})], style={"width": "48%", "display": "inline-block"}),
        html.Div([dcc.Graph(id='category-box',config={"displayModeBar": False})], style={"width": "100%", "display": "inline-block"}),
        html.Div([dcc.Graph(id='prod-type-box',config={"displayModeBar": False})], style={"width": "100%", "display": "inline-block"}),
        html.Div([dcc.Graph(id='segment-box',config={"displayModeBar": False})], style={"width": "100%", "display": "inline-block"}),
        html.Div([dcc.Graph(id='collection-box',config={"displayModeBar": False})], style={"width": "100%", "display": "inline-block"}),
    ])
])

# Callback for cascading filter options
@dash.callback(
    Output('filter-category', 'options'),
    Output('filter-segment', 'options'),
    Output('filter-collection', 'options'),
    Output('filter-product_type', 'options'),
    Input('filter-category', 'value'),
    Input('filter-segment', 'value'),
    Input('filter-collection', 'value'),
    Input('filter-product_type', 'value')
)
def update_dropdown_options(category, segment, collection, product_type):
    params = {
        "category": category or None,
        "segment": segment or None,
        "collection": collection or None,
        "product_type": product_type or None
    }
    new_filters = requests.get(f"{API_BASE}/filters", params=params).json()
    return to_options(new_filters["categorys"]), \
           to_options(new_filters["segments"]), \
           to_options(new_filters["collections"]), \
           to_options(new_filters["product_types"])

# Callback for dashboard data
@dash.callback(
    Output('kpi-cards', 'children'),
    Output('overpriced-table', 'data'),
    Output('price-index-hist', 'figure'),
    Output('competitor-bar', 'figure'),
    Output('category-box', 'figure'),
    Output('prod-type-box', 'figure'),
    Output('segment-box', 'figure'),
    Output('collection-box', 'figure'),
    Input('filter-category', 'value'),
    Input('filter-segment', 'value'),
    Input('filter-collection', 'value'),
    Input('filter-product_type', 'value')
)
def update_dashboard(category, segment, collection, product_type):
    params = {
        "category": category or None,
        "segment": segment or None,
        "collection": collection or None,
        "product_type": product_type or None
    }

    # KPI metrics
    metrics = requests.get(f"{API_BASE}/metrics", params=params).json()
    kpis = []
    for key, value in metrics.items():
        kpis.append(html.Div([
            html.H4(key.replace("_"," ").title()),
            html.P(f"{value}")
        ], style={"border": "1px solid #ccc", "padding": "10px", "flex": "1"}))

    # Top overpriced products
    rows = requests.get(f"{API_BASE}/overpriced-products", params=params).json()
    overpriced_df = pd.DataFrame(rows)

    # Price index distribution
    dist_rows = requests.get(f"{API_BASE}/price-distribution", params=params).json()
    dist_df = pd.DataFrame(dist_rows)
    if not dist_df.empty:
        fig_hist = px.histogram(dist_df, x='price_index', nbins=30, title="Price Index Distribution",color_discrete_sequence=color_seq)
        fig_hist.update_layout({'plot_bgcolor': 'rgba(0, 0, 0, 0)','paper_bgcolor':'rgba(0, 0, 0, 0)'})  
    else:
        fig_hist=px.histogram(title="Price Index Distribution")

    # Competitor average price index
    comp_rows = requests.get(f"{API_BASE}/competitor-analysis", params=params).json()
    comp_df = pd.DataFrame(comp_rows)
    if not comp_df.empty:
        fig_bar = px.bar(comp_df, x='competitor_vendor', y='avg_price_index', title="Avg Price Index by Competitor",color_discrete_sequence=color_seq,hover_data={'listings': True, 'avg_price_index': ':.2f'}, 
        labels={'listings': 'Total Listings', 'avg_price_index': 'Avg Price Index'})
        fig_bar.update_layout({'plot_bgcolor': 'rgba(0, 0, 0, 0)','paper_bgcolor':'rgba(0, 0, 0, 0)'})    
    else :
        fig_bar=px.bar(title="Avg Price Index by Competitor")

    # Category plot
    cat_rows = requests.get(f"{API_BASE}/category-analysis", params=params).json()
    cat_df = pd.DataFrame(cat_rows)
    if not cat_df.empty:
        fig_box = px.bar(cat_df, x='category', y='avg_price_index', title="Avg Price Index by Category",color_discrete_sequence=color_seq,hover_data={'listings': True, 'avg_price_index': ':.2f'}, 
        labels={'listings': 'Total Listings', 'avg_price_index': 'Avg Price Index'})
        fig_box.update_layout({'plot_bgcolor': 'rgba(0, 0, 0, 0)','paper_bgcolor':'rgba(0, 0, 0, 0)'})  
    else:
        fig_box = px.bar(title="Avg Price Index by Category")

    
    # prod_type plot
    prod_type_rows = requests.get(f"{API_BASE}/prod-type-analysis", params=params).json()
    prod_type_df = pd.DataFrame(prod_type_rows)
    if not prod_type_df.empty:
        prod_type_fig = px.bar(prod_type_df, x='product_type', y='avg_price_index', title="Avg Price Index by Product Type",color_discrete_sequence=color_seq,hover_data={'listings': True, 'avg_price_index': ':.2f'}, 
        labels={'listings': 'Total Listings', 'avg_price_index': 'Avg Price Index'})
        prod_type_fig.update_layout({'plot_bgcolor': 'rgba(0, 0, 0, 0)','paper_bgcolor':'rgba(0, 0, 0, 0)'})  
    else:
        prod_type_fig = px.bar(title="Avg Price Index by Product Type")

    # segment plot
    seg_rows = requests.get(f"{API_BASE}/segment-analysis", params=params).json()
    seg_df = pd.DataFrame(seg_rows)
    if not seg_df.empty:
        seg_fig = px.bar(seg_df, x='segment', y='avg_price_index', title="Avg Price Index by Segment",color_discrete_sequence=color_seq,hover_data={'listings': True, 'avg_price_index': ':.2f'}, 
        labels={'listings': 'Total Listings', 'avg_price_index': 'Avg Price Index'})
        seg_fig.update_layout({'plot_bgcolor': 'rgba(0, 0, 0, 0)','paper_bgcolor':'rgba(0, 0, 0, 0)'})  
    else:
        seg_fig = px.bar(title="Avg Price Index by Segment")

    # collection plot
    coll_rows = requests.get(f"{API_BASE}/collection-analysis", params=params).json()
    coll_df = pd.DataFrame(coll_rows)
    if not coll_df.empty:
        coll_fig = px.bar(coll_df, x='collection', y='avg_price_index', title="Avg Price Index by Collection",color_discrete_sequence=color_seq,hover_data={'listings': True, 'avg_price_index': ':.2f'}, 
        labels={'listings': 'Total Listings', 'avg_price_index': 'Avg Price Index'})
        coll_fig.update_layout({'plot_bgcolor': 'rgba(0, 0, 0, 0)','paper_bgcolor':'rgba(0, 0, 0, 0)'})  
    else:
        coll_fig = px.bar(title="Avg Price Index by Collection")




    return kpis, overpriced_df.to_dict('records'), fig_hist, fig_bar, fig_box, prod_type_fig, seg_fig, coll_fig