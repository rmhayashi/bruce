from classes import *

webservices = Blueprint('webservices', __name__,url_prefix="/webservices")

@webservices.before_request
def before_request():
<<<<<<< HEAD
  current_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bases/bruce.sqlite3'
=======
  current_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bases/bruce.sqlite3'
>>>>>>> 6ebb39c93bdeefe6bc16f16e582b390d36bece14
