FROM python:3.11-slim-bookworm
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set python3.11 as the default python
RUN ln -sf $(which python3.11) /usr/local/bin/python && \
    ln -sf $(which python3.11) /usr/local/bin/python3

# Install dependencies
COPY requirements.txt /requirements.txt
RUN uv pip install --upgrade -r /requirements.txt --no-cache-dir --system

# Add files
ADD app.py .

RUN uv run playwright install --with-deps

CMD uv run /app.py

# sudo docker build --platform linux/amd64 --tag mantrakp04/crawler:v1 . && sudo docker push mantrakp04/crawler:v1
# sudo docker run -it --platform linux/amd64 -p 7860:7860 --rm mantrakp04/crawler:v1