from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.contrib.messages.views import SuccessMessageMixin
from django.core.paginator import Paginator
from django.core.signing import BadSignature
from django.db.models import Q
from django.http import HttpResponse, Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.template import loader, TemplateDoesNotExist
from django.template.loader import get_template
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, TemplateView, DeleteView
from .forms import AdvertForm, ProfileEditForm, RegisterForm, SearchForm, AdForm, AIFormSet, UserCommentForm
from .models import Advert, Category, AdvUser, Comment
from .utilites import signer


def index(request):
    ads = Advert.objects.filter(is_active=True).select_related('category')[:10]
    categories = Category.objects.all()
    paginator = Paginator(ads, 2)
    if 'page' in request.GET:
        page_num = request.GET['page']
    else:
        page_num = 1
    page = paginator.get_page(page_num)
    context = {'categories': categories, 'page': page, 'ads': page.object_list }
    return render(request, 'main/index.html', context)

def other_page(request, page):
    try:
        template = get_template('main/' + page + '.html')
    except TemplateDoesNotExist:
        raise Http404
    return HttpResponse(template.render(request=request))

def category_ads(request, pk):
    category = get_object_or_404(Category, pk=pk)
    ads = Advert.objects.filter(is_active=True, category=pk)
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        q = Q(title__icontains=keyword) | Q(content__icontains=keyword)
        ads = ads.filter(q)
    else:
        keyword = ''
    form = SearchForm(initial={'keyword': keyword})
    paginator = Paginator(ads, 2)
    if 'page' in request.GET:
        page_num = request.GET['page']
    else:
        page_num = 1
    page = paginator.get_page(page_num)
    context = {'category': category, 'page': page, 'ads': page.object_list,
               'form': form}
    return render(request, 'main/category_ads.html', context)

def ad_detail(request, category_pk, pk):
    ad = Advert.objects.get(pk=pk)
    initial = {'ad': ad.pk}
    if request.user.is_authenticated:
        initial['author'] = request.user.username
        form_class = UserCommentForm
    form = form_class(initial=initial)
    if request.method == 'POST':
        c_form = form_class(request.POST)
        if c_form.is_valid():
            c_form.save()
            messages.add_message(request, messages.SUCCESS,
                                 'Комментарий добавлен')
            return redirect(request.get_full_path_info())
        else:
            form = c_form
            messages.add_message(request, messages.WARNING,
                                 'Комментарий не добавлен')
    ais = ad.additionalimage_set.all()
    comments = Comment.objects.filter(ad=pk, is_active=True)
    context = {'ad': ad, 'ais': ais, 'comments': comments, 'form': form}
    return render(request, 'main/ad_detail.html', context)

class AdvertCreateView(CreateView):
    template_name = 'main/ad_create.html'
    form_class = AdvertForm
    success_url = reverse_lazy('board:index')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ads'] = Advert.objects.filter(category=context['category_id'])
        context['categories'] = Category.objects.all()
        context['current_category'] = Category.objects.all()
        return context
class LoginView(LoginView):
    template_name = 'main/login.html'

@login_required
def profile(request):
    ads = Advert.objects.filter(author=request.user.pk)
    context = {'ads': ads}
    return render(request, 'main/profile.html', context)

class LogoutView(LogoutView):
    pass

class ProfileEditView(SuccessMessageMixin, LoginRequiredMixin, UpdateView):
    model = AdvUser
    template_name = 'main/profile_edit.html'
    form_class = ProfileEditForm
    success_url = reverse_lazy('board:profile')
    success_message = 'Данные пользователя изменены'

    def setup(self, request, *args, **kwargs):
        self.user_id = request.user.pk
        return super().setup(request, *args, **kwargs)

    def get_object(self, queryset=None):
        if not queryset:
            queryset = self.get_queryset()
        return get_object_or_404(queryset, pk=self.user_id)

class PasswordEditView(SuccessMessageMixin, LoginRequiredMixin, PasswordChangeView):
    template_name = 'main/password_edit.html'
    success_url = reverse_lazy('board:profile')
    success_message = 'Пароль пользователя изменен'

class RegisterView(CreateView):
    model = AdvUser
    template_name = 'main/register.html'
    form_class = RegisterForm
    success_url = reverse_lazy('board:register_done')

class RegisterDoneView(TemplateView):
    template_name = 'main/register_done.html'

def user_activate(request, sign):
    try:
        username = signer.unsign(sign)
    except BadSignature:
        return render(request, 'main/activation_failed.html')
    user = get_object_or_404(AdvUser, username=username)
    if user.is_activated:
        template = 'main/activation_done_earlier.html'
    else:
        template = 'main/activation_done.html'
        user.is_active = True
        user.is_activated = True
        user.save()
    return render(request, template)

class ProfileDeleteView(SuccessMessageMixin, LoginRequiredMixin, DeleteView):
    model = AdvUser
    template_name = 'main/profile_delete.html'
    success_url = reverse_lazy('board:index')
    success_message = 'Пользователь удален'

    def setup(self, request, *args, **kwargs):
        self.user_id = request.user.pk
        return super().setup(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        logout(request)
        return super().post(request, *args, **kwargs)

    def get_object(self, queryset=None):
        if not queryset:
            queryset = self.get_queryset()
        return get_object_or_404(queryset, pk=self.user_id)

@login_required
def profile_ad_detail(request, pk):
    ad = get_object_or_404(Advert, pk=pk)
    ais = ad.additionalimage_set.all()
    comments = Comment.objects.filter(ad=pk, is_active=True)
    context = {'ad': ad, 'ais': ais, 'comments': comments}
    return render(request, 'main/profile_ad_detail.html', context)

@login_required
def profile_ad_add(request):
    if request.method == 'POST':
        form = AdForm(request.POST, request.FILES)
        if form.is_valid():
            ad = form.save()
            formset = AIFormSet(request.POST, request.FILES, instance=ad)
            if formset.is_valid():
                formset.save()
                messages.add_message(request, messages.SUCCESS,
                                     'Объявление добавлено')
                return redirect('board:profile')
    else:
        form = AdForm(initial={'author': request.user.pk})
        formset = AIFormSet()
    context = {'form': form, 'formset': formset}
    return render(request, 'main/profile_ad_add.html', context)

@login_required
def profile_ad_edit(request, pk):
    ad = get_object_or_404(Advert, pk=pk)
    if request.method == 'POST':
        form = AdvertForm(request.POST, request.FILES, instance=ad)
        if form.is_valid():
            ad = form.save()
            formset = AIFormSet(request.POST, request.FILES, instance=ad)
            if formset.is_valid():
                formset.save()
                messages.add_message(request, messages.SUCCESS,
                                     'Объявление исправлено')
                return redirect('board:profile')
    else:
        form = AdvertForm(instance=ad)
        formset = AIFormSet(instance=ad)
    context = {'form': form, 'formset': formset}
    return render(request, 'main/profile_ad_edit.html', context)

@login_required
def profile_ad_delete(request, pk):
    ad = get_object_or_404(Advert, pk=pk)
    if request.method == 'POST':
        ad.delete()
        messages.add_message(request, messages.SUCCESS, 'Объявление удалено')
        return redirect('board:profile')
    else:
        context = {'ad': ad}
        return render(request, 'main/profile_ad_delete.html', context)
