from classes import *

soap = Blueprint('soap', __name__,url_prefix="/soap")

# MONTA O SELECT DE OPÇÕES DE SOAP
def monta_opcao():
        sel_soap = ''
        id_soap = req('id_soap')
        df = pd.read_sql('''SELECT ID_SOAP, NO_SOAP FROM TSOAP WHERE FL_ATIVO = 1 ORDER BY NO_SOAP''', g.conn)
        
        for x, y in df[['ID_SOAP','NO_SOAP']].values:
            if str(id_soap) == str(x):
                sel = 'selected'
            else:
                sel = ''
            sel_soap += '<option value="'+ str(x) +'" '+ sel +'>'+ y +'</option>'
        return sel_soap

# CONECTA NAS BASES NECESSÁRIAS
def conectar():
    con_change,con_edition,con_sales,con_bill_change,con_bill_edition,con_bill_sales = '','','','','',''

    df = pd.read_sql('''SELECT NO_BASE, DS_STR 
        FROM TBASES WHERE NO_BASE IN 
            ('SAVVION CHANGE', 'SAVVION EDITION', 'SAVVION SALES',
            'SAVVION BILLING CHANGE','SAVVION BILLING EDITION','SAVVION BILLING SALES')
        ORDER BY NO_BASE
        ''',g.conn)
    try:
        con_change = cx_Oracle.connect(df[df['NO_BASE'] == 'SAVVION CHANGE']['DS_STR'].iloc[0])
    except Exception as e:
        flash('Falha na Savvion Change - '+ str(e))
        pass

    try:   
        con_edition = cx_Oracle.connect(df[df['NO_BASE'] == 'SAVVION EDITION']['DS_STR'].iloc[0])
    except Exception as e:
        flash('Falha na Savvion Edition - '+ str(e))
        pass

    try:
        con_sales = cx_Oracle.connect(df[df['NO_BASE'] == 'SAVVION SALES']['DS_STR'].iloc[0])
    except Exception as e:
        flash('Falha na Savvion Sales - '+ str(e))
        pass
    
    try:
        con_bill_change = cx_Oracle.connect(df[df['NO_BASE'] == 'SAVVION BILLING CHANGE']['DS_STR'].iloc[0])
    except Exception as e:
        flash('Falha na Savvion Billing Change - '+ str(e))
        pass

    try: 
        con_bill_edition = cx_Oracle.connect(df[df['NO_BASE'] == 'SAVVION BILLING EDITION']['DS_STR'].iloc[0])
    except Exception as e:
        flash('Falha na Savvion Billing Edition - '+ str(e))
        pass

    try:
        con_bill_sales = cx_Oracle.connect(df[df['NO_BASE'] == 'SAVVION BILLING SALES']['DS_STR'].iloc[0])
    except Exception as e:
        flash('Falha na Savvion Billing Sales - '+ str(e))
        pass

    return con_change,con_edition,con_sales,con_bill_change,con_bill_edition,con_bill_sales

