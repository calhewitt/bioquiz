from django.http import HttpResponse
from django import template
import settings
from django.db import connection

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
    context = template.Context({"quizlist": quizzes})
    return HttpResponse(t.render(context))
