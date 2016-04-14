# -*- coding: utf-8 -*-

import datetime
import json
import bisect
import requests
from datetime import datetime, timedelta
from django.shortcuts import render
from django.http import HttpResponse

from .models import *


# Create your views here.
def index(request):
    # return HttpResponse('Hello from Python!')
    return render(request, 'index.html')


def db(request):
    greeting = Greeting()
    greeting.save()

    greetings = Greeting.objects.all()

    return render(request, 'db.html', {'greetings': greetings})


def toei(request,):
    # there has to be a better way to do this.
    bus_stop = request.path_info.rsplit('/')[2]
    bus1 = Bus(bus_stop)

    return render(request, 'toei.html', {'bus': bus1})




