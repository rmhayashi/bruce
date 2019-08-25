from classes import *

usuarios = Blueprint('usuarios', __name__,url_prefix="/usuarios")

@usuarios.route("/",methods=['POST','GET'])
def index():
    funcao_menu = 'Controle de Usuários'
    try:
        if request.method == 'POST':
            ds_senha = md5(req('ds_login'))
            user = (req('ds_login'), req('no_usuario'), req('ds_email'), ds_senha, session['id_usuario'])
            g.cur.execute ('''INSERT INTO TUSUARIO (DS_LOGIN, NO_USUARIO, DS_EMAIL, DS_SENHA, FK_USUARIO_CADASTRO) 
                VALUES (?,UCASE(?),LCASE(?),?,?) ''',user)
            g.cur.execute("SELECT @@IDENTITY AS ID_USUARIO")
            id_usuario = g.cur.fetchone()
            id_usuario = int(id_usuario.ID_USUARIO)
            for x in list([7,8,12,14]): # ACESSOS PADRÃO DE QUALQUER USUÁRIO
                g.cur.execute ('''INSERT INTO TUSUARIO_ACESSO (FK_USUARIO, FK_TIPO_ACESSO, FK_USUARIO_CADASTRO) 
                    VALUES (?,?,?)''', (id_usuario, x, session['id_usuario']))
            flash('Usuário Cadastrado com Sucesso!')

        table = g.cur.execute('''SELECT ID_USUARIO, DS_LOGIN, NO_USUARIO, DT_ACESSO, FL_ATIVO
            FROM TUSUARIO WHERE ID_USUARIO > 1
            ORDER BY FL_ATIVO DESC, NO_USUARIO''')
    except Exception as e:
        flash(e)

    return render_template('usuarios.html',**locals())


@usuarios.route('/acessos',methods=['POST','GET'])
def acessos():
    funcao_menu = 'Controle de Usuários \ Acessos'
    if request.method == 'POST':
        try:
            id_usuario = req('id_usuario')
            params = (id_usuario, id_usuario)
            dft = pd.read_sql('SELECT ID_TIPO, DS_TIPO FROM TTIPO WHERE FK_TIPO = 6 AND FL_ATIVO = 1 ORDER BY DS_TIPO', g.conn)
            dfa = pd.read_sql('''
                SELECT ID_USUARIO_ACESSO, ID_TIPO
                FROM VW_USUARIO_ACESSO V 
                WHERE V.FK_USUARIO = ?
                ORDER BY DS_TIPO''', g.conn,params=[id_usuario])
            df = pd.merge(dft,dfa,on="ID_TIPO",how="left")
            
        except Exception as e:
            flash(e)

    return render_template('usuario_acesso.html',**locals())

