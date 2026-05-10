---
name: tools-usage
description: 뉴스 검색·파이썬 분석 도구 사용 지침. 앱 에이전트 런타임에 주입된다.
disable-model-invocation: true
---

# tools-usage

## search_news

- 짧은 키워드(2~8단어)로 검색합니다.
- 스텁 환경에서는 더미 URL이 반환될 수 있음을 사용자에게 알립니다.

## run_python_analysis

- `math`·기본 내장만 사용하는 짧은 코드를 작성합니다.
- 파일·네트워크·서브프로세스는 사용하지 않습니다.
