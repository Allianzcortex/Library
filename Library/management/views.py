# -*- coding:utf-8 -*-
# 这可以说是在整个过程中最有挑战性的一部分了


from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from .forms import setPasswordForm, registrationForm, loginForm, addBookForm, addImageForm
from .utils import permission_check


def index(request):
    if request.user:
        user = request.user
    else:
        user = None

    context = {
        'user': user,
    }

    return render(request, 'management/index.html', context)


# 进行有关注册的部分
def user_register(request):
    pass


# 进行有关登陆的部分
def user_login(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect('/homepage')
    state = None

    if request.method == 'POST':
        form = loginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)

            if user:
                login(request, user)
                return HttpResponseRedirect('/homepage')
            else:
                state = 'not exist or password error'

    context = {
        'state': state,
        'user': None,
        'form': loginForm(),
    }
    return render(request, 'management/login.html', context)


@login_required()
def user_logout(request):
    logout(request)
    return HttpResponseRedirect('/homepage')


# 关于用户重新设置密码的一些问题
@login_required
def set_password(request):
    user = request.user
    state = None
    if request.method == 'POST':
        form = setPasswordForm(request.POST)
        if form.is_valid():
            old_password = form.cleaned_data.get(old_password)
            new_password = form.cleaned_data.get(new_password)
            repeat_password = form.cleaned_data.get(repeat_password)

            if user.check_password(old_password):
                if not new_password:
                    state = 'new password not exist'
                elif new_password != repeat_password:
                    state = 'not equal'
                else:
                    user.set_password(new_password)
                    user.save(commit=True)
                    state = 'success'
                # 我个人感觉这里应该？？？

            else:
                state = 'password error'

        context = {
            'state': state,
            'user': user,
        }

        return render(request, 'management/set_password.html', context)

    # 下面是关于加入图书的部分
    # 首先就是权限管理，最后再统一看

@user_passes_test(permission_check)
def add_book(request):
    user = request.user
    state = None
    if request.method == 'POST':
        form = addBookForm(request.POST)
        if form.is_valid():
            book = form.cleaned_data
            new_book = Book(
                    name=book.get('name'),
                    author=book.get('author'),
                    category=book.get('category'),
                    price=book.get('price'),
                    publish_date=book.get('publish_date'),
            )
            new_book.save()
            state = 'success'

    context = {
        'state': state,
        'user': user,
        'form': addBookForm(),
    }
    return render(request, 'management/add_book.html', context)


# 下面应该是查看关于具体的书目列表的信息
# 我觉得在这里的思路应该是非常清晰的，用 category_list来表示左边的列表目录
# 用 book_list 来表示右边的书籍目录
# 用 query_category 来表示选择要查看的 category

def view_book_list(request):
    # 所以还是没有
    user = request.user if request.user.is_authenticated() else None
    category_list = Book.objects.values_list('category', flat=True).distinct()
    query_category = request.get('category', 'all')

    if not query_category or Book.objects.filter(category=query_category).count()==0:
        query_category = 'all'
        book_list = Book.objects.all()
    else:
        book_list = Book.objects.filter(category=query_category)

    # 下面是关于搜索的情况
    if request.method == 'POST':
        keyword = request.POST.get('keyword', '')
        book_list = Book.objects.filter(name_contains=keyword)
    # 换言之，这里的 query_category 个人感觉不用也可以，只是还要在 模板文件里 看清楚

    # 关于分页，这里只能先按照它写的来，之后再看文档
    paginator = Paginator(book_list, 3)
    # 从当前页码中得到点击
    page = request.GET.page('page')
    try:
        book_list = paginator.page(page)
    except PageNotAnInteger:
        book_list = paginator.page(1)
    except EmptyPage:
        book_list = paginator.page(num_pages)
    context = {
        'user': user,
        'category_list': category_list,
        'book_list': book_list,
        'query_category': query_category,
    }
    return render(request, 'management/view_book_list.html', context)


def detail(request):
    # 获取一个书籍的详细信息
    user = request.user if request.user.is_authenticated() else None
    # 这里可以用 key ，也可以用 if
    book_id = request.get('id')
    if not book_id:
        return HttpResponseRedirect('/view_book_list')

    try:
        book = Book.objects.get(pk=book_id)
    except Book.DoesNotExist:
        return HttpResponseRedirect('/view_book_list')

    context = {
        'user': user,
        'book': book,
    }
    return render(request, 'management/detail.html', context)


# 在 add_image 之前应该还有一个权限检测
@user_passes_test(permission_check)
def add_image(request):
    user = request.user
    state = None
    if request.method == 'POST':
        form = addImageForm()
        if form.is_valid():
            try:
                cleaned_data = form.cleaned_data
                new_image = image(
                        name=cleaned_data.get('name'),
                        description=cleaned_data.get('description'),
                        image=cleaned_data.get('image'),
                        book=Book.objects.get(pk=cleaned_data.get('book')),
                )
            except Book.DoesNotExist:
                state = 'book not exist'
            else:
                state = 'success'

    context = {
        'user': user,
        'state': state,
        'book_list': Book.objects.all(),
    }

    return render(request, 'management/add_image.html', context)

# 好吧，完成基本的view,下面就是对应 url 以及模板的编写了  # Create your views here.
