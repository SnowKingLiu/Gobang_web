"""Gobang_web URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from django.views.generic import TemplateView, RedirectView
from gobang_ai.views import send_chessboard
from train.views import send_train_chessboard

urlpatterns = [
    url(r'^favicon\.ico$', RedirectView.as_view(url='/static/media/favicon.ico')),
    url(r'^admin/', admin.site.urls),
    url(r'^$', TemplateView.as_view(template_name="chessboard.html"), name="chessboard"),
    url(r'^send_chessboard', send_chessboard, name="send_chessboard"),
    url(r'^send_train_chessboard', send_train_chessboard, name="send_train_chessboard"),
    url(r'^train', TemplateView.as_view(template_name="train.html"), name="train"),
]
