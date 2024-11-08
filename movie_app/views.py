from django.db.models import Count
from django.views.generic import DetailView, ListView
from utils.tools import get_client_ip
from .models import Serie, Film, Part, Season, FilmByQuality, FilmVisit, SerieVisit, Genre, Date,Shows,Bookings,Payment,Comment
from django.shortcuts import get_object_or_404, render,redirect
from django.urls import reverse
from django.http import HttpResponse
from django.views import View
from django.contrib.auth.decorators import login_required
from .forms import CommentForm

class SerieComponent(DetailView):
    template_name = 'serie_download_page.html'
    model = Serie
    context_object_name = 'serie'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        loaded_serie = self.object
        context['seasons'] = Season.objects.filter(serie__slug=loaded_serie.slug).all()
        context['parts'] = Part.objects.filter(season__serie__slug=loaded_serie.slug).all()
        context['trailer'] = loaded_serie.trailer.url if loaded_serie.trailer else None
        context['related_series'] = Serie.objects.filter(genre=loaded_serie.genre.first()).exclude(pk=loaded_serie.id)
        if self.request.user.is_authenticated:
            context['is_favorite'] = self.request.user.saved_series.filter(pk=loaded_serie.id).exists()
        user_ip = get_client_ip(self.request)
        user_id = None
        if self.request.user.is_authenticated:
            user_id = self.request.user.id

        has_been_visited = SerieVisit.objects.filter(ip__iexact=user_ip, serie_id=loaded_serie.id).exists()

        if not has_been_visited:
            new_visit = SerieVisit(ip=user_ip, user_id=user_id, serie_id=loaded_serie.id)
            new_visit.save()

        return context

from django.utils import timezone
class FilmComponent(DetailView):
    template_name = 'film_download_page.html'
    model = Film
    context_object_name = 'film'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        loaded_film = self.object
        context['film_qualities'] = FilmByQuality.objects.prefetch_related().filter(film__slug=loaded_film.slug).all()
        context['related_films'] = Film.objects.filter(genre=loaded_film.genre.first()).exclude(pk=loaded_film.id)
        context['trailer'] = loaded_film.trailer.url if loaded_film.trailer else None

        context['comments'] = Comment.objects.filter(film=loaded_film)
        context['form'] = CommentForm()

        all_ratings = Comment.objects.filter(film=loaded_film).values_list('rating', flat=True)
        context['average_rating'] = sum(all_ratings) / len(all_ratings) if all_ratings else 0
        context['loop_time'] = range(5,0,-1)
        context['loop_times'] = range(1,6)
       
        if self.request.user.is_authenticated:
            context['is_favorite'] = self.request.user.saved_films.filter(pk=loaded_film.id).exists()

        user_ip = get_client_ip(self.request)
        user_id = None
        if self.request.user.is_authenticated:
            user_id = self.request.user.id

        has_been_visited = FilmVisit.objects.filter(ip__iexact=user_ip, film_id=loaded_film.id).exists()

        if not has_been_visited:
            new_visit = FilmVisit(ip=user_ip, user_id=user_id, film_id=loaded_film.id)
            new_visit.save()

        return context
    
    def post(self, request, *args, **kwargs):
        # Handle POST request for comments
        self.object = self.get_object()  # Load the film object
        
        edit_comment_id = request.POST.get('edit_comment_id')
        if edit_comment_id:
            comment = get_object_or_404(Comment, id=edit_comment_id)  # Fetch the comment
            if comment.user == request.user:  # Ensure the user is the comment owner
                comment.content = request.POST.get('content')  # Update the comment content
                comment.created_at = timezone.now()  # Update created_at to now
                comment.save()  # Save the comment
                return redirect(reverse('film-page', kwargs={'slug': self.object.slug}))
        
        
        # Handle comment deletion
        delete_comment_id = request.POST.get('delete_comment_id')
        if delete_comment_id:
            comment = get_object_or_404(Comment, id=delete_comment_id)  # Fetch the comment
            if comment.user == request.user:  # Ensure the user is the comment owner
                comment.delete()  # Delete the comment
                return redirect(reverse('film-page', kwargs={'slug': self.object.slug}))  

      
            
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.film = self.object
            comment.user = request.user
            comment.save()
            return redirect(reverse('film-page', kwargs={'slug': self.object.slug}))
        
        # If form is not valid, re-render page with form errors
        context = self.get_context_data()
        context['form'] = form
        return self.render_to_response(context)
    

