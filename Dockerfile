FROM python:3.6
RUN mkdir /project
ADD ./ /project
WORKDIR /project
RUN pip install -r requirements.txt -i https://pypi.mirrors.ustc.edu.cn/simple/
CMD python service.py