FROM mcr.microsoft.com/devcontainers/python:3.11

WORKDIR /workspace

# requirements.txt je o úroveň výš
COPY ../requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# zkopíruje celý projekt
COPY .. .

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
