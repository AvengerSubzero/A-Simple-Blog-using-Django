from urllib import quote_plus
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render,get_object_or_404,redirect
from .models import Post
from .forms import PostForm
from django.contrib import messages
from django.utils import timezone
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# Create your views here.

def post_create(request):
    if not request.user.is_staff or not request.user.is_superuser:
        raise Http404

    if not request.user.is_authenticated():
        raise Http404

    form = PostForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        instance = form.save(commit= False)
        instance.user = request.user
        instance.save()
        messages.success(request, "Successfully created")
        return HttpResponseRedirect(instance.get_absolute_url())
    context = {
        "form":form
    }
    return render(request,"post_form.html",context)

def post_detail(request,slug=None): #retrieve
    instance = get_object_or_404(Post, slug=slug)
    share_string = quote_plus(instance.content)
    context = {
        "instance":instance,
        "title" : instance.title,
        "share_string":share_string,
    }
    return render(request,"post_detail.html",context)

def post_list(request): #list items
    queryset_list = Post.objects.filter(draft=False).filter(publish__lte=timezone.now())
    #all().order_by("-timestamp")
    paginator = Paginator(queryset_list, 2) # Show 25 posts per page

    page_request_var = 'page'
    page = request.GET.get(page_request_var)
    try:
        queryset = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        queryset = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        queryset = paginator.page(paginator.num_pages)
    context = {
        "object_list":queryset,
        "title" : "List",
        "page_request_var":page_request_var

    }
    return render(request,"post_list.html",context)

def post_update(request,slug=None):
    if not request.user.is_staff or not request.user.is_superuser:
        raise Http404
    instance = get_object_or_404(Post, slug=slug)
    form = PostForm(request.POST or None, request.FILES or None, instance=instance) #Instance is added 
    if form.is_valid():
        instance = form.save(commit= False)
        instance.save()
        messages.success(request, "Successfully saved")
        return HttpResponseRedirect(instance.get_absolute_url())
    else:
        messages.error(request, "Not successfully saved")
    context = {
        "instance":instance,
        "title" : instance.title,
        "form":form
    }
    return render(request,"post_form.html",context)

def post_delete(request,id=None):
    if not request.user.is_staff or not request.user.is_superuser:
        raise Http404
    instance = get_object_or_404(Post, id=id)
    instance.delete()
    messages.success(request, "Successfully deleted")
    return redirect("posts:list")
