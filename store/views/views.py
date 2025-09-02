from django.views.generic import ListView, DetailView
from django.conf import settings
from django.views import View
from django.http import JsonResponse
from django.shortcuts import redirect, get_object_or_404

from django.db.models import Q
from django.utils.dateparse import parse_date
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied

from django.shortcuts import render
from django.urls import reverse

import stripe

from blog.models import Category, Tag
from ..models import Book, Product, Payment
from ..utils.payment import BasePayment

from django.contrib.contenttypes.models import ContentType

from abc import ABC

# Configuracion de Stripe

stripe.api_key = settings.STRIPE_SECRET


    

