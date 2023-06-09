from flask import Flask, render_template, request
from flask_restful import Api
from mysql_connection import get_connection
from mysql.connector import Error

from resources.board import FindRelatedPostsResource, WriteContentResource

 
app = Flask(__name__)

api = Api(app)

# 게시글 작성
api.add_resource(WriteContentResource,'/board/new')
api.add_resource(FindRelatedPostsResource,'/board/related')

# mysql 연결
connection = get_connection()



# 게시글 목록
@app.route("/")
def index():
    cursor = None
    
    try:
        # DB 연결
        connection = get_connection()
        cursor = connection.cursor()
        
        # 게시글 목록 가져오기
        query = '''select title, created_at,id from post;'''
        cursor.execute(query)
        rows = cursor.fetchall()
        print(rows)
        # html에 연결 후 데이터 전달
        return render_template("index.html", rows=rows)
    
    # 예외 처리
    except Error as e:

        print(e)
        return {"error": str(e)}, 500
    
    finally:

        if cursor:
            cursor.close()
        if connection:
            connection.close()

# 게시글 작성 화면
@app.route('/write')
def write():
    
    
    # html화면 연결
    return render_template('write.html')

# 본문, 연관 게시물 조회
@app.route('/post/<int:post_id>')
def show_post(post_id) :
    try :
        connection = get_connection()
        cursor = connection.cursor()

        # 본문 조회
        post_query = '''select title, content, created_at from post where id = %s '''
        record = (post_id,)

        cursor.execute(post_query,record)
        post = cursor.fetchall()
        # print(post[0])

        # 연관 게시글 조회 (연관률이 높은 순서대로)
        related_post_query = '''select post.id,post.title, post.created_at
                                FROM related_post
                                inner join post
                                on related_post.related_post_id = post.id
                                where related_post.post_id = %s
                                order by similarity desc;'''

        record = (post_id,)        

        cursor.execute(related_post_query,record)

        related_post = cursor.fetchall()

        return render_template("post.html",post = post, related_post = related_post)
    
    except Error as e:
        print(e)
        return{"error" : str(e)},500
    
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


  
if __name__ == "__main__":
  app.run()



 