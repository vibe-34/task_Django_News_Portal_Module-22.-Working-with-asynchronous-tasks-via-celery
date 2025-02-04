from django.urls import path
from .views import SignUp, IndexView, upgrade_me

urlpatterns = [
    path('', IndexView.as_view()),  # перенаправляемся в представление IndexView
    path('signup/', SignUp.as_view(), name='signup'),
    path('upgrade/', upgrade_me, name='upgrade')
]
