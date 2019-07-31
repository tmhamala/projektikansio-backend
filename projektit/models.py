# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from django.db.models import Max

import boto3, mimetypes, os
from django.conf import settings


class Registereduser(models.Model):
    
    user = models.OneToOneField(User)
    name = models.CharField(max_length=50, null=True)
    email = models.CharField(max_length=50, null=True)
    info = models.CharField(max_length=1000, null=True)
    
    auth_token = models.CharField(max_length=100, null=True)
    token_valid_until = models.DateTimeField(null=True)
    
    password_reset_token = models.CharField(max_length=100, null=True)
    password_reset_token_valid_until = models.DateTimeField(default=datetime(1800, 1, 1))
    
    avatar = models.CharField(max_length=100, null=True)
    
    avatar_s3_key = models.CharField(max_length=200, null=True)
    avatar_s3_url = models.CharField(max_length=200, null=True)
    
    url_token = models.CharField(max_length=50, null=True, unique=True)
    
    notifications_read = models.DateTimeField(default=datetime(1800, 1, 1))
    
    
    def userobject(self):

        user_object = {}
        user_object['name'] = self.name
        user_object['username'] = self.user.username
        user_object['email'] = self.email
        user_object['avatar_s3_url'] = self.avatar_s3_url
        user_object['info'] = self.info
        user_object['user_id'] = self.id
        
    
        
        projects = Activationproject.objects.filter(user = self).annotate(latest_step_taken=Max('step__step_taken')).order_by('-latest_step_taken')
        
        
        projectlist = []
        for project in projects:
            projectlist.append(project.listobject())
        
        
        user_object['projects'] = projectlist
        
        
        notifications = []
        new_notifications_count = 0
        user_notifications = Notification.objects.filter(user = self).order_by('-date')[:20]
        for notification in user_notifications:
            
            notificationelement = {}
            
            
            if(notification.date > self.notifications_read):
                notificationelement['new'] = True
                new_notifications_count = new_notifications_count + 1
            else:
                notificationelement['new'] = False
            
            
            if(notification.action_maker.name):
                notificationelement['action_maker_name'] = notification.action_maker.name
            else:
                notificationelement['action_maker_name'] = notification.action_maker.user.username
            
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
        
    
    
        if (self.user.username == 'admintomi'):
            user_object['admin'] = True
        else:
            user_object['admin'] = False
        
    
    
        return user_object
        
    
    







    def move_avatar_to_s3(self):
        
        
        if(self.avatar):
            
            session = boto3.Session(
            aws_access_key_id = settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key = settings.AWS_SECRET_ACCESS_KEY,
            )
            
            s3 = session.resource('s3')
            
            contentType = mimetypes.guess_type('{0}/projektikansio/static/temp/{1}'.format(settings.BASE_DIR, self.avatar))[0]
            s3data = open('{0}/projektikansio/static/temp/{1}'.format(settings.BASE_DIR, self.avatar), 'rb')
            
            try:
                s3.Bucket(settings.AWS_S3_BUCKET_NAME).put_object(ACL="public-read", Key='avatarkuvat/{0}'.format(self.avatar), Body=s3data, ContentType=contentType)
                self.avatar_s3_key = 'avatarkuvat/{0}'.format(self.avatar)
                url = '{}/{}/{}'.format('https://s3.eu-west-2.amazonaws.com', 'projektikansio', 'avatarkuvat/{0}'.format(self.avatar))
                self.avatar_s3_url = url
    
                
                s3data.close()
        
                try:
                    os.remove('{0}/projektikansio/static/temp/{1}'.format(settings.BASE_DIR, self.avatar))
                    self.avatar = None
                except:
                    pass
        
                
            except:
                pass
            
        
            
            self.save()
    
        return True
    















class JWTAuthenticationToken(models.Model):
    
    user = models.ForeignKey(Registereduser)
    token = models.CharField(max_length=300, blank=True)
    device_info = models.CharField(max_length=300, blank=True)





