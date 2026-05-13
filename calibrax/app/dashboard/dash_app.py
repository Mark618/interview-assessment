import dash
import dash_bootstrap_components as dbc
from dash import  html,Dash

API_BASE = "http://localhost:8080"

external_stylesheets = [dbc.themes.JOURNAL, 'https://fonts.googleapis.com/icon?family=Material+Icons']

app = Dash(__name__,use_pages=True,external_stylesheets=external_stylesheets)
color_seq = ["#DAD7CD","#A3B18A","#588157","#3A5A40","#344E41"]
app.title = "Technical Assessment"

nav = dbc.NavbarSimple(
    children=[
        html.Div(
             dbc.NavLink(f"{page['name']}", href=page["relative_path"])
        ) for page in dash.page_registry.values()      
    ],
    brand="Technical Assessment",   
    color="#3A5A40"
)

app.layout = html.Div(
    children=[
        nav,
        dbc.Container(
            [       
                dash.page_container,    
            ],
            fluid=True
        )
    ]
)

if __name__ == "__main__":
    app.run(debug=True,port=8081)