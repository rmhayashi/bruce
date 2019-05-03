from classes import *

queries = Blueprint('queries', __name__,url_prefix="/queries")

@queries.before_request
def before_request():
    current_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bases/bruce.sqlite3'

