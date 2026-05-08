from django.shortcuts import render


def home(request):
    context = {
        'title': 'Головна сторінка',
        'text': 'Це головна сторінка мого Django-проєкту.',
        'links': [
            {
                'name': 'Про сайт',
                'url_name': 'about',
            },
            {
                'name': 'Контакти',
                'url_name': 'contacts',
            },
        ],
        'show_home_link': False,
    }

    return render(request, 'pages/page.html', context)


def about(request):
    context = {
        'title': 'Про сайт',
        'text': 'Це сторінка з інформацією про мій сайт.',
        'links': [],
        'show_home_link': True,
    }

    return render(request, 'pages/page.html', context)


def contacts(request):
    context = {
        'title': 'Контакти',
        'text': 'Це сторінка контактів. Тут може бути email, телефон або інша інформація.',
        'links': [],
        'show_home_link': True,
    }

    return render(request, 'pages/page.html', context)