############################################## EXCEÇÃO DE SAVVION E BYPASS ####################################################
def excecao_savvion(incidente,ordem):
    df = pd.DataFrame(columns=['INCIDENTE', 'ORDEM', 'PROCESSO','ATIVIDADE', 'BASE'])
    try:
        con_change, con_edition, con_sales, con_bill_change, con_bill_edition, con_bill_sales = conectar()
        
        df = pd.DataFrame(columns=['INCIDENTE', 'ORDEM', 'PROCESSO', 'ATIVIDADE', 'BASE'])

        df_c = pd.read_sql("""SELECT '"""+ incidente +"""' AS INCIDENTE, PON ORDEM, PRCTEMPLATENAME PROCESSO, 
            ATIVIDADEQUEDEUERRO AS ATIVIDADE, 
            --EXCEPTIONMESSAGE AS ERRO, 
            'CHANGE' AS BASE
            FROM SAV_FULFILLMENT_OWNER.BIZLOGIC_DS_204 CHANGE
            WHERE PON = '"""+ ordem +"""'""",con_change)
        if df_c['ORDEM'].count() > 0:
            df = df.append(df_c, ignore_index=True, sort=True)

        df_e = pd.read_sql("""SELECT '"""+ incidente +"""' AS INCIDENTE, PON ORDEM, PRCTEMPLATENAME PROCESSO, 
            ATIVIDADEQUEDEUERRO AS ATIVIDADE, 
            --EXCEPTIONMESSAGE AS ERRO, 
            'EDITION' AS BASE
            FROM SAV_FULFILLMENT_OWNER.BIZLOGIC_DS_119 EDITION
            WHERE PON = '"""+ ordem +"""'""",con_edition)
        if df_e['ORDEM'].count() > 0:
            df = df.append(df_e, ignore_index=True, sort=True)

        df_s = pd.read_sql("""SELECT '"""+ incidente +"""' AS INCIDENTE, PON ORDEM, PRCTEMPLATENAME PROCESSO, 
            ATIVIDADEQUEDEUERRO AS ATIVIDADE, 
            --EXCEPTIONMESSAGE AS ERRO, 
            'SALES' AS BASE
            FROM SAV_FULFILLMENT_OWNER.BIZLOGIC_DS_46 SALES
            WHERE PON = '"""+ ordem +"""'""",con_sales)
        if df_s['ORDEM'].count() > 0:
            df = df.append(df_s, ignore_index=True, sort=True)

        df.drop_duplicates(keep='first',inplace=True)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        lista = (exc_type, fname, exc_tb.tb_lineno)
        msg = ' '.join(str(i) for i in lista)
        flash(msg)

    return df[['INCIDENTE', 'ORDEM', 'PROCESSO', 'ATIVIDADE', 'BASE']]

def soap_execute_bypass(incidente,ordem,atividade,senha):
    try:
        url="http://sv2kpint1:7001/IT_Suporte_Integracao_WS_v2/SavvionBaOnlineService"
        headers = {'content-type': 'text/xml;charset=iso-8859-1'}
        body = '''
            <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ws="http://ws.itss.gvt.com/">
            <soapenv:Header/>
            <soapenv:Body>
                <ws:byPassAtividade>
                    <userManagement>
                        <username>{}</username>
                        <password>{}</password>
                    </userManagement>
                    <maquina>{}</maquina>
                    <pon>{}</pon>
                    <atividade>{}</atividade>
                    <savvion>baonline</savvion>
                    <incidente>{}</incidente>
                </ws:byPassAtividade>
            </soapenv:Body>
            </soapenv:Envelope>
        '''
        body = body.format(session['matricula'], senha, session['hostname'], ordem, atividade, incidente)

        xml_file = requests.post(url,data=body,headers=headers)
        tree = ET.fromstring(xml_file.content)
        root = tree.find('.//{http://schemas.xmlsoap.org/soap/envelope/}Body').find('.//{http://ws.itss.gvt.com/}byPassAtividadeResponse').find('Resultado')

        codigo, mensagem = root.find('codigo').text, root.find('mensagem').text

        log = body + ' | '+ mensagem

        sql = "INSERT INTO TLOG (FK_TIPO_LOG, FK_USUARIO_CADASTRO, DS_IP, DS_LOG) VALUES (?,?,?,?)"
        g.cur.execute (sql,(15,session['id_usuario'],session['ip'], log))
    
    except Exception as e:
        flash(xml_file)
        codigo = 500
        mensagem = str(e)

    return codigo, mensagem

