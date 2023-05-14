from itertools import combinations
from konlpy.tag import Okt
from flask import Request, redirect, render_template, request
from flask_restful import Resource
from mysql_connection import get_connection
from mysql.connector import Error
from collections import defaultdict



# 게시글 작성
class WriteContentResource(Resource):
    def post(self):
        try:
            # MySQL 데이터베이스 연결
            connection = get_connection()

            # HTTP 요청에서 게시글 제목과 내용 추출
            title = request.form['title']
            content = request.form['content']

            # SQL 쿼리를 사용하여 게시글 생성
            cursor = connection.cursor()
            query = "INSERT INTO post (title, content) VALUES (%s, %s)"
            record = (title, content)
            cursor.execute(query, record)
            connection.commit()

            # MySQL 연결 종료
            cursor.close()
            connection.close()

            # HTTP 응답 반환
            return redirect("/board/related")
        

        except Error as e:
            # 에러 발생시 HTTP 500 에러 응답 반환
            print(e)
            cursor.close()
            connection.close()
            return {"error": str(e)}, 500

# 전체 게시글에서 60퍼센트 이상 쓰이는 단어 제외한 데이터 추출하는 함수
def extract_words(content):
    okt = Okt()
    words = okt.nouns(content)
    words = [word for word in words if len(word) > 1]
    return words


# 모든 게시글 단어 추출 후 word 테이블에 저장 후 연관 게시글 저장
class FindRelatedPostsResource(Resource):
    def get(self):
        try:
            connection = get_connection()
            cursor = connection.cursor(dictionary=True)

            # 모든 게시글 가져오기
            query = "select id, content from post"
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
            
            # 단어의 전체 출현 횟수 계산
            total_word_count = sum(count_dict['count'] for count_dict in word_counts.values())

            # 출현 빈도가 60% 이상인 단어 제외
            for word, count_dict in list(word_counts.items()):
                count = count_dict['count']
                if count / total_word_count >= 0.6:
                    del word_counts[word]

            # 모든 게시글 쌍에 대해 공통 단어 개수 계산
            post_similarities = {}
            for post_ids in combinations(word_counts.values(), 2):
                post_id1, post_id2 = post_ids
                common_words = post_id1['post_ids'].intersection(post_id2['post_ids'])
                if len(common_words) > 1:
                    post_similarities[(frozenset(post_id1['post_ids']), frozenset(post_id2['post_ids']))] = len(common_words)

            # related_post 테이블에 연관성 정보 저장
            insert_query = "insert ignore into related_post (post_id, related_post_id, similarity) VALUES (%s, %s, %s)"
            for (post_id1, post_id2), similarity in post_similarities.items():
                post_id1 = list(post_id1)[0]
                post_id2 = list(post_id2)[0]
                if post_id1 != post_id2:
        
                    cursor.execute(insert_query, (post_id1, post_id2, similarity))
                    cursor.execute(insert_query, (post_id2, post_id1, similarity))

            # word_table에 단어와 빈도수 저장
            insert_word_query = "insert into word_table (word, count) VALUES (%s, %s)"
            for word, count_dict in word_counts.items():
                count = count_dict['count']
                cursor.execute(insert_word_query, (word, count))

            connection.commit()
            cursor.close()
            connection.close()

            return redirect("/")
        
        except Error as e:
            print(e)
            cursor.close()
            connection.close()
            return {"result": "fail", "error": str(e)}, 500

    



# # 게시글 목록
# class PostListResource(Resource) : 

#     def get(self) :

#         try : 
#             connection = get_connection()

#             query = '''select * from post;'''

#             cursor = connection.cursor(dictionary=True)

#             cursor.execute(query, )

#             rows = cursor.fetchall()

#             i = 0
#             for row in rows :
#                 rows[i]['created_at'] = row['created_at'].strftime('%Y-%m-%d')
#                 rows[i]['updated_at'] = row['updated_at'].strftime('%Y-%m-%d')
#                 i = i + 1

#             cursor.close()
#             connection.close()

#         except Error as e :
#             print(e)
#             cursor.close()
#             connection.close()

#             return{"result" : "fail", "error": str(e)},500
        
#         return render_template("index.html", rows=rows)
    



            