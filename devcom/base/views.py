from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from .models import Room,Topic,Message
from .forms import RoomForm
from django.db.models import Q

# Create your views here.

# rooms = [
#     {'id': 1, 'name': 'web developer'},
#     {'id': 2, 'name': 'app developer'},
#     {'id': 3, 'name': 'designer'},
# ]


def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    rooms = Room.objects.filter(Q(topic__name__icontains=q) |
                                Q(name__icontains=q) |
                                Q(description__icontains=q))
    topic = Topic.objects.all()
    room_count = rooms.count()
    room_message = Message.objects.filter(Q(room__topic__name__icontains=q))
    context = {'rooms': rooms,'topics':topic,'room_count':room_count,'room_message':room_message}
    return render(request, 'base/home.html', context)


def room(request, pk):
    room = Room.objects.get(id=pk)
    room_message = room.message_set.all()
    participants = room.participants.all()
    if request.method == 'POST':
        messages = Message.objects.create(
            user = request.user,
            room = room,
            body = request.POST.get('msg_body')
        )
        room.participants.add(request.user)
        return redirect('room',pk=room.id)
    context = {'room': room,'room_message':room_message,'participants':participants}
    return render(request, 'base/room.html', context)

@login_required(login_url='login-page')
def createRoom(request):
    form = RoomForm()
    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    context = {'form':form}
    return render(request,'base/room_form.html',context)

@login_required(login_url='login-page')
def updateRoom(request,pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)
    if request.user != room.host:
        return HttpResponse("Access Denied!")

    if request.method == 'POST':
        form = RoomForm(request.POST,instance=room)
        if form.is_valid():
            form.save()
            return redirect('home')
    context = {'form':form}
    return render(request,'base/room_form.html',context)

@login_required(login_url='login-page')
def deleteRoom(request,pk):
    room = Room.objects.get(id=pk)
    if request.user != room.host:
        return HttpResponse("Access Denied!")

    if request.method == 'POST':
        room.delete()
        return redirect('home')
    context = {'obj':room}
    return render(request,'base/room_delete.html',context)

@login_required(login_url='login-page')
def deleteMessage(request,pk):
    msg = Message.objects.get(id=pk)
    if request.user != msg.user:
        return HttpResponse('You Can not Delete this message!')
    if request.method == 'POST':
        msg.delete()
        return redirect('home')
    return render(request, 'base/room_delete.html',{'obj':msg})
def userLogin(request):
    page = 'login'
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, 'User does not exist!')
        user = authenticate(request,username=username,password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'username or password incorrect!')

    context = {'page':page}
    return render(request,'base/register_login.html',context)

def userLogout(request):
    logout(request)
    return redirect('home')

def userRegister(request):
    form = UserCreationForm()
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request,user)
            return redirect('home')
        else:
            messages.error(request,'something went wrong! pleae check it out.')
    context={'form':form}
    return render(request,'base/register_login.html',context)

def userProfile(request,pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    room_message = user.message_set.all()
    topics = Topic.objects.all()
    context = {'user':user,'rooms':rooms,'topics':topics,'room_message': room_message}
    return render(request,'base/profile.html',context)