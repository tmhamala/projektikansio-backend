# -*- coding: utf-8 -*-


from .models import  Registereduser, Activationproject, Step, StepLike, Notification, Comment
from datetime import datetime

from rest_framework.decorators import api_view, renderer_classes
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
import uuid, os, base64
from dateutil.relativedelta import relativedelta
import boto3, mimetypes

from .projects import countNumericTotal
from django.conf import settings
from .profile import check_authorization







@api_view(['POST'])
@renderer_classes((JSONRenderer,))
def stepcomments(request, step_id):
    
    
    
    #NEW STEPCOMMENT
    if(request.method == 'POST'):
        
        authorization_ok, user_instance = check_authorization(request)
    
        if(not authorization_ok):
            return Response({'error': True, 'error_message': 'Authorization error'})
        
        
        try:
            kommentti = request.data['comment']
            step = Step.objects.get(id = step_id)
        
        except:
            response = {'error': True, 'error_message': "Tuntematon ongelma tietojen lukemisen kanssa."}
            return Response(response)
        
        
        try:
            newComment = Comment()
            newComment.user = user_instance       
            newComment.project = None
            newComment.step = step
            newComment.comment = kommentti
            newComment.save()
            
            if(user_instance != step.project.user):
                notification = Notification(user = step.project.user, action = "step_comment_added", action_maker = user_instance, project = step.project, step = step)
                notification.save()
            
        except:
            response = {'error': True, 'error_message': "Tuntematon ongelma."}
            return Response(response)
    
    
        comments = step.get_commentlist()
    
    
    
        response = response = {'error': False, 'error_message': None, 'comments': comments}
        return Response(response)











@api_view(['DELETE'])
@renderer_classes((JSONRenderer,))
def stepcomment(request, step_id, comment_id):
    
    
    #DELETE STEPCOMMENT
    if(request.method == 'DELETE'):
        
        authorization_ok, user_instance = check_authorization(request)
    
        if(not authorization_ok):
            return Response({'error': True, 'error_message': 'Authorization error'})
    
    
        try:
            comment = Comment.objects.get(id = int(comment_id))
            step = comment.step
        except:
            response = {'error': True, 'error_message': "Tuntematon ongelma tietojen lukemisen kanssa."}
            return Response(response)
        
    
        
        if(comment.step.project.user != user_instance and comment.user != user_instance):
            response = {'error': True, 'error_message': "Ei oikeuksia poistaa kommenttia."}
            return Response(response) 
        
        
        
        
        try:
            comment.delete()
        except:
            response = {'error': True, 'error_message': "Tuntematon ongelma."}
            return Response(response)
    
    
    
        kommenttilista = step.get_commentlist()
    
    
        response = response = {'error': False, 'error_message': None, 'comments': kommenttilista}
        return Response(response)









@api_view(['POST'])
@renderer_classes((JSONRenderer,))
def steps(request):
    
    
    #ADD NEW STEP TO PROJECT
    if(request.method == 'POST'):
    
        authorization_ok, user_instance = check_authorization(request)
    
        if(not authorization_ok):
            return Response({'error': True, 'error_message': 'Authorization error'})
        

    
        try:
            project_id = request.data['project_id']
            projekti = Activationproject.objects.get(id=project_id)
        except:
            stepdata = {'error': True, 'error_message': "Project not found"}
        
        
    
        if(projekti.user != user_instance):
            return Response({'error': True, 'error_message': 'Authorization error'})
        
        
    
        newStep = Step()
        newStep.project = projekti
        newStep.topic = request.data['step_topic']
        newStep.description = request.data['step_description']
        try:
            newStep.numeric_value = request.data['step_numeric_value']
        except:
            pass
        
        try:
            newStep.rating = request.data['step_rating']
        except:
            pass
        
        newStep.step_taken = datetime.now()   
        
        imagedata = request.data['proof_image_base64'].split(",")[-1]
        contentType = request.data['proof_image_base64'].split(":")[1].split(";")[0]
        tiedostopaate = request.data['proof_image_name'].split(".")[-1]
            
        kuva = base64.b64decode(imagedata)
        tiedostonimi = "step-" + str(uuid.uuid4()) + "." + tiedostopaate
        
        
        
        if not os.path.exists('{0}/projektikansio/static/temp'.format(settings.BASE_DIR)):
            os.makedirs('{0}/projektikansio/static/temp'.format(settings.BASE_DIR))
    
    
        with open('{0}/projektikansio/static/temp/{1}'.format(settings.BASE_DIR, tiedostonimi), 'wb+') as destination:
            destination.write(kuva)
        
        
        newStep.proof1 = tiedostonimi
        newStep.save()
        
        newStep.move_image_to_s3()
        
        
        projekti.save()
        
        countNumericTotal(projekti)
        
        stepdata = {'error': False, 'error_message': None}
            
    
    
        
        
        return Response(stepdata)









