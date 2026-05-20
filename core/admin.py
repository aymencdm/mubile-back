from django.contrib import admin
from .models import UserProfile, HydrationSession, WaterLog

admin.site.register(UserProfile)
admin.site.register(HydrationSession)
admin.site.register(WaterLog)

