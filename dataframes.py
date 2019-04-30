from classes import *

global df_acumulado, lg_acumulado, ultimo_dia, msg, hoje, nform, lg_escalonados, df_equipe
df_acumulado, lg_acumulado, ultimo_dia, msg, hoje, nform, lg_escalonados, df_equipe = '','','','','','','',''


def carrega_bases():
    hoje = dt.datetime.now()
    ano = str(hoje.year)
    mes = str(hoje.month)
    mes_atual = mes +'/'+ ano

    arquivo_equipe = ('0' + mes_atual.replace('/',''))[-6:]
    arquivo_equipe = arquivo_equipe[-2:] + arquivo_equipe[:2]
    arquivo_equipe = 'equipe_'+ arquivo_equipe + '.csv'

    nform = pd.read_csv('bases/formularios.csv',sep=';',encoding='cp1252',low_memory=False);
    df_equipe = pd.read_csv('bases/'+ arquivo_equipe,sep=';',encoding='cp1252',low_memory=False);
    df_equipe = df_equipe.sort_values('nome')
    df_acumulado = pd.read_csv('bases/acumulado.csv',sep=';',encoding='utf8',low_memory=False,
                                    names=['persid','incidente','ordem','open_date','resolve_date',
                                        'dia_abertura','dia_fechamento','sla_violation','dt_sla','dia_sla',
                                        'analista','grupo_abertura','grupo_final','operacao_abertura','operacao_final',
                                        'formulario','fl_status','ds_status'])  
    lg_acumulado = pd.read_csv('bases/acumulado_log.csv',sep=';',encoding='utf8',low_memory=False,
                    names=['incidente','fl_log','ds_log','analista','dt_log','dia_log']);

    df_acumulado['analista'] = df_acumulado['analista'].str.upper()
    lg_acumulado['analista'] = lg_acumulado['analista'].str.upper()
    df_acumulado['operacao_abertura'] = df_acumulado['operacao_abertura'].str.upper()
    df_acumulado['operacao_final'] = df_acumulado['operacao_final'].str.upper()

    df_acumulado['mes'] = pd.DatetimeIndex(pd.to_datetime(df_acumulado['open_date'],format='%Y-%m-%d %H:%M:%S')).month
    df_acumulado['ano'] = pd.DatetimeIndex(pd.to_datetime(df_acumulado['open_date'],format='%Y-%m-%d %H:%M:%S')).year
    df_acumulado['mes_ano'] = df_acumulado['mes'].map(str) + '/' + df_acumulado['ano'].map(str)

    df_acumulado['mes_fechamento'] = pd.DatetimeIndex(pd.to_datetime(df_acumulado['resolve_date'],format='%Y-%m-%d %H:%M:%S')).month
    df_acumulado['ano_fechamento'] = pd.DatetimeIndex(pd.to_datetime(df_acumulado['resolve_date'],format='%Y-%m-%d %H:%M:%S')).year
    df_acumulado['mes_fechamento'].fillna(0,inplace=True)
    df_acumulado['ano_fechamento'].fillna(0,inplace=True)
    df_acumulado['mes_ano_fechamento'] = df_acumulado['mes_fechamento'].map(int).map(str) + '/' + \
                                        df_acumulado['ano_fechamento'].map(int).map(str)

    df_acumulado['dia_fechamento'] = pd.DatetimeIndex(pd.to_datetime(df_acumulado['resolve_date'],format='%Y-%m-%d %H:%M:%S')).day

    lg_acumulado['mes'] = pd.DatetimeIndex(pd.to_datetime(lg_acumulado['dt_log'],format='%Y-%m-%d %H:%M:%S')).month
    lg_acumulado['ano'] = pd.DatetimeIndex(pd.to_datetime(lg_acumulado['dt_log'],format='%Y-%m-%d %H:%M:%S')).year
    lg_acumulado['mes_ano'] = lg_acumulado['mes'].map(str) + '/' + lg_acumulado['ano'].map(str)

    lg_reaberto = lg_acumulado[lg_acumulado['ds_log'].str.find("Reaberto por") >= 0]
    df_acumulado.loc[df_acumulado['incidente'].isin(lg_reaberto['incidente']),'reaberto'] = 1
    df_acumulado['reaberto'].fillna(0,inplace=True)

    lg_escalonados = lg_acumulado[lg_acumulado['ds_log'].str.find("para 'Escalonado'") >= 0]
    df_acumulado.loc[(df_acumulado['operacao_final'] == 'OUTROS'),'escalonado'] = 1
    df_acumulado['escalonado'].fillna(0,inplace=True)

    ultimo_dia = df_acumulado['open_date'].max()
    ultimo_dia = dt.datetime.strptime(ultimo_dia,'%Y-%m-%d %H:%M:%S')
    ultimo_dia = ultimo_dia.replace(hour=0, minute=0, second=0, microsecond=0)
    ultimo_dia = dt.date(ultimo_dia.year, ultimo_dia.month,ultimo_dia.day)
    ultimo_dia += dt.timedelta(days=1)

    return df_acumulado, lg_acumulado, ultimo_dia, lg_escalonados, df_equipe, nform


