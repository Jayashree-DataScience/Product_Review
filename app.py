from dash import Dash
import dash_core_components as dcc
import dash_html_components as html
import pickle
import pandas as pd
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_extraction.text import CountVectorizer
import plotly.graph_objects as go
import numpy as np
from dash.dependencies import Input, Output,State
import dash_bootstrap_components as dbc
import webbrowser


from io import BytesIO

import pandas as pd
from wordcloud import WordCloud
import base64

reviews = pd.read_csv("etsy_reviews.csv")

app = Dash(__name__, title='Product Review Analysis',
           update_title='Processing...', external_stylesheets=[dbc.themes.BOOTSTRAP])

def open_browser():
  # Open the default web browser
  webbrowser.open_new('http://127.0.0.1:8050/')
    
class customer_feedback:
    def __init__(self, balanced_reviews, scrapped_reviews, app):
        self.balanced_reviews = balanced_reviews
        self.scrapped_reviews = scrapped_reviews
        self.app = app
        self.load_model()

    def load_model(self):
        with open("model_files/trained_model.pkl", 'rb') as file:
            pickle_model = pickle.load(file)
            self.pickle_model = pickle_model
        with open("model_files/vocab.pkl", 'rb') as vocab:
            vocab = pickle.load(vocab)
            self.vocab = vocab

    def check_review(self, reviewText):
        transformer = TfidfTransformer()
        loaded_vec = CountVectorizer(
            decode_error="replace", vocabulary=self.vocab)
        reviewText = transformer.fit_transform(
            loaded_vec.fit_transform([reviewText]))
        return self.pickle_model.predict(reviewText)

    def create_app_ui(self):
        self.balanced_reviews = self.balanced_reviews.dropna()
        self.balanced_reviews['Positivity'] = np.where(
            self.balanced_reviews['overall'] > 3, 1, 0)
        labels = ['Positive Reviews', 'Negative Reviews', 'Neutral Reviews']
        values = [self.balanced_reviews[self.balanced_reviews.overall > 3].dropna().shape[0], self.balanced_reviews[self.balanced_reviews.overall < 3].dropna(
        ).shape[0], self.balanced_reviews[self.balanced_reviews.overall == 3].dropna().shape[0]]

        #labels1 = ['+ve Reviews', '-ve Reviews']
        #values1 = [len(self.balanced_reviews[self.balanced_reviews.Positivity == 1]), len(
         #   self.balanced_reviews[self.balanced_reviews.Positivity == 0])]

        colors = ['#00cd00', '#d80000', '#a6a6a6']

        main_layout = html.Div([
                        dbc.Container(
            dbc.Jumbotron(
                [
                    html.H1(id='heading1', children='Product Review Analysis',
                            className='display-2 mb-3', style={'font': 'sans-seriff', 'font-weight': 'bold', 'font-size': '50px', 'color': 'blue'}),
                     html.Br(),
    
                    html.Img(id = "banner", src = app.get_asset_url('banner.png'), 
                             style={'height':'40%','width':'60%'}),
       
                    html.Br(), 
                    
                    html.P(id='heading5', children='Distribution of Reviews',
                           className='display-3 mb-3', style={'font': 'sans-seriff', 'font-weight': 'bold', 'font-size': '30px', 'color': 'blue'}),
                    
                    dbc.Container(
                        dcc.Loading(
                            dcc.Graph(
                                figure={'data': [go.Pie(labels=labels, values=values, hole=.3, pull=[0.2, 0, 0], textinfo='value', marker=dict(colors=colors, line=dict(color='#000000', width=2)))],
                                        'layout': go.Layout(height=600, width=1000, autosize=False)
                                        }
                            )
                        ),
                        className='d-flex justify-content-center',
                        style={'max-width': '100%',
                           'background-color': '#ffcc00'},
                    ),

                    html.Hr(),
                    
                    html.P(id='heading4', children='Wordcloud of Reviews',
                           className='display-3 mb-4', style={'font': 'sans-seriff', 'font-weight': 'bold', 'font-size': '30px', 'color': 'blue'}),
                    
                    
                    html.Hr(),
                    
                    dbc.Container(
                     html.Img(id="image_wc"),
                    
                    ),
                    
                           
                    
                    html.P(id='heading2', children='Customer Instant Feedback!',
                           className='display-3 mb-4', style={'font': 'sans-seriff', 'font-weight': 'bold', 'font-size': '30px', 'color': 'blue'}),
                    dbc.Textarea(id='textarea', className="mb-3", placeholder="Enter your feedback on the product",
                                 value='', style={'resize': 'none'}),

                    html.Div(id='result'),
                    html.Hr(),

                    html.P(id='heading3', children='Scraped Review Sentiments',
                           className='display-3 mb-4', style={'font': 'sans-serif', 'font-weight': 'bold', 'font-size': '30px', 'color': 'blue'}),

                    dbc.Container([
                        dcc.Dropdown(
                            id='dropdown',
                            placeholder='See what people think',
                            options=[{'label': i[:100] + "...", 'value': i}
                                     for i in self.scrapped_reviews.reviews],
                            value=self.balanced_reviews.reviewText[0],
                            style={'margin':'10px'}

                        )
                    ]),

                    html.Div(id='result1')
                ],
                className='text-center',
                style={'max-width': '100%',
                           'background-color': '#ffcc00'}
            ),
            className='mt-3',
            style={'max-width': '100%',
                           'background-color': '#ffcc00'}
        )
         ],
                    style={'background-color': '#ffcc00', 'font-family': 'Proxima Nova Bold'},
                )               
        return main_layout

def plot_wordcloud(data):
    comments=data.values
    wc=WordCloud(width = 800, height = 500,min_word_length=3,max_words=500, background_color='black', random_state=12).generate(str(comments))
    
    return wc.to_image()

@app.callback(Output('image_wc', 'src'), [Input('image_wc', 'id')])
def make_image(b):
    img = BytesIO()
    plot_wordcloud(data=reviews['reviews']).save(img, format='PNG')
    
    return 'data:image/png;base64,{}'.format(base64.b64encode(img.getvalue()).decode())

@app.callback(
    Output('result', 'children'),
    [
        Input('textarea', 'value')
    ]
)
def update_app_ui(value):
    rev = customer_feedback(None, None, app)
    rev.load_model()
    result_list = rev.check_review(value)[0]

    if (result_list == 0):
        return dbc.Alert("Negative Feedback!", color="danger")
    elif (result_list == 1):
        return dbc.Alert("Positive Feedback!", color="success")
    elif (result_list == ''):
        return dbc.Alert("Awaiting Feedback", color="dark")


@app.callback(
    Output('result1', 'children'),
    [
        Input('dropdown', 'value')
    ]
)
def update_dropdown(value):
    rev = customer_feedback(None, None, app)
    rev.load_model()
    result_list = rev.check_review(value)[0]

    if (result_list == 0):
        return dbc.Alert("Negative Feedback!", color="danger")
    elif (result_list == 1):
        return dbc.Alert("Positive Feedback!", color="success")
    elif (result_list == None):
        return dbc.Alert("Awaiting Feedback", color="dark")


def main():
    open_browser()
    
    global app
    balanced_reviews = pd.read_csv("balanced_reviews.csv")
    scrapped_reviews = pd.read_csv("etsy_reviews.csv")
    app.layout = customer_feedback(
        balanced_reviews, scrapped_reviews, app).create_app_ui()
    app.run_server(host='0.0.0.0')
    app = None

if __name__ == '__main__':
    main()
