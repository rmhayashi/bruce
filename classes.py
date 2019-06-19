from flask import Flask, render_template, request, flash, url_for, session, app, Response, Blueprint
import cx_Oracle #, threading
from flask_sqlalchemy import SQLAlchemy
import xml.etree.ElementTree as ET

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
from xmlgen import *


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
        
        
class XML(object):

    def __init__(self, cnlCode, nrc,  cnlAcronym, streetType, streetName, streetNumber,
                       district, city, stateOrProvince, streetCode, tecnology, hasBA, orderType,
                       ddd, checkDigit, telephoneNumber, telephonicArea, productCode, office,identifier,
                       operationType, productTopologyType, productTopologyCategory, portabilityCode, serviceOrderNumber):

        self.cnlCode = cnlCode
        self.nrc = nrc
        self.cnlAcronym = cnlAcronym
        self.streetType = streetType
        self.streetName = streetName
        self.streetNumber = streetNumber
        self.district = district
        self.city = city
        self.stateOrProvince = stateOrProvince
        self.streetCode = streetCode
        self.tecnology = tecnology
        self.hasBA = hasBA
        self.orderType = orderType
        self.ddd = ddd

        self.checkDigit = checkDigit
        self.telephoneNumber = telephoneNumber
        self.telephonicArea = telephonicArea
        self.productCode = productCode
        self.office = office
        self.operationType = operationType
        self.identifier = identifier
        self.productTopologyType = productTopologyType
        self.productTopologyCategory = productTopologyCategory
        self.portabilityCode = portabilityCode
        self.serviceOrderNumber = serviceOrderNumber
        
    def indent(elem, level=0):
        i = "\n" + level * "  "
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + "  "
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
            for elem in elem:
                indent(elem, level + 1)
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i

    # WebServices do sigres

    def sigReserve(self):
        # XML REALIZA RESERVA

        ns_res = {'xmlns:soapenv': 'http://schemas.xmlsoap.org/soap/envelope/',
                  'xmlns:all': 'http://service.vivo.com.br/oss/ServiceManagementAndOperations/ServiceConfigurationActivation/ServiceInventoryMgt/v3/AllocateSpecificServiceParameterstoServices',
                  'xmlns:loc': 'http://model.vivo.com.br/OSS/v2/CommonBusiness/Location',
                  'xmlns:prod': 'http://model.vivo.com.br/OSS/v2/Product/Product',
                  'xmlns:res': 'http://model.vivo.com.br/OSS/v2/Common/Result',
                  'xmlns:cus': 'http://model.vivo.com.br/OSS/v2/Customer/Customer',
                  'xmlns:prod1': 'http://model.vivo.com.br/OSS/v5/Product/Product'}

        no_envelope = ET.Element('soapenv:Envelope', ns_res)

        no_header = ET.SubElement(no_envelope, "soapenv:Header")
        no_body = ET.SubElement(no_envelope, "soapenv:Body")

        no_reserveParams = ET.SubElement(no_body, 'all:ReserveServiceParameters_Request')

        no_listTerminal = ET.SubElement(no_reserveParams, "all:listTerminal")
        ET.SubElement(no_listTerminal, 'loc:cnlCode').text = self.cnlCode
        ET.SubElement(no_listTerminal, 'loc:conjugate').text = "0"
        ET.SubElement(no_listTerminal, 'loc:ddd').text = self.ddd
        ET.SubElement(no_listTerminal, 'loc:checkDigit').text = self.checkDigit
        ET.SubElement(no_listTerminal, 'loc:telephoneNumber').text = self.telephoneNumber

        ET.SubElement(no_reserveParams, "all:nrc").text = self.nrc

        no_station = ET.SubElement(no_reserveParams, "all:station")
        ET.SubElement(no_station, 'loc:cnlAcronym').text = self.cnlAcronym
        ET.SubElement(no_station, 'loc:telephonicArea').text = self.telephonicArea

        no_reservations = ET.SubElement(no_reserveParams, "all:reservations")
        no_reservation = ET.SubElement(no_reservations, 'loc:Reservation')

        no_product = ET.SubElement(no_reservation, "loc:product")
        no_productClass = ET.SubElement(no_product, "prod:productClass")

        ET.SubElement(no_product, 'prod:productCode').text = self.productCode
        ET.SubElement(no_product, 'prod:productTopologyType').text = self.productTopologyType
        ET.SubElement(no_product, 'prod:productTopologyCategory').text = self.productTopologyCategory

        no_operationType = ET.SubElement(no_reserveParams, 'all:operationType').text = self.operationType

        no_customerAddress = ET.SubElement(no_reserveParams, 'all:customerAddress')
        ET.SubElement(no_customerAddress, 'loc:streetType').text = self.streetType
        ET.SubElement(no_customerAddress, 'loc:streetName').text = self.streetName
        ET.SubElement(no_customerAddress, 'loc:streetNumber').text = self.streetNumber
        ET.SubElement(no_customerAddress, 'loc:district').text = self.district
        ET.SubElement(no_customerAddress, 'loc:city').text = self.city
        ET.SubElement(no_customerAddress, 'loc:stateOrProvince').text = self.stateOrProvince
        ET.SubElement(no_customerAddress, 'loc:postCode')
        ET.SubElement(no_customerAddress, 'loc:streetCode').text = self.streetCode

        no_portabilityCode = ET.SubElement(no_reserveParams, "all:portabilityCode").text = self.portabilityCode
        no_expirationPeriod = ET.SubElement(no_reserveParams, "all:expirationPeriod").text = "360"

        no_networkTerminal = ET.SubElement(no_reserveParams, "all:networkTerminal")
        ET.SubElement(no_networkTerminal, 'loc:cnlCode').text = self.cnlCode

        no_networkStation = ET.SubElement(no_reserveParams, "all:networkStation")
        ET.SubElement(no_networkStation, 'loc:telephonicArea').text = self.telephonicArea

        no_serviceOrderNumber = ET.SubElement(no_reserveParams, "all:serviceOrderNumber").text = self.serviceOrderNumber
        no_originSystem = ET.SubElement(no_reserveParams, "all:originSystem").text = "GVT"
        no_fixedLineHas = ET.SubElement(no_reserveParams, "all:fixedLineHas").text = "N"

        indent(no_envelope)
        root = ET.tostring(no_envelope)
        return root

    def sigConfirm(self):
        # XML CONFIRMA RESERVA

        ns_con = {'xmlns:soapenv': 'http://schemas.xmlsoap.org/soap/envelope/',
                       'xmlns:all': 'http://service.vivo.com.br/oss/ServiceManagementAndOperations/ServiceConfigurationActivation/ServiceInventoryMgt/v3/AllocateSpecificServiceParameterstoServices',
                       'xmlns:loc': 'http://model.vivo.com.br/OSS/v6/CommonBusiness/Location',
                       'xmlns:prod': 'http://model.vivo.com.br/OSS/v2/Product/Product',
                       'xmlns:res': 'http://model.vivo.com.br/OSS/v2/Common/Result',
                       'xmlns:loc1': 'http://model.vivo.com.br/OSS/v2/CommonBusiness/Location',
                       'xmlns:cus': 'http://model.vivo.com.br/OSS/v5/Customer/Customer',
                       'xmlns:loc2':'http://model.vivo.com.br/OSS/v5/CommonBusiness/Location'}

        no_envelope = ET.Element('soapenv:Envelope', ns_con)

        no_header = ET.SubElement(no_envelope, "soapenv:Header")
        no_body = ET.SubElement(no_envelope, "soapenv:Body")

        no_allocateParams = ET.SubElement(no_body, 'all:AllocateServiceParameters_Request')

        no_reservation = ET.SubElement(no_allocateParams, "all:reservation")
        ET.SubElement(no_reservation, 'loc:identifier').text = self.identifier

        no_product = ET.SubElement(no_reservation, "loc:product")
        ET.SubElement(no_product, 'prod:productCode').text = self.productCode
        ET.SubElement(no_product, 'prod:productTopologyType').text = self.productTopologyType
        ET.SubElement(no_product, 'prod:productTopologyCategory').text = self.productTopologyCategory

        no_terminal = ET.SubElement(no_allocateParams, 'all:terminal')
        ET.SubElement(no_terminal, 'loc1:cnlCode').text = self.cnlCode
        ET.SubElement(no_terminal, 'loc1:conjugate').text = "0"
        ET.SubElement(no_terminal, 'loc1:checkDigit').text = self.checkDigit
        ET.SubElement(no_terminal, 'loc1:telephoneNumber').text = self.telephoneNumber

        no_serviceOrderNumber = ET.SubElement(no_allocateParams, 'all:ServiceOrderNumber').text = self.serviceOrderNumber

        no_station = ET.SubElement(no_allocateParams, 'all:station')
        ET.SubElement(no_station, 'loc2:telephonicArea').text = self.telephonicArea

        no_originSystem = ET.SubElement(no_allocateParams, 'all:originSystem').text = 'GVT'
        no_portabilityType = ET.SubElement(no_allocateParams, 'all:portabilityType').text = self.portabilityCode

        indent(no_envelope)
        root = ET.tostring(no_envelope)
        return root

    def sigCancel(self):
        # XML CANCELA RESERVA

        ns_can = {'xmlns:soapenv': 'http://schemas.xmlsoap.org/soap/envelope/',
                       'xmlns:all': 'http://service.vivo.com.br/oss/ServiceManagementAndOperations/ServiceConfigurationActivation/ServiceInventoryMgt/v3/AllocateSpecificServiceParameterstoServices',
                       'xmlns:loc': 'http://model.vivo.com.br/OSS/v2/CommonBusiness/Location',
                       'xmlns:prod': 'http://model.vivo.com.br/OSS/v2/Product/Product',
                       'xmlns:res': 'http://model.vivo.com.br/OSS/v2/Common/Result',
                       'xmlns:loc1': 'http://model.vivo.com.br/OSS/v4/CommonBusiness/Location',
                       'xmlns:loc2': 'http://model.vivo.com.br/OSS/v5/CommonBusiness/Location'}

        no_envelope = ET.Element('soapenv:Envelope', ns_can)

        no_header = ET.SubElement(no_envelope, "soapenv:Header")
        no_body = ET.SubElement(no_envelope, "soapenv:Body")

        no_releaseParams = ET.SubElement(no_body, 'all:ReleaseAllocateServiceParameters_Request')

        no_reservation = ET.SubElement(no_releaseParams, "all:reservation")
        ET.SubElement(no_reservation, 'loc:identifier').text = self.identifier

        no_product = ET.SubElement(no_reservation, "loc:product")

        ET.SubElement(no_product, 'prod:productTopologyType').text = self.productTopologyType
        ET.SubElement(no_product, 'prod:operationType').text = self.operationType
        ET.SubElement(no_product, 'prod:productTopologyCategory').text = self.productTopologyCategory

        no_originSystem = ET.SubElement(no_envelope, "all:originSystem").text = "GVT"

        indent(no_envelope)
        root = ET.tostring(no_envelope)
        return root

    def sigActivate(self):
        # XML ATIVA RESERVA

        ns_ocu = {'xmlns:soapenv': 'http://schemas.xmlsoap.org/soap/envelope/',
                       'xmlns:imp': 'http://service.vivo.com.br/oss/ServiceManagementAndOperations/ServiceConfigurationActivation/ServiceInventoryMgt/v2/ImplementConfigureAndActivateService',
                       'xmlns:prod': 'http://model.vivo.com.br/OSS/v2/Product/Product',
                       'xmlns:loc': 'http://model.vivo.com.br/OSS/v2/CommonBusiness/Location',
                       'xmlns:res': 'http://model.vivo.com.br/OSS/v5/Resource/Resource',
                       'xmlns:loc1': 'http://model.vivo.com.br/OSS/v5/CommonBusiness/Location',
                       'xmlns:loc2': 'http://model.vivo.com.br/OSS/v5/CommonBusiness/Location'}

        no_envelope = ET.Element('soapenv:Envelope', ns_ocu)

        no_header = ET.SubElement(no_envelope, "soapenv:Header")
        no_body = ET.SubElement(no_envelope, "soapenv:Body")

        no_activeReserve = ET.SubElement(no_body, 'imp:ActivateService_Request')

        no_originSystem = ET.SubElement(no_activeReserve, "imp:originSystem").text = "GVT"
        no_serviceOrderNumber = ET.SubElement(no_activeReserve, "imp:serviceOrderNumber").text = self.serviceOrderNumber
        no_operationType = ET.SubElement(no_activeReserve, 'imp:operationType').text = self.operationType

        no_product = ET.SubElement(no_activeReserve, "imp:product")
        ET.SubElement(no_product, 'prod:productCode').text = self.productCode
        ET.SubElement(no_product, 'prod:productTopologyType').text = self.productTopologyType
        ET.SubElement(no_product, 'prod:productTopologyCategory').text = self.productTopologyCategory

        no_terminal = ET.SubElement(no_activeReserve, 'imp:terminal')
        ET.SubElement(no_terminal, 'loc:cnlCode').text = self.cnlCode
        ET.SubElement(no_terminal, 'loc:conjugate').text = "0"
        ET.SubElement(no_terminal, 'loc:checkDigit').text = self.checkDigit
        ET.SubElement(no_terminal, 'loc:telephoneNumber').text = self.telephoneNumber

        no_office = ET.SubElement(no_activeReserve, 'imp:office').text = self.office

        no_station = ET.SubElement(no_activeReserve, 'imp:station')
        ET.SubElement(no_station, 'loc2:cnlAcronym').text = self.cnlAcronym
        ET.SubElement(no_station, 'loc2:telephonicArea').text = self.telephonicArea

        no_installationIndicative = ET.SubElement(no_activeReserve, 'imp:installationIndicative').text = 0

        indent(no_envelope)
        root = ET.tostring(no_envelope)
        return root


