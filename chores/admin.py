from django.contrib import admin

from .models import ChoreOccurrence, ChoreSeries

admin.site.register(ChoreSeries)
admin.site.register(ChoreOccurrence)
