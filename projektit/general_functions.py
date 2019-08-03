# -*- coding: utf-8 -*-

from django.contrib.auth import authenticate


from .models import  Registereduser, Project, Notification, JWTAuthenticationToken
from datetime import datetime
from django.contrib.auth.models import User
from django.db.models import Max
from rest_framework import status
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
import uuid, os, base64, boto3, mimetypes
from dateutil.relativedelta import relativedelta


from wsgiref.util import FileWrapper
import shutil, requests
from django.utils.encoding import smart_str
from django.conf import settings
from jose import jwt

from django.db import connection








def make_projectlist(projects_queryset):
    
    
    projectlist = []
    
    for project in projects_queryset:
    
    
        projektiobjekti = {}
        projektiobjekti['name'] = project.name
        projektiobjekti['id'] = project.id
        projektiobjekti['description'] = project.description
    
        projektiobjekti['project_owner_avatar'] = project.user.avatar_s3_url
        projektiobjekti['like_count'] = project.like_count
        projektiobjekti['latest_step_taken_isoformat'] = project.latest_step_taken
        
        
        if(project.user.name):
            projektiobjekti['project_owner_name'] = project.user.name
        else:
            projektiobjekti['project_owner_name'] = "No name"
            
            
        if(project.certificated_root_project):
            projektiobjekti['certificated_root_project'] = project.certificated_root_project.id
            projektiobjekti['cover_photo_s3_url'] = project.certificated_root_project_cover_photo_s3_url
        else:
            projektiobjekti['certificated_root_project'] = None
            projektiobjekti['cover_photo_s3_url'] = project.cover_photo_s3_url
            
        projektiobjekti['step_count'] = project.step_count
        projektiobjekti['url_token'] = project.url_token
        projektiobjekti['goal'] = project.goal
        projektiobjekti['status'] = project.status
        projektiobjekti['project_likes_allowed'] = project.project_likes_allowed
    
        
        if(project.goal == 'numeric' and project.numeric_goal_unit != 'project_step'):
            projektiobjekti['complete_percentage'] = project.numeric_percentage
        if(project.goal == 'numeric' and project.numeric_goal_unit == 'project_step'):
            projektiobjekti['complete_percentage'] = project.step_percentage    
      
    
        projectlist.append(projektiobjekti)
    
    return projectlist
    
    









def make_userobject(user):

    user_object = {}
    user_object['name'] = user.name
    user_object['username'] = user.user.username
    user_object['email'] = user.email
    user_object['avatar_s3_url'] = user.avatar_s3_url
    user_object['info'] = user.info
    user_object['user_id'] = user.id
    

    
    projects = Project.objects.filter(user = user).annotate(latest_step_taken=Max('step__step_taken')).select_related('user', 'certificated_root_project').order_by('-latest_step_taken')
    
    
    
    user_object['projects'] = make_projectlist(projects)
    
    
    notifications = []
    new_notifications_count = 0
    user_notifications = Notification.objects.filter(user = user).select_related('action_maker', 'project', 'step').order_by('-date')[:20]
    for notification in user_notifications:
        
        notificationelement = {}
        
        
        if(notification.date > user.notifications_read):
            notificationelement['new'] = True
            new_notifications_count = new_notifications_count + 1
        else:
            notificationelement['new'] = False
        
        
        if(notification.action_maker.name):
            notificationelement['action_maker_name'] = notification.action_maker.name
        else:
            notificationelement['action_maker_name'] = "No name"
        
        notificationelement['action_maker_url_token'] = notification.action_maker.url_token
        notificationelement['action_maker_avatar_s3_url'] = notification.action_maker.avatar_s3_url
        
        if(notification.project):
            notificationelement['project_name'] = notification.project.name
            notificationelement['project_url_token'] = notification.project.url_token
        else:
            notificationelement['project_name'] = None
            notificationelement['project_url_token'] = None
            
        if (notification.step):
            notificationelement['step_topic'] = notification.step.topic
            notificationelement['step_id'] = notification.step.id
        else:
            notificationelement['step_topic'] = None
            notificationelement['step_id'] = None
        
        
        notificationelement['date'] = notification.date
        notificationelement['action'] = notification.action
        notifications.append(notificationelement)
        
        
    user_object['notifications'] = notifications
    user_object['new_notifications_count'] = new_notifications_count
    


    if (user.user.username == 'admintomi'):
        user_object['admin'] = True
    else:
        user_object['admin'] = False
    


    return user_object

