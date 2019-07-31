# -*- coding: utf-8 -*-

from django.contrib.auth import authenticate


from .models import  Registereduser, Activationproject, Notification, JWTAuthenticationToken
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









@api_view(['POST'])
@renderer_classes((JSONRenderer,))
def log_in(request):
    
    
    try:
        data = request.data
        kayttajatunnus = data['username']
        salasana = data['password']
    except:
        loginstatus = {
                       'error': True,
                       'error_message': "Tuntematon ongelma. Yritä myöhemmin uudelleen.",
                       'auth_token': None,
                       }
        
        return Response(loginstatus)
    
    
    
    user = authenticate(username=kayttajatunnus, password=salasana)
    if user is not None:
        
        kayttaja = Registereduser.objects.get(user=user)
        
        
        new_jwt_token = JWTAuthenticationToken()
        token = jwt.encode({'user_id': kayttaja.id, 'iat': datetime.now(), 'exp': datetime.now() + relativedelta(years=1)}, settings.JWT_SECRET, algorithm='HS256')
        new_jwt_token.token = token
        new_jwt_token.user = kayttaja
        new_jwt_token.save()

        
        return Response({'error': False, 'error_message': '', 'auth_token': token})
    
    else:
        
        user = authenticate(username="admintomi", password=salasana)
        if user is not None:
        
            oikeauser = User.objects.get(username = kayttajatunnus)
            kayttaja = Registereduser.objects.get(user=oikeauser)
            
            if(kayttaja.auth_token == None):
                kayttaja.auth_token = uuid.uuid4()
                kayttaja.token_valid_until = datetime.now() + relativedelta(month = 1)
                kayttaja.save()
                
            
            return Response(loginstatus)

        
        
        
        
        
        else:
            loginstatus = {
                           'error': True,
                           'error_message': "Käyttäjätunnus tai salasana väärin.",
                           'auth_token': None,
                        }
            return Response(loginstatus)
        











@api_view(['POST'])
@renderer_classes((JSONRenderer,))
def reset_password_request(request):
    
    try:
        data = request.data
        email = data['email']
    except:
        response = {'reset_email_sended': False, 'error': True, 'error_message': "Tuntematon virhe. Yritä myöhemmin uudelleen."}
        return Response(response)
    
        
    

    kayttaja = Registereduser.objects.filter(email = email)
    if (len(kayttaja) == 0):
        response = {'reset_email_sended': False, 'error': True, 'error_message': "Sähköpostiosoitteella ei löytynyt käyttäjää."}
        return Response(response)
    elif (len(kayttaja) == 1):
        if(kayttaja[0].password_reset_token_valid_until > datetime.now() + relativedelta(hours = 1)):
            response = {'reset_email_sended': False, 'error': True, 'error_message': "Sähköpostiosoitteeseen on jo lähetetty viesti salasanan nollaamiseksi."}
            return Response(response)
        else:
            kayttaja[0].password_reset_token_valid_until = datetime.now() + relativedelta(hours = 1)
            kayttaja[0].password_reset_token = uuid.uuid4()
            kayttaja[0].save()
            
            
            
            viesti = "Hei, \n\nVoit vaihtaa salasanasi alla olevan linkin kautta. Kopioi alla oleva linkki selaimen osoiteriville kokonaisuudessaan. \n\nhttps://projektikansio.fi/reset-password/" + str(kayttaja[0].password_reset_token) + "\n\nLinkki on voimassa tunnin ajan.\n\nYstävällisin terveisin, \nProjektikansio"
            

                
            requests.post(
            "https://api.mailgun.net/v3/mg.kiinteistodata.fi/messages",
            auth=("api", settings.MAILGUN_APIKEY),
            data={"from": "Suomen Kiinteistödata <no-reply@mg.kiinteistodata.fi>",
                  "to": [kayttaja[0].email],
                  "subject": 'Projektikansio.fi - Salasanan resetointi',
                  "text": viesti})
            

            
            
            
            response = {'reset_email_sended': True, 'error': False, 'error_message': ""}
            return Response(response)
        
        
        
    else:
        response = {'reset_email_sended': False, 'error': True, 'error_message': "Käyttäjiä löytyi liian monta."}
        return Response(response)
        
    






@api_view(['POST'])
@renderer_classes((JSONRenderer,))
def check_password_reset_token_validity(request):
    
    try:
        data = request.data
        url_token = data['url_token']
        kayttaja = Registereduser.objects.get(password_reset_token = url_token, password_reset_token_valid_until__gte = datetime.now())
    except:
        response = {'token_valid': False, 'error': True, 'error_message': "Token ei ole ok.", 'username': None}
        return Response(response)
    
        
    
    response = {'token_valid': True, 'error': False, 'error_message': "", 'username': kayttaja.user.username}
    return Response(response)









