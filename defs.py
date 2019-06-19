from classes import *

def req(variavel):
    return request.form.get(variavel)

def md5(variavel):
    return hashlib.md5(variavel.encode('utf-8')).hexdigest()

def query_builder(ds_tipo,ds_campo):
    sel = ''
    sel_base = ''
    base = ''
    query = ''

    df = pd.read_csv('bases/consultas.csv',sep=';')
    df = df.sort_values(by = ['base'])
    for x in df['base'].unique():
        sel_base += '<optgroup label="'+ x +'" style="background-color:silver">'
        for y, q in df[df['base'] == x][['tipo','query']].values:
            if ds_tipo == y:
                sel = 'selected'
                base = x
                query = q
            else:
                sel = ''
            sel_base += '<option value="'+ y +'" style="background-color:white" '+ sel +'>'+ y +'</option>'

        sel_base += '</optgroup>'
    if y == "Ultimo CDR":
        return (base, sel_base, query.format(ds_campo,ds_campo,ds_campo,ds_campo))
    return (base, sel_base, query.format(ds_campo))