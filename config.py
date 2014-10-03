import os

development = os.getenv('FLASK_ENV') == 'development'
DEBUG = development

MONGOLAB_URI = os.getenv('MONGOLAB_URI')

CLASSZONE_QRTN_PASSWORD = os.getenv('CLASSZONE_QRTN_PASSWORD')
QRTN_DROPBOX_UID = os.getenv('QRTN_DROPBOX_UID')
