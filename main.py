from classes import *

@app.before_request
def before():
    if 'logado' in session:
        if session['logado']:
            session['logado'] = session['logado']
            session['nome'] = session['nome']
            session['matricula'] = session['matricula']
            # print(session.logado)


@app.route("/")
def main():
    session['logado'] = False
    return render_template("default.html"), 200


@app.route("/login",methods=['GET', 'POST'])
def login():
    matricula = req('matricula')
    senha = req('senha')
    alt_senha = req('alt_senha')

    if matricula == senha:
        if alt_senha == 'S':
            senha = req('nova_senha')
            nova_senha = md5(req('nova_senha'))
            usuario.query.filter_by(matricula = matricula).update({'senha' : nova_senha})
            flash('Senha atualizada com Sucesso!')
            fl = ''
            logs = tlog(session['matricula'],'Alteração de Senha', dt.datetime.now(), session['ip'])
            db.session.add(logs)
            db.session.commit()
        else:
            fl = 'S'
            flash("Necessário Alterar Senha")
        
        return render_template("default.html",**locals()), 200
    else:
        v = usuario.query.filter_by(matricula = req('matricula'),senha = md5(req('senha'))).first()
        if v:
            session['logado'] = True
            session['nome'] = v.nome
            session['matricula'] = v.matricula
            session['ip'] = request.remote_addr
        else:
            flash('Matrícula ou Senha incorretos!')
            return render_template("default.html")


    return render_template("top.html",**locals()), 200



@app.route("/novo",methods=['POST','GET'])
def novo():
    if not 'logado' in session:
        session['logado'] = False
        return render_template("top.html"), 200

    if request.method == 'POST':
        user = usuario(req('matricula'),req('nome'),req('matricula'))
        db.session.add(user)
        flash('Usuário Cadastrado com Sucesso!')

    usrs = usuario.query.filter(usuario.matricula != '80656720',usuario.matricula != '80479177').order_by('nome').all()

    return render_template('novo.html',**locals())



@app.route("/logs",methods=['POST','GET'])
def logs():
    if not 'logado' in session:
        session['logado'] = False
        return render_template("top.html"), 200

    dt1 = dt.datetime.now().date()
    dt2 = dt.datetime.now().date()
    
    if request.method == 'POST':
        dt1 = req('dt1')
        dt2 = req('dt2')
        dt1f = dt.datetime.strptime(dt1,'%Y-%m-%d')
        dt2f = dt.datetime.strptime(dt2,'%Y-%m-%d') + dt.timedelta(days=1)
        # logs = tlog.query.order_by('dt').all()
        logs = tlog.query.join(usuario,tlog.matricula == usuario.matricula) \
            .add_columns(tlog.id, tlog.dt, tlog.matricula, usuario.nome, tlog.descricao, tlog.ip) \
            .filter(tlog.dt >= dt1f, tlog.dt <= dt2f).order_by('dt').all()
        
    return render_template('logs.html',**locals())



@app.route("/valida_login",methods=['POST','GET'])
def valida_login():
    if not 'logado' in session:
        session['logado'] = False
        return render_template("top.html"), 200

    if request.method == 'POST':
        matricula = req('matricula')
        if req('acao') == 'select':
            v = usuario.query.filter_by(matricula = matricula).first()
            if v:
                return '''
                    <script>
                        parent.document.getElementById("matricula").value = "";
                        parent.document.getElementById("matricula").focus();
                    </script>
                    <span style="color:red;font-size:14px">Usuário Já Existe</span>'''
            else:
                return ''
        elif req('acao') == 'excluir' and session['matricula'] in ('80656720','80479177'):
            logs = tlog(session['matricula'],'Exclusão Usuário '+ matricula, dt.datetime.now(), session['ip'])
            db.session.add(logs)

            usuario.query.filter_by(matricula = req('matricula')).delete()
            return '''
                    <script>
                        parent.window.location.href = '/novo';
                    </script>
                    '''
        else:
            return '<script>alert("Sem Acesso!")</script>'


if __name__ == "__main__":
    db.create_all()
    app.run(debug=True, use_reloader=True,port=80,host='0.0.0.0')