class FilmList(ListView):
    template_name = 'films_page.html'
    model = Film
    context_object_name = 'films'
    ordering = ['-imdb']
    paginate_by = 6

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['most_visit'] = Film.objects.filter(is_active=True).annotate(
            visit_count=Count('filmvisit')).order_by('-visit_count')[:8]
        context['all_genres'] = Genre.objects.all()
        context['all_years'] = Date.objects.all()
        # film_ids = context['films'].values_list('id', flat=True)  # Get the list of film IDs
        # context['shows'] = Shows.objects.filter(film_id__in=film_ids)

        return context


class SerieList(ListView):
    template_name = 'series_page.html'
    model = Serie
    context_object_name = 'series'
    ordering = ['-imdb']
    paginate_by = 6

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['most_visit'] = Serie.objects.filter(is_active=True).annotate(
            visit_count=Count('serievisit')).order_by('-visit_count')[:8]
        context['all_genres'] = Genre.objects.all()
        context['all_years'] = Date.objects.all()

        return context
        
def seat(request,id):
    show = Shows.objects.get(shows=id)
    seat = Bookings.objects.filter(shows=id)
    user_has_booking = False
    if request.user.is_authenticated:
        user_has_booking = Bookings.objects.filter(user=request.user, shows=show).exists()
    return render(request,"seat.html", {'show':show, 'seat':seat,'user_has_booking':user_has_booking})    

def ticket(request,id):
    ticket = Bookings.objects.get(id=id)
    return render(request,"ticket.html", {'ticket':ticket})

def booked(request):
    if request.method == 'POST':
        user = request.user
        seat = ','.join(request.POST.getlist('check'))
        show = request.POST['show']
        book = Bookings(useat=seat, shows_id=show, user=user)
        book.save()
        return render(request,"booked.html", {'book':book})  


def bookings(request):
    user = request.user
    book = Bookings.objects.filter(user=user.pk)
    # book_ids = book.values_list('bookid', flat=True)

    # # Use the book_ids list to filter payments
    # payments = Payment.objects.filter(book_id__in=book_ids)
    return render(request,"booking.html", {'book':book} )   



def delete(request,id):
    booked_delete = Bookings.objects.get(id=id);
    booked_delete.delete();
    return redirect('/movies/bookings')


def add_shows(request):
    return render(request,"addshow.html")














import hashlib
import hmac
import json
import urllib
import urllib.parse
import urllib.request
import random
import requests
from datetime import datetime
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect


from movie_app.models import PaymentForm
from movie_app.vnpay import vnpay


def index(request):
    return render(request, "payment/index.html", {"title": "Danh sách demo"})


def hmacsha512(key, data):
    byteKey = key.encode('utf-8')
    byteData = data.encode('utf-8')
    return hmac.new(byteKey, byteData, hashlib.sha512).hexdigest()


def payment(request,id):
    payment = Bookings.objects.get(id=id)

    if request.method == 'POST':
        # Process input data and build url payment
        form = PaymentForm(request.POST)
        if form.is_valid():
            order_type = form.cleaned_data['order_type']
            order_id = form.cleaned_data['order_id']
            amount = form.cleaned_data['amount']
            order_desc = form.cleaned_data['order_desc']
            bank_code = form.cleaned_data['bank_code']
            language = form.cleaned_data['language']
            ipaddr = get_client_ip(request)
            # Build URL Payment
            vnp = vnpay()
            vnp.requestData['vnp_Version'] = '2.1.0'
            vnp.requestData['vnp_Command'] = 'pay'
            vnp.requestData['vnp_TmnCode'] = settings.VNPAY_TMN_CODE
            vnp.requestData['vnp_Amount'] = amount * 100000
            vnp.requestData['vnp_CurrCode'] = 'VND'
            vnp.requestData['vnp_TxnRef'] = order_id
            vnp.requestData['vnp_OrderInfo'] = order_desc
            vnp.requestData['vnp_OrderType'] = order_type
            # Check language, default: vn
            if language and language != '':
                vnp.requestData['vnp_Locale'] = language
            else:
                vnp.requestData['vnp_Locale'] = 'vn'
                # Check bank_code, if bank_code is empty, customer will be selected bank on VNPAY
            if bank_code and bank_code != "":
                vnp.requestData['vnp_BankCode'] = bank_code

            vnp.requestData['vnp_CreateDate'] = datetime.now().strftime('%Y%m%d%H%M%S')  # 20150410063022
            vnp.requestData['vnp_IpAddr'] = ipaddr
            vnp.requestData['vnp_ReturnUrl'] = settings.VNPAY_RETURN_URL
            vnpay_payment_url = vnp.get_payment_url(settings.VNPAY_PAYMENT_URL, settings.VNPAY_HASH_SECRET_KEY)
            print(vnpay_payment_url)
            return redirect(vnpay_payment_url)
        else:
            print("Form input not validate")
    else:
        return render(request, "payment/payment.html", {"title": "Thanh toán","payment":payment})


