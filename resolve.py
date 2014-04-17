import flask

class InvalidFormat(Exception):
    pass

def hrw(**kwargs):
    try:
        title = kwargs['document']['title']
        isbn_10 = kwargs['document']['isbn_10']
        data = kwargs['document']['access']['hrw'][kwargs['index']]
    except KeyError:
        raise InvalidFormat

    data['url'] = 'http://my.hrw.com/tabnav/controller.jsp?isbn=' + isbn_10
    return flask.render_template('post.html',
            title=title, action='http://my.hrw.com/index.jsp', data=data)

def glencoe_literature(**kwargs):
    try:
        title = kwargs['document']['title']
        isbn_13 = kwargs['document']['isbn_13']
    except KeyError:
        raise InvalidFormat

    return flask.redirect('http://www.glencoe.com/ebooks/literature/{}/glencoe_main.html'.format(isbn_13))

convert = {
    'hrw': hrw,
    'glencoe_lit': glencoe_literature,
}
