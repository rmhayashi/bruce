from classes import *

performance = Blueprint('performance', __name__,url_prefix="/performance")

@performance.route('/',methods=['GET','POST'])
def index():
    funcao_menu = 'Performance'
    dt_ini = dt.datetime.strptime('01/10/2018','%d/%m/%Y')
    dt_fim = dt.datetime.now()

    sel_mes = ''
    sel = ''
    mes = ''
    sel_analista = ''
    matricula = ''

    df = pd.read_sql('SELECT DS_MATRICULA, NO_PESSOA FROM TEQUIPE WHERE DT_SAIDA IS NULL ORDER BY NO_PESSOA',g.conn)

    if request.method == 'POST':
        mes = req('mes')
        matricula = req("matricula")
        

    while dt_fim > dt_ini:
        if str(mes) == str(dt_fim.month) + '/' + str(dt_fim.year):
            sel = 'selected'
        else:
            sel = ''
        sel_mes += '<option value="'+ str(dt_fim.month) + '/' + str(dt_fim.year) +'" '+ sel +'>'+ str(dt_fim.month) + '/' + str(dt_fim.year) +'</option>'
        dt_fim += relativedelta(months=-1)

    if session['matricula'] == '80656720':
        for row in df[['DS_MATRICULA','NO_PESSOA']].itertuples():
            if str(row.DS_MATRICULA) == str(matricula):
                sel = 'selected'
            else:
                sel = ''
            sel_analista += '<option value="'+ str(row.DS_MATRICULA) +'" '+ sel +'>'+ str(row.DS_MATRICULA) + ' - ' + str(row.NO_PESSOA) +'</option>'
    else:
        sel_analista = '<option value="'+ str(session['matricula']) +'" selected>'+ str(session['matricula']) + ' - ' + str(session['nome']) +'</option>'

    # global df_acumulado, lg_acumulado, ultimo_dia, msg, hoje, df_equipe
    # # df_acumulado, lg_acumulado, ultimo_dia, hoje = dia_base()
    
    

    #     graf_retail = graf_operacao('RETAIL',mes)
    #     graf_tv = graf_operacao('TV',mes)
    #     graf_bill = graf_operacao('BILLING',mes)
    #     graf_corp = graf_operacao('CORPORATE',mes)

    #     # graf_analista_acumulado = grafanalista_acumulado(session['matricula'],mes)
    #     graf_analista_acumulado = grafanalista_acumulado(matricula,mes)
    #     graf_analista_mes = grafanalista_mes(matricula,mes)
    #     graf_analista_formulario = grafanalista_formulario(matricula,mes)

    

    


    grafgeral = graf_geral()
    grafatual = graf_atual()

    return render_template('performance.html',**locals())