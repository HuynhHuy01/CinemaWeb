from django.urls import path
from . import views
from .views import SerieComponent, FilmComponent, FilmList, SerieList

urlpatterns = [
    path('series/<slug:slug>', SerieComponent.as_view(), name="serie-page"),
    path('films/<slug:slug>', FilmComponent.as_view(), name="film-page"),
    path('films/', FilmList.as_view(), name='film-list-page'),
    path('series/', SerieList.as_view(), name='serie-list-page'),
    path('seat/<int:id>',views.seat,name='seat'),
    path('ticket/<int:id>',views.ticket,name='ticket'),
    path('booked',views.booked,name='booked'),
    path('bookings',views.bookings, name='bookings'),
    path('delete/<int:id>',views.delete,name='delete'),
    path('addshows/',views.add_shows,name='show'),


    path('pay',views.index, name='index'),
    path('payment/<int:id>',views.payment, name='payment'),
    path('payment_ipn',views.payment_ipn, name='payment_ipn'),
    path('payment_return',views.payment_return, name='payment_return'),
    path('query',views.query, name='query'),
    path('refund',views.refund, name='refund'),

]
