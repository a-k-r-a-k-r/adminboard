from django.urls import path
from django.conf.urls import url
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('changecompleted/<todo_id>', views.changecompleted, name='changecompleted'),
    path('segmentation.html', views.pages, name='segmentation'),
    path('result.html', views.showsegmentationresult, name='segmentationresult'),
    path('user-profile.html', views.user_profile, name='user-profile'),
    path('tables.html', views.showtables, name='tables'),
    path('download', views.download, name='download'),
    url(r'^.*\.*', views.pages, name='pages'),
]
# url(r'^.*\.*', views.pages, name='pages'),