from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from django.contrib.auth import get_user_model

from .models import Clients, Plans, ClientPlans, SiteConfig, VDbApi, UserTokens, VWrfData, VWrfRevision, SiteConfig1


admin.site.register(get_user_model())
admin.site.register(Plans)
admin.site.register(ClientPlans)
admin.site.register(SiteConfig)
admin.site.register(VDbApi)
admin.site.register(UserTokens)
admin.site.register(VWrfData)
admin.site.register(VWrfRevision)
# SiteConfig1
admin.site.register(SiteConfig1)



