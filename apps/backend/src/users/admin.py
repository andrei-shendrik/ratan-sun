from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    ordering = ('email',)
    list_display = ('email', 'first_name', 'last_name', 'is_superuser', 'is_staff', 'is_active')
    search_fields = ('email', 'first_name', 'last_name')

    # убрано поле username из всех панелей редактирования
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    # создание пользователя
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password', 'password2'),  # password2 обязателен для формы создания UserAdmin
        }),
    )
    # add_fieldsets = (
    #     (None, {
    #         'classes': ('wide',),
    #         'fields': ('email', 'password', 'first_name', 'last_name')} # , 'is_staff', 'is_active'
    #      ),
    # )

    def get_readonly_fields(self, request, obj=None):
        """
        защита от эскалации привилегий: если текущий юзер не суперпользователь, он не может менять права доступа
        """
        readonly = super().get_readonly_fields(request, obj)

        is_super = getattr(request.user, 'is_superuser', False)
        if not is_super:
            return readonly + ('is_superuser', 'is_staff', 'groups', 'user_permissions')
        return readonly

    def has_change_permission(self, request, obj=None):
        """
        staff не может редактировать профиль суперпользователя.
        """
        target_is_super = getattr(obj, 'is_superuser', False)
        current_is_super = getattr(request.user, 'is_superuser', False)

        if obj and target_is_super and not current_is_super:
            return False

        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        """
        staff не может удалить суперпользователя.
        """
        target_is_super = getattr(obj, 'is_superuser', False)
        current_is_super = getattr(request.user, 'is_superuser', False)

        if obj and target_is_super and not current_is_super:
            return False

        return super().has_delete_permission(request, obj)