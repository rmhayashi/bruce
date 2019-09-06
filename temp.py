# import requests
# url="https://apps.correios.com.br/SigepMasterJPA/AtendeClienteService/AtendeCliente"
# #headers = {'content-type': 'application/soap+xml'}
# headers = {'content-type': 'text/xml; charset=utf-8'}
# body = '''
#         <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:cli="http://cliente.bean.master.sigep.bsb.correios.com.br/">
#     <soapenv:Header/>
#     <soapenv:Body>
#         <cli:consultaCEP>
#             <cep>{}</cep>
#         </cli:consultaCEP>
#     </soapenv:Body>
#     </soapenv:Envelope>'''

# response = requests.post(url,data=body,headers=headers)
# print(response.content)

nome = input("Digite seu nome: ")
print(nome)
# import requests
# url="http://sv2kpint1:7001/IT_Suporte_Integracao_WS_v2/SavvionBaOnlineService?wsdl"
# headers = {'content-type': 'application/soap+xml'}
# # headers = {'content-type': 'text/xml'}
# body = """
#     <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ws="http://ws.itss.gvt.com/">
#    <soapenv:Header/>
#    <soapenv:Body>
#       <ws:byPassAtividade>
#          <pon>8-A613B6914E8-1</pon>
#          <atividade>ConfirmarReservaRecursosAdapter</atividade>
#          <savvion>baonline</savvion>
#          <incidente>INC000000000000</incidente>
#          <maquina>NPRCURJB0000000</maquina>
#          <usuario>USUARIO DE REDE</usuario>
#          <senha>SENHA DE REDE</senha>
#       </ws:byPassAtividade>
#    </soapenv:Body>
# </soapenv:Envelope>
# """

# response = requests.post(url,data=body,headers=headers)
# print(response.content)


# import requests
# url="http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL"
# #headers = {'content-type': 'application/soap+xml'}
# headers = {'content-type': 'text/xml'}
# body = """<?xml version="1.0" encoding="UTF-8"?>
#          <SOAP-ENV:Envelope xmlns:ns0="http://ws.cdyne.com/WeatherWS/" xmlns:ns1="http://schemas.xmlsoap.org/soap/envelope/" 
#             xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/">
#             <SOAP-ENV:Header/>
#               <ns1:Body><ns0:GetWeatherInformation/></ns1:Body>
#          </SOAP-ENV:Envelope>"""

# response = requests.post(url,data=body,headers=headers)
# print response.content