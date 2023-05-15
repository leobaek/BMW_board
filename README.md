# board
## 목적 및 준비물
목적 : 게시판 만들기\
언어 : Python\
프레임워크 : Flask\
DB : MySQL

## Table
post : id, title, content, created_at\
related_post = id, post_id, related_post_id, similarity\
word : word_id, word, count

## Start Project
konlpy : text의 단어나 어절등 나눠주는 모듈

### 게시글 구현
목록 : 게시글 쿼리셋을 가져와 목록 구현\
생성 : 게시글 폼을 만들어 유효하면 생성\
작성 : 게시글 작성 폼을 만들어 제출 후 단어 추출, 연관 게시물 연결 시행

### 연관 게시글
konlpy 모듈을 이용하여 모든 게시글에서 단어를 추출하고 빈도를 계산한 후 출현 횟수의 60%이상인 단어는 삭제\
게시글의 모든 단어를 쌍으로 묶어 공통 단어 개수를 계산하고 , 연관 게시물로 저장\
공통 단어가 많을수록 연관게시글 상위에 위치

