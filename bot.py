import streamlit as st
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import AzureOpenAIEmbeddings
from langchain_community.chat_models import AzureChatOpenAI
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.callbacks.base import BaseCallbackHandler
from langchain_core.documents import Document
from dotenv import load_dotenv
import time, os, json
load_dotenv()

# Streamlit 페이지 설정
st.set_page_config(page_title="OpenAPI Chat Agent", layout="wide")
st.title("OpenAPI 문서 기반 챗봇")

# 1. JSON 파일 로드
with open("apis/stripe-openapi.json", encoding="utf-8") as f:
    openapi = json.load(f)

# 2. OpenAPI 문서에서 path와 method를 추출하여 Document 객체 생성
texts = []
for path, methods in openapi.get("paths", {}).items():
    for method, spec in methods.items():
        doc_dict = {"path": path, "method": method, "spec": spec}
        content = json.dumps(doc_dict, ensure_ascii=False, indent=2)
        texts.append(Document(page_content=content))

# 3. Chroma DB 경로 설정 및 Azure OpenAI 임베딩 초기화
chroma_db_path = "chroma_db"
embeddings = AzureOpenAIEmbeddings(
    deployment="dev-text-embedding-3-large",
    chunk_size=1000,
    openai_api_version="2024-02-01"
)

# 4. Chroma DB 로드 또는 생성
if os.path.exists(chroma_db_path) and os.listdir(chroma_db_path):
    # 기존 Chroma DB가 존재하면 로드
    vectorstore = Chroma(
        embedding_function=embeddings,
        persist_directory=chroma_db_path
    )
else:
    print("Chroma DB가 존재하지 않거나 비어 있습니다. 새로 생성합니다.")
    # 새로운 Chroma DB 생성
    vectorstore = Chroma(
        embedding_function=embeddings,
        persist_directory=chroma_db_path
    )
    # 텍스트를 Chroma DB에 추가
    for idx, doc in enumerate(texts, start=1):
        vectorstore.add_documents([doc])
        print(f"{idx}/{len(texts)} 문서가 Chroma DB에 추가되었습니다.")
        time.sleep(1)
    # Chroma DB를 디스크에 저장
    vectorstore.persist()
    print("Chroma DB가 성공적으로 생성되었습니다.")

# RAG 체인 생성 (근거 JSON 포함)
llm = AzureChatOpenAI(
    deployment_name="dev-gpt-4.1-mini",
    temperature=0,
    streaming=True,
    openai_api_version="2024-12-01-preview",
)

# 프롬프트 템플릿: 답변에 반드시 관련 OpenAPI JSON 엔드포인트, 설명 등을 포함하도록 지시
custom_prompt = PromptTemplate(
    input_variables=["context", "question"],
    template="""
        질문: {question}
        아래는 OpenAPI JSON에서 추출한 관련 정보입니다:
        {context}
        ---
        위 정보를 참고하여, 관련 path, method, 설명 등 구조적 정보를 근거와 함께 명확히 답변하세요.
        반드시 답변과 함께 관련 테이블로 api 파라미터를 정리하여 엔드포인트, 설명을 출력하세요.
        필요하다면, 관련 JSON을 분석한 결과를 사용자가 요청할 수 있는 Java와 Python 샘플 코드, cURL 호출 전문을 짧게 출력하세요.
        모든 호출 도메인은 https://api.stripe.com/ 입니다.

        답변 예시: 
        답변: 
        파라미터 테이블:
    """
)

qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=vectorstore.as_retriever(search_kwargs={"k": 2}),
    return_source_documents=True,
    chain_type_kwargs={"prompt": custom_prompt}
)

class StreamHandler(BaseCallbackHandler):
    def __init__(self, container):
        self.container = container
        self.text = ""

    def on_llm_new_token(self, token: str, **kwargs):
        self.text += token
        self.container.markdown(f"**답변:**\n{self.text}", unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("질문을 입력하세요"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        container = st.empty()
        stream_handler = StreamHandler(container)
        # 직접 score 확인
        docs_and_scores = vectorstore.similarity_search_with_score(prompt, k=2)
        filtered = [doc for doc, score in docs_and_scores if score >= 0.7]
        if not filtered:
            answer = "❌ 관련된 정보를 찾을 수 없습니다. 질문을 더 구체적으로 입력해 주세요."
            container.markdown(f"{answer}")
            st.session_state.messages.append({"role": "assistant", "content": answer})
        else:
            result = qa_chain(
                {"query": prompt},
                callbacks=[stream_handler]
            )
            answer = result.get("result", "")
            container.markdown(f"{answer}")
            st.session_state.messages.append({"role": "assistant", "content": answer})

