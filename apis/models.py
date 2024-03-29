from django.db import models
from django.contrib.auth.models import AbstractUser

from .manager import UserManager


class Plans(models.Model):
    is_active = models.BooleanField(default=True)
    plan_type = models.CharField(max_length=20, unique=True)
    date_added = models.DateTimeField(auto_now_add=True)
    def __str__(self) -> str:
        return self.plan_type



class Clients(AbstractUser):
    class Roles(models.TextChoices):
        ADMIN = "ADMIN", "Admin"
        CLIENT = "CLIENT", "Client"

    username = models.CharField(max_length=14, unique=True)
    email = models.EmailField(max_length=200, unique=True)
    client_short = models.CharField(max_length=10)
    role_type = models.CharField(max_length=10, choices=Roles.choices, default=Roles.CLIENT)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=True)
    date_updated = models.DateTimeField(auto_now=True)
    logos = models.ImageField(upload_to='client_logos/', default="None")
    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        db_table = 'clients'

    def __str__(self) -> str:
        return f"{self.username}"

class ClientType(models.Model):

    class TypeNames(models.TextChoices):
        SOLAR = "SOLAR","Solar"
        POWER = "POWER","Power"
    
    cl_type = models.CharField(max_length=200,choices=TypeNames.choices,default=TypeNames.SOLAR)
    client_id = models.ForeignKey(Clients,on_delete=models.CASCADE,related_name='client_id')
    date_added = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateField(auto_now=True)
    
    

class ClientPlans(models.Model):
    client_id = models.ForeignKey(Clients, on_delete=models.CASCADE,related_name='client_plans')
    plan_id = models.ForeignKey(Plans, on_delete=models.CASCADE,to_field='plan_type')
    date_added = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)


class SiteConfig(models.Model):
    class Verification(models.TextChoices):
        VERIFIED = "VERIFIED", "VERIFIED".title()
        UNVERIFIED = "UNVERIFIED", "UNVERIFIED".title()

    class SiteType(models.TextChoices):
        SOLAR = 'Solar', 'Solar'
        WIND = 'Wind', 'Wind'

    site_name = models.CharField(max_length=20)
    state = models.CharField(max_length=40)
    capacity = models.FloatField(blank=True, null=True)
    type = models.CharField(max_length=12, choices=SiteType.choices, default=SiteType.SOLAR)
    latitude = models.FloatField(blank=False)
    longitude = models.FloatField(blank=False)

    # row_id = models.AutoField(name='row_identity',)

    log_ts = models.DateTimeField(auto_now_add=True)
    client_name = models.CharField(max_length=120)
    # client_name = models.ForeignKey(Clients,on_delete=models.CASCADE,to_field='username',related_name='client_name')
    site_status = models.CharField(choices=(("ACTIVE", "Active"), ("INACTIVE", "Inactive")), default='Active')
    verified = models.CharField(choices=Verification.choices, default=Verification.UNVERIFIED)

    class Meta:
        db_table = 'site_config'
        # unique_together = ('timestamp', 'site_name')

    def __str__(self) -> str:
        return self.site_name


class SiteConfig1(models.Model):
    site_name = models.TextField(blank=True, null=True)
    state = models.TextField(blank=True, null=True)
    capacity = models.FloatField(blank=True, null=True)
    type = models.TextField(blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    row_id = models.BigIntegerField(blank=True, null=True)
    log_ts = models.DateTimeField(blank=True, null=True)
    client_name = models.CharField(max_length=200, blank=True, null=True)
    site_status = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'site_config_1'



class ClientSiteConfigs(models.Model):
    client_id = models.ForeignKey(Clients, on_delete=models.CASCADE)
    site_id = models.ForeignKey(SiteConfig, on_delete=models.CASCADE)
    plan_id = models.ForeignKey(Plans, on_delete=models.CASCADE)
    date_added = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)


class VDbApi(models.Model):
    site_name = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(blank=True, null=True)
    wind_speed_10m_mps = models.FloatField(blank=True, null=True)
    wind_direction_in_deg = models.FloatField(blank=True, null=True)
    temp_c = models.FloatField(blank=True, null=True)
    nowcast_ghi_wpm2 = models.FloatField(blank=True, null=True)
    swdown2 = models.FloatField(blank=True, null=True)
    cs_data = models.FloatField(blank=True, null=True)
    ci_data = models.FloatField(blank=True, null=True)
    tz = models.TextField(blank=True, null=True)
    ct_data = models.FloatField(blank=True, null=True)
    ct_flag_data = models.TextField(blank=True, null=True)
    forecast_method = models.TextField(blank=True, null=True)
    log_ts = models.TextField(unique=True, primary_key=True)

    class Meta:
        # managed = False
        db_table = 'v_db_api'
        unique_together = ('timestamp', 'site_name')

    def __str__(self) -> str:
        return self.site_name


class UserTokens(models.Model):
    client = models.ForeignKey(Clients, on_delete=models.CASCADE,related_name='user_tokens')
    created_at = models.DateTimeField(auto_now_add=True)
    valid_till = models.DateTimeField()
    user_token = models.CharField(max_length=50, unique=True)

    def __str__(self) -> str:
        return self.user_token


class VWrfData(models.Model):
    site_name = models.TextField(blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    site_type = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(primary_key=True)
    timezone = models.TextField(blank=True, null=True)
    temp_c = models.FloatField(blank=True, null=True)
    wind_speed_10m_mps = models.FloatField(blank=True, null=True)
    wind_direction_in_deg = models.FloatField(blank=True, null=True)
    swdown_wpm2 = models.FloatField(blank=True, null=True)

    class Meta:
        # managed = False
        unique_together = ('timestamp', 'site_name')
        db_table = 'v_wrf_data'

class VWrfRevision(models.Model):
    site_name = models.TextField(blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    site_type = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(primary_key=True)
    timezone = models.TextField(blank=True, null=True)
    temp_c = models.FloatField(blank=True, null=True)
    wind_speed_10m_mps = models.FloatField(blank=True, null=True)
    wind_direction_in_deg = models.FloatField(blank=True, null=True)
    swdown_wpm2 = models.FloatField(blank=True, null=True)
    swdown2_wpm2 = models.FloatField(blank=True, null=True)
    clearsky_wpm2 = models.FloatField(blank=True, null=True)
    rain_mm = models.FloatField(blank=True, null=True)
    cloud_index = models.FloatField(blank=True, null=True)

    class Meta:
        # managed = False
        unique_together = ('timestamp', 'site_name')
        db_table = 'v_wrf_revision'
