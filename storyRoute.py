import sys
import random

from classes import Story, Chapter, User
from flask import Blueprint, render_template
from flask import request
from flask import redirect, url_for
from database import db
from flask_login import login_required, current_user

story_blueprint = Blueprint('storyRoute', __name__)

##ROUTES FOR STORY HANDLING
@story_blueprint.route("/", methods = ["GET", "POST"])
def home():
    if request.form:
        user = User.query.filter_by(id=current_user.id).first()
        chapter = Chapter(name = request.form.get("chapter_name"),
            codes = request.form.get("codes"))
        story = Story(title=request.form.get("title"),
                      description=request.form.get("description"))

        user.stories.append(story)
        user.chapters.append(chapter)

        story.chapters.append(chapter)
        db.session.add(story)
        db.session.add(chapter)
        db.session.commit()
    stories = Story.query.all()
    #return render_template("home.html", stories = stories)
    return render_template("index.html", stories=stories)

@story_blueprint.route("/add", methods = ["GET","POST"])
@login_required
def add():
    return render_template("addStory.html")

@story_blueprint.route("/get/<id>", methods = ["GET", "POST"])
def get(id):
    isUser = False
    story = Story.query.filter_by(id=id).first()
    if current_user.is_authenticated:
        if story.user_id == current_user.id:
            isUser = True
    if request.method == "POST":
        if request.form.get("form_name") == "newChapter":
            user = User.query.filter_by(id=current_user.id).first()
            chapterName = request.form.get("chapter_name")
            chapterCodes = request.form.get("newcodes")
            newChapter = Chapter(name=chapterName, codes=chapterCodes)

            user.chapters.append(newChapter)
            story.chapters.append(newChapter)
            db.session.add(newChapter)
            db.session.commit()

        if request.form.get("form_name") == "updateStory":
            newTitle = request.form.get("newtitle")
            newDesc = request.form.get("newdesc")
            print(newTitle, newDesc)
            story.title = newTitle
            story.description = newDesc
            db.session.commit()
    chapters = story.chapters
    return render_template("getStory.html", story=story, chapters=chapters, isUser=isUser)

@story_blueprint.route("/update/<id>", methods = ["GET", "POST"])
@login_required
def update(id):
    story = Story.query.filter_by(id=id).first()
    return render_template("update.html", story=story)

@story_blueprint.route("/delete/<id>", methods = ["GET"])
@login_required
def delete(id):
    story = Story.query.filter_by(id=id).first()
    db.session.delete(story)
    db.session.commit()
    return redirect("/")

@story_blueprint.route("/run/<id>", methods = ["GET"])
@login_required
def run(id):
    story = Story.query.filter_by(id=id).first()
    chapters = story.chapters
    file = open("tmp.py", "r+")
    file.truncate(0)
    file.write("import math" + "\n")
    file.write("##"+story.title+"\n")
    for chapter in chapters:
        file.write("##"+chapter.name+"\n")
        file.write(chapter.codes+"\n")
    file.close()

    orig_stdout = sys.stdout
    output = open("output.txt", "w+")
    output.truncate(0)
    sys.stdout = output
    exec(open("tmp.py").read())
    sys.stdout = orig_stdout
    output.close()

    display = open("output.txt", "r+")
    content = display.read()

    return render_template("output.html", display=content, story=story, chapters=chapters)

@story_blueprint.route('/search', methods=["POST"])
def search():
    stories = Story.query.all()
    search_result = []
    if request.method == "POST":
        if request.form.get("form_name") == "search_form":
            keyword = request.form.get("search").lower()
            for story in stories:
                description = story.description.lower()
                title = story.title.lower()
                #If keyword found in story description OR title
                if description.find(keyword) != -1 or title.find(keyword) != -1:
                    search_result.append(story)
            if len(search_result) == 0:
                empty = "No results found!"
            else:
                empty = False
    return render_template("search.html", search_result = search_result, empty=empty)

@story_blueprint.route('/surprise')
def surprise():
    list = []
    stories = Story.query.all()
    for story in stories:
        id = story.id
        list.append(id)
    random_story = random.choice(list)
    return redirect(url_for('storyRoute.get', id= random_story))

@story_blueprint.route('/mystories')
def mystories():
    user = current_user
    stories = []
    storiesList = Story.query.all()
    for story in storiesList:
        if story.user.id == user.id:
            stories.append(story)
    return render_template("stories.html", stories=stories)

@story_blueprint.route('/mycontributions')
def mycontributions():
    user = current_user
    stories = []
    storiesList = Story.query.all()
    for story in storiesList:
        chapters = story.chapters
        for chapter in chapters:
            if chapter.user_id == user.id:
                stories.append(story)
                break
    return render_template("contributions.html", stories=stories)
