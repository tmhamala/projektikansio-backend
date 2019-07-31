# -*- coding: utf-8 -*-

from django.db.models import Max, Min, Prefetch
from .models import  Registereduser, Activationproject, Step, ProjectLike, StepLike, Notification, Comment
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










@api_view(['GET', 'POST'])
@renderer_classes((JSONRenderer,))
def projects(request):
    
    
    #GETS PROJECTLIST
    if(request.method == 'GET'):
        
        
        
        authorization_ok, user_instance = check_authorization(request)
    
        if(authorization_ok):
            userdata = user_instance.userobject()
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
    
    
        
        projektit = Activationproject.objects.annotate(latest_step_taken=Max('step__step_taken'), first_step_taken=Min('step__step_taken')).exclude(latest_step_taken = None)
        if(projects_to_show != 'all'):
            projektit = projektit.filter(status = projects_to_show)
        if(len(search_term) > 0):
            projektit = projektit.filter(name__icontains=search_term)
            
        matching_project_count = projektit.count()
            
        projektit = projektit.order_by(order)[:projects_to_show_count]
        
    
        projektilista = []
        for projekti in projektit:
            projektilista.append(projekti.listobject())
        
    
        all_projects_object = {'error': False, 'error_message': '', 'projects': projektilista, 'matching_project_count': matching_project_count}
    

        
        data = {
            'all_projects_data': all_projects_object,
            'userdata': userdata
        }
        
        
        return Response(data)





    #NEW PROJECT
    if(request.method == 'POST'):


        authorization_ok, user_instance = check_authorization(request)
    
        if(authorization_ok):
            userdata = user_instance.userobject(user_instance)
        else:
            projectdata = {'error': True, 'error_message': "Authorization error."}
            return Response(projectdata)

    
    
        if(not request.data['challenge']):
    
    
            try:
                newProject = Activationproject()
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
                    
    
                    projekti.move_coverphoto_to_s3()
                    
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
                challenge = Activationproject.objects.get(id = challenge_id)
            
            except:
                response = {'challenge_started': False, 'error': True, 'error_message': "Tuntematon ongelma."}
                return Response(response)
            
            
            
            try:
                newProject = Activationproject()
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
        userdata = user_instance.userobject()
    else:
        userdata = None
    
    
    categories = {}
    

    projektilista = []
    
    projektit = Activationproject.objects.filter(certificated_project = True).order_by('order_number')
            
    for projekti in projektit:
        projektiobjekti = {}
        projektiobjekti['name'] = projekti.name
        projektiobjekti['id'] = projekti.id
        projektiobjekti['description'] = projekti.description
        projektiobjekti['cover_photo_s3_url'] = projekti.cover_photo_s3_url
        projektiobjekti['goal'] = projekti.goal
        projektiobjekti['numeric_goal'] = projekti.numeric_goal
        projektiobjekti['numeric_goal_unit'] = projekti.numeric_goal_unit
        projektiobjekti['time_limit'] = projekti.time_limit
        projektiobjekti['time_limit_days'] = projekti.time_limit_days
        projektiobjekti['category'] = projekti.category
        
        categories[projekti.category] = True
        

        enrolled_users_projects = Activationproject.objects.filter(certificated_root_project = projekti).annotate(latest_step_taken=Max('step__step_taken')).select_related('user')
        
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
        
        
        projektiobjekti['challenge_completed_users'] = challenge_completed_users
        projektiobjekti['challenge_accepted_users'] = challenge_accepted_users
        projektiobjekti['enrolled_user_ids'] = enrolled_user_ids
        projektiobjekti['completed_user_ids'] = completed_user_ids
        
        projektilista.append(projektiobjekti)
    
    
    categorylist = [ k for k in categories ]
    
    
    return Response({'error': False, 'error_message': '', 'categories': categorylist, 'challenges': projektilista, 'userdata': userdata})













