
from flask import request
from flask_restful import Resource
from mysql_connection import get_connection
from mysql.connector import Error


# 게시글 작성
class WriteContentResource(Resource) : 

    def post(self) :

        # 게시글 id
        # 제목
        # 본문
        # 날짜

        data = request.get_json()

        try :
            connection = get_connection()

            query = '''insert into post (title,content) 
                    values (%s,%s);'''
            
            record = (data["title"],data["content"])

            cursor = connection.cursor()

            cursor.execute(query, record)

            connection.commit()

            cursor.close()
            connection.close()

        except Error as e :
            print(e)
            cursor.close()
            connection.close()
            return{"error" : str(e)}, 500
        
        return {"result" : "success"}



# 게시글 목록
class PostListResource(Resource) : 

    def get(self) :

        try : 
            connection = get_connection()

            query = '''select * from post;'''

            cursor = connection.cursor(dictionary=True)

            cursor.execute(query, )

            result_list = cursor.fetchall()

            i = 0
            for row in result_list :
                result_list[i]['createdAt'] = row['createdAt'].strftime('%Y-%m-%d')

                i = i + 1

            cursor.close()
            connection.close()

        except Error as e :
            print(e)
            cursor.close()
            connection.close()

            return{"result" : "fail", "error": str(e)},500
        
        return{"result" : "success", "user":result_list},200

            