import flask

class InvalidFormat(Exception):
    pass

def hrw(document):
    try:
        title = document['title']
        isbn_10 = document['isbn_10']
        data = document['access']['hrw'][0]
    except KeyError:
        raise InvalidFormat

    data['url'] = 'http://my.hrw.com/tabnav/controller.jsp?isbn=' + isbn_10
    return flask.render_template('post.html',
            title=title, action='http://my.hrw.com/index.jsp', data=data)

def glencoe_literature(document):
    try:
        title = document['title']
        isbn_13 = document['isbn_13']
    except KeyError:
        raise InvalidFormat

    return flask.redirect('http://www.glencoe.com/ebooks/literature/{}/glencoe_main.html'.format(isbn_13))

convert = {
    'hrw': hrw,
    'glencoe_lit': glencoe_literature,
}
