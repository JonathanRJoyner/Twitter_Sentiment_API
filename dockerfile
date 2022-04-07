FROM public.ecr.aws/lambda/python:3.8

COPY tweet_sent.py ${LAMBDA_TASK_ROOT}

COPY requirements.txt .
RUN pip3 install -r requirements.txt --target "${LAMBDA_TASK_ROOT}"

CMD ["tweet_sent.lambda_handler"]