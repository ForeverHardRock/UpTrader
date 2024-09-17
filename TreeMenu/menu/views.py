from django.shortcuts import render


def home_view(request):
    return render(request, 'home.html', context={'menu': ""})


def menu_view(request, menu):
    menu_name = menu.split('/')[0]
    return render(request, 'home.html', context={'menu': menu_name})