def soap_bypass(incidente,ordem,senha):
    df = excecao_savvion(incidente,ordem)
    table = ''
    resultado = ''
    html = ''

    if df.size < 5: # DEVIDO AOS 5 CAMPOS DO DATAFRAME
        flash('Ordem '+ ordem +' sem Exceção!')
    
    elif df.size == 5:
        if df['ATIVIDADE'][0] not in ('AddCircuitISR','Decomposition','Split ServiceOrders Provisioning','SplitSupplementa SOManagement','Start Billing Flow','Suspend Processes','Call Gathering OM WS'):

            codigo, mensagem = soap_execute_bypass(incidente,ordem,df['ATIVIDADE'][0],senha)
            
            if mensagem == 'Erro ao realizar complete work item':
                flash('Senha de rede inválida!')
            
            elif mensagem == 'Sucesso':
                resultado = 'Bypass executado com Sucesso!'
                table = excecao_savvion(incidente,ordem)
                if table.size > 5:
                    table = [table.to_html(classes='rel',index=False)]
                    flash('Ordem retornou mais exceção!')
                else:
                    table = ''
            
            else:
                flash(mensagem)

        else:
            flash('Exceção '+ df['ATIVIDADE'][0] +' não pode ser executado Bypass!')
    
    else: # ORDEM COM MAIS DE UMA EXCEÇÃO PRECISA SELECIONAR QUAL VAI EXECUTAR BYPASS
        html = '''
            <form name="frm_bypass" method="post" action="'''+ url_for('soap.multibypass') +'''">
            <table class="rel">
                <thead>
                    <tr>
            '''
        for x in df[['INCIDENTE', 'ORDEM', 'PROCESSO', 'ATIVIDADE', 'BASE']].columns.values:
            html += '<th>'+ x +'</th>'

        html += '''
                    <th>BYPASS</th>
                </tr>
            </thead>
            <tbody>'''

        for ix, x in df[['INCIDENTE', 'ORDEM', 'PROCESSO', 'ATIVIDADE', 'BASE']].iterrows():
            html += '''
                <tr>
                    <td style="text-align:center">'''+ x['INCIDENTE'] +'''</td>
                    <td style="text-align:center">'''+ x['ORDEM'] +'''</td>
                    <td>'''+ x['PROCESSO'] +'''</td>
                    <td>'''+ x['ATIVIDADE'] +'''</td>
                    <td>'''+ x['BASE'] +'''</td>
                    <td style="text-align:center"><input type="checkbox" name="excecao" value="'''+ x['ATIVIDADE'] +'''"></td>
                </tr>'''

        html += '''
                <tr>
                    <td colspan="6" style="text-align:center">
                        <input type="hidden" name="incidente" id="incidente" value="'''+ incidente +'''">
                        <input type="hidden" name="ordem" id="ordem" value="'''+ ordem +'''">
                        <input type="hidden" name="senha" id="ds_senha" value="'''+ senha +'''">
                        <input type="submit" name="btnBypass" value="BYPASS MÚLTIPLAS EXCEÇÕES">
                    </td>
                </tbody>
            </table>
            
            </form>'''

        flash('Ordem com mais de uma Exceção! Selecione a(s) Exceção a ser executado "Bypass".')
        

    return table, resultado, html

############################################## FIM DA EXCEÇÃO DE SAVVION E BYPASS #############################################


############################################## REEXECUTAR SAVVION ####################################################
def soap_reexecute_savvion(incidente,ordem,atividade,senha):
    try:
        url="http://sv2kpint1:7001/IT_Suporte_Integracao_WS_v2/SavvionBaOnlineService"
        headers = {'content-type': 'text/xml;charset=iso-8859-1'}
        body = '''
            <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ws="http://ws.itss.gvt.com/">
            <soapenv:Header/>
            <soapenv:Body>
                <ws:reexecutarExcecao>
                    <pon>{}</pon>
                    <atividade>{}</atividade>
                    <savvion>baonline</savvion>
                    <incidente>{}</incidente>
                    <maquina>{}</maquina>
                    <usuario>{}</usuario>
                    <senha>{}</senha>
                </ws:reexecutarExcecao>
            </soapenv:Body>
            </soapenv:Envelope>
        '''
        # body = body.format(ordem, atividade, incidente, 'NPRCURJBR7028TX', '80514494', 'c0uv3fl*r')
        body = body.format(ordem, atividade, incidente, session['hostname'], session['matricula'], senha)

        xml_file = requests.post(url,data=body,headers=headers)
        tree = ET.fromstring(xml_file.content)
        root = tree.find('.//{http://schemas.xmlsoap.org/soap/envelope/}Body').find('.//{http://ws.itss.gvt.com/}reexecutarExcecaoResponse').find('Resultado')

        codigo, mensagem = root.find('codigo').text, root.find('mensagem').text

        log = body + ' | '+ mensagem

        sql = "INSERT INTO TLOG (FK_TIPO_LOG, FK_USUARIO_CADASTRO, DS_IP, DS_LOG) VALUES (?,?,?,?)"
        g.cur.execute (sql,(15,session['id_usuario'],session['ip'], log))

    except Exception as e:
        codigo = 500
        mensagem = str(e)

    return codigo, mensagem

