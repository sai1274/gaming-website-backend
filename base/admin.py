from django.contrib import admin
from .models import Tournament, Transaction,UTRID, TeamDetail, Match, CustomUser, Wallet, TeamStat



class CustomUserAdmin(admin.ModelAdmin):
    list_display = ['username', 'phone', 'email', 'is_staff', 'is_superuser', 'is_active']
    search_fields = ['username', 'phone', 'email']
    list_filter = ['is_staff', 'is_superuser', 'is_active']
# Register your models here.
    
# admin.site.unregister(CustomUser)
admin.site.register(Tournament)
admin.site.register(Transaction)
admin.site.register(UTRID)
admin.site.register(TeamDetail)
admin.site.register(Match)
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Wallet)
admin.site.register(TeamStat)
