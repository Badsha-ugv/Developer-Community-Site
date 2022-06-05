from django.shortcuts import render, redirect
from django.http import HttpResponse

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from django.contrib import messages
from django.urls import reverse
from .models import Room, Topic, Message,User 
from .forms import RoomForm, UserForm, MyUserCreationForm
from django.db.models import Q
from django.core.paginator import Paginator

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

    # paginator

    p = Paginator(rooms,3)
    page_number = request.GET.get('page')
    page_obj = p.get_page(page_number)

    context = {'rooms': rooms, 'topics': topic,
               'room_count': room_count, 'room_message': room_message,'page_obj':page_obj}

    return render(request, 'base/home.html', context)


def room(request, pk):
    room = Room.objects.get(id=pk)
    room_message = room.message_set.all()
    participants = room.participants.all()
    if request.method == 'POST':
        messages = Message.objects.create(
            user=request.user,
            room=room,
            body=request.POST.get('msg_body')
        )
        room.participants.add(request.user)
        return redirect('room', pk=room.id)
    context = {'room': room, 'room_message': room_message,
               'participants': participants}
    return render(request, 'base/room.html', context)


@login_required(login_url='login-page')
def createRoom(request):
    form = RoomForm()
    topics = Topic.objects.all()
    if request.method == 'POST':
        form = RoomForm(request.POST)
        topic_name = request.POST.get('topic')
        topic,created = Topic.objects.get_or_create(name=topic_name)
        Room.objects.create(
            host = request.user,
            topic = topic,
            name = request.POST.get('name'),
            description = request.POST.get('description'),
        )
        #
        return redirect('home')
        # if form.is_valid():
        #     room = form.save(commit=False)
        #     room.host = request.user
        #     room.save()
    context = {'form': form,'topics':topics}
    return render(request, 'base/room_form.html', context)


@login_required(login_url='login-page')
def updateRoom(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)
    topics = Topic.objects.all()
    if request.user != room.host:
        return HttpResponse("Access Denied!")

    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic,created = Topic.objects.get_or_create(name=topic_name)
        room.name = request.POST.get('name')
        room.topic = topic
        room.description = request.POST.get('description')
        room.save()

        # form = RoomForm(request.POST, instance=room)
        # if form.is_valid():
        #     form.save()
        return redirect('home')
    context = {'form': form,'topics':topics,'room':room}
    return render(request, 'base/room_form.html', context)


@login_required(login_url='login-page')
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)
    if request.user != room.host:
        return HttpResponse("Access Denied!")

    if request.method == 'POST':
        room.delete()
        return redirect('home')
    context = {'obj': room}
    return render(request, 'base/room_delete.html', context)


@login_required(login_url='login-page')
def deleteMessage(request, pk):
    msg = Message.objects.get(id=pk)
    if request.user != msg.user:
        return HttpResponse('You Can not Delete this message!')
    if request.method == 'POST':
        msg.delete()
        return redirect(reverse('home'))
    return render(request, 'base/room_delete.html', {'obj': msg})


def userLogin(request):
    page = 'login'
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, 'User does not exist!')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'username or password incorrect!')

    context = {'page': page}
    return render(request, 'base/register_login.html', context)


def userLogout(request):
    logout(request)
    return redirect('home')


def userRegister(request):
    form = MyUserCreationForm()
    if request.method == 'POST':
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(
                request, 'something went wrong! pleae check it out.')
    context = {'form': form}
    return render(request, 'base/register_login.html', context)


def userProfile(request, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    room_message = user.message_set.all()
    topics = Topic.objects.all()
    context = {'user': user, 'page_obj': rooms,
               'topics': topics, 'room_message': room_message}
    return render(request, 'base/profile.html', context)
@login_required(login_url='login')
def updateUser(request):
    user = request.user
    form = UserForm(instance=user)
    if request.method == 'POST':
        form = UserForm(request.POST,request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user-profile',pk=user.id)

    return render(request, 'base/update-user.html',{'form':form})