def soap_reexecute(incidente,ordem,senha):
    df = excecao_savvion(incidente,ordem)
    table = ''
    resultado = ''
    html = ''

    if df.size < 5: # DEVIDO AOS 5 CAMPOS DO DATAFRAME
        flash('Ordem '+ ordem +' sem Exceção!')
    
    elif df.size == 5:
        codigo, mensagem = soap_execute_bypass(incidente,ordem,df['ATIVIDADE'][0],senha)
        
        if mensagem == 'Erro ao realizar complete work item':
            flash('Senha de rede inválida!')
        
        elif mensagem == 'Sucesso':
            resultado = 'Bypass executado com Sucesso!'
            table = excecao_savvion(incidente,ordem)
            if table.size > 5:
                table = [table.to_html(classes='rel',index=False)]
                flash('Ordem retornou mais exceção!')
            else:
                table = ''
        
        else:
            flash(mensagem)

    
    else: # ORDEM COM MAIS DE UMA EXCEÇÃO PRECISA SELECIONAR QUAL VAI EXECUTAR BYPASS
        html = '''
            <form name="frm_bypass" method="post" action="'''+ url_for('soap.multireexecute') +'''">
            <table class="rel">
                <thead>
                    <tr>
            '''
        for x in df[['INCIDENTE', 'ORDEM', 'PROCESSO', 'ATIVIDADE', 'BASE']].columns.values:
            html += '<th>'+ x +'</th>'

        html += '''
                    <th>REEXECUTAR EXCEÇÃO</th>
                </tr>
            </thead>
            <tbody>'''

        for ix, x in df[['INCIDENTE', 'ORDEM', 'PROCESSO', 'ATIVIDADE', 'BASE']].iterrows():
            html += '''
                <tr>
                    <td style="text-align:center">'''+ x['INCIDENTE'] +'''</td>
                    <td style="text-align:center">'''+ x['ORDEM'] +'''</td>
                    <td>'''+ x['PROCESSO'] +'''</td>
                    <td>'''+ x['ATIVIDADE'] +'''</td>
                    <td>'''+ x['BASE'] +'''</td>
                    <td style="text-align:center"><input type="checkbox" name="excecao" value="'''+ x['ATIVIDADE'] +'''"></td>
                </tr>'''

        html += '''
                <tr>
                    <td colspan="6" style="text-align:center">
                        <input type="hidden" name="incidente" id="incidente" value="'''+ incidente +'''">
                        <input type="hidden" name="ordem" id="ordem" value="'''+ ordem +'''">
                        <input type="hidden" name="senha" id="ds_senha" value="'''+ senha +'''">
                        <input type="submit" name="btnBypass" value="REEXECUTAR MÚLTIPLAS EXCEÇÕES">
                    </td>
                </tbody>
            </table>
            
            </form>'''

        flash('Ordem com mais de uma Exceção! Selecione a(s) Exceção(ões) para serem reexecutadas.')
        

    return table, resultado, html

############################################## FIM DE REEXECUTAR SAVVION #############################################


