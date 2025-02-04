from django.shortcuts import redirect
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView
from .forms import SignUpForm
from new_portal.models import Author


class SignUp(CreateView):
    model = User
    form_class = SignUpForm                      # Форма, которая будет заполняться пользователем
    success_url = '/accounts/login'              # url на который перенаправит после успешного заполнения формы
    template_name = 'registration/signup.html'   # Шаблон отражающий форму


class IndexView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)  # получаем весь контекст из класса-родителя
        # добавляем новую контекстную переменную is_not_authors
        context['is_not_authors'] = not self.request.user.groups.filter(name='authors').exists()  # is_no t_premium
        return context


@login_required
def upgrade_me(request):
    user = request.user                                          # Получаем текущего авторизованного пользователя
    author_group = Group.objects.get(name='authors')             # Получаем имя необходимой группы
    if not request.user.groups.filter(name='authors').exists():  # Проверяем, что пользователь не связан с этой группой
        author_group.user_set.add(user)                          # и если его нет, то добавляем в группу authors
    if not Author.objects.filter(user=user).exists():      # Если авторизованный пользователь не связан с моделью Author
        Author.objects.create(user=user)                         # то делаем его экземпляром класса Author
    return redirect('/')
