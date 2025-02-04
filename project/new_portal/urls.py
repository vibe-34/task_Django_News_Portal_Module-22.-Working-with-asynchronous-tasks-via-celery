from django.urls import path
from .views import PostList, PostDetail, PostCreate, PostUpdate, PostDelete, subscriptions

urlpatterns = [
	path('', PostList.as_view(), name='post'),
	path('<int:pk>/', PostDetail.as_view(), name='post_detail'),
	path('search/', PostList.as_view(), name='post_search'),
	path('news/create/', PostCreate.as_view(), name='news_create'),
	path('articles/create/', PostCreate.as_view(), name='articles_create'),
	path('<int:pk>/update/', PostUpdate.as_view(), name='post_update'),
	path('<int:pk>/delete/', PostDelete.as_view(), name='post_delete'),
	# path('news/<int:pk>/delete/', PostDelete.as_view(), name='news_delete'),
	# path('articles/<int:pk>/delete/', PostDelete.as_view(), name='articles_delete'),
	# path('news/<int:pk>/update/', PostUpdate.as_view(), name='news_update'),
	# path('articles/<int:pk>/update/', PostUpdate.as_view(), name='articles_update'),
	path('subscriptions/', subscriptions, name='subscriptions'),
	]
