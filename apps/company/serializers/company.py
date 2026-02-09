from rest_framework import serializers
from ..models import Company

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ["id","name", "total_sunat","limit_sunat", "date_finish_sunat","created_at"]