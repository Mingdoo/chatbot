#!/bin/bash

# 사용법: ./deploy.sh v1.0.0
tag=$1

if [ -z "$tag" ]; then
  echo "❌ 이미지 태그를 입력해야 합니다. 예: ./deploy.sh v1.0.0"
  exit 1
fi

container_name="streamlit-app"

echo "🔍 기존 컨테이너 확인 중..."

# 기존 컨테이너가 실행 중이면 중지
if [ "$(docker ps -q -f name=$container_name)" ]; then
  echo "🛑 컨테이너 중지 중..."
  docker stop $container_name
fi

# 중지된 컨테이너가 존재하면 제거
if [ "$(docker ps -a -q -f name=$container_name)" ]; then
  echo "🗑️ 컨테이너 제거 중..."
  docker rm $container_name
fi

echo "🚀 새 컨테이너 실행 중..."
docker run \
  --name $container_name \
  -p 8501:8501 \
  -v /home/myadmin/chatbot/chroma_db:/app/chroma_db \
  -v /home/myadmin/chatbot/.env:/app/.env \
  -dt devmanduacr001.azurecr.io/streamlit-app:$tag

echo "✅ 배포 완료: $container_name (태그: $tag)"