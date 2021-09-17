from django.urls import path

from .views import DiscourseView

urlpatterns = [
    path('', DiscourseView.as_view()),
]
