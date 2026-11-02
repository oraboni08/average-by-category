FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY mapper.py reducer.py input/data.csv ./

CMD sh -c "python3 mapper.py < data.csv && python3 reducer.py"