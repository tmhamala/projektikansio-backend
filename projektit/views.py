# -*- coding: utf-8 -*-

from django.http import HttpResponse
from .models import  Project
from django.shortcuts import render

from rest_framework.decorators import api_view, renderer_classes
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer


import telegram
from django.conf import settings

from django import get_version




def index(request):
    
    context = {'version': 'Django ' + get_version()}
    return render(request, context=context, template_name='index.html')



def sitemap(request):
    
    projektit = Project.objects.all()
    
    content = ""
    
    for projekti in projektit:
        content = content + 'https://projektikansio.fi/p/' + projekti.url_token + '\n'
    
    return HttpResponse(content, content_type='text/plain')






        




    




@api_view(['POST'])
@renderer_classes((JSONRenderer,))
def send_message(request):
    
    data = request.data
    viesti = "PROJEKTIKANSIO \n\n" + data['sender'] + ": \n" + data['body']
    
    bot = telegram.Bot(token=settings.TELEGRAM_BOT_TOKEN)
    bot.send_message(chat_id=settings.TELEGRAM_CHAT_ID, text=viesti)
    
    return Response(200)