class Activationproject(models.Model):
    
    user = models.ForeignKey(Registereduser, null=True)
    
    order_number = models.IntegerField(default=0)
    category = models.CharField(max_length=100, null=True)
    
    certificated_project = models.BooleanField(default=False)
    certificated_root_project = models.ForeignKey('self', on_delete=models.SET_NULL, null=True)
    
    name = models.CharField(max_length=300, null=True)
    description = models.CharField(max_length=10000, null=True)
    cover_photo = models.CharField(max_length=100, null=True)
    
    cover_photo_s3_key = models.CharField(max_length=200, null=True)
    cover_photo_s3_url = models.CharField(max_length=200, null=True)
    certificated_root_project_cover_photo_s3_url = models.CharField(max_length=200, null=True)
    
    
    url_token = models.CharField(max_length=50, null=True, unique=True)
    status = models.CharField(max_length=50, default="active")
    
    project_started = models.DateTimeField(null=True)
    
    goal = models.CharField(max_length=50, null=True)
    
    numeric_goal = models.FloatField(null=True)
    numeric_goal_unit = models.CharField(max_length=50, null=True)
    numeric_total = models.FloatField(null=True, default = 0)
    numeric_percentage = models.FloatField(null=True, default = 0)
    
    step_goal = models.IntegerField(null=True)
    step_count = models.IntegerField(null=True, default = 0)
    step_percentage = models.FloatField(null=True, default = 0)
    
    step_ratings = models.BooleanField(default = False)
    
    like_count = models.IntegerField(null=True, default = 0)
    project_likes_allowed = models.BooleanField(default = True)
    step_likes_allowed = models.BooleanField(default = True)
    step_comments_allowed = models.BooleanField(default = False)
    
    time_limit = models.BooleanField(default = False)
    time_limit_days = models.IntegerField(null=True, default = 30)
    
    
    
    
    def listobject(self):
        
        projektiobjekti = {}
        projektiobjekti['name'] = self.name
        projektiobjekti['id'] = self.id
        projektiobjekti['description'] = self.description


        projektiobjekti['project_owner_avatar'] = self.user.avatar_s3_url
        projektiobjekti['like_count'] = self.like_count
        projektiobjekti['latest_step_taken_isoformat'] = self.latest_step_taken
        
        try:
            projektiobjekti['project_started_isoformat'] = self.first_step_taken
        except:
            projektiobjekti['project_started_isoformat'] = datetime(1800, 1, 1)
        
        if(self.user.name):
            projektiobjekti['project_owner_name'] = self.user.name
        else:
            projektiobjekti['project_owner_name'] = self.user.user.username
            
            
        if(self.certificated_root_project):
            projektiobjekti['certificated_root_project'] = self.certificated_root_project.id
            projektiobjekti['cover_photo_s3_url'] = self.certificated_root_project_cover_photo_s3_url
        else:
            projektiobjekti['certificated_root_project'] = None
            projektiobjekti['cover_photo_s3_url'] = self.cover_photo_s3_url
            
        projektiobjekti['step_count'] = self.step_count
        projektiobjekti['url_token'] = self.url_token
        projektiobjekti['goal'] = self.goal
        projektiobjekti['status'] = self.status
        projektiobjekti['project_likes_allowed'] = self.project_likes_allowed
    
        
        if(self.goal == 'numeric' and self.numeric_goal_unit != 'project_step'):
            projektiobjekti['complete_percentage'] = self.numeric_percentage
        if(self.goal == 'numeric' and self.numeric_goal_unit == 'project_step'):
            projektiobjekti['complete_percentage'] = self.step_percentage    
      
        
        
        if(self.latest_step_taken):
            
            if(self.latest_step_taken.date() == datetime.now().date()):
                projektiobjekti['last_update'] = self.latest_step_taken.strftime("Tänään klo %H:%M")
            elif(self.latest_step_taken.date() == (datetime.now() - relativedelta(days = 1)).date()):
                projektiobjekti['last_update'] = self.latest_step_taken.strftime("Eilen klo %H:%M")
            elif(self.latest_step_taken.date() == (datetime.now() - relativedelta(days = 2)).date()):
                projektiobjekti['last_update'] = self.latest_step_taken.strftime("Toissapäivänä klo %H:%M")
            else:
                projektiobjekti['last_update'] = self.latest_step_taken.strftime("%d.%m.%Y klo %H:%M")
                
        else:
            projektiobjekti['last_update'] = None
    
    
    
        return projektiobjekti
    
    
    
    
    
    
    
    
    def poista(self):
        
        
        all_steps = Step.objects.filter(project = self)
        
        for step in all_steps:
            step.poista()
        

        if self.cover_photo_s3_key:
            

            try:
                if(self.cover_photo_s3_key):
                    session = boto3.Session(
                    aws_access_key_id = settings.AWS_ACCESS_KEY_ID,
                    aws_secret_access_key = settings.AWS_SECRET_ACCESS_KEY,
                    )
                    
                    s3 = session.resource('s3')
                    s3.Object(settings.AWS_S3_BUCKET_NAME, self.cover_photo_s3_key).delete()
    
            except:
                pass
             
             
        self.delete()
    
    
    
    
    
    
    def get_likers(self):
        
        
        likers = []
        project_likers = ProjectLike.objects.filter(project = self)
        for liker in project_likers:
            likerElement = {}
            likerElement['date'] = liker.date
    
            if(liker.user.name):
                likerElement['liker_name'] = liker.user.name
            else:
                likerElement['liker_name'] = liker.user.user.username
            
            likerElement['liker_avatar'] = liker.user.avatar
            likerElement['liker_url_token'] = liker.user.url_token
            
            likers.append(likerElement)
    
    
        return likers
    






    def move_coverphoto_to_s3(self):
        
        
        if(self.cover_photo):
        
        
            session = boto3.Session(
            aws_access_key_id = settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key = settings.AWS_SECRET_ACCESS_KEY,
            )
            
            s3 = session.resource('s3')
            
            contentType = mimetypes.guess_type('{0}/projektikansio/static/temp/{1}'.format(settings.BASE_DIR, self.cover_photo))[0]
            s3data = open('{0}/projektikansio/static/temp/{1}'.format(settings.BASE_DIR, self.cover_photo), 'rb')
            
            try:
                s3.Bucket(settings.AWS_S3_BUCKET_NAME).put_object(ACL="public-read", Key='projektikuvat/{0}/{1}'.format(self.id, self.cover_photo), Body=s3data, ContentType=contentType)
                self.cover_photo_s3_key = 'projektikuvat/{0}/{1}'.format(self.id, self.cover_photo)
                url = '{}/{}/{}'.format('https://s3.eu-west-2.amazonaws.com', 'projektikansio', 'projektikuvat/{0}/{1}'.format(self.id, self.cover_photo))
                self.cover_photo_s3_url = url
                
                s3data.close()
        
                try:
                    os.remove('{0}/projektikansio/static/temp/{1}'.format(settings.BASE_DIR, self.cover_photo))
                    self.cover_photo = None
                except:
                    pass
        
                
            except:
                pass
            
        
            
            self.save()
    
        return True



    
    


