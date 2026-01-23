from django.shortcuts import render
from django.http import HttpResponse


def signup(request):
    """Simple placeholder view for signup"""
    return HttpResponse("Signup page")


def landing_page(request):
    """Simple placeholder view for landing page"""
    return HttpResponse("Landing page")
