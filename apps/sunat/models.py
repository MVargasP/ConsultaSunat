from django.db import models
from apps.common.models import ModelsBase
from apps.company.models import Company

class InteractionSunat(ModelsBase):
    document_number = models.CharField(max_length=24)
    payload = models.JSONField(null=True)
    company = models.ForeignKey(Company,on_delete=models.CASCADE, null=True)

    class Meta:
        db_table = 'Interaction_Sunat'

class Ruc(ModelsBase):
    document_number = models.CharField(max_length=24,unique=True)
    payload = models.JSONField(null=True)

    class Meta:
        db_table = 'Ruc'