############################################## EXCEÇÃO DE BILLING ####################################################
def excecao_billing(incidente,ordem):
    df = pd.DataFrame(columns=['INCIDENTE', 'ORDEM', 'PROCESSO','ATIVIDADE', 'BASE'])

    try:
        con_change, con_edition, con_sales, con_bill_change, con_bill_edition, con_bill_sales = conectar()

        df_c = pd.read_sql ("""
            SELECT '"""+ incidente +"""' INCIDENTE, B1.NUMEROORDEM ORDEM,
                B1.PROCESS_INSTANCE_ID PROCESSO, WI.WORKSTEP_NAME ATIVIDADE,
                --B2.EXCEPTIONMESSAGE EXCECAO, 
                'BILLING CHANGE' BASE
            FROM SAV_BILLING_OWNER.BIZLOGIC_DS_31 B1
                LEFT JOIN SAV_BILLING_OWNER.BIZLOGIC_DS_33 B2 ON B1.PROCESS_INSTANCE_ID = B2.PROCESSINSTANCEID
                LEFT JOIN SAV_BILLING_OWNER.BIZLOGIC_WORKSTEPINSTANCE WI ON B1.PROCESS_INSTANCE_ID = WI.PROCESS_INSTANCE_ID
                    AND WI.ENDTIME = 0
            WHERE B1.NUMEROORDEM = '"""+ ordem +"""' """, con_bill_change)
        if df_c['ORDEM'].count() > 0:
            df = df.append(df_c, ignore_index=True, sort=True)


        df_e = pd.read_sql ("""
            SELECT '"""+ incidente +"""' INCIDENTE, B1.NUMEROORDEM ORDEM,
                B1.PROCESS_INSTANCE_ID PROCESSO, WI.WORKSTEP_NAME ATIVIDADE, 
                --B2.EXCEPTIONMESSAGE EXCECAO, 
                'BILLING EDITION' BASE
            FROM SAV_BILLING_OWNER.BIZLOGIC_DS_36 B1
                LEFT JOIN SAV_BILLING_OWNER.BIZLOGIC_DS_37 B2 ON B1.PROCESS_INSTANCE_ID = B2.PROCESSINSTANCEID
                LEFT JOIN SAV_BILLING_OWNER.BIZLOGIC_WORKSTEPINSTANCE WI ON B1.PROCESS_INSTANCE_ID = WI.PROCESS_INSTANCE_ID 
                    AND WI.ENDTIME = 0
            WHERE B1.NUMEROORDEM = '"""+ ordem +"""' """,con_bill_edition)
        if df_e['ORDEM'].count() > 0:
            df = df.append(df_e, ignore_index=True, sort=True)


        df_s = pd.read_sql("""
            SELECT DISTINCT '"""+ incidente +"""' INCIDENTE, BO.NUMEROORDEM ORDEM, 
                BO.PROCESS_INSTANCE_ID PROCESSO, WI.WORKSTEP_NAME ATIVIDADE,
                --EX.EXCEPTIONMESSAGE EXCECAO, 
                'BILLING SALES' BASE
            FROM SAV_BILLING_OWNER.PROCESSINSTANCE PI
                INNER JOIN SAV_BILLING_OWNER.BILLINGORDER BO ON BO.PROCESS_INSTANCE_ID = PI.PROCESS_INSTANCE_ID
            LEFT JOIN SAV_BILLING_OWNER.BIZLOGIC_DS_34 EX ON EX.PROCESSINSTANCEID=BO.PROCESS_INSTANCE_ID
            LEFT JOIN SAV_BILLING_OWNER.BIZLOGIC_WORKSTEPINSTANCE WI ON BO.PROCESS_INSTANCE_ID = WI.PROCESS_INSTANCE_ID
                AND WI.ENDTIME = 0
            WHERE BO.NUMEROORDEM = '"""+ ordem +"""' """,con_bill_sales)
        if df_s['ORDEM'].count() > 0:
            df = df.append(df_s, ignore_index=True, sort=True)
            
        df.drop_duplicates(keep='first',inplace=True)
    
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        lista = (exc_type, fname, exc_tb.tb_lineno)
        msg = ' '.join(str(i) for i in lista)
        flash(msg)
        
    return df[['INCIDENTE', 'ORDEM', 'PROCESSO','ATIVIDADE', 'BASE']]

