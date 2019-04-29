from flask import Flask, render_template, request, flash, url_for, session, app, Response, Blueprint
import cx_Oracle #, threading
from flask_sqlalchemy import SQLAlchemy
import datetime as dt, pyodbc, time
import hashlib
from dateutil.relativedelta import *
import io
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

import pandas as pd, json, numpy as np
import plotly, plotly.graph_objs as go

from dataframes import *
from defs import *
from performance import *
from query import *


app = Flask(__name__)
app.config['SECRET_KEY'] = 'hashsometHingthatcantberepliedneVer'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bases/bruce.sqlite3'
app.config['PERMANENT_SESSION_LIFETIME'] = 1200 #tempo em segundos
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.register_blueprint(performance)

db = SQLAlchemy(app)

class usuario(db.Model):
#    id = db.Column(db.Integer, primary_key = True)
    matricula = db.Column(db.String(10), primary_key = True)
    nome = db.Column(db.String(300))
    senha = db.Column(db.String(50))

    def __init__(self, matricula, nome, senha):
        self.matricula = matricula
        self.nome = nome
        self.senha = senha


class tlog(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    matricula = db.Column(db.String(10))
    descricao = db.Column(db.String)
    dt = db.Column(db.DateTime)
    ip = db.Column(db.String)

    def __init__(self, matricula, descricao, dt, ip):
        self.matricula = matricula
        self.descricao = descricao
        self.dt = dt
        self.ip = ip


class tequipe(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    dt = db.Column(db.DateTime)
    matricula = db.Column(db.String(10))
    nome = db.Column(db.String(300))
    operacao = db.Column(db.String)

    def __init__(self, dt, matricula, nome, operacao):
        self.dt = dt
        self.matricula = matricula
        self.nome = nome
        self.operacao = operacao


class tform(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    formulario = db.Column(db.String)
    dificuldade = db.Column(db.String)

    def __init__(self, formulario, dificuldade):
        self.formulario = formulario
        self.dificuldade = dificuldade


