# Build a Sentence (단어 배열)

Writing → **Build a Sentence** 선택 후 붙여넣기.

## 규칙

- 문제 하나 = **상대 말 한 줄(없어도 됨)** + **정답 문장 한 줄**
- 문제끼리는 **빈 줄**로 구분
- 정답 문장 안에서
  - `/` : 보기 덩어리 경계 (안 쓰면 단어 하나씩 보기가 됨)
  - `[ ]` : 미리 채워진 단어 (보기로 안 나옴)
  - 끝의 `.` `?` `!` 는 자동으로 고정
- 함정 보기(정답에 안 쓰는 단어)는 정답 다음 줄에 `extra:` 로. 여러 개면 `/` 나 `,` 로 구분
- 앞의 `1.` `-` 같은 번호, `A:` `B:` 같은 화자 표시는 있어도 됨

## 예시

```
What did you think of the field trip?
I / really enjoyed / [the] / museum visit / the most.
extra: enjoy

Do you know when the library closes?
I think / [it] / closes / at / nine / on weekdays.

Why were you late this morning?
The bus / [didn't] / come / on time / again.
extra: comes, did

Could you help me with the assignment?
Sure, / what part / are you / having trouble / with?
```

## 다른 형식도 됨

화자 표시로 주기 (빈 줄 없어도 두 줄씩 묶음):

```
A: Did you finish the report?
B: Not yet, but I will finish it tonight.
A: When is the meeting?
B: It starts at three.
```

정답 문장만 한 줄에 하나씩 (상대 말 없이, 단어 하나씩 보기):

```
1. The professor asked us to submit the essay by Friday.
2. Could you tell me where the station is?
3. She has been working here for five years.
```
