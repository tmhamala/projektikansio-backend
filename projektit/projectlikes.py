# -*- coding: utf-8 -*-

from django.db.models import Max, Min, Prefetch, Count
from .models import  Registereduser, Project, Step, Like, Notification, Comment
from datetime import datetime

from rest_framework import status
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
import uuid, os, base64, boto3, mimetypes
from dateutil.relativedelta import relativedelta


from django.utils.encoding import smart_str
from django.conf import settings
from django.forms.models import model_to_dict
from .profile import check_authorization
from .general_functions import make_projectlist, make_userobject

from django.db import connection





@api_view(['POST'])
@renderer_classes((JSONRenderer,))
def projectlikes(request, project_id):
    
    
    if(request.method == 'POST'):
        return add_projectlike(request, project_id)
    

            


@api_view(['DELETE'])
@renderer_classes((JSONRenderer,))
def projectlike(request, project_id, like_id):


    if(request.method == 'DELETE'):
        return delete_projectlike(request, project_id, like_id)









def add_projectlike(request, project_id):
    
    
    authorization_ok, user_instance = check_authorization(request)

    if(not authorization_ok):
        return Response({'error': True, 'error_message': "Login needed."})
    
    
    
    try:
        projekti = Project.objects.get(id=project_id)
    except:
        return Response({'error': True, 'error_message': "Project not found"})
    
    

    try:
        liketest = Like.objects.get(project = projekti, user = user_instance)
        addProjectlikeResponse = {'error': True, 'error_message': "Already liked."}
        return Response(addProjectlikeResponse)
        
    except:
        newLike = Like(project = projekti, user = user_instance)
        newLike.save()
        projekti.like_count = len(Like.objects.filter(project = projekti))
        projekti.save()
        
        notification = Notification(user = projekti.user, action = "project_like_added", action_maker = user_instance, project = projekti, step = None)
        notification.save()
        
        
        likers = projekti.get_likes()
        
        
    addProjectlikeResponse = {'error': False, 'error_message': '', 'likers': likers}
    return Response(addProjectlikeResponse)


    
    


def delete_projectlike(request, project_id, like_id):
    
    
    authorization_ok, user_instance = check_authorization(request)

    if(not authorization_ok):
        return Response({'error': True, 'error_message': "Login needed."})


    try:
        project = Project.objects.get(id=project_id)
    except:
        removeProjectlikeResponse = {'error': True, 'error_message': "Authentication error."}
        return Response(removeProjectlikeResponse)
    


    try:
        liketest = Like.objects.get(id = like_id, user = user_instance)
        liketest.delete()
        project.like_count = len(Like.objects.filter(project = project))
        project.save()
        
        try:
            notification = Notification.objects.get(action = "project_like_added", action_maker = user_instance, project = project)
            notification.delete()
        except:
            pass
        

        likers = project.get_likes()
        
        
        removeProjectlikeResponse = {'error': False, 'error_message': '', 'likers': likers}
        return Response(removeProjectlikeResponse)
        
    except:
        removeProjectlikeResponse = {'error': True, 'error_message': "Like not found"}
        return Response(removeProjectlikeResponse)
