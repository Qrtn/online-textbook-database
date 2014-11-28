from urllib.parse import urlencode
import flask

import config

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
    return flask.render_template('post.html', title=title, action='http://my.hrw.com/index.jsp', data=data)

def glencoe_swf_lit(**kwargs):
    try:
        isbn_13 = kwargs['document']['isbn_13']
    except KeyError:
        raise InvalidFormat

    return flask.redirect('http://www.glencoe.com/ebooks/literature/{}/glencoe_main.html'.format(isbn_13))

def glencoe_swf_ss(**kwargs):
    try:
        isbn_13 = kwargs['document']['isbn_13']
    except KeyError:
        raise InvalidFormat

    return flask.redirect('http://www.glencoe.com/ebooks/social_studies/{}/mhssg_main.html'.format(isbn_13))

def glencoe_showbook(**kwargs):
    try:
        title = kwargs['document']['title']
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

def glencoe_pdfserver(**kwargs):
    try:
        path = kwargs['document']['access']['glencoe_pdfserver']
    except KeyError:
        raise InvalidFormat

    return flask.redirect('http://www.glencoe.com/cgi-bin/pdfServer.pl/{}'.format(path))

def glencoe_wl_locator(**kwargs):
    try:
        data = kwargs['document']['access']['glencoe_wl_locator']
    except KeyError:
        raise InvalidFormat

    return flask.redirect('http://www.glencoe.com/sec/worldlanguages/french/ose/ose_locator.php?' + urlencode(data))

def glencoe_ss_locator(**kwargs):
    try:
        data = kwargs['document']['access']['glencoe_ss_locator']
    except KeyError:
        raise InvalidFormat

    return flask.redirect('http://www.glencoe.com/sites/common_assets/socialstudies/ose/ose_locator.php?' + urlencode(data))

def glencoe_health_locator(**kwargs):
    try:
        data = kwargs['document']['access']['glencoe_health_locator']
    except KeyError:
        raise InvalidFormat

    return flask.redirect('http://www.glencoe.com/sites/common_assets/health/ose/ose_locator.php?' + urlencode(data))

def glencoe_corsair(**kwargs):
    try:
        corsair = kwargs['document']['access']['glencoe_corsair']
    except KeyError:
        raise InvalidFormat

    return flask.redirect('http://www.glencoe.com/corsair/isbn/{}/content/page/{}.html'.format(corsair['isbn'], corsair['page']))

def classzone_qrtn(**kwargs):
    try:
        title = kwargs['document']['title']
        resource = kwargs['document']['access']['classzone_qrtn']
    except KeyError:
        raise InvalidFormat

    data = {
        'username': 'Qrtn',
        'password': config.CLASSZONE_QRTN_PASSWORD,
        'redirectUrl': 'http://www.classzone.com/cz/books/{}/secured/resources/applications/ebook/index.jsp'.format(resource)
    }
    return flask.render_template('post.html', title=title, action='http://www.classzone.com/cz/login.htm', data=data)

def qrtn_dropbox(**kwargs):
    fields = {}
    try:
        fields['isbn_13'] = kwargs['document']['isbn_13']
        fields['index'] = kwargs['document']['access']['qrtn_dropbox']
    except KeyError:
        raise InvalidFormat
    fields['uid'] = config.QRTN_DROPBOX_UID

    return flask.redirect('https://dl.dropboxusercontent.com/u/{uid}/{isbn_13}/{index}'.format(**fields))


convert = {
    'hrw': hrw,
    'glencoe_swf_lit': glencoe_swf_lit,
    'glencoe_swf_ss': glencoe_swf_ss,
    'glencoe_showbook': glencoe_showbook,
    'glencoe_pdf_la': glencoe_pdf_la,
    'glencoe_pdfserver': glencoe_pdfserver,
    'glencoe_wl_locator': glencoe_wl_locator,
    'glencoe_ss_locator': glencoe_ss_locator,
    'glencoe_health_locator': glencoe_health_locator,
    'glencoe_corsair': glencoe_corsair,
    'classzone_qrtn': classzone_qrtn,
    'qrtn_dropbox': qrtn_dropbox,
}

priority = {
    'qrtn_dropbox': 0,
    'hrw': 1,
    'classzone_qrtn': 1,
    'glencoe_showbook': 1,
    'glencoe_wl_locator': 2,
    'glencoe_ss_locator': 2,
    'glencoe_health_locator': 2,
    'glencoe_swf_lit': 3,
    'glencoe_swf_ss': 3,
    'glencoe_corsair': 3,
    'glencoe_pdf_la': 4,
    'glencoe_pdfserver': 4,
}
