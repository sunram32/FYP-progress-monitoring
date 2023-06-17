from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(User)
#admin.site.register(SupervisorManager)
admin.site.register(Supervisor)
admin.site.register(SupervisorProfile)
admin.site.register(Project)
#admin.site.register(StudentManager)
admin.site.register(Student)
admin.site.register(StudentProfile)
admin.site.register(MeetingRecord)
admin.site.register(Task)
admin.site.register(Resource)
admin.site.register(Subtask)
admin.site.register(TaskMessage)
admin.site.register(ResourceMessage)
admin.site.register(Notification)