# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'DbMysql11',
        'USER': 'DbMysql11',
        'PASSWORD': 'DbMysql11',
        'HOST': 'mysqlsrv.cs.tau.ac.il',
        'PORT': '3306',
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': 'SET character_set_client=utf8mb4,character_set_results=utf8mb4,character_set_connection=utf8mb4,collation_connection=utf8mb4_unicode_ci'
        }
    }
}
