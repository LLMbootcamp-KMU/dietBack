# WHIP : 팀 채찍피티
## 👋프로젝트 소개
국민대학교 & magicecole 의 LLM 부트캠프에서 진행한 프로젝트,
LLM을 사용한 식단관리 서비스입니다.
기간 : 2024년 07월 22일 월 ~ 2024년 07월 26일 금 ( 5일)

기존의 식단 관리 어플들은 음식을 기입하려면, 수 많은 음식속에서 내가 먹은 음식의 브랜드를 찾아야하고, 먹은 음식의 양도 직접입력해야하는 불편함이 존재했습니다.
또한 한 눈에 보이는 정보가 너무 많아서 혼란스럽다는 문제가 있습니다.
따라서, 자연어를 처리해주는 LLM을 사용해서, 사용성이 좋고, 직관적인 식단관리 서비스를 만들었습니다.

이곳은 백엔드 페이지 입니다. 
[프론트엔드 페이지로 이동](https://github.com/LLMbootcamp-KMU/diet)
## 👯팀소개
<table>
  <tr>
    <th>이름</th>
    <th>역할</th>
    <th>깃허브 주소</th>
  </tr>
  <tr>
    <td>박정빈(팀장)</td>
    <td>프론트엔드,배포,LLM</td>
    <td><a href="https://github.com/obb8923">@obb8923</a></td>
  </tr>
  <tr>
    <td>김상엽</td>
    <td>백엔드,데이터베이스</td>
    <td><a href="https://github.com/Nak-Yeop">@Nak-Yeop</a></td>
  </tr>
  <tr>
    <td>이종윤</td>
    <td>백엔드,데이터베이스</td>
    <td><a href="https://github.com/jongyo0N">@jongyo0N</a></td>
  </tr>
  <tr>
    <td>김준서</td>
    <td>백엔드,LLM</td>
    <td><a href="https://github.com/wnstjakstp">@wnstjakstp</a></td>
  </tr>
  <tr>
    <td>이총명</td>
    <td>프론트엔드</td>
    <td><a href="https://github.com/intelligent04">@intelligent04</a></td>
  </tr>
</table>

## 📋사용법 
+ `Home`에서 식단을 '줄글'로 입력하여 저장합니다.
+ `Home`에서 식단을 '사진'으로 입력하여 저장합니다.
+ `Calendar`에서 입력된 식단을 달력형태로, 월 별로 조회할 수 있습니다.
+ `Calendar`에서 날짜를 클릭하여 하루 식단 정보를 조화할 수 있습니다.
+ `Calendar`에서 `한 달 요약` 버튼을 눌러 한 달 요약(영양 정보)을 조회하고, 조언을 받을 수 있습니다.
+ `Profile` 에서 회원 정보 수정을 할 수 있습니다. 

## 📢주요 기능 , 시스템 구조 소개
### 기능 사진
#### Home 화면
![Home 화면](https://github.com/user-attachments/assets/999c3628-60b6-4e4a-b34d-f29c7aeaa27c)
#### 식단 입력- 텍스트 '샌드위치 한개' 입력
![식단 입력- 텍스트 '샌드위치 한개' 입력](https://github.com/user-attachments/assets/86d5cf2f-0151-4773-be8d-1278dfb08e8d)
#### Calendar 화면
![Calendar 화면](https://github.com/user-attachments/assets/40802cc5-8ab5-4cf5-9bee-075b454264ed)
#### Calendar 화면2
![Calendar 화면2](https://github.com/user-attachments/assets/3532f071-3376-4856-9c60-9a597b2ea5a6)
#### 한달 요약 보기 화면
![한달 요약 보기 화면](https://github.com/user-attachments/assets/983264b3-8d0a-435b-96e7-665d25fa4b1a)
#### Profile 화면
![Profile 화면](https://github.com/user-attachments/assets/77f84592-5acd-478a-945f-f4d6be0b8b34)
#### 일일 정보 화면
![일일 정보 화면](https://github.com/user-attachments/assets/570dadfe-5f37-40fd-b4c6-4d23b1743514)
#### 일일 정보 화면 - 기록된 식단 없을때
![일일 정보 화면 - 기록된 식단 없을때](https://github.com/user-attachments/assets/ab467104-e6ae-416d-b5ba-92b1273e99aa)


### 시스템 구조도 System Architecture Diagram
<img src="https://github.com/user-attachments/assets/199a78d7-f47b-43b0-a1bb-4e86b9d731c5" alt="시스템 구조도" width="480">

### ERD E-R Diagram
<img src="https://github.com/user-attachments/assets/41e0eca3-f3dc-4a65-b6fe-8feb65c37938" alt="ERD" width="480">

## 시퀀스 다이어그램 Sequence Diagram 
<table>
  <tr>
    <th>식단 입력</th>
    <th>조언</th>
  </tr>
  <tr>
     <td><img src="https://github.com/user-attachments/assets/e300f0d9-febc-40af-8e04-cb3441829cd6" alt="사진"/>
</td>
    <td>
      <img src="https://github.com/user-attachments/assets/1d1d88b4-15c7-40be-8f90-e278a66744ae" alt="사진"/>
</td>
  </tr>
</table>

## 고군분투의 흔적
<table>
  <tr>
    <th>화면 구성 고민</th>
    <th>데이터 흐름 고민</th>
    <th>DB구성 고민</th>
  </tr>
  <tr>
     <td><img src="https://github.com/user-attachments/assets/7a368325-10dd-4a3f-a89b-f27a9f547f76" alt="사진"/>
</td>
    <td>
      <img src="https://github.com/user-attachments/assets/bee368c8-5c3d-486f-841e-90f8e1eb313d" alt="사진"/>
</td>
    <td><img src="https://github.com/user-attachments/assets/cc446f23-dd31-493a-8c17-d5f87d3d39c7" alt="사진"/>
</td>
  </tr>
</table>

## 🪡사용한 기술

* ### 언어
    <img src="https://img.shields.io/badge/javascript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black">
  <img src="https://img.shields.io/badge/python-3776AB?style=for-the-badge&logo=python&logoColor=white">

* ### 기술
  <img src="https://img.shields.io/badge/react-61DAFB?style=for-the-badge&logo=react&logoColor=black">
   <img src="https://img.shields.io/badge/flask-000000?style=for-the-badge&logo=flask&logoColor=white">
  <img src="https://img.shields.io/badge/mySQL-4479A1?style=for-the-badge&logo=mySQL&logoColor=white">
* ### 배포
   <img src="https://img.shields.io/badge/vercel-000000?style=for-the-badge&logo=vercel&logoColor=white">
    <img src="https://img.shields.io/badge/Amazon EC2-ff9900?style=for-the-badge&logo=Amazon EC2&logoColor=white">
       <img src="https://img.shields.io/badge/Amazon RDS-527FFF?style=for-the-badge&logo=Amazon RDS&logoColor=white">
* ### 소통
  <img src="https://img.shields.io/badge/github-181717?style=for-the-badge&logo=github&logoColor=white">
  <img src="https://img.shields.io/badge/git-F05032?style=for-the-badge&logo=git&logoColor=white">
   <img src="https://img.shields.io/badge/KakaoTalk-FFCD00?style=for-the-badge&logo=KakaoTalk&logoColor=black">
