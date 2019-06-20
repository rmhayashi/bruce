from classes import *

@app.before_request
def before():
    if 'logado' in session:
        if session['logado']:
            session['logado'] = session['logado']
            session['nome'] = session['nome']
            session['matricula'] = session['matricula']
            # print(session.logado)


@app.route("/")
def main():
    session['logado'] = False
    return render_template("default.html"), 200


@app.route("/login",methods=['GET', 'POST'])
def login():
    matricula = req('matricula')
    senha = req('senha')
    alt_senha = req('alt_senha')

    if matricula == senha:
        if alt_senha == 'S':
            senha = req('nova_senha')
            nova_senha = md5(req('nova_senha'))
            usuario.query.filter_by(matricula = matricula).update({'senha' : nova_senha})
            flash('Senha atualizada com Sucesso!')
            fl = ''
            logs = tlog(matricula,'Alteração de Senha', dt.datetime.now(), request.remote_addr)
            db.session.add(logs)
            db.session.commit()
        else:
            fl = 'S'
            flash("Necessário Alterar Senha")

        return render_template("default.html",**locals()), 200
    else:
        v = usuario.query.filter_by(matricula = req('matricula'),senha = md5(req('senha'))).first()
        if v:
            session['logado'] = True
            session['nome'] = v.nome
            session['matricula'] = v.matricula
            session['ip'] = request.remote_addr
        else:
            flash('Matrícula ou Senha incorretos!')
            return render_template("default.html")


    return render_template("top.html",**locals()), 200



@app.route("/novo",methods=['POST','GET'])
def novo():
    if not 'logado' in session:
        session['logado'] = False
        return render_template("top.html"), 200

    funcao_menu = 'Controle de Usuários'

    if request.method == 'POST':
        user = usuario(req('matricula'),req('nome'),req('matricula'))
        db.session.add(user)
        flash('Usuário Cadastrado com Sucesso!')

    usrs = usuario.query.filter(usuario.matricula != '80656720',usuario.matricula != '80479177').order_by('nome').all()

    return render_template('novo.html',**locals())



@app.route("/logs",methods=['POST','GET'])
def logs():
    if not 'logado' in session:
        session['logado'] = False
        return render_template("top.html"), 200

    funcao_menu = 'Log de Acessos e Consultas'

    dt1 = dt.datetime.now().date()
    dt2 = dt.datetime.now().date()

    if request.method == 'POST':
        dt1 = req('dt1')
        dt2 = req('dt2')
        dt1f = dt.datetime.strptime(dt1,'%Y-%m-%d')
        dt2f = dt.datetime.strptime(dt2,'%Y-%m-%d') + dt.timedelta(days=1)
        # logs = tlog.query.order_by('dt').all()
        logs = tlog.query.join(usuario,tlog.matricula == usuario.matricula) \
            .add_columns(tlog.id, tlog.dt, tlog.matricula, usuario.nome, tlog.descricao, tlog.ip) \
            .filter(tlog.dt >= dt1f, tlog.dt <= dt2f).order_by('dt').all()

    return render_template('logs.html',**locals())



@app.route("/valida_login",methods=['POST','GET'])
def valida_login():
    if not 'logado' in session:
        session['logado'] = False
        return render_template("top.html"), 200

    if request.method == 'POST':
        matricula = req('matricula')
        if req('acao') == 'select':
            v = usuario.query.filter_by(matricula = matricula).first()
            if v:
                return '''
                    <script>
                        parent.document.getElementById("matricula").value = "";
                        parent.document.getElementById("matricula").focus();
                    </script>
                    <span style="color:red;font-size:14px">Usuário Já Existe</span>'''
            else:
                return ''
        elif req('acao') == 'excluir' and session['matricula'] in ('80656720','80479177'):
            logs = tlog(session['matricula'],'Exclusão Usuário '+ matricula, dt.datetime.now(), session['ip'])
            db.session.add(logs)

            usuario.query.filter_by(matricula = req('matricula')).delete()
            return '''
                    <script>
                        parent.window.location.href = '/novo';
                    </script>
                    '''
        else:
            return '<script>alert("Sem Acesso!")</script>'


