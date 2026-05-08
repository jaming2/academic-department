
# Python Study System

## 지원 기능

- 로그인 / 회원가입
- 문제 풀이 시스템
- Python 코드 제출
- 실제 서버 채점
- 성공 여부 DB 저장
- 여러 스터디 확장 가능
- 여러 테스트케이스 자동 채점
- 입력 없는 문제 지원
- 다크모드 UI

---

# 문제 폴더 구조

예시:

study_judges/
└── 2학기_1차_파이썬_스터디/
    ├── 1번문제/
    ├── 2번문제/
    └── 3번문제/

---

# 테스트케이스 구조

각 문제 폴더 안:

3번문제/
├── testcase1_input.txt
├── testcase1_output.txt
├── testcase2_input.txt
├── testcase2_output.txt

숫자 기준으로 자동 매칭됩니다.

---

# 입력 없는 문제

입력이 없는 문제는:

testcase1_input.txt

를 빈 파일로 두면 됩니다.

예시:

testcase1_output.txt

Hello World

---

# 채점 방식

- 모든 테스트케이스 실행
- 하나라도 틀리면 실패
- 전부 맞으면 성공
- strip() 처리 포함

---

# 새로운 문제 추가 방법

예시:

4번문제/
├── testcase1_input.txt
├── testcase1_output.txt

만들면 자동 적용됩니다.

---

# 새로운 스터디 추가 방법

study_judges/
└── 2학기_2차_파이썬_스터디/

추가 후:

server.py 의

CURRENT_STUDY = '2학기_1차_파이썬_스터디'

변경하면 됩니다.

---

# 지원 예시

## Hello World

testcase1_input.txt
(빈 파일)

testcase1_output.txt
Hello World

---

## 두 수 곱하기

testcase1_input.txt
3 4

testcase1_output.txt
12

---

# 주의사항

문제 폴더 이름은 반드시:

1번문제
2번문제
3번문제

형식이어야 합니다.

띄어쓰기 사용 금지.
