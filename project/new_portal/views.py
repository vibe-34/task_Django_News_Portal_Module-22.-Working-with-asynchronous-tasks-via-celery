from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import PermissionRequiredMixin  # только для зарегистрированных пользователей
from django.db.models import Exists, OuterRef
from django.urls import reverse_lazy
from django.views.decorators.csrf import csrf_protect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.shortcuts import render
from .forms import PostForm
from .models import Post, Author, Category, Subscription
from .filters import PostFilter


class PostList(ListView):
    model = Post
    ordering = '-time_in'                                  # сортировка по времени создания (от более свежей публикации)
    context_object_name = 'post'                           # имя списка содержащего все объекты
    paginate_by = 10                                       # указываем количество записей на странице

    # Переопределяем функцию получения списка товаров
    def get_queryset(self):
        queryset = super().get_queryset()                   # Получаем обычный запрос
        # Используем наш класс фильтрации. self.request.GET содержит объект QueryDict
        # сохраняем нашу фильтрацию в объекте класса, чтобы потом добавить в контекст и использовать в шаблоне.
        self.filterset = PostFilter(self.request.GET, queryset)
        return self.filterset.qs                             # Возвращаем из функции отфильтрованный список товаров

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filterset'] = self.filterset                # Добавляем в контекст объект фильтрации.
        return context

    def get_template_names(self):
        if self.request.path == '/post/search/':
            return 'search.html'
        return 'post.html'


class PostDetail(DetailView):
    model = Post
    template_name = 'post_id.html'
    context_object_name = 'post_id'                            # имя для обращения в шаблоне


class PostCreate(PermissionRequiredMixin, CreateView):
    permission_required = ('new_portal.add_post',)
    model = Post
    form_class = PostForm                                       # Указываем разработанную форму
    template_name = 'create_post.html'                          # Шаблон, в котором будет использоваться форма
    success_url = reverse_lazy('post')                          # URL для перенаправления после успешного создания поста

    def form_valid(self, form):
        author = Author.objects.get(user=self.request.user)      # Получаем текущего автора
        form.instance.author = author                            # Устанавливаем автора
        post = form.save(commit=False)
        if self.request.path == '/post/news/create/':
            post.choice_type = 'NW'
        post.save()
        return super().form_valid(form)


class PostUpdate(PermissionRequiredMixin, UpdateView):
    permission_required = ('new_portal.change_post',)
    model = Post
    form_class = PostForm                        # Указываем разработанную форму (ту же самую, что и при создании поста)
    template_name = 'create_post.html'           # Шаблон, в котором будет использоваться форма
    success_url = reverse_lazy('post')           # URL для перенаправления после успешного создания поста


class PostDelete(PermissionRequiredMixin, DeleteView):
    permission_required = ('new_portal.delete_post',)
    model = Post
    template_name = 'post_delete.html'
    success_url = reverse_lazy('post')


@login_required               # для того, что бы представление могли использовать только зарегистрированные пользователи
@csrf_protect                 # будет автоматически проверяться CSRF-токен в получаемых формах
def subscriptions(request):
    # Обработка POST запроса
    if request.method == 'POST':                         # Проверяем является ли метод запроса POST
        category_id = request.POST.get('category_id')    # Получаем id категории из POST-запроса
        category = Category.objects.get(id=category_id)  # Получаем объект категории из базы данных по переданному id.
        action = request.POST.get('action')              # Извлекаем действие (подписка или отписка)

        # Управление подписками
        if action == 'subscribe':    # Если подписка, то создается запись в моделе Subscription связь юзера с категорией
            Subscription.objects.create(user=request.user, category=category)
        elif action == 'unsubscribe':                     # Если отписка, то удаляется запись
            Subscription.objects.filter(user=request.user, category=category, ).delete()

    # annotate добавляет доп.поле user_subscribed к каждому объекту категории. Поле будет True если есть подписка
    # это проверяет Exists (наличие записи в таблице Subscription для текущего пользователя и категории)
    categories_with_subscriptions = Category.objects.annotate(
        user_subscribed=Exists(
            Subscription.objects.filter(
                user=request.user,
                category=OuterRef('pk'),
            )
        )
    ).order_by('name')
    return render(request, 'email/subscriptions.html', {'categories': categories_with_subscriptions},)
