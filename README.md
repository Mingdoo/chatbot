# OpenAPI를 활용한 챗봇
Author: 강민수

## 챗봇 구성
### streamlit과 RAG를 활용한 OpenAPI 챗봇
### chroma 벡터 스토어와 LangChain을 사용하여 OpenAPI 문서에 기반한 챗봇을 구현합니다.
### 이 코드는 Streamlit을 사용하여 웹 인터페이스를 제공하며, LangChain을 사용하여 RAG(정보 검색 증강 생성) 기능을 구현합니다.
### OpenAPI 문서를 로드하여 벡터 스토어를 생성한 후, 사용자의 질문에 대해 OpenAI 모델을 통해 응답을 생성합니다.
### 이 코드는 OpenAPI 문서의 내용을 기반으로 사용자의 질문에 대한 답변을 제공하는 기능을 포함하고 있습니다.
### Azure OpenAI를 사용하여 질문에 대한 답변을 생성합니다.
### 문서는 apis/stripe-openapi.json에서 로드됩니다.

> API 제공: https://github.com/stripe/openapi