def payment_ipn(request):
    inputData = request.GET
    
    if inputData:
        vnp = vnpay()
        vnp.responseData = inputData.dict()
        order_id = inputData['vnp_TxnRef']
        # order_type = inputData['vnp_OrderType']
        amount = inputData['vnp_Amount']
        order_desc = inputData['vnp_OrderInfo']
        vnp_TransactionNo = inputData['vnp_TransactionNo']
        vnp_ResponseCode = inputData['vnp_ResponseCode']
        vnp_TmnCode = inputData['vnp_TmnCode']
        vnp_PayDate = inputData['vnp_PayDate']
        vnp_BankCode = inputData['vnp_BankCode']
        vnp_CardType = inputData['vnp_CardType']
        if vnp.validate_response(settings.VNPAY_HASH_SECRET_KEY):
            # Check & Update Order Status in your Database
            # Your code here
            firstTimeUpdate = True
            totalamount = True
            if totalamount:
                if firstTimeUpdate:
                    if vnp_ResponseCode == '00':
                        print('Payment Success. Your code implement here')
                    else:
                        print('Payment Error. Your code implement here')

                    # Return VNPAY: Merchant update success
                    result = JsonResponse({'RspCode': '00', 'Message': 'Confirm Success'})
                else:
                    # Already Update
                    result = JsonResponse({'RspCode': '02', 'Message': 'Order Already Update'})
            else:
                # invalid amount
                result = JsonResponse({'RspCode': '04', 'Message': 'invalid amount'})
        else:
            # Invalid Signature
            result = JsonResponse({'RspCode': '97', 'Message': 'Invalid Signature'})
    else:
        result = JsonResponse({'RspCode': '99', 'Message': 'Invalid request'})

    return result


def payment_return(request):
    inputData = request.GET
      
       
    if inputData:
        vnp = vnpay()
        vnp.responseData = inputData.dict()
        order_id = inputData['vnp_TxnRef']
        # order_type = inputData['vnp_OrderType']
        amount = int(inputData['vnp_Amount']) / 100
        order_desc = inputData['vnp_OrderInfo']
        vnp_TransactionNo = inputData['vnp_TransactionNo']
        vnp_ResponseCode = inputData['vnp_ResponseCode']
        vnp_TmnCode = inputData['vnp_TmnCode']
        vnp_PayDate = inputData['vnp_PayDate']
        vnp_BankCode = inputData['vnp_BankCode']
        vnp_CardType = inputData['vnp_CardType']

        try:
           booking_instance = Bookings.objects.get(bookid=order_id)
        except Bookings.DoesNotExist:
            return HttpResponse("Booking not found", status=404)

        payment = Payment.objects.create(
            bookid = booking_instance,
            price = amount,
            order_desc = order_desc,
            vnp_TransactionNo = vnp_TransactionNo,
            vnp_ResponseCode = vnp_ResponseCode
        )



        if vnp.validate_response(settings.VNPAY_HASH_SECRET_KEY):
            if vnp_ResponseCode == "00":
                return render(request, "payment/payment_return.html", {"title": "Kết quả thanh toán",
                                                               "result": "Thành công", "order_id": order_id,
                                                               "amount": amount,
                                                               "order_desc": order_desc,
                                                               "vnp_TransactionNo": vnp_TransactionNo,
                                                               "vnp_ResponseCode": vnp_ResponseCode})
            else:
                return render(request, "payment/payment_return.html", {"title": "Kết quả thanh toán",
                                                               "result": "Lỗi", "order_id": order_id,
                                                               "amount": amount,
                                                               "order_desc": order_desc,
                                                               "vnp_TransactionNo": vnp_TransactionNo,
                                                               "vnp_ResponseCode": vnp_ResponseCode})
        else:
            return render(request, "payment/payment_return.html",
                          {"title": "Kết quả thanh toán", "result": "Lỗi", "order_id": order_id, "amount": amount,
                           "order_desc": order_desc, "vnp_TransactionNo": vnp_TransactionNo,
                           "vnp_ResponseCode": vnp_ResponseCode, "msg": "Sai checksum"})
    else:
        return render(request, "payment/payment_return.html", {"title": "Kết quả thanh toán", "result": ""})


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

n = random.randint(10**11, 10**12 - 1)
n_str = str(n)
while len(n_str) < 12:
    n_str = '0' + n_str


