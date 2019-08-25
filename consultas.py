from classes import *

consultas = Blueprint('consultas', __name__,url_prefix="/")

@consultas.route("/consultas",methods=['GET', 'POST'])
def index():
    funcao_menu = 'Consultas Pré-Construídas'

    ds_tipo = req('ds_tipo')
    ds_campo = str(req('ds_campo')).replace(";","").strip()

    base, sel_base, query = query_builder(ds_tipo, ds_campo)
    
    if request.method == 'POST':
        pd.set_option('display.max_colwidth', -1)

        df = pd.read_sql('''SELECT CONEXAO 
            FROM BASES_ORACLE 
            WHERE BASE = ? AND STATUS = 1 
            ORDER BY BASE''', g.conn, params=[base])
        conexao = df['CONEXAO'].to_string(index=False)
        try:
            conn_oracle = cx_Oracle.connect(conexao)
            df_o = pd.read_sql(query, conn_oracle)
            resultado = df_o
            tables=[df_o.to_html(classes='rel')]

            sql = "INSERT INTO TLOG (FK_TIPO_LOG, FK_USUARIO_CADASTRO, DS_IP, DS_LOG) VALUES (?,?,?,?)"
            g.cur.execute (sql,(3,session['id_usuario'],session['ip'], base + ' - '+ query))

            return render_template("consultas.html", **locals())

        except Exception as e:
            sql = "INSERT INTO TLOG (FK_TIPO_LOG, FK_USUARIO_CADASTRO, DS_IP, DS_LOG) VALUES (?,?,?,?)"
            g.cur.execute (sql,(13,session['id_usuario'],session['ip'], query +' - '+ str(e)))

            if str(e).find('password') > 0:
                g.cur.execute('UPDATE BASES_ORACLE SET STATUS = 0 WHERE BASE = ?', base)
                g.cur.execute (sql,(4,session['id_usuario'],session['ip'], 'Inativação de Logon Oracle - Base '+ base))
                base, sel_base, query = query_builder(ds_tipo, ds_campo)

            flash(e)
            return render_template("consultas.html", **locals())
    return render_template("consultas.html", sel_base = sel_base, ds_campo = '', funcao_menu = funcao_menu)