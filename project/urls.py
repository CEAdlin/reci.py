"""
URL configuration for project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from core import views as core_views

urlpatterns = [
    path('accounts/', include('allauth.urls')),
    path('admin/', admin.site.urls),
    path('', core_views.index, name='index'),
    path('recipes/<int:pk>/', core_views.recipe_detail, name='recipe_detail'),
    path('profile', core_views.profile, name='profile'),
    path('recipes/submit/', core_views.submit_recipe, name='submit_recipe'),
    # My recipes: edit and delete (user story #9)
    path('my-recipes/', core_views.my_recipes, name='my_recipes'),
    path('recipes/<int:pk>/edit/', core_views.edit_recipe,
         name='edit_recipe'),
    path('recipes/<int:pk>/delete/', core_views.delete_recipe,
         name='delete_recipe'),
    # Notifications Integration
    path('inbox/notifications/',
         include('notifications.urls', namespace='notifications')),
    path('inbox/', core_views.notifications_inbox, name='notifications_inbox'),

    # Incoming Recipe & Comment Systems
    path('recipes/<int:pk>/', core_views.recipe_detail, name='recipe_detail'),
    path('comments/<int:pk>/edit/', core_views.comment_edit,
         name='comment_edit'),
    path('comments/<int:pk>/delete/', core_views.comment_delete,
         name='comment_delete'),
    path('recipes/admin', core_views.recipe_admin, name='recipe_admin'),
    path('recipes/review/', core_views.recipe_review, name='recipe_review'),
    path('recipes/approve/<int:pk>', core_views.recipe_approve,
         name='recipe_approve'),
    path('recipes/reject/<int:pk>', core_views.recipe_reject,
         name='recipe_reject'),
    path('recipes/comment_review/', core_views.comment_review,
         name='comment_review'),
    path('recipes/comment_approve/<int:pk>', core_views.comment_approve,
         name='comment_approve'),
    path('recipes/comment_reject/<int:pk>', core_views.comment_reject,
         name='comment_reject'),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
     )
