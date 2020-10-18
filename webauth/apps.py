'''webauth Application Configuration'''
from django.apps import AppConfig
from django.db.models.signals import pre_save
from webauth.signals import clean_save

class WebauthConfig(AppConfig):
    '''webauth Config'''
    name = 'webauth'

    def ready(self):
        pre_save.connect(clean_save, dispatch_uid='clean_save')
