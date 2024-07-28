from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.urls import path
from django.shortcuts import render
from django.contrib.auth.models import User

from github_app.models import Repository


# Register your models here.
class CustomUserAdmin(UserAdmin) :
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_active', 'is_staff', 'is_superuser')
    list_filter = ('is_active', 'is_staff', 'is_superuser')
    search_fields = ('username', 'email', 'first_name', 'last_name')


# Unregister the default UserAdmin
admin.site.unregister(User)

# Register the custom UserAdmin
admin.site.register(User, CustomUserAdmin)


class CustomAdminSite(admin.AdminSite) :
    site_header = 'Custom Admin Dashboard'
    site_title = 'Admin Dashboard'
    index_title = 'Welcome to Custom Admin Dashboard'

    def get_urls(self) :
        urls = super().get_urls()
        custom_urls = [
            path('dashboard/', self.admin_view(self.dashboard_view))
        ]
        return custom_urls + urls

    def dashboard_view(self, request) :
        users_count = User.objects.count()
        active_users_count = User.objects.filter(is_active=True).count()
        staff_users_count = User.objects.filter(is_staff=True).count()
        superuser_count = User.objects.filter(is_superuser=True).count()

        context = dict(
            self.each_context(request),
            users_count=users_count,
            active_users_count=active_users_count,
            staff_users_count=staff_users_count,
            superuser_count=superuser_count,
            user_details=User.objects.all(),
        )
        return render(request, 'admin/index.html', context)


custom_admin_site = CustomAdminSite(name='custom_admin')

# Register your models with the custom admin site
custom_admin_site.register(User, CustomUserAdmin)
