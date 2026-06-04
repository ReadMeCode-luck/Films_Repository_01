from django.contrib import admin
from django.urls import path, include, re_path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.urls import include, path
from debug_toolbar.toolbar import debug_toolbar_urls

urlpatterns = [
    path('', views.index, name='index'),
    path('films/', views.films_page, name='films'),
    path('cartoons/', views.cartoons_page, name='cartoons'),
    re_path(r'^films/(?P<slug>[-\wЀ-ӿ]+)/$', views.film_detail, name='film_detail'),
    path('showtime/<int:showtime_id>/seats/', views.seat_selection, name='seat_selection'),
    path('showtime/<int:showtime_id>/book/', views.book_seats, name='book_seats'),
    path('profile/', include('users.urls')),
    path('films/<int:film_id>/favorite/', views.toggle_favorite, name='toggle_favorite'),
    path('films/<int:film_id>/remove-favorite/', views.remove_favorite, name='remove_favorite'),
    path('favorites/clear/', views.clear_all_favorites, name='clear_all_favorites'),
    path('my-tickets/', views.my_tickets, name='my_tickets'),
    path('search/live/', views.live_search, name='live_search'),
    path('api/films/', views.FilmList.as_view(), name='film-list'),
    path('admin/', admin.site.urls),
    path('entrance/', views.entrance, name='entrance'),
    path('accounts/password_reset/', auth_views.PasswordResetView.as_view(template_name='registration/password_reset_form.html'), name='password_reset'),
    path('accounts/password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'), name='password_reset_done'),
    path('accounts/reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'), name='password_reset_confirm'),
    path('accounts/reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'), name='password_reset_complete'),
] + debug_toolbar_urls()


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler400 = 'films.views.e_handler400'
handler404 = 'films.views.e_handler404'
handler403 = 'films.views.csrf_failure'
handler500 = 'films.views.e_handler500'