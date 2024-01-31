FROM python:3.12.1-alpine


# Create a directory for our workspace.
RUN mkdir "/workspace/"

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install system dependencies
#RUN apk update && apk add -y netcat


# install dependencies
RUN pip install --no-cache-dir --upgrade pip
COPY requirements.txt /workspace/
RUN pip install  --no-cache-dir -r  /workspace/requirements.txt
COPY pytest.ini /workspace/



# copy project
COPY ./db_dummy_data/ /workspace/db_dummy_data/
COPY ./src/ecommerce_cart/ /workspace/ecommerce_cart/

# Use non-root user for safety.
RUN adduser --disabled-password --gecos "" django
RUN chown -R django:django /workspace/ecommerce_cart/
USER django

# Change work directory to our project's directory.
WORKDIR /workspace/ecommerce_cart/
