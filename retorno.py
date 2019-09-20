from classes import *

retorno = Blueprint('retorno', __name__,url_prefix="/retorno")

@retorno.route('/valida_login',methods=['POST'])
def valida_login():
    if not 'logado' in session:
        # session['logado'] = False
        return render_template("top.html"), 200

    if request.method == 'POST':
        ds_login = req('ds_login')
        df = pd.read_sql('SELECT FL_ATIVO FROM TUSUARIO WHERE DS_LOGIN = ?',g.conn,params=[ds_login])
        if df.size > 0:
            msg = ''
            if df['FL_ATIVO'][0] == 0:
                msg = ' mas encontra-se Bloqueado'

            return '''
                <script>
                    parent.document.getElementById("ds_login").value = "";
                    parent.document.getElementById("ds_login").focus();
                </script>
                <span style="color:red;font-size:14px">Usuário já existe '''+ msg +'''</span>'''
        else:
            return ''
    

@retorno.route('/excluir_login', methods=['POST','GET'])    
def excluir_login():
    try:
        id_usuario = req("id_usuario")
        ds_login = req('ds_login')
        no_usuario = req('no_usuario')

        g.cur.execute('''UPDATE TUSUARIO SET FL_ATIVO = 0, DT_ATUALIZACAO = NOW(), FK_USUARIO_ATUALIZACAO = ?
            WHERE ID_USUARIO = ?''',(session['id_usuario'], id_usuario))

        sql = "INSERT INTO TLOG (FK_TIPO_LOG, FK_USUARIO_CADASTRO, DS_IP, DS_LOG) VALUES (?,?,?,?)"
        g.cur.execute (sql,(4,session['id_usuario'],session['ip'], 'Inativação do usuário '+ ds_login +' - '+ no_usuario))

        return '''
                <script>
                    parent.window.location.href = "'''+ url_for('usuarios.index') +'''";
                </script>
                '''
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        lista = (exc_type, fname, exc_tb.tb_lineno)
        msg = ' '.join(str(i) for i in lista)
        return '<script>alert("'+ msg +'")</script>'


@retorno.route('/atu_acesso',methods=['POST','GET'])
def atu_acesso():
    # try:
    id_usuario = req('id_usuario')
    id_tipo = reqls('id_tipo')

    # ds_login = req('ds_login')
    no_usuario = req('no_usuario')
    ds_email = req('ds_email')
    fl_ativo = req('fl_ativo')
    ds_host = req('ds_host')

    g.cur.execute('''UPDATE TUSUARIO SET NO_USUARIO = ?, DS_EMAIL = ?, FL_ATIVO = ?, DS_HOST = ?
        WHERE ID_USUARIO = ?
        ''',(no_usuario,ds_email,fl_ativo,ds_host,id_usuario))

    g.cur.execute('DELETE FROM TUSUARIO_ACESSO WHERE FK_USUARIO = ?', id_usuario)
    for x in id_tipo:
        g.cur.execute('''
            INSERT INTO TUSUARIO_ACESSO (FK_USUARIO, FK_TIPO_ACESSO, FK_USUARIO_CADASTRO)
            VALUES (?, ?, ?)''', (id_usuario, x, session['id_usuario']))
    
    flash('Dados Atualizados com Sucesso!')

    return '''
            <script>
                parent.window.location.href = "'''+ url_for('usuarios.index') +'''";
            </script>
            '''
    # except Exception as e:
    #     exc_type, exc_obj, exc_tb = sys.exc_info()
    #     fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    #     lista = (exc_type, fname, exc_tb.tb_lineno)
    #     msg = ' '.join(str(i) for i in lista)
    #     return '<script>alert("'+ msg +'");parent.window.history.back();</script>'


@retorno.route('/css', methods=['POST','GET'])    
def css():
    try:
        ds_estilo = req('ds_estilo')
        g.cur.execute ('UPDATE TUSUARIO SET DS_ESTILO = ? WHERE ID_USUARIO = ?',(ds_estilo, session['id_usuario']))
        session['estilo'] = ds_estilo
        return '''
                <script>
                    parent.window.location.href = "'''+ url_for('preferencias.index') +'''";
                </script>
                '''
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        lista = (exc_type, fname, exc_tb.tb_lineno)
        msg = ' '.join(str(i) for i in lista)
        return '<script>alert("'+ msg +'")</script>'


@retorno.route('/plc_soap', methods=['POST','GET'])    
def plc_soap():
    id_soap = req('id_soap')
    df = pd.read_sql('''SELECT DS_SOAP, DS_PARAMETROS FROM TSOAP WHERE ID_SOAP = ?''',g.conn, params=[id_soap])
    if df.size > 0:
        msg = df['DS_SOAP'][0]
        plc = df['DS_PARAMETROS'][0]
        return '''
            <script>
                parent.document.getElementById("dv_ds").innerHTML = "'''+ msg +'''";
                parent.document.getElementById("ds_parametros").placeholder = "'''+ plc +'''";
                parent.document.getElementById("ds_parametros").focus();
            </script>
            '''
    else:
        return '''
            <script>
                alert('Erro\n'''+ str(id_soap) +''');
            </script>
            '''

