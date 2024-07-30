from django.contrib import admin
from MyApp.models import Child, Notification, Message, GameSession, Setting,\
    GameSetting,GeneralSetting,SingleGameSetting,ArtSetting,FitnessSetting,EducationSetting,ChatSetting
# Register your models here.
admin.site.register(Child)
admin.site.register(Notification)
admin.site.register(Message)
admin.site.register(GameSession)
admin.site.register(Setting)
admin.site.register(GameSetting)
admin.site.register(SingleGameSetting)
admin.site.register(GeneralSetting)
admin.site.register(ArtSetting)
admin.site.register(FitnessSetting)
admin.site.register(EducationSetting)
admin.site.register(ChatSetting)