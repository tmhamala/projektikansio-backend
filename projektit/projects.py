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









@api_view(['GET', 'POST'])
@renderer_classes((JSONRenderer,))
def projects(request):
    
    
    #GETS PROJECTLIST
    if(request.method == 'GET'):
        
        
        
        authorization_ok, user_instance = check_authorization(request)
    
        if(authorization_ok):
            userdata = make_userobject(user_instance)
        else:
            userdata = None
        
        
        
    
        try:
            projects_to_show_count = int(request.GET.get('projectsToShowCount', 20))
        except:
            projects_to_show_count = 20
            
            
        try:
            order = request.GET.get('order', '-latest_step_taken')
        except:
            order = '-latest_step_taken'
    
        try:
            projects_to_show = request.GET.get('projectsToShow', 'all')
        except:
            projects_to_show = 'all'
    
        try:
            search_term = request.GET.get('searchTerm', '')
        except:
            search_term = ''
    
        
        
        projects = Project.objects.annotate(latest_step_taken=Max('step__step_taken')).select_related('user', 'certificated_root_project').prefetch_related('project_likes').exclude(latest_step_taken = None)
        if(projects_to_show != 'all'):
            projects = projects.filter(status = projects_to_show)
        if(len(search_term) > 0):
            projects = projects.filter(name__icontains=search_term)
            
        matching_project_count = projects.count()
            
        projects = projects.order_by(order)[:projects_to_show_count]
        
        projectlist = make_projectlist(projects)
    
        all_projects_object = {'error': False, 'error_message': '', 'projects': projectlist, 'matching_project_count': matching_project_count}
    
    
        data = {
            'all_projects_data': all_projects_object,
            'userdata': userdata
        }
        
        
        return Response(data)





    #NEW PROJECT
    if(request.method == 'POST'):


        authorization_ok, user_instance = check_authorization(request)
    
        if(authorization_ok):
            userdata = make_userobject(user_instance)
        else:
            projectdata = {'error': True, 'error_message': "Authorization error."}
            return Response(projectdata)

    
    
        if(not request.data['challenge']):
    
    
            try:
                newProject = Project()
                newProject.user = user_instance        
                newProject.name = request.data['project_name']
                newProject.description = request.data['project_info']
                newProject.project_started = datetime.now()
                newProject.url_token = str(uuid.uuid4()).split("-")[-1]
                newProject.step_count = 0
                newProject.goal = 'no-goal'
                newProject.save()
                
            
                if not os.path.exists('{0}/projektikansio/static/temp'.format(settings.BASE_DIR)):
                    os.makedirs('{0}/projektikansio/static/temp'.format(settings.BASE_DIR))
                
                
                try:
                    imagedata = request.data['project_cover_photo_base64'].split(",")[-1]
                    tiedostopaate = request.data['project_cover_photo_name'].split(".")[-1]
                    kuva = base64.b64decode(imagedata)
                    tiedostonimi = "cover-" + str(uuid.uuid4()) + "." + tiedostopaate
    
                    with open('{0}/projektikansio/static/temp/{1}'.format(settings.BASE_DIR, tiedostonimi), 'wb+') as destination:
                        destination.write(kuva)
                
                    newProject.cover_photo = tiedostonimi
                    newProject.save()
                    
    
                    newProject.move_coverphoto_to_s3()
                    
                except:
                    newProject.cover_photo = None
                    newProject.save()
            
                projectdata = {'error': False, 'error_message': None}
    
            except:
                projectdata = {'error': True, 'error_message': "Authentikointitiedot virheelliset."}
            
            
            return Response(projectdata)





        if(request.data['challenge']):

            try:
                challenge_id = request.data['challenge_id']
                challenge = Project.objects.get(id = challenge_id)
            
            except:
                response = {'challenge_started': False, 'error': True, 'error_message': "Tuntematon ongelma."}
                return Response(response)
            
            
            
            try:
                newProject = Project()
                newProject.user = user_instance  
                newProject.name = challenge.name
                newProject.description = challenge.description
                newProject.project_started = datetime.now()
                newProject.url_token = str(uuid.uuid4()).split("-")[-1]
                newProject.step_count = 0
                newProject.certificated_root_project = challenge
                newProject.certificated_root_project_cover_photo_s3_url = challenge.cover_photo_s3_url
                newProject.cover_photo = challenge.cover_photo
                newProject.goal = challenge.goal
                newProject.numeric_goal = challenge.numeric_goal
                newProject.numeric_goal_unit = challenge.numeric_goal_unit
                newProject.step_goal = newProject.step_goal
                
                newProject.time_limit = challenge.time_limit
                newProject.time_limit_days = challenge.time_limit_days
                newProject.save()
            except:
                response = {'challenge_started': False, 'error': True, 'error_message': "Tuntematon ongelma."}
                return Response(response)
        
        
            response = response = {'challenge_started': True, 'error': False, 'error_message': None, 'project_url_token': newProject.url_token}
            return Response(response)




