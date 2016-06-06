from secret import MYSQL_SERVER_PASSWORD

# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'musicfilter',
        'USER': 'root',
        'PASSWORD': MYSQL_SERVER_PASSWORD,
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
