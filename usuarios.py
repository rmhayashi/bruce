from classes import *

usuarios = Blueprint('usuarios', __name__,url_prefix="/usuarios")

@usuarios.route("/",methods=['POST','GET'])
def index():
    funcao_menu = 'Controle de Usuários'
    try:
        if request.method == 'POST':
            ds_senha = md5(req('ds_login'))
            user = (req('ds_login'), req('no_usuario'), req('ds_email'), ds_senha, req('ds_host'), session['id_usuario'])
            g.cur.execute ('''INSERT INTO TUSUARIO (DS_LOGIN, NO_USUARIO, DS_EMAIL, DS_SENHA, DS_HOST, FK_USUARIO_CADASTRO) 
                VALUES (?,UCASE(?),LCASE(?),?,?,?) ''',user)
            g.cur.execute("SELECT @@IDENTITY AS ID_USUARIO")
            id_usuario = g.cur.fetchone()
            id_usuario = int(id_usuario.ID_USUARIO)
            for x in list([7,8,12,14]): # ACESSOS PADRÃO 7 QUERY, 8 CONSULTAS PRONTAS, 12 PERFORMANCE, 14 CONFIGURAÇÕES
                g.cur.execute ('''INSERT INTO TUSUARIO_ACESSO (FK_USUARIO, FK_TIPO_ACESSO, FK_USUARIO_CADASTRO) 
                    VALUES (?,?,?)''', (id_usuario, x, session['id_usuario']))
            flash('Usuário Cadastrado com Sucesso!')

        table = g.cur.execute('''SELECT ID_USUARIO, DS_LOGIN, NO_USUARIO, DT_ACESSO, FL_ATIVO, DS_EMAIL
            FROM TUSUARIO WHERE ID_USUARIO > 1
            ORDER BY FL_ATIVO DESC, NO_USUARIO''')
    except Exception as e:
        flash(str(e))

    return render_template('usuarios.html',**locals())


@usuarios.route('/acessos',methods=['POST','GET'])
def acessos():
    funcao_menu = 'Controle de Usuários \ Acessos'
    if request.method == 'POST':
        try:
            id_usuario = req('id_usuario')
            df = pd.read_sql('''SELECT DS_LOGIN, NO_USUARIO, DS_EMAIL, FL_ATIVO, DS_HOST
                FROM TUSUARIO WHERE ID_USUARIO = ?
                ''', g.conn, params=[id_usuario])
            ds_login = df['DS_LOGIN'][0]
            no_usuario = df['NO_USUARIO'][0]
            ds_email = df['DS_EMAIL'][0]
            fl_ativo = df['FL_ATIVO'][0]
            ds_host = df['DS_HOST'][0]

            params = (id_usuario)
            dft = pd.read_sql('SELECT ID_TIPO, DS_TIPO FROM TTIPO WHERE FK_TIPO = 6 AND FL_ATIVO = 1 ORDER BY DS_TIPO', g.conn)
            dfa = pd.read_sql('''
                SELECT ID_USUARIO_ACESSO, ID_TIPO
                FROM VW_USUARIO_ACESSO V 
                WHERE V.FK_USUARIO = ?
                ORDER BY DS_TIPO''', g.conn, params=[id_usuario])
            df = pd.merge(dft,dfa,on="ID_TIPO",how="left")
            
        except Exception as e:
            flash(str(e))

    return render_template('usuario_acesso.html',**locals())