def atu_base(hoje,ultimo_dia):
    try:
        hoje = "'"+ str(hoje) +"'"
        ultimo_dia = "'"+ str(ultimo_dia) +"'"

        conn_sql = pyodbc.connect('DRIVER={SQL Server};SERVER=SV2KPSQL20\CARSQLPRD;DATABASE=MDB;UID=DATAZEN;PWD=Vivo#2018')
        # conn_sql = pyodbc.connect('DRIVER={SQL Server};SERVER=SV2KPSQL20\CARSQLPRD;DATABASE=MDB;UID=CENSERSDSQL;PWD=BruceLee2.0')
        sql = '''
            select persid,incidente,ordem,open_date,resolve_date,dia_abertura,dia_fechamento,
                    sla_violation,dt_sla,dia_sla,analista,grupo_abertura,
                    grupo_final,operacao_abertura,operacao_final,formulario,fl_status,ds_status
                from
                (
                select cr.persid, cr.ref_num as incidente, cr.zordem ordem,
                    dateadd(ss,cr.open_date -7200,'19700101') open_date, 
                    dateadd(ss,cr.resolve_date -7200,'19700101') resolve_date,

                    datepart(day,dateadd(ss,cr.open_date -7200,'19700101')) dia_abertura,
                    case when dateadd(ss,cr.resolve_date -7200,'19700101') > '''+ hoje +''' then null 
                    else datepart(day,dateadd(ss,cr.resolve_date -7200,'19700101')) 
                    end dia_fechamento,

                    cr.sla_violation,
                    case when cr.sla_violation = 1 then dateadd(ss,ev.first_fire_time -7200,'19700101') else null end dt_sla,
                    case when cr.sla_violation = 1 then 
                        case when dateadd(ss,ev.first_fire_time -7200,'19700101') > '''+ hoje +''' then null 
                        else datepart(day,dateadd(ss,ev.first_fire_time -7200,'19700101')) end 
                    end dia_sla,

                    a.last_name analista,

                    cnt.last_name grupo_abertura,
                    g.last_name grupo_final,

                    case when cnt.last_name in 
                        ('it suporte inc - atendimento','it suporte inc - atendimento -  bloq.desbl','it suporte inc - atendimento - ba',
                        'it suporte inc - atendimento - massivos', 'it suporte inc - atendimento - tbs',
                        'it suporte inc - atendimento - portal','it suporte inc - atendimento - zeus', 'it suporte inc - atendimento - ouvidoria'
                        ) then 'retail'
                    when cnt.last_name = 'it suporte inc - atendimento - corporate' then 'corporate'
                    when cnt.last_name = 'it suporte inc - atendimento - tv' then 'tv'
                    when cnt.last_name in 
                        ('it suporte inc - billing - ajuste nivel 1',
                        'it suporte inc - billing - anatel','it suporte inc - billing - cont_arrec_cobr','it suporte inc - billing - conta ou instancia','it suporte inc - billing – cyber',
                        'it suporte inc - billing - eif - boleto nao gerado','it suporte inc - billing - eif - escalonados','it suporte inc - billing - fat nao gerada',
                        'it suporte inc - billing - fat nao gerada - eif ou boleto nao gerado','it suporte inc - billing - faturamento','it suporte inc - billing - hierarquia ou tracking id',
                        'it suporte inc - billing - integracao','it suporte inc - billing - ouvidoria','it suporte inc - billing - retencao','it suporte inc - billing – são paulo',
                        'it suporte inc - cobranca - sysrec nivel 1','it suporte inc - integração finance') then 'billing'
                    else 'outros' 
                    end operacao_abertura,
                    case when g.last_name in 
                        ('it suporte inc - atendimento','it suporte inc - atendimento -  bloq.desbl','it suporte inc - atendimento - ba',
                        'it suporte inc - atendimento - massivos',
                        'it suporte inc - atendimento - portal','it suporte inc - atendimento - zeus','it suporte inc - atendimento - ouvidoria'
                        ) then 'retail'
                    when g.last_name = 'it suporte inc - atendimento - corporate' then 'corporate'
                    when g.last_name = 'it suporte inc - atendimento - tv' then 'tv'
                    when cnt.last_name = 'it suporte inc - atendimento - tbs' then 'tbs'
                    when g.last_name in 
                        ('it suporte inc - billing - ajuste nivel 1',
                        'it suporte inc - billing - anatel','it suporte inc - billing - cont_arrec_cobr','it suporte inc - billing - conta ou instancia','it suporte inc - billing – cyber',
                        'it suporte inc - billing - eif - boleto nao gerado','it suporte inc - billing - eif - escalonados','it suporte inc - billing - fat nao gerada',
                        'it suporte inc - billing - fat nao gerada - eif ou boleto nao gerado','it suporte inc - billing - faturamento','it suporte inc - billing - hierarquia ou tracking id',
                        'it suporte inc - billing - integracao','it suporte inc - billing - ouvidoria','it suporte inc - billing - retencao','it suporte inc - billing – são paulo',
                        'it suporte inc - cobranca - sysrec nivel 1','it suporte inc - integração finance') then 'billing'
                    else 'outros' 
                    end operacao_final,

                    f.sym formulario, cr.status fl_status, crs.sym ds_status	
                    
                from call_req cr
                    inner join cr_stat crs on crs.code = cr.status
                    inner join prob_ctg f on f.persid = cr.category
                    inner join ca_contact g on g.contact_uuid = cr.group_id
                    inner join ca_contact cnt on cnt.contact_uuid = f.group_id
                    inner join att_evt ev on ev.obj_id = cr.persid
                        and group_name = 'sla'
                        and event_tmpl in ('evt:400606','evt:400712')
                    left join ca_contact a on a.contact_uuid = cr.assignee
                where cr.status not in ('cncl','canceluser','cancvivo1','vivo1')
                    and cnt.last_name in ('it suporte inc - atendimento','it suporte inc - atendimento -  bloq.desbl','it suporte inc - atendimento - ba',
                        'it suporte inc - atendimento - massivos','it suporte inc - atendimento - portal','it suporte inc - atendimento - tbs','it suporte inc - atendimento - zeus',
                        'it suporte inc - atendimento - corporate',
                        'it suporte inc - atendimento - tv',
                        'it suporte inc - atendimento - ouvidoria',
                        'it suporte inc - billing - ajuste nivel 1',
                        'it suporte inc - billing - anatel','it suporte inc - billing - cont_arrec_cobr','it suporte inc - billing - conta ou instancia','it suporte inc - billing – cyber',
                        'it suporte inc - billing - eif - boleto nao gerado','it suporte inc - billing - eif - escalonados','it suporte inc - billing - fat nao gerada',
                        'it suporte inc - billing - fat nao gerada - eif ou boleto nao gerado','it suporte inc - billing - faturamento','it suporte inc - billing - hierarquia ou tracking id',
                        'it suporte inc - billing - integracao','it suporte inc - billing - ouvidoria','it suporte inc - billing - retencao','it suporte inc - billing – são paulo',
                        'it suporte inc - cobranca - sysrec nivel 1','it suporte inc - integração finance')
                ) base
                where open_date between '''+ ultimo_dia +''' and '''+ hoje +''' 
                group by persid,incidente,ordem,open_date,resolve_date,dia_abertura,dia_fechamento,
                    sla_violation,dt_sla,dia_sla,analista,grupo_abertura,
                    grupo_final,operacao_abertura,operacao_final,formulario,fl_status,ds_status
                '''
        df = pd.read_sql(sql, conn_sql)

        # print(df['formulario'])

        with open('bases/acumulado.csv', 'a', encoding='utf-8') as f:
            df.to_csv(f, header=False, sep=';', index=False, encoding='utf-8')

        sql = '''
            select base.incidente, act.type fl_log, act.description ds_log, 
                ca.last_name analista,
                dateadd(ss,act.last_mod_dt -7200,'19700101') dt_log, 
                case when dateadd(ss,act.last_mod_dt -7200,'19700101') > '''+ hoje +''' then null 
                else datepart(day,dateadd(ss,act.last_mod_dt -7200,'19700101')) end dia_log
            from
            (
            select cr.persid, cr.ref_num as incidente, dateadd(ss,cr.open_date -7200,'19700101') open_date
                
            from call_req cr
                inner join cr_stat crs on crs.code = cr.status
                inner join prob_ctg f on f.persid = cr.category
                inner join ca_contact g on g.contact_uuid = cr.group_id
                inner join ca_contact cnt on cnt.contact_uuid = f.group_id
                inner join att_evt ev on ev.obj_id = cr.persid
                    and group_name = 'sla'
                    and event_tmpl in ('evt:400606','evt:400712','evt:400715')
                left join ca_contact a on a.contact_uuid = cr.assignee
            where cr.status not in ('cncl','canceluser','cancvivo1','vivo1')
                and cnt.last_name in ('it suporte inc - atendimento','it suporte inc - atendimento -  bloq.desbl','it suporte inc - atendimento - ba',
                    'it suporte inc - atendimento - massivos','it suporte inc - atendimento - portal','it suporte inc - atendimento - tbs','it suporte inc - atendimento - zeus',
                    'it suporte inc - atendimento - corporate',
                    'it suporte inc - atendimento - tv',
                    'it suporte inc - atendimento - ouvidoria',
                    'it suporte inc - billing - ajuste nivel 1',
                    'it suporte inc - billing - anatel','it suporte inc - billing - cont_arrec_cobr','it suporte inc - billing - conta ou instancia','it suporte inc - billing – cyber',
                    'it suporte inc - billing - eif - boleto nao gerado','it suporte inc - billing - eif - escalonados','it suporte inc - billing - fat nao gerada',
                    'it suporte inc - billing - fat nao gerada - eif ou boleto nao gerado','it suporte inc - billing - faturamento','it suporte inc - billing - hierarquia ou tracking id',
                    'it suporte inc - billing - integracao','it suporte inc - billing - ouvidoria','it suporte inc - billing - retencao','it suporte inc - billing – são paulo',
                    'it suporte inc - cobranca - sysrec nivel 1','it suporte inc - integração finance')
            ) base
                inner join act_log act on act.call_req_id = base.persid 
                inner join ca_contact ca on ca.contact_uuid = act.analyst
                where base.open_date between '''+ ultimo_dia +''' and '''+ hoje +'''
                    and (act.type in ('fld','tr','st','re','soln') or act.type = 'PRIORIZACAO' and act.description like '%zswat%SIM%')
                    and dateadd(ss,act.last_mod_dt -7200,'19700101') < '''+ hoje +'''
            '''
        df = pd.read_sql(sql, conn_sql)

        with open('bases/acumulado_log.csv', 'a', encoding='utf-8') as f:
            df.to_csv(f, header=False, sep=';', index=False, encoding='utf-8')
    except Exception as e:
        flash(e)
    return 'OK'