def query(request):
    if request.method == 'GET':
        return render(request, "payment/query.html", {"title": "Kiểm tra kết quả giao dịch"})

    url = settings.VNPAY_API_URL
    secret_key = settings.VNPAY_HASH_SECRET_KEY
    vnp_TmnCode = settings.VNPAY_TMN_CODE
    vnp_Version = '2.1.0'

    vnp_RequestId = n_str
    vnp_Command = 'querydr'
    vnp_TxnRef = request.POST['order_id']
    vnp_OrderInfo = 'kiem tra gd'
    vnp_TransactionDate = request.POST['trans_date']
    vnp_CreateDate = datetime.now().strftime('%Y%m%d%H%M%S')
    vnp_IpAddr = get_client_ip(request)

    hash_data = "|".join([
        vnp_RequestId, vnp_Version, vnp_Command, vnp_TmnCode,
        vnp_TxnRef, vnp_TransactionDate, vnp_CreateDate,
        vnp_IpAddr, vnp_OrderInfo
    ])

    secure_hash = hmac.new(secret_key.encode(), hash_data.encode(), hashlib.sha512).hexdigest()

    data = {
        "vnp_RequestId": vnp_RequestId,
        "vnp_TmnCode": vnp_TmnCode,
        "vnp_Command": vnp_Command,
        "vnp_TxnRef": vnp_TxnRef,
        "vnp_OrderInfo": vnp_OrderInfo,
        "vnp_TransactionDate": vnp_TransactionDate,
        "vnp_CreateDate": vnp_CreateDate,
        "vnp_IpAddr": vnp_IpAddr,
        "vnp_Version": vnp_Version,
        "vnp_SecureHash": secure_hash
    }

    headers = {"Content-Type": "application/json"}

    response = requests.post(url, headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        response_json = json.loads(response.text)
    else:
        response_json = {"error": f"Request failed with status code: {response.status_code}"}

    return render(request, "payment/query.html", {"title": "Kiểm tra kết quả giao dịch", "response_json": response_json})

def refund(request):
    if request.method == 'GET':
        return render(request, "payment/refund.html", {"title": "Hoàn tiền giao dịch"})

    url = settings.VNPAY_API_URL
    secret_key = settings.VNPAY_HASH_SECRET_KEY
    vnp_TmnCode = settings.VNPAY_TMN_CODE
    vnp_RequestId = n_str
    vnp_Version = '2.1.0'
    vnp_Command = 'refund'
    vnp_TransactionType = request.POST['TransactionType']
    vnp_TxnRef = request.POST['order_id']
    vnp_Amount = request.POST['amount']
    vnp_OrderInfo = request.POST['order_desc']
    vnp_TransactionNo = '0'
    vnp_TransactionDate = request.POST['trans_date']
    vnp_CreateDate = datetime.now().strftime('%Y%m%d%H%M%S')
    vnp_CreateBy = 'user01'
    vnp_IpAddr = get_client_ip(request)

    hash_data = "|".join([
        vnp_RequestId, vnp_Version, vnp_Command, vnp_TmnCode, vnp_TransactionType, vnp_TxnRef,
        vnp_Amount, vnp_TransactionNo, vnp_TransactionDate, vnp_CreateBy, vnp_CreateDate,
        vnp_IpAddr, vnp_OrderInfo
    ])

    secure_hash = hmac.new(secret_key.encode(), hash_data.encode(), hashlib.sha512).hexdigest()

    data = {
        "vnp_RequestId": vnp_RequestId,
        "vnp_TmnCode": vnp_TmnCode,
        "vnp_Command": vnp_Command,
        "vnp_TxnRef": vnp_TxnRef,
        "vnp_Amount": vnp_Amount,
        "vnp_OrderInfo": vnp_OrderInfo,
        "vnp_TransactionDate": vnp_TransactionDate,
        "vnp_CreateDate": vnp_CreateDate,
        "vnp_IpAddr": vnp_IpAddr,
        "vnp_TransactionType": vnp_TransactionType,
        "vnp_TransactionNo": vnp_TransactionNo,
        "vnp_CreateBy": vnp_CreateBy,
        "vnp_Version": vnp_Version,
        "vnp_SecureHash": secure_hash
    }

    headers = {"Content-Type": "application/json"}

    response = requests.post(url, headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        response_json = json.loads(response.text)
    else:
        response_json = {"error": f"Request failed with status code: {response.status_code}"}

    return render(request, "payment/refund.html", {"title": "Kết quả hoàn tiền giao dịch", "response_json": response_json})

