from .models import ConstituentCollege
from django.contrib import admin

@admin.register(ConstituentCollege)
class ConstituentCollegeAdmin(admin.ModelAdmin):
    list_display = ('name',)
   