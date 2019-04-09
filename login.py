from classes import *

login = Blueprint('login', __name__,url_prefix="/login")

@login.route("/",methods=['GET', 'POST'])
def index():
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