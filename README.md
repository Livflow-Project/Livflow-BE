사용방법

1단계
git clone git@github.com:glory-coffee-project/back-end-coffee.git
cd Desktop/back-end-coffee

2단계
docker-compose -f docker-compose-dev.yml up --build

3단계
http://localhost:8000


# back-end-coffee
백엔드 coffee project

백엔드 사용 툴

언어 : python

프레임워크 : django , postgresql, redis, docker

내용

개인 NAS를 구축하여 서버를 돌림

docker와 필요에 따라서 poetry를 사용해서 종속성을 유지함

기본적인 가계부, 단가계산 등은 장고 프레임워크를 사용하여 구성

키오스크와 가계부 연동시에는 redis를 사용하여 인메모리로 빠르게 정보를 전달할 계획

소셜로그인은 프론트엔드와 같이 사용하여 사용자 편의성을 증대시킬 예정

또한 개인 정보 보호에 대한 위험성을 줄이기 위해 일반 로그인은 만들지 않을 예정


cicd 확인용 21:15