class Step(models.Model):
    
    project = models.ForeignKey(Activationproject)
    
    topic = models.CharField(max_length=100, null=True)
    description = models.CharField(max_length=5000, null=True)
    
    proof1 = models.CharField(max_length=100, null=True)
    proof2 = models.CharField(max_length=100, null=True)
    
    proof_s3_key = models.CharField(max_length=200, null=True)
    proof_s3_url = models.CharField(max_length=200, null=True)
    
    step_taken = models.DateTimeField(null=True)
    
    numeric_value = models.FloatField(null=True)
    
    rating = models.FloatField(null=True)
    
    like_count = models.IntegerField(null=True, default=0)
    
    
    
    def poista(self):
        

        if self.proof_s3_key:
            

            try:
                if(self.proof_s3_key):
                    session = boto3.Session(
                    aws_access_key_id = settings.AWS_ACCESS_KEY_ID,
                    aws_secret_access_key = settings.AWS_SECRET_ACCESS_KEY,
                    )
                    
                    s3 = session.resource('s3')
                    s3.Object(settings.AWS_S3_BUCKET_NAME, self.proof_s3_key).delete()
    
            except:
                pass
             
             
        self.delete()
        
        
        
    def get_commentlist(self):
        
        kommenttilista = []
        kommentit = Comment.objects.filter(step = self).select_related('user').order_by('-date')
                
        for kommentti in kommentit:
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
            
            
            
            kommenttilista.append(objekti)
        
        return kommenttilista
    
    
    def get_likers(self):
        
        likers = []
        for liker in self.step_likes.all().order_by('-date'):
            likerElement = {}
            likerElement['id'] = liker.id
            likerElement['date'] = liker.date
        
            if(liker.user.name):
                likerElement['liker_name'] = liker.user.name
            else:
                likerElement['liker_name'] = liker.user.user.username
            
            likerElement['liker_avatar_s3_url'] = liker.user.avatar_s3_url
            likerElement['liker_url_token'] = liker.user.url_token
            
            likers.append(likerElement)
            
        return likers
    
    
    
    
    
    
    
    def move_image_to_s3(self):
    
    
        if(self.proof1):
        
            session = boto3.Session(
            aws_access_key_id = settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key = settings.AWS_SECRET_ACCESS_KEY,
            )
            
            s3 = session.resource('s3')
            
            contentType = mimetypes.guess_type('{0}/projektikansio/static/temp/{1}'.format(settings.BASE_DIR, self.proof1))[0]
            s3data = open('{0}/projektikansio/static/temp/{1}'.format(settings.BASE_DIR, self.proof1), 'rb')
            
            try:
                s3.Bucket(settings.AWS_S3_BUCKET_NAME).put_object(ACL="public-read", Key='projektikuvat/{0}/{1}'.format(self.project.id, self.proof1), Body=s3data, ContentType=contentType)
                self.proof_s3_key = 'projektikuvat/{0}/{1}'.format(self.project.id, self.proof1)
                url = '{}/{}/{}'.format('https://s3.eu-west-2.amazonaws.com', 'projektikansio', 'projektikuvat/{0}/{1}'.format(self.project.id, self.proof1))
                self.proof_s3_url = url
                
                s3data.close()
        
                try:
                    os.remove('{0}/projektikansio/static/temp/{1}'.format(settings.BASE_DIR, self.proof1))
                    self.proof1 = None
                except:
                    pass
        
                
            except:
                pass
            
        
            
            self.save()
    
        return True
    
    
    
    
    
    
    
    
    
    
    
    
    
class ProjectLike(models.Model):
    
    user = models.ForeignKey(Registereduser)
    project = models.ForeignKey(Activationproject, related_name="project_likers")
    
    date = models.DateTimeField(auto_now_add=True)





class StepLike(models.Model):
    
    user = models.ForeignKey(Registereduser)
    step = models.ForeignKey(Step, related_name="step_likes")
    
    date = models.DateTimeField(auto_now_add=True)
    

class Notification(models.Model):
    
    user = models.ForeignKey(Registereduser)
    
    date = models.DateTimeField(auto_now_add=True)
    action = models.CharField(max_length=50, null=True)
    action_maker = models.ForeignKey(Registereduser, related_name='action_maker')
    project = models.ForeignKey(Activationproject, null=True)
    step = models.ForeignKey(Step, null=True)
    
    
    
    
    
class Comment(models.Model):
    
    user = models.ForeignKey(Registereduser)
    project = models.ForeignKey(Activationproject, null=True, related_name="project_comments")
    step = models.ForeignKey(Step, null=True, related_name="step_comments")
    
    date = models.DateTimeField(auto_now_add=True)
    
    comment = models.CharField(max_length=500, null=True)