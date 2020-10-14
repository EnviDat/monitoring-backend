import environ
from waitress import serve
from project.wsgi import application

# documentation: https://docs.pylonsproject.org/projects/waitress/en/stable/api.html
env = environ.Env()
# Reading .env file
environ.Env.read_env()

if __name__ == '__main__':
    serve(application, host=env("ALLOWED_HOST_1"), port=env("PORT"))