def soap_reexecuta_bill(incidente,ordem,atividade,excecao,senha):
    try:
        url="http://sv2kpint1:7001/IT_Suporte_Integracao_WS_v2/SavvionBillingNSService"
        headers = {'content-type': 'text/xml;charset=iso-8859-1'}
        body = '''    
            <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ws="http://ws.itss.gvt.com/">
            <soapenv:Header/>
            <soapenv:Body>
                <ws:reexecutarExcecao>
                    <userManagement>
                        <username>{}</username>
                        <password>{}</password>
                    </userManagement>
                    <maquina>{}</maquina>
                    <pon>{}</pon>
                    <atividade>{}</atividade>
                    <excecao>{}</excecao>
                    <savvion>billing</savvion>
                    <incidente>{}</incidente>
                </ws:reexecutarExcecao>
            </soapenv:Body>
            </soapenv:Envelope>
            '''
        body = body.format(session['matricula'], senha, session['hostname'], ordem, atividade, excecao, incidente)

        xml_file = requests.post(url,data=body,headers=headers)
        tree = ET.fromstring(xml_file.content)
        
        root = tree.find('.//{http://schemas.xmlsoap.org/soap/envelope/}Body').find('.//{http://ws.itss.gvt.com/}reexecutarExcecaoResponse').find('Resultado')
        
        codigo, mensagem = root.find('codigo').text, root.find('mensagem').text
        
        log = body + ' | '+ mensagem

        sql = "INSERT INTO TLOG (FK_TIPO_LOG, FK_USUARIO_CADASTRO, DS_IP, DS_LOG) VALUES (?,?,?,?)"
        g.cur.execute (sql,(17,session['id_usuario'],session['ip'], log))
        
    except Exception as e:
        codigo = 500
        mensagem = str(e)

    return codigo, mensagem

def soap_billing(incidente,ordem,senha):
    df = excecao_billing(incidente,ordem)
    table = ''
    resultado = ''
    html = ''

    if df.size < 5: # DEVIDO AOS 5 CAMPOS DO DATAFRAME
        flash('Ordem '+ ordem +' sem Exceção!')
    
    elif df.size == 5:
        excecao = df['ATIVIDADE'][0]
        codigo, mensagem = soap_reexecuta_bill(incidente,ordem,df['ATIVIDADE'][0],excecao,senha)
            
        if mensagem == 'Erro ao realizar complete work item':
            flash('Senha de rede inválida!')
        
        elif mensagem == 'Sucesso':
            resultado = 'Bypass executado com Sucesso!'
            df = excecao_billing(incidente,ordem)
            if df.size >= 5:
                table = [df.to_html(classes='rel',index=False)]
                flash('Ordem retornou mais exceção!')
            else:
                table = ''
        
        else:
            flash(mensagem)

    return table, resultado, html

############################################## FIM DA EXCEÇÃO DE BILLING #############################################

@soap.route("/",methods=['GET', 'POST'])
def index():
    funcao_menu = 'SOAP'

    id_soap = req('id_soap')
    ds_parametros = str(req('ds_parametros')).strip()
    ds_senha = req('ds_senha')

    sel_soap = monta_opcao()

    if request.method == 'POST':
        if id_soap == '1': # bypass baonline
            lista = ds_parametros.split(',')
            if len(lista) != 2:
                flash('Parâmetros Incorretos!')
                return render_template("soap.html", **locals())
            else:
                incidente = lista[0].strip()
                ordem = lista[1].strip()

                table, resultado, html = soap_bypass(incidente,ordem,ds_senha)

                return render_template("soap.html", **locals())

        if id_soap == 3: # REEXECUTAR EXCEÇÃO DE BILLING
            lista = ds_parametros.split(',')
            if len(lista) != 2:
                flash('Parâmetros Incorretos!')
                return render_template("soap.html", **locals())
            else:
                incidente = lista[0].strip()
                ordem = lista[1].strip()

                table, resultado, html = soap_billing(incidente,ordem,ds_senha)

                return render_template("soap.html", **locals())

        if id_soap == 4: # REEXECUTAR SAVVION
            lista = ds_parametros.split(',')
            if len(lista) != 2:
                flash('Parâmetros Incorretos!')
                return render_template("soap.html", **locals())
            else:
                incidente = lista[0].strip()
                ordem = lista[1].strip()

                table, resultado, html = soap_reexecute(incidente,ordem,ds_senha)

                return render_template("soap.html", **locals())

            
    return render_template("soap.html", **locals())


