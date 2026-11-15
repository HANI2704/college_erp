from django.contrib import admin
from .models import Staff, Notification, LeaveRequest, Feedback

admin.site.register(Staff)
admin.site.register(Notification)
admin.site.register(LeaveRequest)
admin.site.register(Feedback)
