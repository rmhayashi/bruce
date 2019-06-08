# -*- coding: utf-8 -*-
from classes import *
from xmlgenerator import *

xmlgen = Blueprint('xmlgen', __name__, url_prefix='/xmlgen')

@xmlgen.route('/', methods=['GET', 'POST'])
def gerar_xml():

    sel_op = ''
    sel = ''
    result = ''
    operacao = ''
    data = []
    data2 = []
    dado = []
    dado2 = []

    # Busca o nome do field do html que a variável irá controlar

    op_type = request.form.get("op_type")
    txt_order = request.form.get("txt_order")

    # Realiza a leitura do arquivo operacoes.csv contida no src

    df = pd.read_csv('operacoes.csv', sep=';')
    df = df.sort_values(by=['op_type'])

    # Sorteia os valores do arquivo csv para exibir na view

    for x, y in df[['op_type', 'operacao']].values:

        if op_type == x:
            sel = 'selected'
            operacao = y
        else:

            sel = ''
            sel_op += '<option value="' + x + '" ' + sel + '>' + x + '</option>'


    if request.method == "POST":
        try:
            # Conexao com o banco de dados Oracle

            conn_pweb = cx_Oracle.connect() # DEVE-SE PREENCHER CONEXÃO
            conn_sieb8 = cx_Oracle.connect() # DEVE-SE PREENCHER CONEXÃO

            # DEVE-SE ADICIONAR OS CAMPOS TECNOLOGIA, GERABA, TIPO_ORDEM & DDD DA TABELA DO SIEBEL8

            querys8 = (
            	'''
            	    SELECT sap.x_cnl, asset_integ_id, sap.x_cnl_code, sap.x_street_type, sap.ADDR, sap.x_number,
            	      sap.x_neighborhood, sap.city, sap.state, x_street_code, TECNOLOGIA, GERABA, TIPO_ORDEM, DDD
                    from siebel.s_order so,
                    siebel.s_order_item soi,
                    siebel.s_prod_int spi,
                    siebel.s_org_ext soe,
                    siebel.s_addr_per sap
                    where so.ROW_ID = soi.ORDER_ID
                    and soi.PROD_ID = spi.ROW_ID
                    and so.bill_accnt_id = soe.row_id
                    and soi.x_serv_addr_id = sap.ROW_ID
                    and sap.X_ACCOUNT_ID = soe.ROW_ID
                    and soi.PROD_ID in ('1-7HWB','1-5WPB','1-C1SQ','1-F7ISQ')
                    and so.INTEGRATION_ID in ("''' + txt_order + '''")
                    AND spi.name = 'Linha Telefônica';
                    ''')


            querypwb = ('''
                SELECT substr(substr(xml_translate,instr(xml_translate,'</%:serviceId>') -1 ),0,1),
                substr(substr(xml_translate,instr(xml_translate,'</%:serviceId>') -10 ),0,8),
                substr(substr(xml_translate,instr(xml_translate,'</%:telephonicArea>') -2 ),0,2),
                substr(substr(xml_translate,instr(xml_translate,'</%:provisioningCode>') -6 ),0,6),
                substr(substr(xml_translate,instr(xml_translate,'</%:office>') -2 ),0,2),
                substr(substr(xml_translate,instr(xml_translate,'</%:customerOrderType>') -6 ),0,6),
                RESERVA , substr(substr(xml_translate,instr(xml_translate,'</%:mediaType>') -5 ),0,5),
                substr(substr(xml_translate,instr(xml_translate,'</%:serviceId>') -5 ),0,5)
                FROM omanagement_owner.reserves
                WHERE
                reserva IS NOT NULL
                AND   pon IN ("''' + txt_order + '''");
                ''')


            df_s8 = pd.read_sql(querys8, conn_sieb8)
            df_pwb = pd.read_sql(querypwb, conn_pweb)

            for row in df_s8:
                data.append(row)
            for row in df_pwb:
                data2.append(row)

            data2.append(txt_order)

            # Busca qual será o tipo da ordem no Siebel8 por meio da variável "ot"
            # Busca na sieb8 se a ordem gera ou não BA
            # Busca a tecnologia da Ordem

            ot = data[12]
            geraBA = data[11]
            tecnologia = data[10]

            # Esta linha verifica se deve buscar dados da base da icweb ou preencher com
            # dados da base sieb8

            if tecnologia == "METALICO":

                productTopologyType = "ADSL"
                productTopologyCategory = ""

                if operacao == "res":

                    if geraBA == "SIM" and ot == "Mudança de Oferta" or ot == "Edição de Oferta":
                        operationType = "ALTPRO"

                    elif geraBA == "NAO" and ot == "Mudança de Oferta" or ot == "Edição de Oferta":
                        operationType = "ALTPED"

                    elif ot == "Mudança de Endereço":
                        operationType = "MUDEND"

                    elif operacao == "res" and ot == "Venda de Oferta":
                        operationType = "INSADI"

                else:

                    operationType = data2[5]
                    productTopologyType = data2[7]
                    productTopologyCategory = data2[8]

            else:

                productTopologyType = "FIBRA"
                productTopologyCategory = "VOIP2"
                data[13] = ""

                if operacao == "res":

                    if geraBA == "SIM" and ot == "Mudança de Oferta" or ot == "Edição de Oferta":
                        operationType = "ALTPRO"
                    elif geraBA == "NAO" and ot == "Mudança de Oferta" or ot == "Edição de Oferta":
                        operationType = "ALTPED"
                    elif ot == "Mudança de Endereço":
                        operationType = "MUDEND"
                    elif operacao == "res" and ot == "Venda de Oferta":
                        operationType = "INSADI"
                        data2[1] = "NDS"
                        data2[0] = "DV"

                else:

                    operationType = data2[5]
                    productTopologyType = data2[7]
                    productTopologyCategory = data2[8]

            # Preenchimento dos parâmetros do shape do XML com dados do Oracle, base
            # da icweb e sieb8

            xmlSig = XML(data[0], data[1], data[2], data[3], data[4],
                      data[5], data[6], data[7], data[8], data[9],
                      data[10], data[11], data[12], data[13], data2[0],
                      data2[1], data2[2], data2[3], data2[4], data2[6],
                      operationType, productTopologyType, productTopologyCategory,
                      "N", txt_order)

            # VERIFICA A FUNÇÃO QUE DEVE SER EXECUTADA
            # POR MEIO DO TIPO DE OPERAÇÃO SELECIONADA

            if operacao == "res":
                result = xmlSig.sigReserve()

            elif operacao == "can":
                result = xmlSig.sigCancel()

            elif operacao == "con":
                result = xmlSig.sigConfirm()

            elif operacao == "ocu":
                result = xmlSig.sigActivate()

            elif operacao == "OPERACAO":
                flash("Operacao inválida!")

            return render_template("xmlgen.html", sel_op=sel_op, result=result)

        except Exception as e:
            flash(e)
            return render_template("xmlgen.html", sel_op=sel_op)

    return render_template("xmlgen.html", sel_op=sel_op)



