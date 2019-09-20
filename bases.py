from classes import *

bases = Blueprint('bases', __name__,url_prefix="/bases")

@bases.route("/",methods=['POST','GET'])
def index():
    funcao_menu = 'Bases'
    try:
        if request.method == 'POST':
            base = (req('no_base').upper(), req('ds_user'), req('ds_pass'), req('ds_host').upper(), req('ds_port'), req('no_service').upper(), req('tp_service'))
            g.cur.execute ('''INSERT INTO TBASES (NO_BASE, DS_USER, DS_PASS, DS_HOST, DS_PORT, NO_SERVICE, TP_SERVICE) 
                VALUES (UCASE(?),?,?,?,?,?,?) ''',base)
            flash('Base Cadastrada com Sucesso!')

        table = g.cur.execute('''SELECT ID_BASE, NO_BASE, DS_USER, DS_PASS, DS_HOST, DS_PORT, NO_SERVICE, TP_SERVICE, FL_ATIVO
            FROM TBASES ORDER BY FL_ATIVO DESC, NO_BASE''')
    except Exception as e:
        flash(str(e))

    return render_template('bases.html',**locals())


@bases.route('/detalhe',methods=['POST','GET'])
def detalhe():
    funcao_menu = 'Base Detalhe'
    if request.method == 'POST':
        try:
            id_base = req('id_base')
            df = pd.read_sql('''SELECT NO_BASE, DS_USER, DS_PASS, DS_HOST, DS_PORT, NO_SERVICE, TP_SERVICE, FL_ATIVO
                FROM TBASES WHERE ID_BASE = ?
                ''', g.conn, params=[id_base])
            no_base = df['NO_BASE'][0]
            ds_user = df['DS_USER'][0]
            ds_pass = df['DS_PASS'][0]
            ds_host = df['DS_HOST'][0].upper()
            ds_port = df['DS_PORT'][0]
            no_service = df['NO_SERVICE'][0].upper()
            tp_service = df['TP_SERVICE'][0]
            fl_ativo = df['FL_ATIVO'][0]
            
        except Exception as e:
            flash(str(e))

    return render_template('base_detalhe.html',**locals())


@bases.route('/atu_base',methods=['POST','GET'])
def atu_base():
    if request.method == 'POST':
        try:
            id_base = req('id_base')
            no_base = req('no_base')
            ds_user = req('ds_user')
            ds_pass = req('ds_pass')
            ds_host = req('ds_host').upper()
            ds_port = req('ds_port')
            no_service = req('no_service').upper()
            tp_service = req('tp_service')
            fl_ativo = req('fl_ativo')

            g.cur.execute('''UPDATE TBASES SET DS_USER = ?, DS_PASS = ?, DS_HOST = ?, DS_PORT = ?, NO_SERVICE = ?, TP_SERVICE = ?, FL_ATIVO = ?
            WHERE ID_BASE = ? ''',(ds_user, ds_pass, ds_host, ds_port, no_service, tp_service, fl_ativo, id_base))

            sql = "INSERT INTO TLOG (FK_TIPO_LOG, FK_USUARIO_CADASTRO, DS_IP, DS_LOG) VALUES (?,?,?,?)"
            g.cur.execute (sql,(19,session['id_usuario'],session['ip'], 'Alteração da base '+ no_base))

            flash('Base Atualizada com Sucesso!')
            
        except Exception as e:
            flash(str(e))

    return redirect(url_for('bases.index'))

