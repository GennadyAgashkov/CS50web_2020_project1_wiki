from django.shortcuts import render
from markdown2 import markdown
from django.urls import reverse
from django.http import HttpResponseRedirect, HttpResponseNotFound
from random import randrange
from django import forms
import logging # import the logging library

from . import util

# Get an instance of a logger
logger = logging.getLogger(__name__)

class CreateNew_Form (forms.Form):
    title = forms.CharField(label = "Title")
    md_content = forms.CharField(widget = forms.Textarea)

def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.get_list_entries()
    })

def entry(request, title):
    entry_md_content = util.get_entry(title)

    if not entry_md_content:
        return render(request, "encyclopedia/error.html", {
            "error_string":  f"Error: \"{title}\" entry doesn't exist"
        })

    return render(request, "encyclopedia/entry.html", {
        "title": title,
        "entry_html_content": markdown(entry_md_content)
    })

def search(request):
    if request.method == "GET":
        search_string = request.GET.get("q")
        # logger.error(f"search_string = {search_string}")

        if search_string:
            list_all_entries = util.get_list_entries()
            # logger.error(f"list_all_entries = {list_all_entries}")

            if [s for s in list_all_entries if search_string.lower() == s.lower()]:
                return HttpResponseRedirect(reverse("entry", kwargs={
                    'title': search_string
                    }))

            list_finded_entrys = [s for s in list_all_entries if search_string.lower() in s.lower()]
            # logger.error(f"list_finded_entrys = {list_finded_entrys}")

            if list_finded_entrys:
                return render(request, "encyclopedia/search.html", {
                    "entries": list_finded_entrys    
                })

    return render(request, "encyclopedia/error.html", {
        "error_string":  f"Error: can't find \"{search_string}\""
    })

def create(request):
    if request.method == "POST":
        form = CreateNew_Form(request.POST)
        
        logger.error(f"form.is_valid() = {form.is_valid()}")

        # if not valid form fields - return error
        if not form.is_valid():
            return render(request, "encyclopedia/create.html", {
                    'form': form,
                    'error_string': f"Error: not valid form fields"
                })
            
        title = form.cleaned_data["title"]
        md_content = form.cleaned_data["md_content"]
        
        logger.error(f"form.cleaned_data {form.cleaned_data}")

        # if entry allready exist return error
        # Error will display on the same page to avoid data lost
        if util.get_entry(title):
            return render(request, "encyclopedia/create.html", {
                'form': form,
                'error_string': f"Error: Entry with title \"{title}\" already exist"
            })

        #check for correct MD format
        util.save_entry(title, md_content)
        return HttpResponseRedirect(reverse("entry", kwargs={'title': title}))

    return render(request, "encyclopedia/create.html", {
        'form': CreateNew_Form()
    })

def edit(request, title):
    
    if request.method == "POST":
        form = CreateNew_Form(request.POST)


        if not form.is_valid():
            return render(request, "encyclopedia/edit.html", {
                'title': title,
                'form': form,
                'error_string': f"Error: invalid fields of form"
            })

        # logger.error(f"form.cleaned_data = {form.cleaned_data}")
        title = form.cleaned_data.get('title')
        md_content = form.cleaned_data.get('md_content')

        util.save_entry(title, md_content)
        return HttpResponseRedirect(reverse("entry", kwargs={
            'title': title
            }))
    
    form = CreateNew_Form(initial={
        'title': title,
        'md_content': util.get_entry(title)
        })

    return render(request, "encyclopedia/edit.html", {
        'title': title,
        'form': form
    })

def random(request):
    entries = util.get_list_entries()

    return HttpResponseRedirect(reverse("entry", kwargs={
        'title': entries[randrange(len(entries))]
        }))
   