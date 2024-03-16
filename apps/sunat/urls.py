from django.urls import path
from .views.interaction_sunat import ConsultaRucView

urlpatterns = [
    path('consulta_ruc/', ConsultaRucView.as_view(), name='consulta_ruc'),
    #path('apikey/', GenerarAPIKeyView.as_view()),
]