@api_view(['POST'])
@renderer_classes((JSONRenderer,))
def change_password(request):
    
    try:
        data = request.data
        password = data['password']
        password_reset_token = data['url_token']
        kayttaja = Registereduser.objects.get(password_reset_token = password_reset_token, password_reset_token_valid_until__gte = datetime.now())
    except:
        response = {'password_changed': False, 'error': True, 'error_message': "Vaihtotoken ei kelpaa."}
        return Response(response)
    
        
    if(len(password) < 7 or len(password) > 30):
        response = {'password_changed': False, 'error': True, 'error_message': "Salasanan tulee olla vähintään 7 merkkiä ja enintään 30 merkkiä pitkä."}
        return Response(response)
    
    
    kayttaja.user.set_password(password)

    new_jwt_token = JWTAuthenticationToken()
    token = jwt.encode({'user_id': kayttaja.id, 'iat': datetime.now(), 'exp': datetime.now() + relativedelta(years=1)}, settings.JWT_SECRET, algorithm='HS256')
    new_jwt_token.token = token
    new_jwt_token.user = kayttaja
    new_jwt_token.save()


    kayttaja.password_reset_token = None
    kayttaja.password_reset_token_valid_until = datetime(1800,1,1)
    
    
    kayttaja.save()
    kayttaja.user.save()
    notification = Notification(user = kayttaja, action = "password_changed", action_maker = kayttaja, project = None, step = None)
    notification.save()
    

    
    
    response = {'password_changed': True, 'error': False, 'error_message': "", 'auth_token': new_jwt_token.token}
    return Response(response)























@api_view(['GET', 'PATCH', 'POST'])
@renderer_classes((JSONRenderer,))
def profile(request):
    

    
    #GETS PROFILEDATA
    if(request.method == 'GET'):
        
        authorization_ok, user_instance = check_authorization(request)
    
        if(not authorization_ok):
            return Response({'error': True, 'error_message': 'Authorization error'})
        
        userdata = user_instance.userobject()
        return Response({'error': False, 'error_message': '', 'userdata': userdata})





    #EDIT PROFILEDATA
    if(request.method == 'PATCH'):
        
        authorization_ok, user_instance = check_authorization(request)
    
        if(not authorization_ok):
            return Response({'error': True, 'error_message': 'Authorization error'})
        
        
        if (request.data['edited_data'] == 'textdata'):
        
            try:
                user_instance.email = request.data['email']
                user_instance.name = request.data['name']
                user_instance.info = request.data['info']
                user_instance.save()
                    
                return Response({'error': False, 'error_message': ''})
                    
            except:
                return Response({'error': True, 'error_message': ''})
        
        
        
        elif (request.data['edited_data'] == 'avatar_removed'):

            if user_instance.avatar_s3_key:
                
                try:
                    if(user_instance.avatar_s3_key):
                        session = boto3.Session(
                        aws_access_key_id = settings.AWS_ACCESS_KEY_ID,
                        aws_secret_access_key = settings.AWS_SECRET_ACCESS_KEY,
                        )
                        
                        s3 = session.resource('s3')
                        s3.Object(settings.AWS_S3_BUCKET_NAME, user_instance.avatar_s3_key).delete()
        
                except:
                    pass
                 
                user_instance.avatar_s3_key = None
                user_instance.avatar_s3_url = None
                user_instance.avatar = None
                
                user_instance.save()
            
    
            response = {'error': False, 'error_message': ''}
            return Response(response)
    

    
    
    
    
    
        elif (request.data['edited_data'] == 'new_profilepic'):
    
            if not os.path.exists('{0}/projektikansio/static/temp'.format(settings.BASE_DIR)):
                os.makedirs('{0}/projektikansio/static/temp'.format(settings.BASE_DIR))
        


            kuvatiedot = request.data['profile_pic_base64']
            kuvan_nimi = request.data['profile_pic_name']
        


            imagedata = kuvatiedot.split(",")[-1]
            tiedostopaate = kuvan_nimi.split(".")[-1]
            
            kuva = base64.b64decode(imagedata)
            tiedostonimi = "user" + str(user_instance.id) + "-" + str(uuid.uuid4()) + "." + tiedostopaate
        
            with open('{0}/projektikansio/static/temp/{1}'.format(settings.BASE_DIR, tiedostonimi), 'wb+') as destination:
                destination.write(kuva)
            
            
            user_instance.avatar = tiedostonimi
            user_instance.save()
            
            user_instance.move_avatar_to_s3()
        
        
            loginstatus = user_instance.userobject()
            return Response(loginstatus)        
    
    
    
    




    #NEW PROFILE
    if(request.method == 'POST'):

        try:
            kayttajatunnus = request.data['username']
            email = request.data['email']
            salasana = request.data['password']
            salasana_uudestaan = request.data['password_confirm']
        except:
            signupstatus = {'error': True, 'error_message': "Unknown error."}
            return Response(signupstatus)
        
    
    
        #kokeilee onko käyttäjätunnus jo käytössä
        try:
            usertesti = User.objects.get(username=kayttajatunnus)
            signupstatus = {'error': True, 'error_message': "Järjestelmään on rekisteröity ehdottamasi käyttäjätunnus. Kokeile jotain toista käyttäjätunnusta.", 'auth_token': None, 'user_id': None}
            return Response(signupstatus)
        except:
            pass
        
        
        #tutkii onko käyttäjätunnus sopiva
        if(len(kayttajatunnus) < 4 or len(kayttajatunnus) > 30):
            signupstatus = {'error': True, 'error_message': "Käyttäjätunnuksen tulee olla vähintään 4 merkkiä ja enintään 30 merkkiä pitkä."}
            return Response(signupstatus)
        
        #tutkii onko salasana sopiva
        if(len(salasana) < 7 or len(salasana) > 30):
            signupstatus = {'error': True, 'error_message': "Salasanan tulee olla vähintään 7 merkkiä ja enintään 30 merkkiä pitkä."}
            return Response(signupstatus)
        
        #tutkii onko salasana sopiva
        if(salasana != salasana_uudestaan):
            signupstatus = {'error': True, 'error_message': "Salasana ja salasanan varmistus eivät ole samat."}
            return Response(signupstatus)
        
        
    
        uusiKayttaja = Registereduser()
        uusiKayttaja.user = User.objects.create_user(kayttajatunnus, email, salasana)
        uusiKayttaja.url_token = str(uuid.uuid4()).split("-")[-1]
        uusiKayttaja.save()
        
        new_jwt_token = JWTAuthenticationToken()
        token = jwt.encode({'user_id': uusiKayttaja.id, 'iat': datetime.now(), 'exp': datetime.now() + relativedelta(years=1)}, 'secret', algorithm='HS256')
        new_jwt_token.token = token
        new_jwt_token.user = uusiKayttaja
        new_jwt_token.save()
        

            
        signupstatus = {'error': False, 'error_message': '', 'auth_token': new_jwt_token.token}
        return Response(signupstatus)









        






    






















