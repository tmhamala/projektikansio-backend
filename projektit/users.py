# -*- coding: utf-8 -*-

from .models import  Registereduser, Activationproject

from django.db.models import Max

from rest_framework.decorators import api_view, renderer_classes
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer




@api_view(['GET'])
@renderer_classes((JSONRenderer,))
def user(request, url_token):
    
    
    try:
        user = Registereduser.objects.get(url_token = url_token)
        
        projectlist = []
        projects = Activationproject.objects.filter(user = user).annotate(latest_step_taken=Max('step__step_taken')).order_by('-latest_step_taken')
        
              
        for projekti in projects:
            projectlist.append(projekti.listobject())
            

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
        
        

    