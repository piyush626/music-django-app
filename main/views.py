from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages
from .forms import RegisterForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
import requests
from isodate import parse_duration
from django.conf import settings
import ml_model
from ml_model import Recommendation
# Create your views here.

res = None

def signup_view(request):
    form = RegisterForm()

    if(request.method=="POST"):
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            user = form.cleaned_data.get('username')
            messages.success(request, 'Account created successfully for '+ user)
            return redirect('main:login')
    context = {'formSignUp':form}
    return render(request,'main/signup.html', context)

def login_view(request):
    if(request.method=="POST"):
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request,user)
            return redirect('main:index')
        else:
            messages.info(request, 'username or password is incorrect')

    context = {}
    return render(request,'main/login.html', context)

def logout_view(request):
    logout(request)
    return redirect('main:index')


def index(request):
    return render(request=request, 
                  template_name='main/index1.html')

def predict(request):

    videos=[]
    if request.method=="POST":
       
        if request.POST['submit'] == "back":
            return redirect('main:getstart')

        query = request.POST['search']

        predicted = Recommendation.generate_link(
            Recommendation.get_recomendation_song_name(query, Recommendation.song_df, return_dataframe=False), return_dictionary=True)
        
        search_url = "https://www.googleapis.com/youtube/v3/search"
        video_url = "https://www.googleapis.com/youtube/v3/videos"

        for search in predicted.keys():
            search_params = {
                'part':'snippet',
                'q': search,
                'key': settings.YOUTUBE_DATA_API_KEY,
                'maxResults': 1,
                'type':'video'
            }

            r = requests.get(search_url,params=search_params)

            results = r.json()['items']

            video_ids =[]
            for result in results:
                video_ids.append(result['id']['videoId'])

            video_params ={
                'key': settings.YOUTUBE_DATA_API_KEY,
                'part':'snippet, contentDetails',
                'id' : ','.join(video_ids),
                'maxResults': 1

            }

            v = requests.get(video_url, params=video_params)

            v_results = v.json()['items']


            for i,result in enumerate(v_results,1):
                video_data = {
                    'title':result['snippet']['title'],
                    'id':result['id'],
                    'url': f'https://www.youtube.com/watch?v={ result["id"] }',
                    'duration':parse_duration(result['contentDetails']['duration']),
                    'thumbnail':result['snippet']['thumbnails']['high']['url'],
                    'count':i
                }

                videos.append(video_data)


    context = {
        'videos':videos
    }

    return render(request, 'main/predict.html', context)


def about(request):
    return render(request=request, 
            template_name="main/about.html")


def under_construction(request):
    messages.info(request, "This page coming soon..")
    return render(request=request, 
            template_name="main/under_construction.html")



def get_start(request):
    videos = []
    if request.method=="POST":
        search_url = "https://www.googleapis.com/youtube/v3/search"
        video_url = "https://www.googleapis.com/youtube/v3/videos"

        search_params = {
            'part':'snippet',
            'q':request.POST['search'],
            'key': settings.YOUTUBE_DATA_API_KEY,
            'maxResults': 9,
            'type':'video'
        }

        r = requests.get(search_url,params=search_params)

        results = r.json()['items']

        video_ids =[]
        for result in results:
            video_ids.append(result['id']['videoId'])

        if request.POST['submit'] == "first":
            return redirect(f'https://www.youtube.com/watch?v={ video_ids[0] }')

        video_params ={
            'key': settings.YOUTUBE_DATA_API_KEY,
            'part':'snippet, contentDetails',
            'id' : ','.join(video_ids),
            'maxResults': 9

        }

        v = requests.get(video_url, params=video_params)

        v_results = v.json()['items']


        for i,result in enumerate(v_results,1):
            video_data = {
                'title':result['snippet']['title'],
                'id':result['id'],
                'url': f'https://www.youtube.com/watch?v={ result["id"] }',
                'duration':parse_duration(result['contentDetails']['duration']),
                'thumbnail':result['snippet']['thumbnails']['high']['url'],
                'count':i
            }

            videos.append(video_data)

    context = {
        'videos':videos
    }


    return render(request, 'main/getstart.html', context)


