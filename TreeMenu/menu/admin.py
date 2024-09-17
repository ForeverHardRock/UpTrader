from django.contrib import admin
from .models import Menu, MenuItem
from .forms import MenuItemForm


class MenuItemInline(admin.TabularInline):
    model = MenuItem
    extra = 1
    fields = ('title', 'url',  'parent',)
    ordering = ('title',)


@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    list_display = ('name',)
    inlines = [MenuItemInline]


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    form = MenuItemForm
    list_display = ('title', 'menu', 'parent',)
    list_filter = ('menu',)
    search_fields = ('title',)
