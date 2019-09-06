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
pd.set_option('display.max_colwidth', -1)
#, numpy as np
import plotly, plotly.graph_objs as go

from werkzeug.security import generate_password_hash, check_password_hash
import socket

import xml.etree.ElementTree as ET, requests, ast

from defs import *
from performance import *
from retorno import *
from usuarios import *
from query import *
from consultas import *
from preferencias import *
from soap import *


db_file = os.path.dirname(os.path.abspath("bruce.ipynb")) +"\\bases\\bruce.accdb"
odbc_conn_str = 'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=' + db_file
conn = pyodbc.connect(odbc_conn_str,autocommit=True,timeout=1)

# df = pd.read_sql('''SELECT NO_BASE, DS_USER, DS_PASS, DS_DNS, DS_STR 
#     FROM TBASES WHERE NO_BASE = 'REMEDY' ''',conn)

# dns = df['DS_DNS'][0].split(',')
# senha = df['DS_PASS'][0]
# usuario = df['DS_USER'][0]

# dsnStr = cx_Oracle.makedsn(dns[0],dns[1],dns[2]) 
# con_remedy = cx_Oracle.connect(user=usuario, password=senha, dsn=dsnStr)


app = Flask(__name__)
app.config['SECRET_KEY'] = 'hashsometHingthatcantberepliedneVer'

app.register_blueprint(performance)
app.register_blueprint(retorno)
app.register_blueprint(usuarios)
app.register_blueprint(query)
app.register_blueprint(consultas)
app.register_blueprint(preferencias)
app.register_blueprint(soap)
