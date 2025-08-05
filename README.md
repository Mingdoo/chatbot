# OpenAPI를 활용한 챗봇
Author: 강민수

## 챗봇 구성
#### streamlit과 RAG를 활용한 OpenAPI 챗봇
#### chroma 벡터 스토어와 LangChain을 사용하여 OpenAPI 문서에 기반한 챗봇을 구현합니다.
#### 이 코드는 Streamlit을 사용하여 웹 인터페이스를 제공하며, LangChain을 사용하여 RAG(정보 검색 증강 생성) 기능을 구현합니다.
#### OpenAPI 문서를 로드하여 벡터 스토어를 생성한 후, 사용자의 질문에 대해 OpenAI 모델을 통해 응답을 생성합니다.
#### 이 코드는 OpenAPI 문서의 내용을 기반으로 사용자의 질문에 대한 답변을 제공하는 기능을 포함하고 있습니다.
#### Azure OpenAI를 사용하여 질문에 대한 답변을 생성합니다.
#### 문서는 apis/stripe-openapi.json에서 로드됩니다.

> API 제공: https://github.com/stripe/openapi

## 프로젝트 구성

> 이 프로젝트의 코드는 Stripe OpenAPI 문서를 기반으로 한 RAG(검색 증강 생성) 챗봇을 Streamlit 웹앱으로 구현하고 있습니다.
> 아래와 같이 각 요소가 코드 전반에 자연스럽게 녹아들어 있습니다.

#### 1. LLM과 RAG의 융합
OpenAPI 문서를 path/method별로 세분화하여 벡터화(임베딩)하고, Chroma 벡터스토어에 저장합니다.
사용자의 질문이 들어오면, 벡터스토어에서 유사도가 높은 문서만 추출하여 LLM의 context로 제공합니다.
LLM(Azure OpenAI GPT-4 기반)은 이 context를 바탕으로 답변을 생성하므로, 단순 생성이 아니라 “문서 근거 기반”의 신뢰성 있는 답변이 나옵니다.
답변에는 항상 관련 JSON, 파라미터 테이블, 샘플 코드 등 실질적 근거가 포함되도록 프롬프트가 설계되어 있습니다.

#### 2. 거버넌스(RAIC)와 품질 관리의 코드 내재화
**Responsible/Accountable**: 임계값(score threshold) 적용으로, 관련 없는 엔드포인트는 답변하지 않음(“❌ 관련된 정보를 찾을 수 없습니다” 안내).
**Interpretable**: 답변에 반드시 근거(JSON snippet, 파라미터 표, 샘플 코드 등)를 포함하도록 프롬프트와 출력 로직이 설계됨.
**Controllable**: 프롬프트, 임계값, 임베딩/LLM 파라미터 등 주요 품질 요소가 코드 상수로 명확히 관리됨.
예외 상황(벡터 검색 결과 없음 등)도 사용자에게 명확히 안내하여, 서비스 신뢰성을 높임.

#### 3. Prompt Engineering과 운영의 일상화
프롬프트 템플릿이 코드에 명확히 선언되어 있어, 답변 형식·포맷·샘플코드 포함 여부 등을 쉽게 조정할 수 있습니다.
Prompt를 바꾸면 즉시 서비스 품질과 답변 스타일이 바뀌므로, Prompt Ops(운영)가 실시간으로 가능합니다.

#### 4. 서비스 안정성과 확장성
벡터스토어가 없으면 자동으로 생성, 임베딩 파라미터도 상황에 맞게 조정
Streamlit UI와 LangChain 콜백을 활용해 실시간 스트리밍 답변 제공
Azure OpenAI API 장애 등 외부 이슈 발생 시 graceful degradation(안내 메시지) 구조도 쉽게 추가 가능