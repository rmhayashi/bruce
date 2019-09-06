from classes import *

def req(variavel):
    return request.form.get(variavel)

def reqls(variavel):
    return request.form.getlist(variavel)

def md5(ds_senha):
    return generate_password_hash(password=ds_senha, method='md5')

def vmd5(ds_senha,senha_bd):
    return check_password_hash(password=ds_senha, pwhash=senha_bd)

def monta_menu():
    sql = '''SELECT DS_TIPO, OB_TIPO, OB_TIPO2, NM_ORDEM 
        FROM VW_USUARIO_ACESSO 
        WHERE FK_USUARIO = ? 
        ORDER BY NM_ORDEM, DS_TIPO'''
    df = pd.read_sql(sql, g.conn,params=[session['id_usuario']])
    html = ''
    for i, x in df.iterrows():
        if request.endpoint == x['OB_TIPO2']:
            cl = 'active'
        else:
            cl = ''
        html += '''
            <a class="'''+ cl +'''" href="''' + url_for(x['OB_TIPO2']) +'''">''' + x['DS_TIPO'] + '''</a>'''
    return html


def query_builder(ds_tipo,ds_campo):
    sel = ''
    sel_base = ''
    base = ''
    query = ''

    df = pd.read_csv('bases/consultas.csv',sep=';')
    df2 = pd.read_sql('''SELECT DISTINCT BASE, CONEXAO, STATUS FROM BASES_ORACLE WHERE STATUS = 1 ORDER BY BASE''', g.conn)
    df = df[df['base'].isin(df2['BASE'])].sort_values(by = ['base','tipo'])
    # df = df.sort_values(by = ['base'])
    for x in df['base'].unique():
        sel_base += '<optgroup label="'+ x +'" style="background-color:silver">'
        for y, q in df[df['base'] == x][['tipo','query']].values:
            if ds_tipo == y:
                sel = 'selected'
                base = x
                query = q
            else:
                sel = ''
            sel_base += '<option value="'+ y +'" style="background-color:white" '+ sel +'>'+ y +'</option>'

        sel_base += '</optgroup>'
    if y == "Ultimo CDR":
        return (base, sel_base, query.format(ds_campo,ds_campo,ds_campo,ds_campo))
    return (base, sel_base, query.format(ds_campo))


# *********************************************************************************************
def graf_geral():
    sql = 'SELECT * FROM TFECHAMENTO ORDER BY DT_CADASTRO'
    df = pd.read_sql(sql,g.conn)
    df['mes'] = pd.DatetimeIndex(df['dt_cadastro']).month
    df['ano'] = pd.DatetimeIndex(df['dt_cadastro']).year
    df['mes_ano'] = df['mes'].map(str) + '/' + df['ano'].map(str)
    
    df_aberto = df.groupby('mes_ano').sum()['qt_aberto']
    df_fechado = df.groupby('mes_ano').sum()['qt_fechado']
    df_movimentado = df.groupby('mes_ano').sum()['qt_movimentado']
    df_escalonado = df.groupby('mes_ano').sum()['qt_escalonado']
    df_reaberto = df.groupby('mes_ano').sum()['qt_reaberto']
    df_violado = df.groupby('mes_ano').sum()['qt_violado']

    aberto = go.Bar(
        x = df['mes_ano'].unique(),
        y = df_aberto.loc[df['mes_ano'].unique()],
        name='Abertos',
        marker = dict(
            color = 'navy',
            line = dict(
                color='navy',
                width = 1),
            ),
    )

    movimentado = go.Scatter(
        x = df['mes_ano'].unique(),
        y = df_movimentado.loc[df['mes_ano'].unique()],
        name='Movimentados',
        marker = dict(
            color = 'yellow',
            size = 8
            ),
        line = dict(
            color='yellow',
            width = 4,
            ),
    )

    fechado = go.Bar(
        x = df['mes_ano'].unique(),
        y = df_fechado.loc[df['mes_ano'].unique()],
        name='Fechados',
        width = 0.6,
        marker = dict(
            color = 'green',
            line = dict(
                color='green',
                width = 1),
            ),
    )

    escalonado = go.Bar(
        x = df['mes_ano'].unique(),
        y = df_escalonado.loc[df['mes_ano'].unique()],
        name='Escalonados',
        width = 0.5,
        marker = dict(
            color = 'silver',
            line = dict(
                color='silver',
                width = 1),
            ),
    )

    violado = go.Scatter(
        x = df['mes_ano'].unique(),
        y = df_violado.loc[df['mes_ano'].unique()],
        name='Violados',
        marker = dict(
            color = 'red'
            ),
        line = dict(
            color='red',
            width = 3,
            ),
    )

    reaberto = go.Scatter(
        x = df['mes_ano'].unique(),
        y = df_reaberto.loc[df['mes_ano'].unique()],
        name='Reabertos',
        marker = dict(
            color = 'black',
            line = dict(
                color='black',
                width = 1),
            ),
    )

    layout = go.Layout(
        barmode = 'overlay', 
        title = 'Geral x Mês',
        yaxis = dict(
            title = 'Qtde'
        ),
        legend=dict(orientation="h",
            font=dict(
                family='verdana',
                size=10,
                color='#000'
            )
        )
    )

    data = [aberto, movimentado, fechado, escalonado, violado, reaberto]
    fig = go.Figure(data=data, layout=layout)

    grafgeral = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return grafgeral


