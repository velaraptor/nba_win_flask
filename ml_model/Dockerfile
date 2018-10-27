FROM python:3.6

RUN apt-get update && apt-get install -y \
    git \
    apt-utils \
    build-essential

RUN mkdir /app
COPY requirements.txt /app/
COPY requirements_post.txt /app/
WORKDIR /app

RUN pip install -r requirements.txt
RUN pip install -r requirements_post.txt
RUN git clone https://github.com/mblondel/soft-dtw.git
RUN cd soft-dtw && make cython

RUN cd soft-dtw && PYTHONPATH=. python setup.py build
RUN cd soft-dtw && PYTHONPATH=. python setup.py install

COPY . /app

CMD ["python", "run_model.py"]
