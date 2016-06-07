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
        'OPTIONS': {
            'charset': 'utf8',
            'init_command': 'SET character_set_client=utf8mb4,character_set_results=utf8mb4,character_set_connection=utf8mb4,collation_connection=utf8mb4_unicode_ci'
        }
    }
}