@api_view(['GET', 'DELETE', 'PATCH'])
@renderer_classes((JSONRenderer,))
def project(request, url_token):
    


    if(request.method == 'GET'):

        try:
            project = Activationproject.objects.prefetch_related('project_likers').get(url_token = url_token)
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
            userdata = user_instance.userobject()
        else:
            userdata = None
    
    
    
    
        
        project_owner_id = project.user.id
        project_owner_name = project.user.name
        project_owner_avatar = project.user.avatar_s3_url
        project_owner_url_token = project.user.url_token
        
        
        steplist = []
        
    
        steps = Step.objects.filter(project = project).prefetch_related('step_comments', 'step_likes')
    
        if(len(search_term) > 0):
            steps = steps.filter(topic__icontains=search_term)
        steps = steps.order_by('-step_taken')[:steps_to_show]
            
            
        
        i = project.step_count
        for step in steps:
            stepelementti = {}
            stepelementti['topic'] = step.topic
            stepelementti['id'] = step.id
            stepelementti['step_taken'] = step.step_taken
            stepelementti['description'] = step.description
            stepelementti['proof1'] = step.proof1
            stepelementti['proof_s3_key'] = step.proof_s3_key
            stepelementti['proof_s3_url'] = step.proof_s3_url
            stepelementti['numeric_value'] = step.numeric_value
            stepelementti['rating'] = step.rating
            stepelementti['like_count'] = step.like_count
            stepelementti['index'] = i
            i = i - 1
            
            
            stepelementti['comments'] = []
            for kommentti in step.step_comments.all().order_by('-date'):
                objekti = {}
                objekti['comment'] = kommentti.comment
                objekti['comment_id'] = kommentti.id
                
                if(kommentti.user.name):
                    objekti['user_name'] = kommentti.user.name
                else:
                    objekti['user_name'] = kommentti.user.user.username
                objekti['user_id'] = kommentti.user.id
                objekti['user_avatar_s3_url'] = kommentti.user.avatar_s3_url
                objekti['user_url_token'] = kommentti.user.url_token
                
                
                if(kommentti.date.date() == datetime.now().date()):
                    objekti['date'] = kommentti.date.strftime("Tänään klo %H:%M")
                elif(kommentti.date.date() == (datetime.now() - relativedelta(days = 1)).date()):
                    objekti['date'] = kommentti.date.strftime("Eilen klo %H:%M")
                elif(kommentti.date.date() == (datetime.now() - relativedelta(days = 2)).date()):
                    objekti['date'] = kommentti.date.strftime("Toissapäivänä klo %H:%M")
                else:
                    objekti['date'] = kommentti.date.strftime("%d.%m.%Y klo %H:%M")
            
            
            
                stepelementti['comments'].append(objekti)
                
                
                
                
                
            stepelementti['likers'] = []
            stepelementti['step_liked'] = False;
            for liker in step.step_likes.all().order_by('-date'):
                
                if(userdata):
                    if(liker.user.id == userdata['user_id']):
                        stepelementti['step_liked'] = True
                        stepelementti['my_like_id'] = liker.id
                
                
                likerElement = {}
                likerElement['date'] = liker.date
            
                if(liker.user.name):
                    likerElement['liker_name'] = liker.user.name
                else:
                    likerElement['liker_name'] = liker.user.user.username
                
                likerElement['liker_avatar_s3_url'] = liker.user.avatar_s3_url
                likerElement['liker_url_token'] = liker.user.url_token
                
                stepelementti['likers'].append(likerElement)
                
                  
            
            steplist.append(stepelementti)
    
        
        
        try:
            project_started = Step.objects.filter(project = project).order_by('step_taken').first().step_taken
        except:
            project_started = None
            
        
        
        likers = []
        project_liked = False
        my_like_id = None
        project_likers = ProjectLike.objects.filter(project = project).prefetch_related('user')
        for liker in project_likers:
            
            if(userdata):
                if(liker.user.id == userdata['user_id']):
                    project_liked = True
                    my_like_id = liker.id
            
            likerElement = {}
            likerElement['date'] = liker.date
    
            if(liker.user.name):
                likerElement['liker_name'] = liker.user.name
            else:
                likerElement['liker_name'] = liker.user.user.username
            
            likerElement['liker_avatar_s3_url'] = liker.user.avatar_s3_url
            likerElement['liker_url_token'] = liker.user.url_token
            
            likers.append(likerElement)
        
        
        
        
        if(project.certificated_root_project):
            certificated_root_project_id = project.certificated_root_project.id
        else:
            certificated_root_project_id = None
        
        
        if(not project_started):
            days_passed = 0
            days_passed_percentage = 0
        elif(project.time_limit and project.time_limit_days):
            days_passed = (datetime.now() - project_started).days
            days_passed_percentage = (days_passed * 100) / project.time_limit_days
        else:
            days_passed = 0
            days_passed_percentage = 0
            
            
        
        if(project.certificated_root_project):
            cover_photo_s3_url = project.certificated_root_project_cover_photo_s3_url
        else:
            cover_photo_s3_url = project.cover_photo_s3_url
            
        
        
        
        projectdata = {
                       'error': False,
                       'error_message': None,
                       'project_owner_id': project_owner_id,
                       'project_owner_url_token': project_owner_url_token,
                       'project_owner_avatar': project_owner_avatar,
                       'project_owner_name': project_owner_name,
                       'name': project.name,
                       'description': project.description,
                       'cover_photo_s3_url': cover_photo_s3_url,
                       'goal': project.goal,
                       'numeric_goal': project.numeric_goal,
                       'numeric_goal_unit': project.numeric_goal_unit,
                       'numeric_total': project.numeric_total,
                       'numeric_percentage': project.numeric_percentage,
                       'step_goal': project.step_goal,
                       'step_percentage': project.step_percentage,
                       'step_ratings': project.step_ratings,
                       'step_count': project.step_count,
                       'like_count': project.like_count,
                       'id': project.id,
                       'time_limit': project.time_limit,
                       'time_limit_days': project.time_limit_days,
                       'days_passed': days_passed,
                       'days_passed_percentage': days_passed_percentage,
                       'project_started': project_started,
                       'status': project.status,
                       'certificated_project': project.certificated_project,
                       'certificated_root_project': certificated_root_project_id,
                       'project_likes_allowed': project.project_likes_allowed,
                       'step_likes_allowed': project.step_likes_allowed,
                       'step_comments_allowed': project.step_comments_allowed,
                       'steps': steplist,
                       'project_liked': project_liked,
                       'my_like_id': my_like_id,
                       'category': project.category,
                       'order_number': project.order_number,
                       'likers': likers}
        
        
        return Response({'error': False, 'error_message': '', 'projectdata': projectdata, 'userdata': userdata})






    if(request.method == 'DELETE'):

        authorization_ok, user_instance = check_authorization(request)
    
        if(not authorization_ok):
            projectDeleteResponse = {'error': True, 'error_message': "Login needed."}
            return Response(projectDeleteResponse)


        try:
            projekti = Activationproject.objects.get(url_token=url_token)
        except:
            projectDeleteResponse = {'error': True, 'error_message': "Project not found"}
            return Response(projectDeleteResponse)
        
    
        if(projekti.user != user_instance):
            projectDeleteResponse = {'error': True, 'error_message': "Authorization error"}
            return Response(projectDeleteResponse)
    
    
        try:
            projekti.poista()
        except:
            pass
        
        
        projectDeleteResponse = {'error': False, 'error_message': ''}
        return Response(projectDeleteResponse)








    if(request.method == 'PATCH'):


        authorization_ok, user_instance = check_authorization(request)
    
        if(not authorization_ok):
            return Response({'error': True, 'error_message': "Login needed."})



        try:
            projekti = Activationproject.objects.get(url_token = url_token)
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
        
        
        countNumericTotal(projekti)
        projectEditResponse = {'error': False, 'error_message': ''}
        return Response(projectEditResponse)


































