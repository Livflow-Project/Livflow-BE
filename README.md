## Livflow

<p>가계부 정리부터 메뉴 원가 계산까지,<br />효율적인 비즈니스 관리를 위한 올인원 웹 서비스</h3>

![스크린샷 2025-04-10 오후 9 17 24](https://github.com/user-attachments/assets/5b8063d5-fee0-4088-886d-7381aafc5db4)


<br />

## 목차 (클릭하면 해당 섹션으로 이동)
- [기술 스택](#기술-스택)
- [시스템 아키텍쳐](#시스템-아키텍쳐)
- [ERD](#erd)
- [API 명세서](#api-명세서)
- [프로젝트 구조](#프로젝트-구조)
- [바로 사용해보기](#바로-사용해보기)
- [서비스 소개](#서비스-소개)
- [주요 기능](#주요-기능)
- [팀원 소개](#팀원-소개)
- [라이선스](#라이선스)


<br />

## 기술 스택

<div>
<img src="https://img.shields.io/badge/python-3776AB?style=for-the-badge&logo=python&logoColor=white"/>
<img src="https://img.shields.io/badge/django_rest_framework-092E20?style=for-the-badge&logo=django&logoColor=white"/>
<img src="https://img.shields.io/badge/fastapi-009688?style=for-the-badge&logo=fastapi&logoColor=white"/>
<img src="https://img.shields.io/badge/pandas-150458?style=for-the-badge&logo=pandas&logoColor=white"/>
<img src="https://img.shields.io/badge/tensorflow-FF6F00?style=for-the-badge&logo=tensorflow&logoColor=white"/>
<img src="https://img.shields.io/badge/poetry-60A5FA?style=for-the-badge&logo=python&logoColor=white"/>
<img src="https://img.shields.io/badge/linux-FCC624?style=for-the-badge&logo=linux&logoColor=black"/>
<img src="https://img.shields.io/badge/redis-DC382D?style=for-the-badge&logo=redis&logoColor=white"/>
<img src="https://img.shields.io/badge/postgresql-4169E1?style=for-the-badge&logo=postgresql&logoColor=white"/>
<img src="https://img.shields.io/badge/docker-2496ED?style=for-the-badge&logo=docker&logoColor=white"/>
<img src="https://img.shields.io/badge/github_actions-2088FF?style=for-the-badge&logo=githubactions&logoColor=white"/>
<img src="https://img.shields.io/badge/nginx-009639?style=for-the-badge&logo=nginx&logoColor=white"/>


</div>


## 시스템 아키텍쳐
![스크린샷 2025-04-10 오후 5 04 38](https://github.com/user-attachments/assets/71b34e79-d2f7-4aac-8ae1-202702ba5535)

<br />

## ERD

![스크린샷 2025-04-10 오후 5 16 26](https://github.com/user-attachments/assets/56384d2d-0005-4264-96ed-85120a75c327)


<br />

<br />

## API 명세서

스웨거로 대체합니다.
swagger(https://api.livflow.co.kr:8443/swagger/)


<br />

## 프로젝트 구조

```
django
├── livflow/         # django, base url setting
├── store/           # 가계 기본정보
├── users/           # 사용자 로그인 정보, social login logic
├── costcalcul/      # 단가계산 logic, view
├── ingrdients/      # 재료 저장 logic, view
├── inventory/       # 재고 저장 logic, view
├── ledger/          # 가계부 저장 api, view          
├── salesforecast/   # 매출분석, 상권분석 AI, Fastapi router

Fastapi
├── routes/             # 엔드포인트 경로 설정
│   └── predict.py      # AI 예측 API 
├── utils/              # 유틸리티 함수 및 모델 로딩 모듈
│   └── tf_model.py     # TensorFlow 모델 불러오기 및 전처리 로직
├── main.py             # FastAPI 앱 실행 진입점
├── models.py           # Pydantic 기반 요청/응답 스키마 정의
```

<br />


## 바로 사용해보기

<p>
  1. 
  <a href="https://www.livflow.co.kr" target="_blank" style="display: inline-block; vertical-align: middle;">
    <img src="https://img.shields.io/badge/Livflow%20바로가기-0078D4?style=for-the-badge&logoColor=white"/>
  </a>
</p>

<p>2. 소셜 회원가입 후 로그인</p>
<p>3. 가게 등록 후 가계부 및 재고 관리, 원가 계산 기능 활용</p>

<br />




<br />

## 팀원 소개

<table>
  <tr>
    <td align="center">
    <P><strong>Frontend</strong></P>
      <a href="https://github.com/Yi-HyeonJu" style="text-decoration: none;">
        <img src="https://avatars.githubusercontent.com/u/164320612?v=4" width="250px;" alt="이현주"/><br />
        <span style="font-size: 1.2rem;">이현주</span>
      </a>
    </td>
     <td align="center">
     <P><strong>Backend</strong></P>
      <a href="https://github.com/youngkwangjoo" style="text-decoration: none;">
        <img src="https://avatars.githubusercontent.com/u/164307740?v=4" width="250px;" alt="주영광"/><br />
        <span style="font-size: 1.2rem;">주영광</span>
      </a>
    </td>
  </tr>
</table>


## 라이선스

<p>이 프로젝트는 MIT 라이선스에 따라 배포됩니다. 자세한 내용은 <a href="LICENSE">LICENSE 파일</a>을 참조하세요.</p>

<br />


