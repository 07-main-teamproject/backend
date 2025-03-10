from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):  # ✅ Django 기본 UserAdmin을 활용
    model = User
    list_display = ('email', 'name', 'nickname', 'is_staff', 'is_active')  # ✅ 관리자 페이지에서 보이는 필드
    search_fields = ('email', 'name', 'nickname')  # ✅ 검색 가능 필드
    ordering = ('email',)

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("개인 정보", {"fields": ("name", "nickname")}),
        ("권한", {"fields": ("is_active", "is_staff", "is_superuser")}),
    )