@api_view(['GET'])
@renderer_classes((JSONRenderer,))
def challenges(request):
    
    
    authorization_ok, user_instance = check_authorization(request)

    if(authorization_ok):
        userdata = make_userobject(user_instance)
    else:
        userdata = None
    
    
    categories = {}
    

    projectlist = []
    
    projects = Project.objects.filter(certificated_project = True).order_by('order_number')
            
    for project in projects:
        
        projectobject = model_to_dict(project)
        
        
        categories[project.category] = True
        
        enrolled_users_projects = Project.objects.filter(certificated_root_project = project).annotate(latest_step_taken=Max('step__step_taken')).select_related('user')
        
        challenge_completed_users = []
        challenge_accepted_users = []
        enrolled_user_ids = []
        completed_user_ids = []
        
        for enrolled_user_project in enrolled_users_projects:
            
            
            challenge_user_object = {}
            if(enrolled_user_project.user.name):
                challenge_user_object['name'] = enrolled_user_project.user.name
            else:
                challenge_user_object['name'] = enrolled_user_project.user.user.username
            challenge_user_object['project_started'] = enrolled_user_project.project_started
            challenge_user_object['latest_step_taken'] = enrolled_user_project.latest_step_taken
            challenge_user_object['project_token'] = enrolled_user_project.url_token
            
            challenge_user_object['complete_percentage'] = enrolled_user_project.numeric_percentage

            
            
            if(enrolled_user_project.status == 'ready'):
                challenge_completed_users.append(challenge_user_object)
                completed_user_ids.append(enrolled_user_project.user.id)
            else:
                challenge_accepted_users.append(challenge_user_object)
                enrolled_user_ids.append(enrolled_user_project.user.id)
        
        
        projectobject['challenge_completed_users'] = challenge_completed_users
        projectobject['challenge_accepted_users'] = challenge_accepted_users
        projectobject['enrolled_user_ids'] = enrolled_user_ids
        projectobject['completed_user_ids'] = completed_user_ids
        
        projectlist.append(projectobject)
    
    
    categorylist = [ k for k in categories ]
    
    
    return Response({'error': False, 'error_message': '', 'categories': categorylist, 'challenges': projectlist, 'userdata': userdata})













