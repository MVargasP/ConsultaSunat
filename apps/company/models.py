from django.db import models
from apps.common.models import ModelsBase

class Company(ModelsBase):
    name = models.CharField( max_length=150,unique=True)
    total_sunat = models.IntegerField(default = 0)
    limit_sunat = models.IntegerField(default = 2000)
    date_finish_sunat = models.DateField(null=True)
    token = models.CharField(null=True, max_length=255)

    class Meta:
        db_table = 'Company'