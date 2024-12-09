from django.shortcuts import render, redirect, get_object_or_404
from .forms import PasteForm, PasswordForm, EmailForm
from .models import Paste, CustomUser
from datetime import timedelta
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib.auth import login, get_user_model
from allauth.account.views import LoginView, PasswordResetView
from django.contrib import messages
from allauth.account.models import EmailAddress
from django.contrib.auth.decorators import login_required
from django.core.cache import cache


def paste_create(request):
    if request.method == 'POST':
        form = PasteForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            content = cd['content']
            expiration_option = cd['expiration_option']
            password = cd['password']

            expiration_time_mapping = {
                '10min': timedelta(minutes=10),
                'hour': timedelta(hours=1),
                'day': timedelta(days=1),
                'week': timedelta(weeks=1),
                'month': timedelta(days=30),
                'year': timedelta(days=365),
            }
            expiration_time = expiration_time_mapping.get(expiration_option, timedelta(hours=1))  # По умолчанию 1 час
            paste = Paste(content=content, expiration_time=expiration_time, password=password)
            
            if request.user.is_authenticated:
                paste.author = request.user

            paste.save()

            return redirect('app:paste_detail', unique_hash=paste.unique_hash)
    else:
        form = PasteForm()
    return render(request, 'paste/paste_create.html', {'form': form})


def paste_detail(request, unique_hash):
    # Попробуем получить текст из кэша
    cache_key = f'paste_{unique_hash}'
    paste = cache.get(cache_key)

    if paste is None:
        paste = get_object_or_404(Paste, unique_hash=unique_hash)
        # Сохраняем текст в кэш
        cache.set(cache_key, paste, timeout=3600)  # Кэшируем на 1 час

    # Проверяем, истекло ли время жизни заметки
    if paste.is_expired():
        paste.delete()
        cache.delete(cache_key)
        return render(request, 'paste/paste_was_deleted.html', {'message': 'Текст был удален из-за истечения времени.'})
    
    # если есть пароль на размещённом тексте
    if paste.password:
        if request.method == 'POST':
            form = PasswordForm(request.POST)
            if form.is_valid():
                entered_password = form.cleaned_data['password']
                if entered_password == paste.password:
                    return render(request, 'paste/paste_detail.html', {'paste': paste})
                else:
                    form.add_error('password', 'Неверный пароль. Попробуйте снова.')
        else:
            form = PasswordForm()
        return render(request, 'paste/password_check.html', {'form': form, 'paste': paste})
    # если нет пароля
    return render(request, 'paste/paste_detail.html', {'paste': paste})


@login_required
def paste_edit(request, unique_hash):
    paste = get_object_or_404(Paste, unique_hash=unique_hash)
    # Проверка на соответствие автора
    if paste.author != request.user:
        return render(request, 'paste/paste_edit_denied.html', {'message': 'У вас нет прав для редактирования этого текста.',
                                                                'paste': paste})
    
    if request.method == 'POST':
        form = PasteForm(request.POST, instance=paste)
        if form.is_valid():
            form.save()
            
            # Обновляем кэш
            cache_key = f'paste_{unique_hash}'
            cache.set(cache_key, paste, timeout=3600)  

            return redirect('app:paste_detail', unique_hash=paste.unique_hash)
        
    else:
        form = PasteForm(instance=paste)
    return render(request, 'paste/paste_edit.html', {'form': form, 'paste': paste})


@login_required
def paste_delete(request, unique_hash):
    paste = get_object_or_404(Paste, unique_hash=unique_hash)
    # Проверка на соответствие автора
    if paste.author != request.user:
        return render(request, 'paste/paste_delete_denied.html', {'message': 'У вас нет прав для удаления этого текста.',
                                                                  'paste': paste})
    
    if request.method == 'POST':
        paste.delete()
        return render(request, 'paste/paste_was_deleted.html', {'message': 'Текст был успешно удалён.'})

    return render(request, 'paste/paste_delete.html', {'paste': paste})


# AUTH
def first_page_login(request):
    if request.method == 'POST':
        form = EmailForm(request.POST)
        if form.is_valid(): 
            email = form.cleaned_data['email']
            User = get_user_model()  # Получаем модель пользователя

            try:
                user = User.objects.get(email=email)
                # Проверяем, зарегистрирован ли пользователь через социальную сеть
                if user.social_auth.exists():
                    email_address = EmailAddress.objects.filter(user=user, email=email, verified=True).first()
                    if email_address:
                        return redirect(f"{reverse('account_login')}?email={email}")
                    else:
                        return redirect('password_reset_notification')
                return redirect(f"{reverse('account_login')}?email={email}")
            
            except User.DoesNotExist:
                error_message = 'Пользователь с таким email не найден'
                form.add_error('email', error_message)
    else:
        form = EmailForm()

    return render(request, 'account/first_page_login.html', {'form': form})


def password_reset_notification(request):
    return render(request, 'account/password_reset_notification.html')


class CustomLoginView(LoginView): # email сохраняется в форме даже при ошибке
    def get(self, request, *args, **kwargs):
        email = request.GET.get('email', '')
        context = self.get_context_data()
        context['email'] = email
        return self.render_to_response(context)
    
    def form_invalid(self, form):
        email = self.request.POST.get('login', '')
        return self.render_to_response(self.get_context_data(form=form, email=email))
    
    def form_valid(self, form):
        email = form.cleaned_data.get('login') 
        user = CustomUser.objects.filter(email=email).first()

        if user is None:
            messages.error(self.request, "Пользователь с указанным email не найден.")
            return self.form_invalid(form)
        
        email_address = EmailAddress.objects.filter(email=email, verified=True).first()
        
        if email_address is None:
            messages.error(self.request, "Ваш email еще не подтвержден. Проверьте вашу почту.")
            return redirect('account_email_verification_sent')

        login(self.request, user, backend='django.contrib.auth.backends.ModelBackend')
        return super().form_valid(form)

class CustomPasswordResetView(PasswordResetView): # email сохраняется в форме даже при ошибке
    def get(self, request, *args, **kwargs):
        email = request.GET.get('email', '')
        context = self.get_context_data()
        context['email'] = email
        return self.render_to_response(context)

    def form_invalid(self, form):
        email = self.request.POST.get('email', '')
        return self.render_to_response(self.get_context_data(form=form, email=email))
    
