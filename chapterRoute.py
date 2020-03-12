from classes import Story, Chapter, User
from flask import Blueprint, render_template
from flask import request
from flask import redirect, url_for
from database import db
from flask_login import login_required, current_user

chapter_blueprint = Blueprint('chapterRoute', __name__)

##ROUTES FOR Chapters HANDLING
@chapter_blueprint.route("/add", methods = ["GET","POST"])
@login_required
def add():
    return render_template("addStory.html")

@chapter_blueprint.route("/deleteChapter/<id>", methods = ["GET"])
@login_required
def deleteChapter(id):
    chapter = Chapter.query.filter_by(id=id).first()
    story = chapter.story
    db.session.delete(chapter)
    db.session.commit()
    return redirect(url_for('storyRoute.get', id=story.id))

@chapter_blueprint.route('/newChapter/<id>', methods=["GET", "POST"])
@login_required
def newChapter(id):
    story = Story.query.filter_by(id=id).first()
    chapters = story.chapters
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
    return render_template("newChapter.html", story=story, chapters=chapters)