@api_view(['PATCH', 'DELETE'])
@renderer_classes((JSONRenderer,))
def step(request, step_id):
    
    
    
    #EDIT STEP
    if(request.method == 'PATCH'):
    
        authorization_ok, user_instance = check_authorization(request)
    
        if(not authorization_ok):
            return Response({'error': True, 'error_message': 'Authorization error'})
        

    
        try:
            step_topic = request.data['step']['topic_edit']
            step_description = request.data['step']['description_edit']
            step = Step.objects.get(id=step_id)
        except:
            stepdata = {'error': True, 'error_message': "Step not found."}
        
        
        if(step.project.user != user_instance):
            stepdata = {'error': True, 'error_message': "Authentikointitiedot väärin."}

        
        step.topic = step_topic
        step.description = step_description
        try:
            step.numeric_value = request.data['step']['numeric_value_edit']
        except:
            pass
        
        try:
            step.rating = request.data['step']['rating_edit']
        except:
            pass
        
        
        step.save()
        
        
        countNumericTotal(step.project)
        stepdata = {'error': False, 'error_message': ''}
    
        return Response(stepdata)







    #DELETE STEP
    if(request.method == 'DELETE'):
    
        authorization_ok, user_instance = check_authorization(request)
    
        if(not authorization_ok):
            return Response({'error': True, 'error_message': 'Authorization error'})
        

        try:
            step = Step.objects.get(id=step_id)
        except:
            stepdata = {'error': True, 'error_message': "Step not found"}
        
    

        if(step.project.user != user_instance):
            stepdata = {'error': True, 'error_message': "Authentikointitiedot väärin."}

        
        projekti = step.project

        step.poista()
        countNumericTotal(projekti)
        
        stepdata = {'error': False, 'error_message': None}
        
        return Response(stepdata)









@api_view(['POST'])
@renderer_classes((JSONRenderer,))
def steplikes(request, step_id):


    #NEW STEPLIKE
    if(request.method == 'POST'):
    
        authorization_ok, user_instance = check_authorization(request)
    
        if(not authorization_ok):
            return Response({'error': True, 'error_message': 'Authorization error'})


        try:
            step = Step.objects.get(id=step_id)
        except:
            addSteplikeResponse = {'error': True, 'error_message': "Step not found."}
            return Response(addSteplikeResponse)
    

        try:
            liketest = StepLike.objects.get(step = step, user = user_instance)
            addSteplikeResponse = {'error': True, 'error_message': "Step already liked."}
            return Response(addSteplikeResponse)
            
        except:
            pass
        
        

        newLike = StepLike(step = step, user = user_instance)
        newLike.save()
        step.like_count = len(StepLike.objects.filter(step = step))
        step.save()
        notification = Notification(user = step.project.user, action = "step_like_added", action_maker = user_instance, project = step.project, step = step)
        notification.save()
        
          
        likers = step.get_likers()

        addSteplikeResponse = {'error': False, 'error_message': '', 'likers': likers, 'my_like_id': newLike.id}
        return Response(addSteplikeResponse)
        






@api_view(['DELETE'])
@renderer_classes((JSONRenderer,))
def steplike(request, step_id, like_id):


    #DELETE STEP
    if(request.method == 'DELETE'):
    
        authorization_ok, user_instance = check_authorization(request)
    
        if(not authorization_ok):
            return Response({'error': True, 'error_message': 'Authorization error'})
        
    
        try:
            liketest = StepLike.objects.get(id = like_id, user = user_instance)
            step = liketest.step
            liketest.delete()
            step.like_count = len(StepLike.objects.filter(step = step))
            step.save()
            
            try:
                poistettava_notification = Notification.objects.get(action = "step_like_added", action_maker = user_instance, project = step.project, step = step)
                poistettava_notification.delete()
            except:
                pass
            
            
            likers = step.get_likers()
            
            removeSteplikeResponse = {'error': False, 'error_message': '', 'likers': likers}
            return Response(removeSteplikeResponse)
            
        except:
            removeSteplikeResponse = {'error': True, 'error_message': "Like not found."}
            return Response(removeSteplikeResponse)











