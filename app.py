import os

from flask import Flask
from flask_socketio import SocketIO
from database import db, login_manager
from authTest import authTest_blueprint
from storyRoute import story_blueprint
from chapterRoute import chapter_blueprint
from APIRoute import API_blueprint
from APIUserRoute import APIUser_blueprint


project_dir = os.path.dirname(os.path.abspath(__file__))
database_file = 'mysql+pymysql://root:@localhost/fypdatabase'

app = Flask(__name__, template_folder='./static/templates')
app.config['SECRET_KEY'] = 'secret!'
app.config["SQLALCHEMY_DATABASE_URI"] = database_file
socketio = SocketIO(app)



db.init_app(app)
login_manager.init_app(app)
login_manager.login_view = "authTest.loginHandler"


app.register_blueprint(authTest_blueprint)
app.register_blueprint(story_blueprint)
app.register_blueprint(chapter_blueprint)
app.register_blueprint(API_blueprint)
app.register_blueprint(APIUser_blueprint)

if __name__ == "__main__":
    app.run(debug=True)