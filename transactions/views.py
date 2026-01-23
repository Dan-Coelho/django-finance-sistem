from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def dashboard(request):
    """
    Simple dashboard view that serves as the main landing page after login.
    This is a placeholder that will be expanded in Sprint 4.
    """
    context = {
        'title': 'Dashboard',
    }
    return render(request, 'dashboard.html', context)
