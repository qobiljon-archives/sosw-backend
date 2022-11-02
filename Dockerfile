FROM python:3.10-slim as base

# env to avoid trash
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1


FROM base AS deps

# postgres
RUN apt-get update
RUN apt-get install -y --no-install-recommends gcc
RUN apt-get install libpq-dev -y
ENV LDFLAGS '-L/usr/local/opt/libpq/lib'
ENV CPPFLAGS '-I/usr/local/opt/libpq/include'
ENV PKG_CONFIG_PATH '/usr/local/opt/libpq/lib/pkgconfig'

# pipenv
RUN pip install --upgrade pip
RUN pip install pipenv
COPY Pipfile .
RUN PIPENV_VENV_IN_PROJECT=1 pipenv install --deploy --skip-lock


FROM base AS runtime

# prepare runtime environment
COPY --from=deps /.venv /.venv
ENV PATH="/.venv/bin:$PATH"

# set working directory
RUN useradd --create-home sosw
WORKDIR /home/sosw
USER sosw

# install gunicorn and the app
RUN pip install -U gunicorn
COPY dashboard dashboard
COPY api api
COPY static static
COPY manage.py gunicorn.ini ema_notifier.py ./

# open app port and run the app
EXPOSE 8000
CMD ["gunicorn", "dashboard.wsgi", "-c", "gunicorn.ini"]