def dia_base():
    global df_acumulado, lg_acumulado, ultimo_dia, msg, hoje
    hoje = dt.datetime.now()
    hoje = hoje.replace(hour=0, minute=0, second=0, microsecond=0)       
    hoje = dt.date(hoje.year, hoje.month,hoje.day)

    if hoje > ultimo_dia:
        msg = atu_base(hoje,ultimo_dia)
        df_acumulado, lg_acumulado, ultimo_dia, lg_escalonados, df_equipe, nform = carrega_bases()

    return df_acumulado, lg_acumulado, ultimo_dia, hoje 


df_acumulado, lg_acumulado, ultimo_dia, lg_escalonados, df_equipe, nform = carrega_bases()

df_acumulado, lg_acumulado, ultimo_dia, hoje  = dia_base()
   
###############################################################################################
def graf_geral():
    global df_acumulado, lg_acumulado

    aberto_acumulado = df_acumulado.groupby('mes_ano').count()['incidente']
    fechado_acumulado = df_acumulado[(df_acumulado['mes_ano_fechamento'] != '0/0') 
                & (df_acumulado['escalonado'] == 0)].groupby(['mes_ano_fechamento']).count()['incidente']
    escalonados_acumulado = df_acumulado[df_acumulado['escalonado'] == 1].groupby(['mes_ano']).count()['incidente']
    violados_acumulado = df_acumulado[(df_acumulado['dia_sla'].isnull() == False)
                & (df_acumulado['escalonado'] == 0)].groupby(['mes_ano']).count()['incidente']
    reabertos_acumulado = df_acumulado[(df_acumulado['reaberto'] == 1)].groupby(['mes_ano']).count()['incidente']
    movimentados_acumulado = fechado_acumulado + escalonados_acumulado

    aberto = go.Bar(
        x = df_acumulado['mes_ano'].unique(),
        y = aberto_acumulado.loc[df_acumulado['mes_ano'].unique()],
        name='Abertos',
        marker = dict(
            color = 'navy',
            line = dict(
                color='navy',
                width = 1),
            ),
    )

    movimentado = go.Scatter(
        x = df_acumulado['mes_ano'].unique(),
        y = movimentados_acumulado.loc[df_acumulado['mes_ano'].unique()],
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
        x = df_acumulado['mes_ano'].unique(),
        y = fechado_acumulado.loc[df_acumulado['mes_ano'].unique()],
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
        x = df_acumulado['mes_ano'].unique(),
        y = escalonados_acumulado.loc[df_acumulado['mes_ano'].unique()],
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
        x = df_acumulado['mes_ano'].unique(),
        y = violados_acumulado.loc[df_acumulado['mes_ano'].unique()],
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
        x = df_acumulado['mes_ano'].unique(),
        y = reabertos_acumulado.loc[df_acumulado['mes_ano'].unique()],
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


###############################################################################################
def graf_atual(mes):
    hoje = dt.datetime.now()
    ano = str(hoje.year)
    if mes == '':
        mes = str(hoje.month)
        mes = mes +'/'+ ano

    df = df_acumulado[(df_acumulado['mes_ano'] == str(mes)) | (df_acumulado['mes_ano_fechamento'] == str(mes))].sort_values('dia_abertura')

    aberto = df[df['mes_ano'] == str(mes)].groupby('dia_abertura').count()['incidente']
    total_aberto = df[df['mes_ano'] == str(mes)].count()['incidente']

    fechado = df[(df['mes_ano_fechamento'] == str(mes))
                & (df['escalonado'] == 0)].groupby(['dia_fechamento']).count()['incidente']
    total_fechado = df[(df['mes_ano_fechamento'] == str(mes))
                & (df['escalonado'] == 0)].count()['incidente']

    escalonados = df[(df_acumulado['mes_ano'] == str(mes))
                    & (df['escalonado'] == 1)].groupby(['dia_abertura']).count()['incidente']
    total_escalonados = df[(df_acumulado['mes_ano'] == str(mes))
                    & (df['escalonado'] == 1)].count()['incidente']

    violados = df[(df['dia_sla'].isnull() == False)
                    & (df_acumulado['mes_ano'] == str(mes))
                    & (df['escalonado'] == 0)].groupby(['dia_sla']).count()['incidente']
    total_violados = df[(df['dia_sla'].isnull() == False)
                        & (df_acumulado['mes_ano'] == str(mes))
                        & (df['escalonado'] == 0)].count()['incidente']

    reabertos = df[(df_acumulado['mes_ano'] == str(mes))
                    & (df['reaberto'] == 1)].groupby(['dia_abertura']).count()['incidente']
    total_reabertos = df[(df_acumulado['mes_ano'] == str(mes))
                        & (df['reaberto'] == 1)].count()['incidente']

    movimentados = fechado + escalonados
    total_movimentados = total_fechado + total_escalonados

    aberto = go.Bar(
        x = df[(df['mes_ano'] == str(mes))]['dia_abertura'].unique(),
        y = aberto.loc[df[(df['mes_ano'] == str(mes))]['dia_abertura'].unique()],
        name = 'Abertos - '+ '{:,}'.format(total_aberto).replace(',','.'),
        marker = dict(
            color = 'navy',
            line = dict(
                color='navy',
                width = 1)
            ),
    )

    movimentado = go.Scatter(
        x = df[(df['mes_ano'] == str(mes))]['dia_abertura'].unique(),
        y = movimentados.loc[df[(df['mes_ano'] == str(mes))]['dia_abertura'].unique()],
        name = 'Movimentados - '+ '{:,}'.format(total_movimentados).replace(',','.')
            + ' - {:,.1%}'.format(total_movimentados/total_aberto),
        marker = dict(
            color = 'yellow',
            size = 8,
            line = dict(
                color='black',
                width = 1)
            ),
        line = dict(
            color='yellow',
            width = 4,
            ),
    )

    fechado = go.Bar(
        x = df[(df['mes_ano'] == str(mes))]['dia_abertura'].unique(),
        y = fechado.loc[df[(df['mes_ano'] == str(mes))]['dia_abertura'].unique()],
        name='Fechados - '+ '{:,}'.format(total_fechado).replace(',','.')
            + ' - {:,.1%}'.format(total_fechado/total_aberto),
        width = 0.6,
        marker = dict(
            color = 'green',
            line = dict(
                color='green',
                width = 1),
            ),
    )

    if total_escalonados > 0:
        escalonado = go.Bar(
            x = df[(df['mes_ano'] == str(mes))]['dia_abertura'].unique(),
            y = escalonados.loc[df[(df['mes_ano'] == str(mes))]['dia_abertura'].unique()],
            name = 'Escalonados - '+ '{:,}'.format(total_escalonados).replace(',','.')
                + ' - {:,.1%}'.format(total_escalonados/total_aberto),
            width = 0.5,
            marker = dict(
                color = 'silver',
                line = dict(
                    color='silver',
                    width = 1),
                ),
        )
    else:
        escalonado = ''

    if total_violados > 0:
        violado = go.Bar(
            x = df[(df['mes_ano'] == str(mes))]['dia_abertura'].unique(),
            y = violados.loc[df[(df['mes_ano'] == str(mes))]['dia_abertura'].unique()],
            name = 'Violados - '+ str(total_violados) 
                + ' - {:,.1%}'.format(total_violados/total_aberto),
            marker = dict(
                color = 'red'
                )#,
            # line = dict(
            #     color='red',
            #     width = 3,
            #     ),
        )

    if total_reabertos > 0:
        reaberto = go.Bar(
            x = df[(df['mes_ano'] == str(mes))]['dia_abertura'].unique(),
            y = reabertos.loc[df[(df['mes_ano'] == str(mes))]['dia_abertura'].unique()],
            name = 'Reabertos - '+ str(total_reabertos) 
                + ' - {:,.1%}'.format(total_reabertos/total_aberto),
            marker = dict(
                color = 'black',
                line = dict(
                    color='black',
                    width = 1),
                ),
        )

    layout = go.Layout(
        barmode = 'overlay', 
        title = 'Geral x Dia - '+ mes, #'Mês Atual',
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

    grafatual = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return grafatual
    

###############################################################################################
def graf_operacao(operacao,mes):
    hoje = dt.datetime.now()
    ano = str(hoje.year)
    if mes == '':
        mes = str(hoje.month)
        mes = mes +'/'+ ano

    df = df_acumulado[
            ((df_acumulado['mes_ano'] == str(mes)) | (df_acumulado['mes_ano_fechamento'] == str(mes)))
            & ((df_acumulado['operacao_abertura'] == operacao) | (df_acumulado['operacao_final'] == operacao))
        ].sort_values(['dia_abertura','dia_fechamento'])

    aberto = df[(df['mes_ano'] == str(mes)) & (df['operacao_abertura'] == operacao)].groupby('dia_abertura').count()['incidente']
    total_aberto = df[(df['mes_ano'] == str(mes)) & (df['operacao_abertura'] == operacao)].count()['incidente']

    fechado = df[(df['mes_ano_fechamento'] == str(mes))
                & (df['escalonado'] == 0)
                & (df['operacao_final'] == operacao)].groupby(['dia_fechamento']).count()['incidente']
    total_fechado = df[(df['mes_ano_fechamento'] == str(mes))
                        & (df['escalonado'] == 0)
                        & (df['operacao_final'] == operacao)].count()['incidente']

    escalonados = df[(df['mes_ano'] == str(mes))
                    & (df['escalonado'] == 1)].groupby(['dia_abertura']).count()['incidente']
    total_escalonados = df[(df['mes_ano'] == str(mes))
                            & (df['escalonado'] == 1)].count()['incidente']

    violados = df[(df['dia_sla'].isnull() == False)
                    & (df['mes_ano'] == str(mes))
                    & (df['escalonado'] == 0)].groupby(['dia_sla']).count()['incidente']
    total_violados = df[(df['dia_sla'].isnull() == False)
                        & (df['mes_ano'] == str(mes))
                        & (df['escalonado'] == 0)].count()['incidente']

    reabertos = df[(df['mes_ano'] == str(mes))
                    & (df['reaberto'] == 1)
                    & (df['operacao_abertura'] == operacao)].groupby(['dia_abertura']).count()['incidente']
    total_reabertos = df[(df['mes_ano'] == str(mes))
                            & (df['reaberto'] == 1)
                            & (df['operacao_abertura'] == operacao)].count()['incidente']

    movimentados = pd.merge(fechado.to_frame(),escalonados.to_frame(),left_index=True,right_index=True,how='left')
    movimentados.columns = ['qtf','qte']
    movimentados['qte'].fillna(0,inplace=True)
    movimentados = movimentados['qtf'] + movimentados['qte']
    total_movimentados = total_fechado + total_escalonados

    aberto = go.Bar(
        x = df['dia_abertura'].unique(),
        y = aberto.loc[df['dia_abertura'].unique()],
        name = 'Abertos - '+ '{:,}'.format(total_aberto).replace(',','.'),
        marker = dict(
            color = 'navy',
            line = dict(
                color='navy',
                width = 1)
            ),
    )

    movimentado = go.Scatter(
        x = df['dia_abertura'].unique(),
        y = movimentados.loc[df['dia_abertura'].unique()],
        name = 'Movimentados - '+ '{:,}'.format(total_movimentados).replace(',','.')
            + ' - {:,.1%}'.format(total_movimentados/total_aberto),
        marker = dict(
            color = 'yellow',
            size = 8,
            line = dict(
                color='black',
                width = 1)
            ),
        line = dict(
            color='yellow',
            width = 4,
            ),
    )

    fechado = go.Bar(
        x = df['dia_fechamento'].unique(),
        y = fechado.loc[df['dia_fechamento'].unique()],
        name='Fechados - '+ '{:,}'.format(total_fechado).replace(',','.')
            + ' - {:,.1%}'.format(total_fechado/total_aberto),
        width = 0.6,
        marker = dict(
            color = 'green',
            line = dict(
                color='green',
                width = 1),
            ),
    )

    if total_escalonados > 0:
        escalonado = go.Bar(
            x = df['dia_abertura'].unique(),
            y = escalonados.loc[df['dia_abertura'].unique()],
            name = 'Escalonados - '+ '{:,}'.format(total_escalonados).replace(',','.')
                + ' - {:,.1%}'.format(total_escalonados/total_aberto),
            width = 0.5,
            marker = dict(
                color = 'silver',
                line = dict(
                    color='silver',
                    width = 1),
                ),
        )


    if total_violados > 0:
        violado = go.Bar(
            x = df['dia_abertura'].unique(),
            y = violados.loc[df['dia_abertura'].unique()],
            name = 'Violados - '+ str(total_violados) 
                + ' - {:,.1%}'.format(total_violados/total_aberto),
            marker = dict(
                color = 'red'
                )#,
            # line = dict(
            #     color='red',
            #     width = 3,
            #     ),
        )

    if total_reabertos > 0:
        reaberto = go.Bar(
            x = df['dia_abertura'].unique(),
            y = reabertos.loc[df['dia_abertura'].unique()],
            name = 'Reabertos - '+ str(total_reabertos) 
                + ' - {:,.1%}'.format(total_reabertos/total_aberto),
            marker = dict(
                color = 'black',
                line = dict(
                    color='black',
                    width = 1),
                ),
        )

    layout = go.Layout(
        barmode = 'overlay', 
        title = operacao + ' - '+ mes,
        xaxis = dict(
            tickmode='linear'
        ),
        yaxis = dict(
            title = 'Qtde'
        ),
        legend=dict(orientation="h",
            x=0,
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

    graf = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return graf
    

###############################################################################################
def grafanalista_acumulado(matricula,mes):
    try:
        arquivo = ('0' + mes.replace('/',''))[-6:]
        arquivo = arquivo[-2:] + arquivo[:2]
        arquivo = 'equipe_'+ arquivo + '.csv'

        df_analistas = pd.read_csv('bases/'+ arquivo,sep=';',encoding='cp1252',low_memory=False);
        nome, operacao = df_analistas[df_analistas['matricula'] == matricula][['nome','operacao_analista']].iloc[0]
        ope_pri = operacao.split(', ')[0]
        meta_pc = 100 / df_analistas[(df_analistas['operacao_analista'].str.find(ope_pri) >= 0)].count()['matricula']

        df_analistas = pd.merge(df_acumulado,df_analistas,left_on='analista',right_on='nome')
        df_analistas = df_analistas.sort_values('open_date')

        lg_analista_esc = lg_escalonados[lg_escalonados['analista'] == nome]

        total_fechado = df_analistas[(df_analistas['mes_ano_fechamento'] != '0/0')
            & (df_analistas['escalonado'] == 0)
            & (df_analistas['operacao_final'].str.find(ope_pri) >= 0)].groupby(['mes_ano_fechamento']).count()['incidente']

        meta = total_fechado * meta_pc / 100

        df = df_analistas[df_analistas['matricula'] == matricula].sort_values('open_date')

        fechado = df[(df['mes_ano_fechamento'] != '0/0') & (df['escalonado'] == 0)].groupby(['mes_ano_fechamento']).count()['incidente']
        
        escalonados = lg_analista_esc.groupby(['mes_ano']).count()['incidente']

        violados = df[(df['dia_sla'].isnull() == False) & (df['escalonado'] == 0)].groupby(['mes_ano']).count()['incidente']

        reabertos = df[(df['reaberto'] == 1)].groupby(['mes_ano']).count()['incidente']

        mdf = []
        for x in df['mes_ano_fechamento'].unique():
            media_fechados = df_analistas[(df_analistas['mes_ano_fechamento'] == x) 
                    & (df_analistas['operacao_final'].isin(operacao.split(', '))) 
                    & (df_analistas['matricula'].isin(df_analistas[(df_analistas['operacao_analista'].str.find(ope_pri) >= 0)]['matricula']))
                ].groupby(['mes_ano_fechamento','nome']).count()['incidente'].mean()
            mdf.append('{:,.2f}'.format(media_fechados))


        fechado = go.Bar(
            x = df['mes_ano'].unique(),
            y = fechado.loc[df['mes_ano'].unique()],
            name='Fechados '+ nome[:nome.find(' ')],
            width = 0.6,
            marker = dict(
                color = 'green',
                line = dict(
                    color='green',
                    width = 1),
                ),
        )

        media_f = go.Scatter(
            x = df['mes_ano'].unique(),
            y = mdf,
            name='Média Fechados '+ operacao,
            marker = dict(
                color = 'lightgreen'
                ),
            line = dict(
                color='lightgreen',
                width = 3,
                ),
        )

        meta_mes = go.Scatter(
            x = df['mes_ano'].unique(),
            y = meta.loc[df['mes_ano'].unique()],
            name='Meta',
            marker = dict(
                color = 'yellow'
                ),
            line = dict(
                color='yellow',
                width = 3,
                ),
        )

        if len(escalonados) > 0:
            escalonado = go.Bar(
                x = df['mes_ano'].unique(),
                y = escalonados.loc[df['mes_ano'].unique()],
                name='Escalonados',
                width = 0.5,
                marker = dict(
                    color = 'silver',
                    line = dict(
                        color='silver',
                        width = 1),
                    ),
            )   

        if len(violados) > 0:
            violado = go.Scatter(
                x = df['mes_ano'].unique(),
                y = violados.loc[df['mes_ano'].unique()],
                name='Violados',
                marker = dict(
                    color = 'red'
                    ),
                line = dict(
                    color='red',
                    width = 3,
                    ),
            )

        if len(reabertos) > 0:
            reaberto = go.Scatter(
                x = df['mes_ano'].unique(),
                y = reabertos.loc[df['mes_ano'].unique()],
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
            title = 'Geral x Mês - '+ nome[:nome.find(' ')],
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

        data = [media_f, meta_mes]
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

        grafgeral = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        return grafgeral
    except Exception as e:
        flash(e)
        return ''


###############################################################################################
def grafanalista_mes(matricula,mes):
    try:
        hoje = dt.datetime.now()
        ano = str(hoje.year)
        if mes == '':
            mes = str(hoje.month)
            mes = mes +'/'+ ano
        arquivo = ('0' + mes.replace('/',''))[-6:]
        arquivo = arquivo[-2:] + arquivo[:2]
        arquivo = 'equipe_'+ arquivo + '.csv'

        df_analistas = pd.read_csv('bases/'+ arquivo,sep=';',encoding='cp1252',low_memory=False);
        nome, operacao = df_analistas[df_analistas['matricula'] == matricula][['nome','operacao_analista']].iloc[0]
        ope_pri = operacao.split(', ')[0]
        meta_pc = 100 / df_analistas[(df_analistas['operacao_analista'].str.find(ope_pri) >= 0)].count()['matricula']
        
        df = df_acumulado[(df_acumulado['mes_ano_fechamento'] == str(mes))]
        df = pd.merge(df,df_analistas,left_on='analista',right_on='nome')

        lg_analista_esc = lg_escalonados[(lg_escalonados['mes_ano'] == str(mes)) & (lg_escalonados['analista'] == nome)]
        
        dias_fechamento = sorted(df['dia_fechamento'].unique())

        mdf = []
        for x in dias_fechamento:
            media_fechados = df[(df['dia_fechamento'] == x) 
                    & (df['operacao_final'].isin(operacao.split(', '))) 
                    & (df['matricula'].isin(df[(df['operacao_analista'].str.find(ope_pri) >= 0)]['matricula']))
                ].groupby(['nome']).count()['incidente'].mean()
            mdf.append('{:,.2f}'.format(media_fechados))

        df = df[(df['matricula'] == matricula)].sort_values('dia_fechamento')

        fechado = df[(df['escalonado'] == 0)].groupby(['dia_fechamento']).count()['incidente']
        total_fechado = df[(df['escalonado'] == 0)].count()['incidente']

        escalonados = lg_analista_esc.groupby(['dia_log']).count()['incidente']
        total_escalonados = lg_analista_esc.count()['incidente']

        violados = df[(df['dia_sla'].isnull() == False) & (df['escalonado'] == 0)].groupby(['dia_sla']).count()['incidente']
        total_violados = df[(df['dia_sla'].isnull() == False) & (df['escalonado'] == 0)].count()['incidente']

        reabertos = df[(df['reaberto'] == 1)].groupby(['dia_fechamento']).count()['incidente']
        total_reabertos = df[(df['reaberto'] == 1)].count()['incidente']

        movimentados = pd.merge(fechado.to_frame(),escalonados.to_frame(),left_index=True,right_index=True,how='left')
        movimentados.columns = ['qtf','qte']
        movimentados['qte'].fillna(0,inplace=True)
        movimentados = movimentados['qtf'] + movimentados['qte']
        total_movimentados = total_fechado + total_escalonados

        

        fechado = go.Bar(
            x = dias_fechamento,
            y = fechado.loc[dias_fechamento],
            name='Fechados - '+ '{:,}'.format(total_fechado).replace(',','.'),
            width = 0.6,
            marker = dict(
                color = 'green',
                line = dict(
                    color='green',
                    width = 1),
                ),
        )

        media_f = go.Scatter(
            x = dias_fechamento,
            y = mdf,
            name='Média Fechados '+ operacao,
            marker = dict(
                color = 'yellow'
                ),
            line = dict(
                color='yellow',
                width = 3,
                ),
        )

        if total_escalonados > 0:
            escalonado = go.Bar(
                x = dias_fechamento,
                y = escalonados.loc[dias_fechamento],
                name = 'Escalonados - '+ '{:,}'.format(total_escalonados).replace(',','.')
                    + ' - {:,.1%}'.format(total_escalonados/total_fechado),
                width = 0.6,
                marker = dict(
                    color = 'silver',
                    line = dict(
                        color='silver',
                        width = 1),
                    ),
            )


        if total_violados > 0:
            violado = go.Bar(
                x = dias_fechamento,
                y = violados.loc[dias_fechamento],
                name = 'Violados - '+ str(total_violados) 
                    + ' - {:,.1%}'.format(total_violados/total_fechado),
                width = 0.4,
                marker = dict(
                    color = 'red'
                    )#,
                # line = dict(
                #     color='red',
                #     width = 3,
                #     ),
            )

        if total_reabertos > 0:
            reaberto = go.Bar(
                x = dias_fechamento,
                y = reabertos.loc[dias_fechamento],
                name = 'Reabertos - '+ str(total_reabertos) 
                    + ' - {:,.1%}'.format(total_reabertos/total_fechado),
                width = 0.4,
                marker = dict(
                    color = 'black',
                    line = dict(
                        color='black',
                        width = 1),
                    ),
            )

        layout = go.Layout(
            barmode = 'stack', 
            title = nome + ' - '+ mes,
            xaxis = dict(
                tickmode='linear'
            ),
            yaxis = dict(
                title = 'Qtde'
            ),
            legend=dict(orientation="h",
                x=0,
                font=dict(
                    family='verdana',
                    size=10,
                    color='#000'
                )
            )
        )

        data = [media_f]
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

        graf = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        return graf
    except Exception as e:
        flash(e)
        return ''
    

###############################################################################################
def grafanalista_formulario(matricula,mes):
    try:
        hoje = dt.datetime.now()
        ano = str(hoje.year)
        if mes == '':
            mes = str(hoje.month)
            mes = mes +'/'+ ano
        arquivo = ('0' + mes.replace('/',''))[-6:]
        arquivo = arquivo[-2:] + arquivo[:2]
        arquivo = 'equipe_'+ arquivo + '.csv'

        df_analistas = pd.read_csv('bases/'+ arquivo,sep=';',encoding='cp1252',low_memory=False);
        nome = df_analistas[df_analistas['matricula'] == matricula]['nome'].iloc[0]
        
        df = df_acumulado[(df_acumulado['mes_ano_fechamento'] == str(mes)) 
            & (df_acumulado['analista'] == nome)].sort_values(['dia_fechamento'])

        fm = pd.merge(df,nform,on='formulario',how='left')
        fm['dificuldade'].fillna('ND',inplace=True)
        fm = fm.sort_values('dificuldade')

        data = []
        tamanho = 0.8
        for x in fm['dificuldade'].unique():
            formulario = fm[fm['dificuldade'] == x].groupby(['dia_fechamento']).count()['incidente']
            formulario = go.Bar(
                width = tamanho,
                x = sorted(fm['dia_fechamento'].unique()),
                y = formulario.loc[sorted(fm['dia_fechamento'].unique())],
                name = x,
            )
            data.append(formulario)
            # tamanho -= 0.15

        layout = go.Layout(
            barmode = 'stack', 
            title = nome + ' - '+ mes,
            xaxis = dict(
                tickmode='linear'
            ),
            yaxis = dict(
                title = 'Qtde'
            ),
            legend=dict(orientation="h",
                x=0,
                font=dict(
                    family='verdana',
                    size=10,
                    color='#000'
                )
            )
        )

        fig = go.Figure(data=data, layout=layout)

        graf = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        return graf
    except Exception as e:
        flash(e)
        return ''