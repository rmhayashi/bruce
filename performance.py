from classes import *

performance = Blueprint('performance', __name__,url_prefix="/performance")

@performance.route('/',methods=['GET','POST'])
def index():
    if not 'logado' in session:
        session['logado'] = False
        return render_template("top.html"), 200

    global df_acumulado, lg_acumulado, ultimo_dia, msg, hoje, df_equipe
    df_acumulado, lg_acumulado, ultimo_dia, hoje = dia_base()
    dt_ini = dt.datetime.strptime('01/10/2018','%d/%m/%Y')
    dt_fim = dt.datetime.now()
    sel_mes = ''
    sel = ''
    mes = ''
    sel_analista = ''
    matricula = ''

    if request.method == 'POST':
        mes = req('mes')
        matricula = req("matricula")

        graf_retail = graf_operacao('RETAIL',mes)
        graf_tv = graf_operacao('TV',mes)
        graf_bill = graf_operacao('BILLING',mes)
        graf_corp = graf_operacao('CORPORATE',mes)

        # graf_analista_acumulado = grafanalista_acumulado(session['matricula'],mes)
        graf_analista_acumulado = grafanalista_acumulado(matricula,mes)
        graf_analista_mes = grafanalista_mes(matricula,mes)
        graf_analista_formulario = grafanalista_formulario(matricula,mes)

    while dt_fim > dt_ini:
        if str(mes) == str(dt_fim.month) + '/' + str(dt_fim.year):
            sel = 'selected'
        else:
            sel = ''
        sel_mes += '<option value="'+ str(dt_fim.month) + '/' + str(dt_fim.year) +'" '+ sel +'>'+ str(dt_fim.month) + '/' + str(dt_fim.year) +'</option>'
        dt_fim += relativedelta(months=-1)

    if session['matricula'] == '80656720':
        for row in df_equipe[['matricula','nome']].itertuples():
            if str(row.matricula) == str(matricula):
                sel = 'selected'
            else:
                sel = ''
            sel_analista += '<option value="'+ str(row.matricula) +'" '+ sel +'>'+ str(row.matricula) + ' - ' + str(row.nome) +'</option>'
    else:
        sel_analista = '<option value="'+ str(session['matricula']) +'" selected>'+ str(session['matricula']) + ' - ' + str(session['nome']) +'</option>'


    grafgeral = graf_geral()
    grafatual = graf_atual(mes)

    return render_template('performance.html',**locals())