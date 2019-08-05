# -*- coding: utf-8 -*-


from django.conf.urls import url
from rest_framework import routers



from . import views
from projektit import projects, projectlikes, profile, steps,  users


urlpatterns = [
    url(r'^$', views.index, name='index'),
    
    url(r'^sitemap.txt$', views.sitemap, name='sitemap'),
    
    url(r'^login/$', profile.log_in, name='login'),
    
    
    
    url(r'^profile/$', profile.profile),
    
    url(r'^challenges/$', projects.challenges),
    
    url(r'^projects/$', projects.projects),
    url(r'^projects/(?P<url_token>\w+)/$', projects.project),
    
    url(r'^projects/(?P<project_id>[0-9]+)/projectlikes/$', projectlikes.projectlikes),
    url(r'^projects/(?P<project_id>[0-9]+)/projectlikes/(?P<like_id>[0-9]+)/$', projectlikes.projectlike),
    
    
    
    url(r'^steps/$', steps.steps),
    url(r'^steps/(?P<step_id>[0-9]+)/$', steps.step),
    
    url(r'^steps/(?P<step_id>[0-9]+)/stepcomments/$', steps.stepcomments),
    url(r'^steps/(?P<step_id>[0-9]+)/stepcomments/(?P<comment_id>[0-9]+)/$', steps.stepcomment),

    url(r'^steps/(?P<step_id>[0-9]+)/steplikes/$', steps.steplikes),
    url(r'^steps/(?P<step_id>[0-9]+)/steplikes/(?P<like_id>[0-9]+)/$', steps.steplike),

    url(r'^users/(?P<url_token>\w+)/$', users.user),

    url(r'^notifications/$', profile.notifications),


    url(r'^reset-password-request/$', profile.reset_password_request),
    url(r'^check-password-reset-token-validity/$', profile.check_password_reset_token_validity),
    url(r'^change-password/$', profile.change_password),
    url(r'^delete-account/$', profile.delete_account),
    
    
    
    
    url(r'^send-message/$', views.send_message),
    

]