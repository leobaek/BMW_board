from flask import Flask
from flask_restful import Api
from mysql_connection import get_connection
from mysql.connector import Error

from resources.board import PostListResource, WriteContentResource
 
app = Flask(__name__)

api = Api(app)

api.add_resource(WriteContentResource,'/write')

api.add_resource(PostListResource,'/list')


 
if __name__ == '__main__':
    app.run()
 