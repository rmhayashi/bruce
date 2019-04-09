from classes import *

query = Blueprint('query', __name__,url_prefix="/query")

@query.route("/query",methods=['GET', 'POST'])
def index():
    sel = ''
    sel_base = ''

    ds_base = req("ds_base")
    
    df = pd.read_csv('bases/bases_oracle.csv',sep=';')
    df = df.sort_values(by = ['base'])
    for x, y in df[['base','conexao']].values:
        if ds_base == x:
            sel = 'selected'
            conexao = y
        else:
            sel = ''
        sel_base += '<option value="'+ x +'" '+ sel +'>'+ x +'</option>'

    if request.method == 'POST':
        query = str(req("query")).replace(";","").strip()
        pd.set_option('display.max_colwidth', -1)
        
        if query[0:6].upper() != 'SELECT':
            flash('NÃO É POSSÍVEL EXECUTAR')
            return render_template("query.html", sel_base = sel_base, query = query)
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
                flash(e)
                return render_template("query.html", query = query, sel_base = sel_base)

    return render_template("query.html", sel_base = sel_base)