from django.contrib import admin
from .models import Tournament, Transaction,UTRID, TeamDetail, Match, CustomUser, Wallet, TeamStat

# Register your models here.
admin.site.register(Tournament)
admin.site.register(Transaction)
admin.site.register(UTRID)
admin.site.register(TeamDetail)
admin.site.register(Match)
admin.site.register(CustomUser)
admin.site.register(Wallet)
admin.site.register(TeamStat)