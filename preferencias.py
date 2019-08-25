from classes import *

preferencias = Blueprint('preferencias', __name__,url_prefix="/preferencias")

@preferencias.route('/',methods=['GET','POST'])
def index():
    funcao_menu = 'Preferências'
    
    return render_template('preferencias.html',**locals())