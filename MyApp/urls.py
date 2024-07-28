from django.conf.urls.static import static

from ParentalNotification import settings
from MyApp import views
from django.urls import path

urlpatterns = [path('', views.login_register, name='login_register'),
               path('logout/', views.user_logout, name='logout'),
               path('selectchild/', views.child_selection, name='childselect'),
               path('fetch_urgent_notifications/', views.fetch_urgent_notifications, name='fetch_urgent_notifications'),
               path('addchild/', views.add_child, name='addchild'),
               path('myaccount/', views.my_account, name='my_account'),
               path('notification/<int:child_id>', views.Notifications, name='notification'),
               path('fetch-notifications/<int:child_id>/', views.fetch_notifications, name='fetch_notifications'),
               path('urgentprocess/<int:notification_id>/<int:fromtag>', views.Urgent_process, name='urgentprocess'),
               path('history/<int:child_id>', views.History, name='history'),
               path('history_detail/<int:gamesession_id>', views.History_detail, name='historydetail'),
               path('setting/<int:child_id>', views.Setup, name='setting'),
               path('communication/<int:child_id>', views.Communication, name='communication'),
               path('fetch-messages/<int:child_id>/', views.fetch_messages, name='fetch_messages'),
               path('fetch-history/<int:child_id>/', views.fetch_history, name='fetch_history'),
               path('report/<int:child_id>', views.Report, name='report'),
               path('bigbuddy/<int:child_id>/<int:fromtag>', views.AIinfo, name='bigbuddy'),
               path('paper/<int:link_id>', views.Paper, name='paper'),

               path('chat_TRY/<int:child_id>', views.ChatGPT_TRY, name='ChatGPT_TRY'),

               ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
