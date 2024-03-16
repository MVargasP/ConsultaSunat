from django.db import models
from apps.common.models import ModelsBase

class Company(ModelsBase):
    name = models.CharField( max_length=150,unique=True)
    total_sunat = models.IntegerField(default = 0)
    date_finish_sunat = models.DateField(null=True)

    class Meta:
        db_table = 'Company'