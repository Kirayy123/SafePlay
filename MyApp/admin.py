from django.contrib import admin
from MyApp.models import Child, Notification, Message, GameSession, Setting
# Register your models here.
admin.site.register(Child)
admin.site.register(Notification)
admin.site.register(Message)
admin.site.register(GameSession)
admin.site.register(Setting)