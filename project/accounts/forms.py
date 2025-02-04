from django import forms
from django.contrib.auth.forms import UserCreationForm  # базовая форма (реализованы все валидации и проверки)
from django.contrib.auth.models import User

from allauth.account.forms import SignupForm                            # для обработки регистрации
from allauth.socialaccount.forms import SignupForm as SocialSignupForm  # для обработки регистрации через провайдера
from django.contrib.auth.models import Group

from django.core.mail import send_mail                  # Для отправки писем


class SignUpForm(UserCreationForm):
    # Расширяем базовую форму, добавляем значимые поля (которые есть в модели User)
    email = forms.EmailField(label="Email")
    first_name = forms.CharField(label="Имя")
    last_name = forms.CharField(label="Фамилия")

    class Meta:
        model = User
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "password1",
            "password2",
        )


class CustomSignupForm(SignupForm):
    """
    Добавляет нового пользователя в группу common, при успешном заполнении формы регистрации.
    Функция send_mail отправляет приветственное письмо получателю recipient_list
    """
    def save(self, request):
        # вызываем этот же метод класса-родителя, чтобы необходимые проверки и сохранение в модель User были выполнены.
        user = super(CustomSignupForm, self).save(request)
        common_group = Group.objects.get(name='common')             # получаем объект модели группы common
        common_group.user_set.add(user)                             # возвращаем пользователей группы и добавляем нового

        send_mail(subject='Добро пожаловать на наш новостной портал',
                  message=f'{user.username}, Вы успешно зарегистрировались!',
                  from_email=None,                                   # будет использовано значение DEFAULT_FROM_EMAIL
                  recipient_list=[user.email], )
        return user                                                  # возвращаем объект модели User


class CustomSocialSignupForm(SocialSignupForm):
    """
    Добавляет нового пользователя в группу common, при успешной регистрации через провайдера (google, yandex и т.д.).
    Функция send_mail отправляет приветственное письмо получателю recipient_list
    """
    def save(self, request):
        # вызываем этот же метод класса-родителя, чтобы необходимые проверки и сохранение в модель User были выполнены.
        user = super(CustomSocialSignupForm, self).save(request)
        common_group = Group.objects.get(name='common')             # получаем объект модели группы common
        common_group.user_set.add(user)                             # возвращаем пользователей группы и добавляем нового

        send_mail(subject='Добро пожаловать на наш новостной портал',
                  message=f'{user.username}, Вы успешно зарегистрировались!',
                  from_email=None,                                   # будет использовано значение DEFAULT_FROM_EMAIL
                  recipient_list=[user.email], )
        return user                                                  # возвращаем объект модели User
