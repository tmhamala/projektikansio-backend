# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from django.db.models import Max
from django.forms.models import model_to_dict
import boto3, mimetypes, os
from django.conf import settings
#from .projects import make_projectlist
from django.db.models.query import QuerySet
from django.db.models import Prefetch



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





class Project(models.Model):
    
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
    
    
    
    
    
    
    def get_likes(self, prefetched_likes = None):
        
        
        likelist = []
        
        if(isinstance(prefetched_likes, QuerySet)):
            likes = prefetched_likes
        else:
            likes = self.project_likes.all().prefetch_related('user').order_by('-date')
        
        for like in likes:
            likeDict = {}
            likeDict['id'] = like.id
            likeDict['date'] = like.date
        
            if(like.user.name):
                likeDict['liker_name'] = like.user.name
            else:
                likeDict['liker_name'] = "No name"
            
            likeDict['liker_avatar_s3_url'] = like.user.avatar_s3_url
            likeDict['liker_url_token'] = like.user.url_token
            likeDict['liker_id'] = like.user.id
            
            likelist.append(likeDict)
            
        return likelist






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



    
    
    
    
    
    def get_steps(self, search_term = '', start_index = 0, end_index = 0, steps_to_show = 10):
    
    
        step_comments_qs = Comment.objects.prefetch_related('user')
        step_likes_qs = Like.objects.prefetch_related('user')
    
        steplist = []
        
        steps = Step.objects.filter(project = self).prefetch_related(
            Prefetch('step_comments', queryset=step_comments_qs),
            Prefetch('step_likes', queryset=step_likes_qs),
            )
                      

    
        if(len(search_term) > 0):
            steps = steps.filter(topic__icontains=search_term)
        steps = steps.order_by('-step_taken')[:steps_to_show]
            
            
        
        i = self.step_count
        for step in steps:
            
            stepelement = model_to_dict(step)
            stepelement['index'] = i
            i = i - 1
            
            stepelement['comments'] = step.get_commentlist(prefetched_comments = step.step_comments.all())
            stepelement['likers'] = step.get_likers(prefetched_likers = step.step_likes.all())
            
            steplist.append(stepelement)
    
    
        return steplist
    
    



    def count_numeric_total(self):
        
        steps = Step.objects.filter(project = self)
        
        self.step_count = len(steps)
        
        try:
            step_percentage = (self.step_count * 100) / self.numeric_goal
            if(step_percentage < 0):
                step_percentage = 0
            if (step_percentage > 100):
                step_percentage = 100   
        except:
            step_percentage = 0
        
        
        count = 0
        for step in steps:
            if(step.numeric_value):
                count = count + step.numeric_value
        
        self.numeric_total = count
        
        
        try:
            numeric_percentage = (self.numeric_total * 100) / self.numeric_goal
            if(numeric_percentage < 0):
                numeric_percentage = 0
            if (numeric_percentage > 100):
                numeric_percentage = 100   
        except:
            numeric_percentage = 0
        
        
        
        self.step_percentage = step_percentage
        self.numeric_percentage = numeric_percentage
        self.save()

        return True












class Step(models.Model):
    
    project = models.ForeignKey(Project)
    
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
        
        
        
    def get_commentlist(self, prefetched_comments = None):
        
        kommenttilista = []

        
        if(isinstance(prefetched_comments, QuerySet)):
            kommentit = prefetched_comments
        else:
            kommentit = Comment.objects.filter(step = self).prefetch_related('user').order_by('-date')
                
        for kommentti in kommentit:
            objekti = {}
            objekti['comment'] = kommentti.comment
            objekti['comment_id'] = kommentti.id
            
            if(kommentti.user.name):
                objekti['user_name'] = kommentti.user.name
            else:
                objekti['user_name'] = "No name"
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
    
    
    def get_likers(self, prefetched_likers = None):
        
        likerlist = []
        
        if(isinstance(prefetched_likers, QuerySet)):
            likers = prefetched_likers
        else:
            likers = self.step_likes.all().prefetch_related('user').order_by('-date')
        
        for liker in likers:
            likerElement = {}
            likerElement['id'] = liker.id
            likerElement['date'] = liker.date
        
            if(liker.user.name):
                likerElement['liker_name'] = liker.user.name
            else:
                likerElement['liker_name'] = "No name"
            
            likerElement['liker_avatar_s3_url'] = liker.user.avatar_s3_url
            likerElement['liker_url_token'] = liker.user.url_token
            likerElement['liker_id'] = liker.user.id
            
            likerlist.append(likerElement)
            
        return likerlist
    
    
    
    
    
    
    
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
    
    
    
    
    
    
    
    
    
    
    




class Like(models.Model):
    
    user = models.ForeignKey(Registereduser)
    
    step = models.ForeignKey(Step, null = True, related_name="step_likes")
    project = models.ForeignKey(Project, null = True, related_name="project_likes")
    
    date = models.DateTimeField(auto_now_add=True)
    

class Notification(models.Model):
    
    user = models.ForeignKey(Registereduser)
    
    date = models.DateTimeField(auto_now_add=True)
    action = models.CharField(max_length=50, null=True)
    action_maker = models.ForeignKey(Registereduser, related_name='action_maker')
    project = models.ForeignKey(Project, null=True)
    step = models.ForeignKey(Step, null=True)
    
    
    
    
    
class Comment(models.Model):
    
    user = models.ForeignKey(Registereduser)
    project = models.ForeignKey(Project, null=True, related_name="project_comments")
    step = models.ForeignKey(Step, null=True, related_name="step_comments")
    
    date = models.DateTimeField(auto_now_add=True)
    
    comment = models.CharField(max_length=500, null=True)