@app.route("/query",methods=['GET', 'POST'])
def query():
    if not 'logado' in session:
        session['logado'] = False
        return render_template("top.html"), 200

    funcao_menu = 'Consultas Construídas pelo Usuário'

    ds_base = req("ds_base")
    
    def monta_base():
        sel = ''
        sel_base = ''
        conexao = ''
        df = pd.read_csv('bases/bases_oracle.csv',sep=';')
        df = df.sort_values(by = ['base'])
        for x, y in df[df['status'] == 1][['base','conexao']].values:
            if ds_base == x:
                sel = 'selected'
                conexao = y
            else:
                sel = ''
            sel_base += '<option value="'+ x +'" '+ sel +'>'+ x +'</option>'
        return sel_base, df, conexao

    sel_base, df, conexao = monta_base()

    if request.method == 'POST':
        query = str(req("query")).replace(";","").strip()
        pd.set_option('display.max_colwidth', -1)
        
        if query[0:6].upper() != 'SELECT':
            flash('NÃO É POSSÍVEL EXECUTAR')
            return render_template("query.html", **locals())
        else:
            try:
                conn_oracle = cx_Oracle.connect(conexao)
                # conn_oracle.callTimeout(1)
                df_o = pd.read_sql(query, conn_oracle)
                resultado = df_o
                tables=[df_o.to_html(classes='rel')]

                logs = tlog(session['matricula'], ds_base + ' ['+ query + ']', dt.datetime.now(), session['ip'])
                db.session.add(logs)

                return render_template("query.html", **locals())

            except Exception as e:
                if str(e).find('password') > 0:
                    df.loc[df['base'] == ds_base, 'status'] = 0
                    df.to_csv('bases/bases_oracle.csv',sep=';',index=False)
                flash(e)
                sel_base, df, conexao = monta_base()
                return render_template("query.html", **locals())

return render_template("query.html", **locals())



@app.route("/consultas",methods=['GET', 'POST'])
def consultas():
    if not 'logado' in session:
        session['logado'] = False
        return render_template("top.html"), 200

    funcao_menu = 'Consultas Pré-Construídas'

    ds_tipo = req('ds_tipo')
    ds_campo = str(req('ds_campo')).replace(";","").strip()

    base, sel_base, query = query_builder(ds_tipo, ds_campo)

    if request.method == 'POST':
        pd.set_option('display.max_colwidth', -1)

        df = pd.read_csv('bases/bases_oracle.csv',sep=';')
        conexao = df[df['base'] == base]['conexao'].to_string(index=False)
        try:
            conn_oracle = cx_Oracle.connect(conexao)
            df_o = pd.read_sql(query, conn_oracle)
            resultado = df_o
            tables=[df_o.to_html(classes='rel')]

            logs = tlog(session['matricula'], base + ' ['+ query + ']', dt.datetime.now(), session['ip'])
            db.session.add(logs)

            return render_template("queries.html", **locals())

        except Exception as e:
                flash(e)
                return render_template("queries.html", **locals())
    return render_template("queries.html", sel_base = sel_base, ds_campo = '', funcao_menu = funcao_menu)


@app.route('/webservices', methods=['GET', 'POST'])
def gerar_xml():
<<<<<<< HEAD
=======
    
>>>>>>> 6ebb39c93bdeefe6bc16f16e582b390d36bece14
    if not 'logado' in session:
        session['logado'] = False
        return render_template("top.html"), 200

    funcao_menu = 'Gerador de XML'
<<<<<<< HEAD

=======
    
>>>>>>> 6ebb39c93bdeefe6bc16f16e582b390d36bece14
    sel_op = ''
    sel = ''
    result = ''
    operacao = ''
    data = []
    data2 = []

    op_type = req("op_type")
    txt_order = req("txt_order")
<<<<<<< HEAD

    pd.set_option('display.max_colwidth', -1)

=======
    
    pd.set_option('display.max_colwidth', -1)
    
>>>>>>> 6ebb39c93bdeefe6bc16f16e582b390d36bece14
    df = pd.read_csv('operacoes.csv', sep=';')
    df = df.sort_values(by=['op_type'])

    for x, y in df[['op_type', 'operacao']].values:

        if op_type == x:
            sel = 'selected'
            operacao = y
        else:

            sel = ''
            sel_op += '<option value="' + x + '" ' + sel + '>' + x + '</option>'

<<<<<<< HEAD
=======

>>>>>>> 6ebb39c93bdeefe6bc16f16e582b390d36bece14
    if request.method == "POST":
        try:

            conn_pweb = cx_Oracle.connect()  # DEVE-SE PREENCHER CONEXÃO
<<<<<<< HEAD
            conn_sieb8 = cx_Oracle.connect()  # DEVE-SE PREENCHER CONEXÃO
=======
            conn_sieb8 = cx_Oracle.connect() # DEVE-SE PREENCHER CONEXÃO
