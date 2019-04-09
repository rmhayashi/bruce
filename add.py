from sqlalchemy import create_engine
engine = create_engine('sqlite:///bruce.sqlite3')

# engine.execute('alter table tlog add column ip String')")

# engine.execute ("insert into tform (formulario,dificuldade) values ('IT ATENDIMENTO.CONTA.PROBLEMAS COM CONTA.SIEBEL8 - ITEM NÃO CONTEMPLADO NO CARDÁPIO','DIFICIL')")

# engine.execute ("insert into tequipe (dt, matricula, nome, operacao) values ('01/03/2019','80665425','ABRAAO FELIPE DE FARIAS FRAGA','TV')")

# engine.execute ("delete from tequipe")

result = engine.execute("select nome from tequipe where nome like 'a%' limit 3")
p = result.fetchall()
if p:
    print('OK')
else:
    print('NO')

# print(len(result.all()))

for row in p:
    print(row['nome'])

