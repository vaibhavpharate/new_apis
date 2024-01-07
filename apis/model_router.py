from .models import SiteConfig, VDbApi, VWrfData, VWrfRevision, SiteConfig1

class MyDBRouter(object):

    def db_for_read(self, model, **hints):
        """ reading SomeModel from otherdb """
        if model == SiteConfig:
            return 'site_configs'
        elif model == SiteConfig1:
            return 'site_configs_1'
        elif model == VDbApi:
            return 'data_api'
        elif model == VWrfData or model==VWrfRevision:
            return 'v_wrf_view'
        return None

    def db_for_write(self, model, **hints):
        """ writing SomeModel to otherdb """
        if model == SiteConfig:
            return 'site_configs'
        elif model == SiteConfig1:
            return 'site_configs_1'
        elif model == VDbApi:
            return 'data_api'
        elif model == VWrfData or model== VWrfRevision:
            return 'v_wrf_view'
        return None

