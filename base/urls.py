from django.urls import path
from django.contrib import admin
from . import views
from django.conf import settings
from django.conf.urls.static import static

#changing admin header
admin.site.site_header = 'SeniorCare Administration'
#changing admin title
admin.site.index_title = 'User Information Management'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    #path('register_page/', views.register_page, name='register_page'),
    path('main_page/', views.main_page, name='main_page'), 
    path('home_page/', views.home_page, name='home_page'),   
    path('update_page/', views.update_page, name='update_page'),
    path('update_viewinfo_page/<int:id>', views.update_viewinfo_page, name='update_viewinfo_page'),
    
    path('add_senior', views.add_senior, name='add_senior'),
    path('edit/<int:id>', views.edit, name='edit'),
    path('update/<int:id>', views.update, name='update'),
    path('delete/<int:id>', views.delete, name = 'delete'),
   

     path('search/', views.search, name='search'),
     path('search1/', views.search1, name='search1'),

     path('sms/', views.sms, name='sms'),
     path('clear_messages/', views.clear_messages, name='clear_messages'),
     path('delete_individual_message/<int:message_id>/',views.delete_individual_message, name='delete_individual_message'),

    path('claim_page/', views.claim_page, name='claim_page'),  
    path('claim_detail_page/<int:id>/', views.claim_detail_page, name='claim_detail_page'),
    path('claimed_succesfully/<int:id>', views.claimed_succesfully, name='claimed_succesfully'),
    path('claimed_success/<int:id>', views.claimed_success, name='claimed_success'),
    path('claim_verify_page/', views.claim_verify_page, name='claim_verify_page'),
    path('claim_summary_page/', views.claim_summary_page, name='claim_summary_page'),

    path('camera/', views.camera, name='camera'),
    path('osca_preview/<int:id>', views.osca_preview, name='osca_preview'),
    path('preview/<int:id>', views.preview, name='preview'),
    path('capture_image/', views.capture_image, name='capture_image'),

    path('download_summary/', views.download_summary, name='download_summary'),
    
    path('camera_page/<int:id>/', views.camera_page, name='camera_page'),
    path('facial_recognition/<int:id>/', views.facial_recognition, name='facial_recognition'),
    path('match/<int:id>/', views.match, name='match'),
    path('deleted/<int:id>/', views.deleted, name='deleted'),
    path('check_osca_id/', views.check_osca_id, name='check_osca_id'),
    path('profile_page/', views.profile_page, name='profile_page'),
    path('save_allowance/<int:id>/', views.save_allowance, name='save_allowance'),
    path('delete/<int:id>/', views.delete, name='delete'),
    path('retrieve_entry/<int:id>/', views.retrieve_entry, name='retrieve_entry'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)