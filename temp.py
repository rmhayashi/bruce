import pandas as pd, json, numpy as np
import plotly, plotly.graph_objs as go

from flask import flash

import datetime as dt, pyodbc, time

global df_acumulado, lg_acumulado, ultimo_dia, msg, hoje


def carrega_bases():
    df_acumulado = pd.read_csv('bases/acumulado.csv',sep=';',encoding='utf8',low_memory=False,
                                names=['persid','incidente','ordem','open_date','resolve_date',
                                    'dia_abertura','dia_fechamento','sla_violation','dt_sla','dia_sla',
                                    'analista','grupo_abertura','grupo_final','operacao_abertura','operacao_final',
                                    'formulario','fl_status','ds_status'])  
    lg_acumulado = pd.read_csv('bases/acumulado_log.csv',sep=';',encoding='utf8',low_memory=False,
                    names=['incidente','fl_log','ds_log','analista','dt_log','dia_log']);
    
    ultimo_dia = df_acumulado['open_date'].max()
    ultimo_dia = dt.datetime.strptime(ultimo_dia,'%Y-%m-%d %H:%M:%S')
    ultimo_dia = ultimo_dia.replace(hour=0, minute=0, second=0, microsecond=0)
    ultimo_dia = dt.date(ultimo_dia.year, ultimo_dia.month,ultimo_dia.day)
    ultimo_dia += dt.timedelta(days=1)

    return df_acumulado, lg_acumulado, ultimo_dia 


def atu_base(hoje,ultimo_dia):
    hoje = "'"+ str(hoje) +"'"
    ultimo_dia = "'"+ str(ultimo_dia) +"'"

    conn_sql = pyodbc.connect('DRIVER={SQL Server};SERVER=SV2KPSQL20\CARSQLPRD;DATABASE=MDB;UID=DATAZEN;PWD=Vivo#2018')
    sql = '''
        select *
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
                    'it suporte inc - atendimento - massivos',
                    'it suporte inc - atendimento - portal','it suporte inc - atendimento - zeus') then 'retail'
                when cnt.last_name = 'it suporte inc - atendimento - corporate' then 'corporate'
                when cnt.last_name = 'it suporte inc - atendimento - tv' then 'tv'
                when cnt.last_name = 'it suporte inc - atendimento - ouvidoria' then 'ouvidoria'
                when cnt.last_name = 'it suporte inc - atendimento - tbs' then 'tbs'
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
                    'it suporte inc - atendimento - portal','it suporte inc - atendimento - zeus') then 'retail'
                when g.last_name = 'it suporte inc - atendimento - corporate' then 'corporate'
                when g.last_name = 'it suporte inc - atendimento - tv' then 'tv'
                when g.last_name = 'it suporte inc - atendimento - ouvidoria' then 'ouvidoria'
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
            where open_date between '''+ ultimo_dia +''' and '''+ hoje +''' '''
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

    return 'OK'


def dia_base(ultimo_dia):
    hoje = dt.datetime.now()
    hoje = hoje.replace(hour=0, minute=0, second=0, microsecond=0)       
    hoje = dt.date(hoje.year, hoje.month,hoje.day)

    if hoje > ultimo_dia:
        # global msg
        msg = atu_base(hoje,ultimo_dia)
        df_acumulado, lg_acumulado, ultimo_dia = carrega_bases()

    return df_acumulado, lg_acumulado, ultimo_dia, hoje 


df_acumulado, lg_acumulado, ultimo_dia = carrega_bases()

df_acumulado, lg_acumulado, ultimo_dia, hoje  = dia_base(ultimo_dia)

print(msg)
print(hoje)
print(ultimo_dia)