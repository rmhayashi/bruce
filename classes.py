from flask import Flask, render_template, request, flash, url_for, session, app, Response, Blueprint, g, redirect
import cx_Oracle #, threading

import datetime as dt, pyodbc, time
from dateutil.relativedelta import *
import io, os, sys
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

import pandas as pd, json
#, numpy as np
import plotly, plotly.graph_objs as go

from werkzeug.security import generate_password_hash, check_password_hash

from defs import *
from performance import *
from retorno import *
from usuarios import *
from query import *
from consultas import *
from preferencias import *

db_file = os.path.dirname(os.path.abspath("bruce.ipynb")) +"\\bases\\bruce.accdb"
odbc_conn_str = 'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=' + db_file
conn = pyodbc.connect(odbc_conn_str,autocommit=True,timeout=1)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hashsometHingthatcantberepliedneVer'
app.config['PERMANENT_SESSION_LIFETIME'] = 1200 #tempo em segundos

app.register_blueprint(performance)
app.register_blueprint(retorno)
app.register_blueprint(usuarios)
app.register_blueprint(query)
app.register_blueprint(consultas)
app.register_blueprint(preferencias)
