import sys
import random
import traceback

from classes import Story, Chapter, User
from flask import Blueprint,session, jsonify
from flask import request
from flask import redirect
from database import db
from sqlalchemy import inspect
import json
from database import db, login_manager
from flask_login import login_required, login_user, logout_user,current_user

import re


API_blueprint = Blueprint('APIRoute', __name__)

##ROUTES FOR STORY HANDLING
@API_blueprint.route("/api/stories", methods=["GET"])
def get():
    stories = Story.query.all()
    story_list = []

    for story in stories:
        story_list.append(story.as_dict())

    story_json = {
        'stories': story_list,
    }
    return jsonify(story_json)

@API_blueprint.route("/api/stories/<id>", methods=["GET"])
def get_chapters(id):
    story = Story.query.filter_by(id=id).first()
    chapter_list = []
    chapters = story.chapters

    for chapter in chapters:
        chapter_list.append(chapter.as_dict())

    chapter_json = {
        'chapter_json': chapter_list,
    }

    return jsonify(chapter_json)

@API_blueprint.route("/api/chapters/<id>", methods={"POST"})
def add_chapter(id):
    user_id = request.json.get('user_id')
    user = User.query.filter_by(id=int(user_id)).first()
    story = Story.query.filter_by(id=id).first()
    # story = Story.query.get(21)
    chapter = Chapter(name=request.json.get('title'), codes=request.json.get('codes'))

    user.chapters.append(chapter)
    if story.chapters is None:
        story.chapters.create(chapter)

    else:
        story.chapters.append(chapter)
    db.session.add(chapter)
    db.session.commit()

    return jsonify({'message': 'New chapter successfully created.'}), 200

@API_blueprint.route("/api/stories", methods={"POST","GET"})
def add_story():
    user_id = request.json.get('user_id')
    print(user_id)
    user = User.query.filter_by(id=int(user_id)).first()
    story = Story(title=request.json.get("title"),
                  description=request.json.get("description"))

    user.stories.append(story)

    db.session.add(story)
    db.session.commit()

    return jsonify({'storyId': story.id}), 200



@API_blueprint.route('/api/surprise')
def surprise():
    surprise_list = []
    stories = Story.query.all()

    for story in stories:
        surprise_list.append(story.as_dict())

    surprise_story = random.choice(surprise_list)
    print(surprise_story)

    return jsonify(surprise_story)

@API_blueprint.route("/mobile_run/<id>", methods = ["POST","GET"])
#@login_required
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

    code_json = {
        'code_json': str(content)
    }

    return jsonify(code_json)

@API_blueprint.route("/mobile_run_test", methods = ["POST"])
#@login_required
def runTest():
    codes = request.json.get('codes')
    file = open("tmp.py", "r+")
    file.truncate(0)
    file.write("import math" + "\n")
    file.write(codes+"\n")
    file.close()

    orig_stdout = sys.stdout
    output = open("output.txt", "w+")
    output.truncate(0)
    sys.stdout = output
    err1 = []
    try:
        exec(open("tmp.py").read())
    except:
        try:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            #exc_info = sys.exc_info()

            err = traceback.format_exc().splitlines()
            i = 3
            while i < len(err):
                err1.append(err[i])
                i += 1
            print(str(err))

        finally:
            err2 = '\n'.join(err1)
            error_json = {
                'error_json': str(err2)
            }
            print(error_json)
            return jsonify(error_json)

    sys.stdout = orig_stdout
    output.close()

    display = open("output.txt", "r+")
    content = display.read()

    code_json = {
        'code_json': str(content)
    }

    return jsonify(code_json)