@api_view(['POST'])
@renderer_classes((JSONRenderer,))
def projectlikes(request, project_id):
    
    
    if(request.method == 'POST'):

        
    
        authorization_ok, user_instance = check_authorization(request)
    
        if(not authorization_ok):
            return Response({'error': True, 'error_message': "Login needed."})
        
        
        
        try:
            projekti = Activationproject.objects.get(id=project_id)
        except:
            return Response({'error': True, 'error_message': "Project not found"})
        
        
    
        try:
            liketest = ProjectLike.objects.get(project = projekti, user = user_instance)
            addProjectlikeResponse = {'error': True, 'error_message': "Already liked."}
            return Response(addProjectlikeResponse)
            
        except:
            newLike = ProjectLike(project = projekti, user = user_instance)
            newLike.save()
            projekti.like_count = len(ProjectLike.objects.filter(project = projekti))
            projekti.save()
            
            notification = Notification(user = projekti.user, action = "project_like_added", action_maker = user_instance, project = projekti, step = None)
            notification.save()
            
            
            likers = projekti.get_likers()
            
    
     
            
            
            addProjectlikeResponse = {'error': False, 'error_message': '', 'likers': likers, 'my_like_id': newLike.id}
            return Response(addProjectlikeResponse)
            












@api_view(['DELETE'])
@renderer_classes((JSONRenderer,))
def projectlike(request, project_id, like_id):


    if(request.method == 'DELETE'):


        authorization_ok, user_instance = check_authorization(request)
    
        if(not authorization_ok):
            return Response({'error': True, 'error_message': "Login needed."})
    

        try:
            projekti = Activationproject.objects.get(id=project_id)
        except:
            removeProjectlikeResponse = {'error': True, 'error_message': "Authentikointitiedot väärin. Yritä myöhemmin uudelleen."}
            return Response(removeProjectlikeResponse)
        
    
    
        try:
            liketest = ProjectLike.objects.get(id = like_id, user = user_instance)
            liketest.delete()
            projekti.like_count = len(ProjectLike.objects.filter(project = projekti))
            projekti.save()
            
            try:
                poistettava_notification = Notification.objects.get(action = "project_like_added", action_maker = user_instance, project = projekti)
                poistettava_notification.delete()
            except:
                pass
            

            likers = projekti.get_likers()
            
            
            removeProjectlikeResponse = {'error': False, 'error_message': '', 'likers': likers}
            return Response(removeProjectlikeResponse)
            
        except:
            removeProjectlikeResponse = {'error': True, 'error_message': "Tykkäystä ei löytynyt."}
            return Response(removeProjectlikeResponse)







def countNumericTotal(project):
    
    
    projectSteps = Step.objects.filter(project = project)
    
    project.step_count = len(projectSteps)
    
    
    try:
        step_percentage = (project.step_count * 100) / project.numeric_goal
        if(step_percentage < 0):
            step_percentage = 0
        if (step_percentage > 100):
            step_percentage = 100   
    except:
        step_percentage = 0
    
    
    
    
    
    
    count = 0
    for step in projectSteps:
        if(step.numeric_value):
            count = count + step.numeric_value
    
    project.numeric_total = count
    
    
    try:
        numeric_percentage = (project.numeric_total * 100) / project.numeric_goal
        if(numeric_percentage < 0):
            numeric_percentage = 0
        if (numeric_percentage > 100):
            numeric_percentage = 100   
    except:
        numeric_percentage = 0
    
    
    
    project.step_percentage = step_percentage
    project.numeric_percentage = numeric_percentage
    project.save()