@api_view(['GET', 'DELETE', 'PATCH'])
@renderer_classes((JSONRenderer,))
def project(request, url_token):
    


    if(request.method == 'GET'):

        try:
            project = Project.objects.select_related('user', 'certificated_root_project').prefetch_related('project_likes').get(url_token = url_token)
        except:
            projectdata = {'error': True, 'error_message': "Project not found."}
            return Response(projectdata)
        
        
        try:
            steps_to_show = int(request.GET.get('steps_to_show', 10))
        except:
            steps_to_show = 10  
    
        
        try:
            search_term = request.GET.get('search_term', '')
        except:
            search_term = ''
    
    
    
        authorization_ok, user_instance = check_authorization(request)
    
        if(authorization_ok):
            userdata = make_userobject(user_instance)
        else:
            userdata = None
            
        
        
        
        projectDict = model_to_dict(project)

        projectDict['project_owner_id'] = project.user.id
        projectDict['project_owner_name'] = project.user.name
        projectDict['project_owner_avatar'] = project.user.avatar_s3_url
        projectDict['project_owner_url_token'] = project.user.url_token
        
        
        projectDict['steps'] = project.get_steps(search_term = search_term, steps_to_show = steps_to_show)
        projectDict['likers'] = project.get_likes(prefetched_likes = project.project_likes.all())
    
        
        
        try:
            projectDict['project_started'] = Step.objects.filter(project = project).order_by('step_taken').first().step_taken
        except:
            projectDict['project_started'] = None
            
        
        if(project.certificated_root_project):
            projectDict['certificated_root_project_id'] = project.certificated_root_project.id
            projectDict['cover_photo_s3_url'] = project.certificated_root_project.cover_photo_s3_url
        else:
            projectDict['certificated_root_project_id'] = None
        
        
        if(not projectDict['project_started']):
            projectDict['days_passed'] = 0
            projectDict['days_passed_percentage'] = 0
        elif(project.time_limit and project.time_limit_days):
            projectDict['days_passed'] = (datetime.now() - projectDict['project_started']).days
            projectDict['days_passed_percentage'] = (projectDict['days_passed'] * 100) / project.time_limit_days
        else:
            projectDict['days_passed'] = 0
            projectDict['days_passed_percentage'] = 0
            
            
    
            
    
            
        
        
        return Response({'error': False, 'error_message': '', 'projectdata': projectDict, 'userdata': userdata})






    if(request.method == 'DELETE'):

        authorization_ok, user_instance = check_authorization(request)
    
        if(not authorization_ok):
            projectDeleteResponse = {'error': True, 'error_message': "Login needed."}
            return Response(projectDeleteResponse)


        try:
            projekti = Project.objects.get(url_token=url_token)
        except:
            projectDeleteResponse = {'error': True, 'error_message': "Project not found"}
            return Response(projectDeleteResponse)
        
    
        if(projekti.user != user_instance):
            projectDeleteResponse = {'error': True, 'error_message': "Authorization error"}
            return Response(projectDeleteResponse)
    
    
        try:
            projekti.remove_files_and_delete()
        except:
            pass
        
        
        projectDeleteResponse = {'error': False, 'error_message': ''}
        return Response(projectDeleteResponse)








    if(request.method == 'PATCH'):


        authorization_ok, user_instance = check_authorization(request)
    
        if(not authorization_ok):
            return Response({'error': True, 'error_message': "Login needed."})



        try:
            projekti = Project.objects.get(url_token = url_token)
        except:
            projectEditResponse = {'error': True, 'error_message': "Project not found"}
            return Response(projectEditResponse)
        
        
    
        if(projekti.user != user_instance):
            projectEditResponse = {'error': True, 'error_message': "Authentikointitiedot väärin. Yritä myöhemmin uudelleen."}
            return Response(projectEditResponse)
    
    
            
        projekti.name = request.data['project']['name_edit']
        projekti.description = request.data['project']['description_edit']
        projekti.goal = request.data['project']['goal_edit']
        projekti.numeric_goal = request.data['project']['numeric_goal_edit']
        projekti.step_goal = request.data['project']['step_goal_edit']
        projekti.numeric_goal_unit = request.data['project']['numeric_goal_unit_edit']
        projekti.step_ratings = request.data['project']['step_ratings_edit']
        projekti.status = request.data['project']['status_edit']
        projekti.project_likes_allowed = request.data['project']['project_likes_allowed_edit']
        projekti.step_likes_allowed = request.data['project']['step_likes_allowed_edit']
        projekti.step_comments_allowed = request.data['project']['step_comments_allowed_edit']
        projekti.time_limit = request.data['project']['time_limit_edit']
        projekti.time_limit_days = request.data['project']['time_limit_days_edit']
        
        
        if(user_instance.user.username == 'admintomi' and request.data['project']['certificated_project_edit'] == True):
            projekti.certificated_project = True
            projekti.category = request.data['project']['category_edit']
            projekti.order_number = request.data['project']['order_number_edit']
        else:
            projekti.certificated_project = False
        
        
        
        try:
            
            #TALLENNETAAN UUSI COVERPHOTO LOKAALIIN TEMPPIIN
            imagedata = request.data['project_coverphoto_data']['project_new_coverphoto_image_base64'].split(",")[-1]
            tiedostopaate = request.data['project_coverphoto_data']['project_new_coverphoto_image_name'].split(".")[-1]
            kuva = base64.b64decode(imagedata)
            tiedostonimi = "cover-" + str(uuid.uuid4()) + "." + tiedostopaate
    
            with open('{0}/projektikansio/static/temp/{1}'.format(settings.BASE_DIR, tiedostonimi), 'wb+') as destination:
                destination.write(kuva)
        
            
            projekti.cover_photo = tiedostonimi
            
            
            #POISTETAAN VANHA COVER PHOTO S3SESTA
            if projekti.cover_photo_s3_key:
                
                try:
                    if(projekti.cover_photo_s3_key):
                        session = boto3.Session(
                        aws_access_key_id = settings.AWS_ACCESS_KEY_ID,
                        aws_secret_access_key = settings.AWS_SECRET_ACCESS_KEY,
                        )
                        
                        s3 = session.resource('s3')
                        s3.Object(settings.AWS_S3_BUCKET_NAME, projekti.cover_photo_s3_key).delete()
        
                except:
                    pass
            
            
            
            #SIIRRETÄÄN TEMPIN COVER PHOTO S3SEEN JA POISTETAAN TEMP
            projekti.move_coverphoto_to_s3()
            
            
        
        except:
            pass
        
        
        
        projekti.save()
        
        
        projekti.count_numeric_total()
        projectEditResponse = {'error': False, 'error_message': ''}
        return Response(projectEditResponse)
