def graf_atual(mes = '01/04/2019'):
    nome_mes = dt.datetime.strptime(mes, '%d/%m/%Y').strftime('%B')
    sql = '''SELECT * FROM TFECHAMENTO 
        WHERE DT_CADASTRO BETWEEN ? AND DATEADD('m',1,?)-1 ORDER BY DT_CADASTRO'''
    df = pd.read_sql(sql,g.conn,params=[mes,mes])
    df['dia'] = pd.DatetimeIndex(df['dt_cadastro']).day
   
    df_aberto = df.groupby('dia').sum()['qt_aberto']
    t_aberto = df.sum()['qt_aberto']

    df_fechado = df.groupby('dia').sum()['qt_fechado']
    t_fechado = df.sum()['qt_fechado']

    df_movimentado = df.groupby('dia').sum()['qt_movimentado']
    t_movimentado = df.sum()['qt_movimentado']

    df_escalonado = df.groupby('dia').sum()['qt_escalonado']
    t_escalonado = df.sum()['qt_escalonado']

    df_reaberto = df.groupby('dia').sum()['qt_reaberto']
    t_reaberto = df.sum()['qt_reaberto']

    df_violado = df.groupby('dia').sum()['qt_violado']
    t_violado = df.sum()['qt_violado']

    aberto = go.Bar(
        x = df['dia'].unique(),
        y = df_aberto.loc[df['dia'].unique()],
        name = 'Abertos - '+ '{:,}'.format(t_aberto).replace(',','.'),
        marker = dict(
            color = 'navy',
            line = dict(
                color='navy',
                width = 1),
            ),
    )

    if t_movimentado > 0:
        movimentado = go.Scatter(
            x = df['dia'].unique(),
            y = df_movimentado.loc[df['dia'].unique()],
            name = 'Movimentados - '+ '{:,}'.format(t_movimentado).replace(',','.')
                + ' - {:,.1%}'.format(t_movimentado/t_aberto),
            marker = dict(
                color = 'yellow',
                size = 8
                ),
            line = dict(
                color='yellow',
                width = 4,
                ),
        )

    if t_fechado > 0:
        fechado = go.Bar(
            x = df['dia'].unique(),
            y = df_fechado.loc[df['dia'].unique()],
            name='Fechados - '+ '{:,}'.format(t_fechado).replace(',','.')
                + ' - {:,.1%}'.format(t_fechado/t_aberto),
            width = 0.6,
            marker = dict(
                color = 'green',
                line = dict(
                    color='green',
                    width = 1),
                ),
        )

    if t_escalonado > 0:
        escalonado = go.Bar(
            x = df['dia'].unique(),
            y = df_escalonado.loc[df['dia'].unique()],
            name = 'Escalonados - '+ '{:,}'.format(t_escalonado).replace(',','.')
                    + ' - {:,.1%}'.format(t_escalonado/t_aberto),
            width = 0.5,
            marker = dict(
                color = 'silver',
                line = dict(
                    color='silver',
                    width = 1),
                ),
        )

    if t_violado > 0:
        violado = go.Scatter(
            x = df['dia'].unique(),
            y = df_violado.loc[df['dia'].unique()],
            name = 'Violados - '+ str(t_violado) 
                + ' - {:,.1%}'.format(t_violado/t_aberto),
            marker = dict(
                color = 'red'
                ),
            line = dict(
                color='red',
                width = 3,
                ),
        )

    if t_reaberto > 0:
        reaberto = go.Scatter(
            x = df['dia'].unique(),
            y = df_reaberto.loc[df['dia'].unique()],
            name = 'Reabertos - '+ str(t_reaberto) 
                + ' - {:,.1%}'.format(t_reaberto/t_aberto),
            marker = dict(
                color = 'black',
                line = dict(
                    color='black',
                    width = 1),
                ),
        )

    layout = go.Layout(
        barmode = 'overlay', 
        title = nome_mes +' x Dia' , #'Mês Atual'
        xaxis = dict(
            tickmode='linear'
        ),
        yaxis = dict(
            title = 'Qtde'
        ),
        legend=dict(orientation="h",
            font=dict(
                family='verdana',
                size=10,
                color='#000'
            )
        )
    )

    data = [aberto]
    if 'movimentado' in locals():
        data.append(movimentado)
        
    if 'fechado' in locals():
        data.append(fechado)
        
    if 'escalonado' in locals():
        data.append(escalonado)
        
    if 'violado' in locals():
        data.append(violado)
        
    if 'reaberto' in locals():
        data.append(reaberto)

    fig = go.Figure(data=data, layout=layout)

    graf_atual = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return graf_atual
    

