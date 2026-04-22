"""
Django settings for mysite project.
"""

import environ
import os
import dj_database_url
from pathlib import Path

# 1. まず最初に BASE_DIR を定義する
BASE_DIR = Path(__file__).resolve().parent.parent

# 2. 次に .env を読み込む
env = environ.Env(DEBUG=(bool, False))
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# 3. .env から設定を読み込む
# ※ 元々あった SECRET_KEY = '...' などの行は消して、こちらに統一します
SECRET_KEY = env('SECRET_KEY')
DEBUG = env('DEBUG')
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS')

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    "sns",
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', # 静的ファイル用
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'mysite.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'mysite.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# サーバー（Renderなど）で使うデータベース設定がある場合は上書きする
db_from_env = dj_database_url.config(conn_max_age=600)
DATABASES['default'].update(db_from_env)


# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
]

# Internationalization
LANGUAGE_CODE = 'ja'
TIME_ZONE = 'Asia/Tokyo'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Redirect settings
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = 'sns:index'  # ログアウトしたらトップページに戻る

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL = 'login'

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# --- settings.py の一番最後 ---

# Cloudinaryの接続設定（API Secretはご自身のものに！）
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': 'dbhu45a5z',
    'API_KEY': '893623692642876',
    'API_SECRET': 'QsxeqrPQYYbqo3_12pE13F00YsU',
}

# 【重要】Djangoに「画像保存のメインはCloudinaryだ！」と強制する設定
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'

# INSTALLED_APPS にこれらが確実に入っていることを保証する
if 'cloudinary_storage' not in INSTALLED_APPS:
    # 順番が大事：cloudinary_storage は一番上が好ましいです
    INSTALLED_APPS.insert(0, 'cloudinary_storage')
    INSTALLED_APPS += ['cloudinary']

# メディアURLの設定（これはそのまま）
MEDIA_URL = '/media/'