# ORDEM COM MAIS DE UMA EXCEÇÃO NECESSITA SELECTIONAR QUAL DAR BYPASS
@soap.route("/multibypass",methods=['GET', 'POST'])
def multibypass():
    incidente = req('incidente')
    ordem = req('ordem')
    senha = req('senha')
    excecao = reqls('excecao')
    codigo = ''
    mensagem = ''
    mensagemt = ''
    resultado = ''
    table = ''
    html = ''

    for x in excecao:
        codigo, mensagemt = soap_execute_bypass(incidente,ordem,x,senha)
        if mensagemt == 'Sucesso':
            resultado += x +' - Bypass executado com Sucesso<br>'
        else:
            resultado += x +' - Erro: '+ mensagem
        time.sleep(7.7)

    return render_template("soap.html", **locals())


# ORDEM COM MAIS DE UMA EXCEÇÃO NECESSITA SELECTIONAR QUAL REEXECUTAR
@soap.route("/multireexecute",methods=['GET', 'POST'])
def multireexecute():
    incidente = req('incidente')
    ordem = req('ordem')
    senha = req('senha')
    excecao = reqls('excecao')
    codigo = ''
    mensagem = ''
    mensagemt = ''
    resultado = ''
    table = ''
    html = ''

    for x in excecao:
        codigo, mensagemt = soap_reexecute_savvion(incidente,ordem,x,senha)
        if mensagemt == 'Sucesso':
            resultado += x +' - Reexecução realizada com Sucesso!<br>'
        else:
            resultado += x +' - Erro: '+ mensagem
        time.sleep(7.7)

    return render_template("soap.html", **locals())




############################## CÓDIGO ABAIXO SERIA LENDO O CÓDIGO DO XML NO BANCO #################################################
        #     df = pd.read_sql('''SELECT DS_URL, DS_HEADERS, DS_XML, DS_ROOT, DS_RETORNO
        #         FROM TSOAP WHERE ID_SOAP = ?''',g.conn, params=[id_soap])
            
        #     ds_url = df['DS_URL'][0]
        #     ds_headers = ast.literal_eval(df['DS_HEADERS'][0])
        #     ds_xml = df['DS_XML'][0].format(ds_parametros)

        #     xml_file = requests.post(ds_url,headers=ds_headers,data=ds_xml)
        #     tree = ET.fromstring(xml_file.content)

        #     retorno = xml_file.content
        # try:
        #     conn_oracle = cx_Oracle.connect(conexao)
        #     df_o = pd.read_sql(query, conn_oracle)
        #     resultado = df_o
        #     tables=[df_o.to_html(classes='rel')]

        #     sql = "INSERT INTO TLOG (FK_TIPO_LOG, FK_USUARIO_CADASTRO, DS_IP, DS_LOG) VALUES (?,?,?,?)"
        #     g.cur.execute (sql,(3,session['id_usuario'],session['ip'], base + ' - '+ query))

        #     return render_template("consultas.html", **locals())

        # except Exception as e:
        #     sql = "INSERT INTO TLOG (FK_TIPO_LOG, FK_USUARIO_CADASTRO, DS_IP, DS_LOG) VALUES (?,?,?,?)"
        #     g.cur.execute (sql,(13,session['id_usuario'],session['ip'], query +' - '+ str(e)))

        #     if str(e).find('password') > 0:
        #         g.cur.execute('UPDATE BASES_ORACLE SET STATUS = 0 WHERE BASE = ?', base)
        #         g.cur.execute (sql,(4,session['id_usuario'],session['ip'], 'Inativação de Logon Oracle - Base '+ base))
        #         base, sel_base, query = query_builder(ds_tipo, ds_campo)

        #     flash(e)
    # 
    
    # return render_template("soap.html", sel_soap = sel_soap, ds_parametros = '', funcao_menu = funcao_menu)

##################################################################################################################################

