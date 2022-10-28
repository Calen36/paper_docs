from django.urls import path

from letters.views import get_extended_letter_url, get_extended_ctrp_url


urlpatterns = [
    path('baseletter/<path:tail>', get_extended_letter_url),
    path('counterparty/<path:tail>', get_extended_ctrp_url),
]
