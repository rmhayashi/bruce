from classes import *

query = Blueprint('query', __name__,url_prefix="/")

@query.route("/query",methods=['GET', 'POST'])
def index():
    funcao_menu = 'Consultas Construídas pelo Usuário'

    id_base = req("id_base")
    
    def monta_base():
        sel = ''
        sel_base = ''
        conexao = ''
        ds_base = ''
        df = pd.read_sql('''SELECT ID_BASE, NO_BASE, DS_STR 
            FROM TBASES 
            WHERE FL_ATIVO = 1 
                AND TP_SERVICE = 'HOST' 
            ORDER BY NO_BASE''', g.conn)
        
        for x, y, z in df[['ID_BASE', 'NO_BASE', 'DS_STR']].values:
            if str(id_base) == str(x):
                sel = 'selected'
                conexao = z
                ds_base = y
            else:
                sel = ''
            sel_base += '<option value="'+ str(x) +'" '+ sel +'>'+ y +'</option>'
        return sel_base, conexao, ds_base

    sel_base, conexao, ds_base = monta_base()

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

                sql = "INSERT INTO TLOG (FK_TIPO_LOG, FK_USUARIO_CADASTRO, DS_IP, DS_LOG) VALUES (?,?,?,?)"
                g.cur.execute (sql,(3,session['id_usuario'],session['ip'], ds_base + ' - ' + query))

                return render_template("query.html", **locals())

            except Exception as e:
                sql = "INSERT INTO TLOG (FK_TIPO_LOG, FK_USUARIO_CADASTRO, DS_IP, DS_LOG) VALUES (?,?,?,?)"
                g.cur.execute (sql,(13,session['id_usuario'],session['ip'], query +' - '+ str(e)))

                if str(e).find('password') > 0:
                    g.cur.execute('UPDATE TBASES SET FL_ATIVO = 0 WHERE ID_BASE = ?', id_base)
                    g.cur.execute (sql,(4,session['id_usuario'],session['ip'], 'Inativação de Logon Oracle - Base '+ ds_base))
                
                flash(str(e))
                sel_base, conexao, ds_base = monta_base()
                return render_template("query.html", **locals())

    return render_template("query.html", **locals())