# -----
# SETUP
# -----

faceImagePath = 'assets/faces/' # define path to faces (note: properties of faces [i.e., race, sex] defined by first two letters of file name; e.g., bf = black female; wf = white female; bm = black male; wm = white male; etc.)
faceMatrixPath = 'assets/faceMatrix - Combined.csv' # define path to face matrix generated with compare.py

# -------
# IMPORTS
# -------

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_defer_js_import as dji
from flask import Flask
import re
import os
import fnmatch
import random
import pandas as pd
import numpy

# ---------
# FUNCTIONS
# ---------

def ListFiles (extension, path = ".", shuffle = False):

    extensionRule = re.compile(fnmatch.translate('*.' + extension), re.IGNORECASE)

    files = [name for name in os.listdir(path) if extensionRule.match(name)]

    if (shuffle):
        random.shuffle(files)

    return files

def ReadFaceMatrix (file):
    return(pd.read_csv(file, index_col = 0))

# ---------
# MAIN CODE
# ---------

fileNames = ListFiles(extension = 'jpg', path = faceImagePath, shuffle = True)
filePaths = [os.path.join(faceImagePath, s) for s in fileNames]
fileIDs = [fileName.replace('.', ' ') for fileName in fileNames]

faceImages = []
faceImagesCallbacks = []

for i, eachFile in enumerate(fileNames):
    faceImages.append(html.A(
        className = 'carousel-item', 
        href = '#' + fileIDs[i], 
        children = html.Img(
            src = filePaths[i], 
            id = fileIDs[i],
            className = 'face-selection')))
    faceImagesCallbacks.append(Input(fileIDs[i], 'n_clicks'))

external_stylesheets = [
    'https://cdnjs.cloudflare.com/ajax/libs/materialize/1.0.0/css/materialize.min.css' # https://github.com/Dogfalo/materialize
]

external_scripts = [
    'https://code.jquery.com/jquery-3.4.1.min.js',
    'https://cdnjs.cloudflare.com/ajax/libs/materialize/1.0.0/js/materialize.min.js'
]

app = dash.Dash(
    __name__,
    external_stylesheets = external_stylesheets,
    external_scripts = external_scripts,
    assets_ignore = '.*ignored.*')

app.layout = html.Div([
    html.Div(id = 'carousel', className = 'carousel', children = faceImages),
    html.Div(id = 'my-div', style = {'textAlign': 'center'}),
    dji.Import(src = "assets/ignored.js")
])

@app.callback(Output('my-div', 'children'), faceImagesCallbacks)

def ShowBestFaces (*args):

    ctx = dash.callback_context

    if all(i == None for i in list(args)):
        return(html.Div('Click a face to begin...', style = {'fontWeight': 'bold'}))
    else:
        selectedFace = ctx.triggered[0]['prop_id'].split('.')[0]
        lastSpace = selectedFace.rfind(' ')
        selectedFace = selectedFace[:lastSpace] + '.' + selectedFace[lastSpace+1:]
        selectedFaceProps = selectedFace[:2]

        numFaces = 5

        bestMatches = faceMatrix[[selectedFace]].sort_values(by = [selectedFace], ascending = False).filter(regex = "^" + selectedFaceProps, axis = 0).head(numFaces)

        bestMatchesImages = []

        for i, value in enumerate(bestMatches.index.values):
            bestMatchesImages.append(html.Div([
                html.Img(src = faceImagePath + value, height = 250),
                html.Div(bestMatches.index.values[i]),
                html.Div([
                    html.Span('Similarity:', style = {'fontWeight': 'bold'}),
                    html.Span(' {:.2f}'.format(numpy.round(bestMatches.values[i][0], 2)))
                ])
                ], style = {'display': 'inline-block', 'marginTop': '1em'}))

        return(
            html.Div([
                html.Div([
                    html.Span('Selected face:', style = {'fontWeight': 'bold'}),
                    html.Span(' {}'.format(selectedFace))
                ]),
                html.Div([
                    html.Span('Best matches:', style = {'fontWeight': 'bold'})
                ], style = {'marginTop': '1em'}),
                html.Div(children = bestMatchesImages, style = {'marginBottom': '1em'}),
                html.Div([
                    html.Span('Mean similarity:', style = {'fontWeight': 'bold'}),
                    html.Span(' {:.2f}'.format(numpy.round(numpy.mean(bestMatches.values), 2)))
                ])
            ])
        )

if __name__ == '__main__':

    faceMatrix = ReadFaceMatrix(file = faceMatrixPath)

    debug = False

    if (debug):
        app.run_server(debug = True)
    else:
        app.run_server(
            debug = False,
            port = 5225,
            host = '0.0.0.0')