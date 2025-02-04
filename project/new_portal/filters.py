from django import forms
from django_filters import FilterSet, CharFilter, DateFilter, ModelChoiceFilter
from .models import Post, Author, Category


class PostFilter(FilterSet):
    author = ModelChoiceFilter(queryset=Author.objects.all(),
                               field_name='author__user__username',
                               label='Автор',
                               empty_label="Выбрать автора",
                               lookup_expr='iexact')

    categories = ModelChoiceFilter(queryset=Category.objects.all(),
                                   field_name='categories',
                                   label='Категория',
                                   empty_label='Выбрать категорию',
                                   )

    title = CharFilter(field_name='title',
                       label='Заголовок',
                       lookup_expr='iregex')  # icontains не работает без учета регистра именно в SQLite

    time_in = DateFilter(
                        field_name='time_in',
                        widget=forms.DateInput(attrs={'type': 'date'}),
                        label='Дата публикации',
                        lookup_expr='date__gte',)

    class Meta:
        model = Post
        fields = ['author', 'title', 'time_in', 'categories']
