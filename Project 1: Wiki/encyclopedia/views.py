from django.shortcuts import render

from . import util
from django.http import HttpResponseRedirect
from django.urls import reverse
from django import forms
from random import randint
from markdown2 import Markdown

markdowner = Markdown()


class NewPageForm(forms.Form):
    title = forms.CharField(max_length=64, label="Title")
    content = forms.CharField(widget=forms.Textarea, label="Contents of the article")


def index(request):
    return render(request, "encyclopedia/index.html", {"entries": util.list_entries()})


def entry(request, title):
    entry = util.get_entry(title)
    # converted_entry = markdowner.convert(entry)
    if entry:
        return render(
            request,
            "encyclopedia/entry.html",
            {"entry": markdowner.convert(entry), "title": title},
        )
    return render(
        request,
        "encyclopedia/error.html",
        {
            "message": "Sorry, we don't have a page with this title. You could try modifying your search",
            "title": "Error",
        },
    )


def search(request):
    search_query = request.GET["q"]
    entries = util.list_entries()
    entries_with_substring = []
    for entry in entries:
        if entry.lower() == search_query.lower():
            return HttpResponseRedirect(reverse("entry", args=(entry,)))
        if search_query.lower() in entry.lower():
            entries_with_substring.append(entry)
    return render(
        request,
        "encyclopedia/searchresult.html",
        {
            "entries_with_substring": entries_with_substring,
        },
    )


def new_page(request):
    # If user submits the form, we create a new entry with their data and redirect user there
    if request.method == "POST":
        form = NewPageForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            content = form.cleaned_data["content"]
            # If an entry w/this title exists, error message, otherwise save the entry
            if title in util.list_entries():
                return render(
                    request,
                    "encyclopedia/new_page.html",
                    {
                        "message": "An entry with this name already exists in our encyclopedia!"
                    },
                )
            util.save_entry(title, content)
            return HttpResponseRedirect(
                reverse(
                    "entry",
                    args=(title,),
                )
            )
    # If the user GETs the page, we give them a clean form
    return render(request, "encyclopedia/new_page.html", {"form": NewPageForm()})


def edit_page(request, title):
    if request.method == "POST":
        util.save_entry(request.POST["title"], request.POST["content"])
        return HttpResponseRedirect(reverse("entry", args=(title,)))
    entry = util.get_entry(title)
    data = {"title": title, "content": entry}
    form = NewPageForm(data)
    return render(
        request, "encyclopedia/edit_page.html", {"form": form, "title": title}
    )


def random(request):
    entries = util.list_entries()
    n = randint(0, len(entries) - 1)
    title = entries[n]
    return HttpResponseRedirect(reverse("entry", args=(title,)))
