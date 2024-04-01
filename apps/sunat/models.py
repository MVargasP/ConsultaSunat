from django.db import models
from apps.common.models import ModelsBase
from apps.company.models import Company

class InteractionSunat(ModelsBase):
    document_number = models.CharField(max_length=24)
    payload = models.JSONField(null=True)
    company = models.ForeignKey(Company,on_delete=models.CASCADE, null=True)
    scraping = models.BooleanField(default=False,null=True)

    class Meta:
        db_table = 'Interaction_Sunat'

class Ruc(ModelsBase):
    document_number = models.CharField(max_length=24,unique=True)
    payload = models.JSONField(null=True)

    class Meta:
        db_table = 'Ruc'

class Direccion(ModelsBase):
    ruc = models.CharField(max_length=16, unique=True)
    ubigeo = models.CharField(max_length=30,null =True)
    departamento = models.CharField(max_length=250,null =True)
    provincia = models.CharField(max_length=250,null =True)
    distrito = models.CharField(max_length=250,null =True)

    class Meta:
        db_table = 'Direccion_Sunat'

class TempDireccionSunat(models.Model):
    ruc = models.CharField(max_length=16, null=True)
    ubigeo = models.CharField(max_length=30,null =True)
    departamento = models.CharField(max_length=250,null =True)
    provincia = models.CharField(max_length=250,null =True)
    distrito = models.CharField(max_length=250,null =True)
    
    class Meta:
        db_table = 'temporales\".\"Temp_Direccion_Sunat'