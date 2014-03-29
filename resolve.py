import flask

class InvalidFormat(Exception):
    pass

def hrw(document):
    try:
        title = document['title']
        isbn_10 = document['isbn_10']
        data = document['access']['hrw']
    except KeyError:
        raise InvalidFormat

    data['url'] = 'http://my.hrw.com/tabnav/controller.jsp?isbn=' + document['isbn_10']
    return flask.render_template('post.html',
            title=title, action='http://my.hrw.com/index.jsp', data=data)

convert = {
    'hrw': hrw,
}
