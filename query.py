from classes import *

query = Blueprint('query', __name__,url_prefix="/")

@query.route("/query",methods=['GET', 'POST'])
def index():
    funcao_menu = 'Consultas Construídas pelo Usuário'

    ds_base = req("ds_base")
    
    def monta_base():
        sel = ''
        sel_base = ''
        conexao = ''
        df = pd.read_sql('''SELECT DISTINCT BASE, CONEXAO, STATUS FROM BASES_ORACLE WHERE STATUS = 1 ORDER BY BASE''', g.conn)
        
        for x, y in df[['BASE','CONEXAO']].values:
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

                sql = "INSERT INTO TLOG (FK_TIPO_LOG, FK_USUARIO_CADASTRO, DS_IP, DS_LOG) VALUES (?,?,?,?)"
                g.cur.execute (sql,(3,session['id_usuario'],session['ip'], ds_base + ' - ' + query))

                return render_template("query.html", **locals())

            except Exception as e:
                sql = "INSERT INTO TLOG (FK_TIPO_LOG, FK_USUARIO_CADASTRO, DS_IP, DS_LOG) VALUES (?,?,?,?)"
                g.cur.execute (sql,(13,session['id_usuario'],session['ip'], query +' - '+ str(e)))

                if str(e).find('password') > 0:
                    g.cur.execute('UPDATE BASES_ORACLE SET STATUS = 0 WHERE BASE = ?', ds_base)
                    g.cur.execute (sql,(4,session['id_usuario'],session['ip'], 'Inativação de Logon Oracle - Base '+ ds_base))
                
                flash(e)
                sel_base, df, conexao = monta_base()
                return render_template("query.html", **locals())

    return render_template("query.html", **locals())