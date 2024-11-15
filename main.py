from classes import *

@app.before_request
def before_request():
    session.permanent = True
    app.permanent_session_lifetime = dt.timedelta(minutes=30)
    g.conn = conn
    g.cur = conn.cursor()

    # g.con_remedy = con_remedy

    if 'logado' not in session:
        g.menu = None
        if request.endpoint not in ('login','main','static'):
            flash('Sessão Expirada!')
            return redirect(url_for('main'))
    else:
        g.menu = monta_menu()


@app.route("/")
def main():
    session.pop('logado', None)
    return render_template("default.html"), 200


@app.route("/login",methods=['POST'])
def login():
    ds_login = req('ds_login')
    ds_senha = req('ds_senha')
    alt_senha = req('alt_senha')
    nova_senha = req('nova_senha')

    if ds_login == ds_senha:
        if alt_senha == 'S':
            try:
                ds_senha = md5(nova_senha)
                sql = "UPDATE TUSUARIO SET DS_SENHA = ? WHERE DS_LOGIN = ?"
                g.cur.execute (sql,(ds_senha, ds_login))
                flash('Senha atualizada com Sucesso!')
                fl = ''
                sql = "SELECT ID_USUARIO FROM TUSUARIO WHERE DS_LOGIN = ?"
                df = pd.read_sql(sql, g.conn,params=[ds_login])
                id_usuario = int(df['ID_USUARIO'][0])
                sql = "INSERT INTO TLOG (FK_TIPO_LOG, FK_USUARIO_CADASTRO, DS_IP, DS_LOG) VALUES (?,?,?,?)"
                g.cur.execute (sql,(4,id_usuario,request.remote_addr, 'Alteração de senha'))
            except Exception as e:
                flash('Login inexistente ou bloqueado!')
                return render_template("default.html")
        else:
            fl = 'S'
            flash("Necessário Alterar Senha")
        
        return render_template("default.html",**locals()), 200
    else:
        try:
            sql = '''
                SELECT ID_USUARIO, DS_LOGIN, NO_USUARIO, DS_SENHA, FL_ATIVO, DS_ESTILO, DS_HOST
                FROM TUSUARIO 
                WHERE DS_LOGIN = ? AND FL_ATIVO = 1
                '''
            df = pd.read_sql(sql, g.conn, params=[ds_login])
            v = vmd5(ds_senha,df['DS_SENHA'][0])
            if v:
                session['logado'] = True
                session['id_usuario'] = str(df['ID_USUARIO'][0])
                session['nome'] = str(df['NO_USUARIO'][0])
                session['matricula'] = str(df['DS_LOGIN'][0])
                session['ip'] = request.remote_addr
                session['estilo'] = str(df['DS_ESTILO'][0])
                # hostname = socket.gethostbyaddr(request.remote_addr)
                # session['hostname'] = hostname[0].upper().replace('.REDECORP.BR','').replace('.GVT.NET.BR','')
                session['hostname'] = df['DS_HOST'][0]
                sql = "INSERT INTO TLOG (FK_TIPO_LOG, FK_USUARIO_CADASTRO, DS_IP, DS_LOG) VALUES (?,?,?,?)"
                g.cur.execute (sql,(2,session['id_usuario'],session['ip'], 'Acesso ao sistema'))
                g.cur.execute('UPDATE TUSUARIO SET DT_ACESSO = NOW() WHERE ID_USUARIO = ?',session['id_usuario'])

                g.menu = monta_menu()

                return render_template("top.html",**locals()), 200
            else:
                flash('Login ou Senha incorretos!')
                return render_template("default.html")
        except Exception as e:
            flash('Login inexistente ou bloqueado!')
            return render_template("default.html")

 
@app.route("/logs",methods=['POST','GET'])
def logs():
    funcao_menu = 'Log de Acessos e Consultas'

    dt1 = dt.datetime.now().date()
    dt2 = dt.datetime.now().date()
    
    if request.method == 'POST':
        dt1 = req('dt1')
        dt2 = req('dt2')
        dt1f = dt.datetime.strptime(dt1,'%Y-%m-%d')
        dt2f = dt.datetime.strptime(dt2,'%Y-%m-%d') + dt.timedelta(days=1)
        
        params = (dt1f,dt2f)
        # table = g.cur.execute('''SELECT * FROM VW_LOG V WHERE DATA BETWEEN ? AND ? ORDER BY V.ID_LOG''',params)

        table = pd.read_sql('''SELECT * FROM VW_LOG V WHERE DATA BETWEEN ? AND ? ORDER BY V.ID_LOG''',g.conn,params=params)
        table = [table.to_html(classes='rel',index=False)]
        
    return render_template('logs.html',**locals())


if __name__ == "__main__":
    app.run(debug=True, use_reloader=True,port=5000,host='0.0.0.0')