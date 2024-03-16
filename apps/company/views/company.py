from rest_framework import generics,permissions
from ..serializers.company import CompanySerializer
from ..models import Company

class CompanyListCreateView(generics.ListCreateAPIView):
    #permission_classes = [  permissions.IsAuthenticated ]
    queryset = Company.objects.all()
    serializer_class = CompanySerializer

class CompanyDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [  permissions.IsAuthenticated ]
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
