from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q
from django.core.paginator import Paginator

from .models import NKO, NKOMembership
from .forms import NKOForm, NKOMembershipForm


def nko_list(request):
    """Список всех НКО"""
    nko_list = NKO.objects.filter(status='approved', is_active=True)

    # Фильтрация
    city = request.GET.get('city')
    category = request.GET.get('category')
    search = request.GET.get('search')

    if city:
        nko_list = nko_list.filter(city=city)
    if category:
        nko_list = nko_list.filter(category=category)
    if search:
        nko_list = nko_list.filter(
            Q(name__icontains=search) |
            Q(description__icontains=search)
        )

    # Пагинация
    paginator = Paginator(nko_list, 12)
    page_number = request.GET.get('page')
    nkos = paginator.get_page(page_number)

    # Статистика для фильтров
    cities = NKO.objects.filter(status='approved').values_list('city', flat=True).distinct()

    context = {
        'nkos': nkos,
        'cities': cities,
        'categories': NKO.CATEGORY_CHOICES,
        'selected_city': city,
        'selected_category': category,
        'search_query': search,
    }
    return render(request, 'organizations/nko_list.html', context)


def nko_detail(request, pk):
    """Детальная страница НКО"""
    nko = get_object_or_404(NKO, pk=pk, is_active=True)

    # Получаем участников
    members = nko.memberships.filter(status='approved').select_related('user')

    # Проверяем, является ли пользователь участником
    user_membership = None
    if request.user.is_authenticated:
        try:
            user_membership = NKOMembership.objects.get(user=request.user, nko=nko)
        except NKOMembership.DoesNotExist:
            pass

    context = {
        'nko': nko,
        'members': members,
        'user_membership': user_membership,
        'member_count': members.count(),
    }
    return render(request, 'organizations/nko_detail.html', context)


@login_required
def nko_create(request):
    """Создание новой НКО"""
    if request.method == 'POST':
        form = NKOForm(request.POST, request.FILES)
        if form.is_valid():
            nko = form.save(commit=False)
            nko.owner = request.user
            nko.save()

            messages.success(request, 'НКО успешно создано! Ожидайте модерации.')
            return redirect('organizations:nko_detail', pk=nko.pk)
    else:
        form = NKOForm()

    return render(request, 'organizations/nko_form.html', {'form': form, 'action': 'create'})


@login_required
def nko_edit(request, pk):
    """Редактирование НКО"""
    nko = get_object_or_404(NKO, pk=pk, owner=request.user)

    if request.method == 'POST':
        form = NKOForm(request.POST, request.FILES, instance=nko)
        if form.is_valid():
            form.save()
            messages.success(request, 'Изменения сохранены!')
            return redirect('organizations:nko_detail', pk=nko.pk)
    else:
        form = NKOForm(instance=nko)

    return render(request, 'organizations/nko_form.html', {'form': form, 'action': 'edit', 'nko': nko})


@login_required
def nko_join(request, pk):
    """Вступление в НКО"""
    nko = get_object_or_404(NKO, pk=pk, status='approved', is_active=True)

    # Проверяем, не является ли пользователь уже участником
    if NKOMembership.objects.filter(user=request.user, nko=nko).exists():
        messages.warning(request, 'Вы уже подавали заявку в эту организацию')
        return redirect('organizations:nko_detail', pk=pk)

    if request.method == 'POST':
        form = NKOMembershipForm(request.POST)
        if form.is_valid():
            membership = form.save(commit=False)
            membership.user = request.user
            membership.nko = nko
            membership.save()

            messages.success(request, 'Заявка на вступление отправлена!')
            return redirect('organizations:nko_detail', pk=pk)
    else:
        form = NKOMembershipForm()

    return render(request, 'organizations/nko_join.html', {'form': form, 'nko': nko})


@login_required
def my_organizations(request):
    """Мои организации"""
    # Организации, где пользователь владелец
    owned_nkos = NKO.objects.filter(owner=request.user)

    # Организации, где пользователь участник
    memberships = NKOMembership.objects.filter(user=request.user).select_related('nko')

    context = {
        'owned_nkos': owned_nkos,
        'memberships': memberships,
    }
    return render(request, 'organizations/my_organizations.html', context)