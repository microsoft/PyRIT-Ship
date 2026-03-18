FROM ubuntu:latest

RUN apt-get update && \
    apt-get install -y --no-install-recommends python3 python3-pip python3-venv && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN python3 -m venv /app/venv && \
    /app/venv/bin/pip install --no-cache-dir -r requirements.txt

COPY . .

# pass via docker run -e or --env-file
ENV OPENAI_CHAT_MODEL_NAME="" \
    OPENAI_CHAT_ENDPOINT="" \
    OPENAI_CHAT_KEY="" \
    FLASK_HOST=0.0.0.0 \
    FLASK_PORT=5001 \
    FLASK_DEBUG=false

EXPOSE 5001

# NOTE: InteractiveBrowserCredential will NOT work in a headless container.
# So make sure to provide OPENAI_CHAT_KEY
CMD ["/app/venv/bin/python3", "app.py"]
