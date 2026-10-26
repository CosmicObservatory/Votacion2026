from dash import Dash, html, dcc, Input, Output, callback
from vothmo.dashboard import stats
from vothmo.dashboard import scenario
from vothmo.dashboard import intro
app = Dash(__name__)

app.layout = html.Div(children=[
    html.H1("Participación Ciudadana 2027"),
    dcc.Tabs(id="principal",value="tab-0",
    children=[
    dcc.Tab(label="Primeros Pasos", value="tab-0", children=intro.content),
    dcc.Tab(label="Estadisticas", value="tab-1", children=stats.content),
    dcc.Tab(label="Crecimiento", value="tab-2", children=scenario.content)
    ]),
])




if __name__ == "__main__":
    app.run(debug=True)