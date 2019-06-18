from classes import *

xmlgen = Blueprint('webservices', __name__,url_prefix="/webservices")

@xmlgen.before_request
def before_request():
  current_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bases/bruce.sqlite3'
