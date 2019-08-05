# -*- coding: utf-8 -*-

from .models import  Registereduser, Project

from django.db.models import Max

from rest_framework.decorators import api_view, renderer_classes
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from .general_functions import make_projectlist
from django.db.models import Count


@api_view(['GET'])
@renderer_classes((JSONRenderer,))
def user(request, url_token):
    
    
    try:
        user = Registereduser.objects.get(url_token = url_token)
        
        projectlist = []
        projects = Project.objects.filter(user = user).annotate(latest_step_taken=Max('step__step_taken')).prefetch_related('project_likes').order_by('-latest_step_taken')
        
              
        projectlist = make_projectlist(projects)
            

        userdata = {'error': False,
                    'error_message': None,
                    'info': user.info,
                    'name': user.name,
                    'avatar_s3_url': user.avatar_s3_url,
                    'username': user.user.username,
                    'projects': projectlist}
        
        
    except:
        userdata = {'error': True, 'error_message': "User not found."}
        
        
        
        
    return Response(userdata)
        
        

    