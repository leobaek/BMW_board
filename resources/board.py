from itertools import combinations
from konlpy.tag import Okt
from flask import request
from flask_restful import Resource
from mysql_connection import get_connection
from mysql.connector import Error
from collections import defaultdict


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
                result_list[i]['updatedAt'] = row['updatedAt'].strftime('%Y-%m-%d')
                i = i + 1

            cursor.close()
            connection.close()

        except Error as e :
            print(e)
            cursor.close()
            connection.close()

            return{"result" : "fail", "error": str(e)},500
        
        return{"result" : "success", "user":result_list},200

    
# 전체 게시글에서 60퍼센트 이상 쓰이는 단어 제외한 데이터 추출하는 함수
def extract_words(content):
    okt = Okt()
    words = okt.nouns(content)
    words = [word for word in words if len(word) > 1]
    return words


# 모든 게시글 단어 추출 후 word 테이블에 저장 후 연관 게시글 저장
class FindRelatedPostsResource(Resource):
    def post(self):
        try:
            connection = get_connection()
            cursor = connection.cursor(dictionary=True)

            # 모든 게시글 가져오기
            query = "SELECT id, content FROM post"
            cursor.execute(query)

            # 단어별 출현 횟수를 저장할 defaultdict 생성
            word_counts = defaultdict(lambda: {'count': 0, 'post_ids': set()})

            # 모든 게시글에서 단어 추출하고 빈도 계산
            for row in cursor:
                post_id = row['id']
                content = row['content']
                content_words = extract_words(content)
                
                # 단어별로 빈도 증가 시키기
                for word in content_words:
                    word_counts[word]['count'] += 1
                    word_counts[word]['post_ids'].add(post_id)

            # 모든 게시글 쌍에 대해 공통 단어 개수 계산
            post_similarities = {}
            for post_ids in combinations(word_counts.values(), 2):
                post_id1, post_id2 = post_ids
                common_words = post_id1['post_ids'].intersection(post_id2['post_ids'])
                if len(common_words) > 1:
                    post_similarities[(frozenset(post_id1['post_ids']), frozenset(post_id2['post_ids']))] = len(common_words)

            # related_post 테이블에 연관성 정보 저장
            insert_query = "INSERT IGNORE INTO related_post (post_id, related_post_id, similarity) VALUES (%s, %s, %s)"
            for (post_id1, post_id2), similarity in post_similarities.items():
                post_id1 = list(post_id1)[0]
                post_id2 = list(post_id2)[0]
                if post_id1 != post_id2:
        
                    cursor.execute(insert_query, (post_id1, post_id2, similarity))
                    cursor.execute(insert_query, (post_id2, post_id1, similarity))
                    



            # word_table에 단어와 빈도수 저장
            insert_word_query = "INSERT INTO word_table (word, count) VALUES (%s, %s)"
            for word, count_dict in word_counts.items():
                count = count_dict['count']
                cursor.execute(insert_word_query, (word, count))

            connection.commit()
            cursor.close()
            connection.close()
        except Error as e:
            print(e)
            cursor.close()
            connection.close()
            return {"result": "fail", "error": str(e)}, 500

        return {"result": "success"}, 200


    



            