import os

development = os.getenv('FLASK_ENV') == 'development'
DEBUG = development

STATIC_FOLDER = 'static' if development else None
ASSETS_BASE = '/static/' if development else os.getenv('ASSETS_BASE')
COVERS_BASE = os.getenv('COVERS_BASE')

MONGOLAB_URI = os.getenv('MONGOLAB_URI')

GA_TRACKING_ID = not development and os.getenv('GA_TRACKING_ID')

CLASSZONE_QRTN_PASSWORD = os.getenv('CLASSZONE_QRTN_PASSWORD')
QRTN_DROPBOX_UID = os.getenv('QRTN_DROPBOX_UID')
