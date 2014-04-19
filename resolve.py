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

def glencoe_swf_lit(**kwargs):
    try:
        isbn_13 = kwargs['document']['isbn_13']
    except KeyError:
        raise InvalidFormat

    return flask.redirect('http://www.glencoe.com/ebooks/literature/{}/glencoe_main.html'.format(isbn_13))

def glencoe_showbook(**kwargs):
    try:
        title = kwargs['document']
        data = {'access_code': kwargs['document']['access']['glencoe_showbook'][kwargs['index']]}
    except KeyError:
        raise InvalidFormat

    return flask.render_template('post.html',
        title=title, action='http://www.glencoe.com/ose/showbook.php', data=data)

def glencoe_pdf_la(**kwargs):
    try:
        isbn_13 = kwargs['document']['isbn_13']
    except KeyError:
        raise InvalidFormat

    return flask.redirect('http://www.glencoe.com/cgi-bin/pdfServer.pl/ebooks/language_arts/{}/swopen.pdf'.format(isbn_13))

convert = {
    'hrw': hrw,
    'glencoe_swf_lit': glencoe_swf_lit,
    'glencoe_showbook': glencoe_showbook,
    'glencoe_pdf_la': glencoe_pdf_la,
}
