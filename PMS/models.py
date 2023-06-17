from datetime import datetime
import os
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.
class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Admin"
        STUDENT = "STUDENT", "Student"
        SUPERVISOR = "SUPERVISOR", "Supervisor"

    base_role = Role.ADMIN
    role = models.CharField(max_length=50, choices=Role.choices)
    picture = models.ImageField(upload_to="PMS/file/users", default="PMS/file/users/default_dp.png")

    def save(self, *args, **kwargs):
        if not self.pk:
            self.role = self.base_role
            return super().save(*args, **kwargs)
        
class SupervisorManager(BaseUserManager):
    def get_queryset(self, *args, **kwargs):
        results = super().get_queryset(*args, **kwargs)
        return results.filter(role=User.Role.SUPERVISOR)

class Supervisor(User):
    base_role = User.Role.SUPERVISOR
    supervisor = SupervisorManager()
    class Meta:
        proxy = True

    def welcome(self):
        return "Only for Supervisors"

class SupervisorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=64)
    last_name = models.CharField(max_length=64)
    email = models.EmailField()
    supervisor_id = models.IntegerField(null=True, blank=True)
    
    def __str__(self):
        return self.user.username

@receiver(post_save, sender=Supervisor)
def create_user_profile(sender, instance, created, **kwargs):
    if created and instance.role == "SUPERVISOR":
        SupervisorProfile.objects.create(user=instance)

class Project(models.Model):
    project_title = models.CharField(max_length=128)

    def get_status(self):
        tasks = Task.objects.filter(project=self).order_by("due_date")
        if tasks.count() == 0:
            return "On Track"
        
        next_due_task = None
        for task in tasks:
            if not task.completed:
                next_due_task = task
                break
        if next_due_task is None:
            return "On Track"
        else:
            if datetime.now().date() <= next_due_task.due_date:
                return "On Track"
            elif (datetime.now().date() - next_due_task.due_date).days < 7:
                return "Slightly Behind Schedule"
            else:
                return "Grossly Behind Schedule"

    def __str__(self):
        return self.project_title

class StudentManager(BaseUserManager):
    def get_queryset(self, *args, **kwargs):
        results = super().get_queryset(*args, **kwargs)
        return results.filter(role=User.Role.STUDENT)

class Student(User):
    base_role = User.Role.STUDENT
    student = StudentManager()

    class Meta:
        proxy = True

    def welcome(self):
        return "Only for students"

@receiver(post_save, sender=Student)
def create_user_profile(sender, instance, created, **kwargs):
    if created and instance.role == "STUDENT":
        StudentProfile.objects.create(user=instance)

class StudentProfile(models.Model):
    CAPSTONE_STATUS_CHOICES = [
        ("CP1", "CP1"),
        ("CP2", "CP2"),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=64)
    last_name = models.CharField(max_length=64)
    email = models.EmailField()
    student_id = models.IntegerField(null=True, blank=True)
    capstone_status = models.CharField(max_length=3, choices=CAPSTONE_STATUS_CHOICES)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="project", null=True)
    supervisor = models.ForeignKey(SupervisorProfile, on_delete=models.CASCADE, related_name="supervisor", null=True)

    def __str__(self):
        return self.user.username

class MeetingRecord(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    date = models.DateField()
    time = models.TimeField()
    student = models.CharField(max_length=64)
    supervisor = models.CharField(max_length=64)
    updates_from_previous_meeting = models.TextField()
    items_discussed_this_meeting = models.TextField()
    work_for_coming_meeting = models.TextField()
    approved = models.BooleanField(null=True)
    reject_reason = models.TextField(null=True)

    def __str__(self):
        return f"{self.project.project_title}: {self.date}"

class Task(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    title = models.CharField(max_length=128)
    category = models.CharField(max_length=64)
    start_date = models.DateField()
    due_date = models.DateField()
    description = models.TextField()
    dependency = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE)
    completed = models.BooleanField()

    def is_overdue(self):
        return datetime.now().date() > self.due_date

    def __str__(self):
        return f"{self.project.project_title}: {self.title}"

class Resource(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, null=True)
    title = models.CharField(max_length=128)
    category = models.CharField(max_length=64)
    description = models.TextField()
    file_name = models.FileField(upload_to='PMS/file/resources/', null=True, blank=True)
    file_URL = models.URLField(max_length=256, null=True, blank=True)

    def get_file_name(self):
        return os.path.basename(self.file_name.name)

    def __str__(self):
        return f"{self.project.project_title}: {self.title}"

class Subtask(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    title = models.CharField(max_length=256)
    due_date = models.DateField()
    completed = models.BooleanField()

    def __str__(self):
        return f"{self.task.project.project_title}: {self.task.title} ({self.title})"

class TaskMessage(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    text = models.TextField()
    timestamp = models.DateTimeField()

    def __str__(self):
        return f"{self.task.project.project_title}: Message from '{self.user.username}' in '{self.task.title}'"

class ResourceMessage(models.Model):
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    text = models.TextField()
    timestamp = models.DateTimeField()

    def __str__(self):
        return f"{self.resource.project.project_title}: Message from '{self.user.username}' in {self.resource.title}"
    
class Notification(models.Model):
    class Type(models.TextChoices):
        TASK_OVERDUE = "TASK_OVERDUE", "Task Overdue"
        NEW_TASK = "NEW_TASK", "Added New Task"
        CHAT_TASK = "CHAT_TASK", "Chat In Task"
        NEW_RESOURCE = "NEW_RESOURCE", "Added New Resource"
        CHAT_RESOURCE = "CHAT_RESOURCE", "Chat In Resource"
        NEW_MEETING_RECORD = "NEW_MEETING_RECORD", "Added New Meeting Record"
        UPDATED_MEETING_RECORD = "UPDATED_MEETING_RECORD", "Updated Meeting Record Status"

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    type = models.CharField(choices=Type.choices, max_length=24)
    timestamp = models.DateTimeField(default=datetime.now)
    overdue_task = models.ForeignKey(Task, on_delete=models.CASCADE, null=True, blank=True, related_name="overdue_task")
    new_task = models.ForeignKey(Task, on_delete=models.CASCADE, null=True, blank=True, related_name="new_task")
    chat_task = models.ForeignKey(Task, on_delete=models.CASCADE, null=True, blank=True, related_name="chat_task")
    new_resource = models.ForeignKey(Resource, on_delete=models.CASCADE, null=True, blank=True, related_name="new_resource")
    chat_resource = models.ForeignKey(Resource, on_delete=models.CASCADE, null=True, blank=True, related_name="chat_resource")
    new_meeting_record = models.ForeignKey(MeetingRecord, on_delete=models.CASCADE, null=True, blank=True, related_name="new_mr")
    updated_meeting_record = models.ForeignKey(MeetingRecord, on_delete=models.CASCADE, null=True, blank=True, related_name="update_mr")

    def is_today(self):
        return self.timestamp.date() == datetime.now().date()

    def __str__(self):
        return f"{self.user}: {self.type}"