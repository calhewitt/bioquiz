from django.http import HttpResponseRedirect, HttpResponse
from django import template
import settings
from django.db import connection
from django.core.urlresolvers import reverse
import md5

def showquiz(request):
    rowid = request.GET["id"]
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM quizzes WHERE rowid = ?", (rowid,))
    res  = cursor.fetchone()
    if not res:
        return HttpResponse("404 - not found!")
    title, quiztext = res
    t = template.Template(open(settings.BASE_DIR + "/bioquiz/templates/quiz.html").read())
    context = template.Context({"quiztext": quiztext, "title": title})
    return HttpResponse(t.render(context))

def home(request):
    cursor = connection.cursor()
    cursor.execute("SELECT rowid, title FROM quizzes")
    quizzes = cursor.fetchall()
    t = template.Template(open(settings.BASE_DIR + "/bioquiz/templates/home.html").read())
    context = template.Context({"quizlist": quizzes, "home": request.path})
    return HttpResponse(t.render(context))

def authenticate(request):
    if "password" in request.POST:
        cursor = connection.cursor()
        cursor.execute("SELECT value from misc WHERE key = 'adminpassword'")
        truepass = cursor.fetchone()[0]
        if md5.new(request.POST['password']).hexdigest().lower() == truepass:
            request.session["auth"] = "TRUE"
            return admin(request)
    t = template.Template(open(settings.BASE_DIR + "/bioquiz/templates/auth.html").read())
    context = template.Context()

    return HttpResponse(t.render(context))

def admin(request):
    if "auth" in request.session:
        cursor = connection.cursor()
        cursor.execute("SELECT rowid, title FROM quizzes")
        quizzes = cursor.fetchall()
        t = template.Template(open(settings.BASE_DIR + "/bioquiz/templates/admin.html").read())
        context = template.Context({"quizlist": quizzes})
        return HttpResponse(t.render(context))
    else:
        return authenticate(request)

def edit_quiz(request):
    if "auth" in request.session:
        if "quiztext" in request.POST:
            cursor = connection.cursor()
            rowid, quiztext = request.POST['id'], request.POST['quiztext']
            cursor.execute("UPDATE quizzes SET quiztext = ? WHERE rowid = ?", (quiztext, rowid))
            return HttpResponseRedirect("./")
        else:
            rowid = request.GET["id"]
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM quizzes WHERE rowid = ?", (rowid,))
            res  = cursor.fetchone()
            if not res:
                return HttpResponse("404 - not found!")
            title, quiztext = res
            t = template.Template(open(settings.BASE_DIR + "/bioquiz/templates/edit.html").read())
            context = template.Context({"quiztext": quiztext, "title": title, "id": rowid})
            return HttpResponse(t.render(context))
    else:
        return authenticate(request)

def logout(request):
    del request.session['auth']
    return HttpResponseRedirect("../")

def new(request):
    if "auth" in request.session:
        if "title" in request.POST:
            cursor = connection.cursor()
            quiztext, title = request.POST['quiztext'], request.POST['title']
            cursor.execute("INSERT INTO quizzes VALUES(?, ?)", (title, quiztext))
            return HttpResponseRedirect("./")
        else:
            t = template.Template(open(settings.BASE_DIR + "/bioquiz/templates/new.html").read())
            context = template.Context()
            return HttpResponse(t.render(context))
    else:
        return authenticate(request)

def delete_quiz(request):
    if "auth" in request.session:
        cursor = connection.cursor()
        rowid = request.GET['id']
        cursor.execute("DELETE from quizzes WHERE rowid = ?", (rowid,))
        return HttpResponseRedirect("./")
    else:
        return authenticate(request)
