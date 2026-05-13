FROM docker.n8n.io/n8nio/n8n:latest

# Install Python and pip in the Alpine-based n8n image
USER root
RUN apk add --no-cache python3 py3-pip
USER node