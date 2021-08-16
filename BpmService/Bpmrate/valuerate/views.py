
from django.shortcuts import render
from valuerate.calrate import *

# Create your views here.


def index(request):
    bpmda = "index page"
    return render(request, 'index.html', {'bpmda' : bpmda})

def rat(request):
    rat = rating()
    return render(request, 'rating.html', {'rat' : rat})

def Mda(request):
    Mda = Mdata()
    return render(request, 'mdata.html', {'Mda' : Mda})

def clu(request):
    clu = cluster()
    return render(request, 'cluster.html', {'clu' : clu})

def cal(request):
    cal = calaver()
    return render(request, 'calaver.html', {'cal' : cal})

def rec(request):
    param = request.GET.get('uid', None)
    print(param)
    rec = reccomand(param)
    return render(request, 'reccomand.html', {'rec' : rec})