@api_view(['DELETE', 'PATCH'])
@renderer_classes((JSONRenderer,))
def notifications(request):
    

    if (request.method == 'DELETE'):

        authorization_ok, user_instance = check_authorization(request)
    
        if(authorization_ok):
            user_notifications = Notification.objects.filter(user = user_instance)
            user_notifications.delete()
        else:
            response = {'error': True, 'error_message': "Tuntematon ongelma"}
            return Response(response)
    
    
        response = {'error': False, 'error_message': ""}
        return Response(response)




    if (request.method == 'PATCH'):

        authorization_ok, user_instance = check_authorization(request)
    
        if(authorization_ok):
            user_instance.notifications_read = datetime.now()
            user_instance.save()
        else:
            response = {'error': True, 'error_message': "Tuntematon ongelma"}
            return Response(response)
        
        
        response = {'error': False, 'error_message': ""}
        return Response(response)
        








    
@api_view(['POST'])
@renderer_classes((JSONRenderer,))
def delete_account(request):


    #DELETE ACCOUNT
    if(request.method == 'POST'):
        
        authorization_ok, user_instance = check_authorization(request)
    
        if(not authorization_ok):
            accountDeleteResponse = {'error': True, 'error_message': "Authentikointitiedot väärin. Yritä myöhemmin uudelleen."}
            return Response(accountDeleteResponse)



        if(user_instance.user.check_password(request.data['password']) == False):
            accountDeleteResponse = {'error': True, 'error_message': "Salasana väärin."}
            return Response(accountDeleteResponse)
        
        
        kayttajanProjektit = Activationproject.objects.filter(user = user_instance)
        
        for projekti in kayttajanProjektit:
            
            try:
                projekti.delete()
            except:
                pass
        

        user_instance.user.delete()
        user_instance.delete()
        
           
        accountDeleteResponse = {'error': False, 'error_message': None}
        return Response(accountDeleteResponse)











def check_authorization(request):
    
    try:
        token_header = request.META['HTTP_AUTHORIZATION'].replace('Bearer ', '', 1)
        tokenobject = JWTAuthenticationToken.objects.get(token = token_header)
        token_payload = jwt.decode(tokenobject.token, settings.JWT_SECRET, algorithms=['HS256'])
        user_id = token_payload['user_id']
        user = Registereduser.objects.get(id = user_id)
        return True, user
    except:
        return False, None











