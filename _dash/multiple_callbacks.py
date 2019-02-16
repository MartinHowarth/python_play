
import dash
import dash_core_components as dcc
import dash_html_components as html

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']


def layout():
    return html.Div(
        children=[
            html.H3(
                "Welcome!",
                className="text-center",
                id='text1',
            ),
            html.H3(
                "Welcome2!",
                className="text-center",
                id='text2',
            ),
            html.Button(
                "1",
                id='btn1',
                className="btn btn-lg btn-success btn-block",
            ),
            html.Button(
                "2",
                id='btn2',
                className="btn btn-lg btn-success btn-block",
            ),
            html.Table([
                html.Thead([
                    html.Tr([
                        html.Th('Output 1'),
                        html.Th('Output 2')
                    ])
                ]),
                html.Tbody([
                    html.Tr([html.Td(id='output1'), html.Td(id='output2')]),
                ])
            ]),
        ]
    )


app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = layout()


# @app.callback([dash.dependencies.Output('text1', 'children'), dash.dependencies.Output('text2', 'children')],
#               [dash.dependencies.Input('btn1', 'n_clicks')])
#               # [dash.dependencies.Event('btn1', "click")])
# def text1():
#     return ["text1", "text1_2"]


@app.callback(dash.dependencies.Output('output1', 'children'),
              [dash.dependencies.Input('btn1', 'n_clicks')])
def text1(n_clicks):
    return "text{}".format(n_clicks)


# @app.callback(dash.dependencies.Output('text1', 'children'),
#               [], [],
#               [dash.dependencies.Event('btn2', "click")])
# def text2():
#     return ["text2"]


if __name__ == '__main__':
    app.run_server(debug=True)