>>>>>>> 6ebb39c93bdeefe6bc16f16e582b390d36bece14

            querys8 = ("""SELECT sap.x_cnl, asset_integ_id, sap.x_cnl_code, sap.x_street_type, sap.ADDR, sap.x_number,
                   sap.x_neighborhood, sap.city, sap.state, x_street_code, soi.X_ACCESS_TECHNOLOGY, so.X_GVT_GERA_BA ,x_order_type,
                      substr(SERVICE_NUM, 0,2)
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
                    and so.INTEGRATION_ID in ('{}')
                    AND spi.name = 'Linha Telefônica';""".format(txt_order))

            df_s8 = pd.read_sql(querys8, conn_sieb8)

            # Passa os dados do banco para um array

            for row in df_s8:
                data.append(row)

            tecnologia = data[10]
            geraBA = data[11]
            ot = data[12]

            # Verifica qual consulta deve ser executada.

            if tecnologia == "METALICO":
                querypwb = ("""
                    SELECT substr(substr(xml_translate,instr(xml_translate,'</can:serviceId>') -1 ),0,1),
                    substr(substr(xml_translate,instr(xml_translate,'</can:serviceId>') -10 ),0,8),
                    substr(substr(xml_translate,instr(xml_translate,'</can:telephonicArea>') -2 ),0,2),
                    substr(substr(xml_translate,instr(xml_translate,'</can:provisioningCode>') -6 ),0,6),
                    substr(substr(xml_translate,instr(xml_translate,'</can:centralOffice>') -2 ),0,2),
                    substr(substr(xml_translate,instr(xml_translate,'</can:customerOrderType>') -6 ),0,6),
                    RESERVA , substr(substr(xml_translate,instr(xml_translate,'</can:mediaType>') -4 ),0,4),
                    substr(substr(xml_translate,instr(xml_translate,'</can:serviceId>') -5 ),0,5)
                    FROM omanagement_owner.reserves
                    WHERE
                    reserva IS NOT NULL
                    AND   pon IN ('{}')
                    AND DESIGNADOR LIKE '%013';
                    """.format(txt_order))

            else:
                querypwb = ("""
                    SELECT
                    substr(substr(xml_translate, instr(xml_translate, '</can:serviceId>') - 1 ), 0, 1),
                    substr(substr(xml_translate, instr(xml_translate, '</can:serviceId>') - 10), 0, 8),
                    substr(substr(xml_translate, instr(xml_translate, '</can:telephonicArea>') - 2), 0, 2),
                    substr(substr(xml_translate, instr(xml_translate, '</can:provisioningCode>') - 6), 0, 6),
                    substr(substr(xml_translate, instr(xml_translate, '</can:centralOffice>') - 2), 0, 2),
                    substr(substr(xml_translate, instr(xml_translate, '</can:customerOrderType>') - 6), 0, 6),
                    RESERVA, substr(substr(xml_translate, instr(xml_translate, '</can:mediaType>') - 5), 0, 5),
                    substr(substr(xml_translate, instr(xml_translate, '</can:serviceId>') - 5), 0, 5)
                    FROM omanagement_owner.reserves
                    WHERE reserva IS NOT NULL
                    AND pon IN('{}')
                    AND DESIGNADOR LIKE '%013';
                    """.format(txt_order))

            df_pwb = pd.read_sql(querypwb, conn_pweb)

            for row in df_pwb:
                data2.append(row)

            data2.append(txt_order)

            # Verifica se é uma reserva e qual a tecnologia

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

<<<<<<< HEAD
            xmlSig = xmlSigres(data[0], data[1], data[2], data[3], data[4],
=======
            xmlSig = XML(data[0], data[1], data[2], data[3], data[4],
>>>>>>> 6ebb39c93bdeefe6bc16f16e582b390d36bece14
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
                return '<script>alert("Operacao inválida!")</script>'
<<<<<<< HEAD

            logs = tlog(session['matricula'], operacao + ' [' + xmlSig + ']', dt.datetime.now(), session['ip'])
            db.session.add(logs)

            return render_template("xmlgen.html", **locals())

        except Exception as e:
            flash(e)
            return render_template("xmlgen.html", **locals())

    return render_template("xmlgen.html", sel_op=sel_op, result='', funcao_menu=funcao_menu)

=======
                
            logs = tlog(session['matricula'], operacao + ' ['+ xmlSig + ']', dt.datetime.now(), session['ip'])
            db.session.add(logs)

            return render_template("xmlgen.html",**locals())

        except Exception as e:
            flash(e)
            return render_template("xmlgen.html",**locals())
        
    return render_template("xmlgen.html", sel_op=sel_op, result='', funcao_menu=funcao_menu)


>>>>>>> 6ebb39c93bdeefe6bc16f16e582b390d36bece14
if __name__ == "__main__":
    db.create_all()
    app.run(debug=True, use_reloader=True, port=5000, host='0.0.0.0')
