from django.urls import path, include
from .views import *
from .views import CourseListAPIView, CourseRequestAPIView

urlpatterns = [
    path('register/', registerAPIView.as_view()),
    path('login/', LoginAPIView.as_view()),
    path('user/', UserView.as_view()),
    path('logout/', LogoutView.as_view()),
    path('courses/', CourseListAPIView.as_view(), name='course-list'),
    path('course-request/', CourseRequestAPIView.as_view(), name='course-request'),
]
