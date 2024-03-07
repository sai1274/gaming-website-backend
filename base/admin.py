from django.contrib import admin
from .models import Tournament, Transaction,UTRID, TeamDetail, Matches

# Register your models here.
admin.site.register(Tournament)
admin.site.register(Transaction)
admin.site.register(UTRID)
admin.site.register(TeamDetail)
admin.site.register(Matches)