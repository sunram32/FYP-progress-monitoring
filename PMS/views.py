import random
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from PMS.forms import *
from PMS.models import *
from datetime import datetime

# utility functions
def get_user_profile(user):
    if user.role == "STUDENT":
        return StudentProfile.objects.get(user=user)
    elif user.role == "SUPERVISOR":
        return SupervisorProfile.objects.get(user=user)
    
def get_project_title(project_id):
    return Project.objects.get(id=project_id)

def remove_duplicates_from_list(list):
    list_without_duplicates = []
    for element in list:
        if element not in list_without_duplicates:
            list_without_duplicates.append(element)
    return list_without_duplicates

# Create your views here.
def index(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse("home"))
    else:
        return HttpResponseRedirect(reverse("login"))
    
def login_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse("home"))
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            # generate task overdue notifications for supervisors
            if request.user.role == "SUPERVISOR":
                supervisor_profile = SupervisorProfile.objects.get(user=user)
                student_profiles = StudentProfile.objects.filter(supervisor=supervisor_profile)
                projects = [student_profile.project for student_profile in student_profiles]
                for project in projects:
                    tasks = Task.objects.filter(project=project)
                    existing_overdue_notifications = Notification.objects.filter(type="TASK_OVERDUE", overdue_task__project=project)
                    tasks_in_existing_overdue_notifications = [notification.overdue_task for notification in existing_overdue_notifications]
                    for task in tasks:
                        if task.is_overdue() and task not in tasks_in_existing_overdue_notifications:
                            new_overdue_notification = Notification(user=request.user, type="TASK_OVERDUE", timestamp=task.due_date, overdue_task=task)
                            new_overdue_notification.save()

            return HttpResponseRedirect(reverse('home'))
        else:
            return render(request, 'PMS/login.html', {
                "failed_auth": True
            })
    else:
        logged_out = request.GET.get('logout', False)
        return render(request, "PMS/login.html", {
            "logged_out": logged_out
        })

def logout_handler(request):
    logout(request)
    return HttpResponseRedirect(reverse("login") + "?logout=true")

def home(request):
    def generate_random_icon():
        icons = ["fa-code", "fa-share-alt", "fa-pie-chart", "fa-laptop", "fa-tasks"]
        selected_icon = random.choice(icons)
        return selected_icon
    
    if not request.user.is_authenticated:
        return HttpResponse("401 Forbidden", status=401)
    
    user_profile = get_user_profile(request.user)
    if request.user.role == "SUPERVISOR":
        projects = [student.project for student in StudentProfile.objects.filter(supervisor=user_profile)]
    else:
        projects = ""

    if request.user.role == "STUDENT":
        tasks = Task.objects.filter(project=user_profile.project).order_by("due_date")
        first_four_unfinished_tasks = [task for task in tasks if not task.completed][:4]
    else:
        first_four_unfinished_tasks = ""

    notifications = Notification.objects.filter(user=request.user).order_by("-timestamp")[:4]

    return render(request, "PMS/home.html", {
        "user_profile": user_profile,
        "projects": projects,
        "first_four_unfinished_tasks": first_four_unfinished_tasks,
        "generate_random_icon": generate_random_icon,
        "notifications": notifications
    })

def projects(request):
    if not request.user.is_authenticated:
        return HttpResponse("401 Forbidden", status=401)
    if not request.user.role == "SUPERVISOR":
        return HttpResponse("403 Unauthorized", status=403)
    user_profile = get_user_profile(request.user)
    students = StudentProfile.objects.filter(supervisor=user_profile)
    return render(request, "PMS/projects.html", {
        "user_profile": user_profile,
        "students": students
    })

def notifications(request):
    if not request.user.is_authenticated:
        return HttpResponse("401 Forbidden", status=401)
    user_profile = get_user_profile(request.user)
    notification_list = Notification.objects.filter(user=request.user).order_by("-timestamp")
    return render(request, "PMS/notifications.html", {
        "user_profile": user_profile,
        "notification_list": notification_list,
    })

def project(request, project_id):
    if not request.user.is_authenticated:
        return HttpResponse("401 Forbidden", status=401)
    return HttpResponseRedirect(reverse("tasks", kwargs={"project_id": project_id}))

def tasks(request, project_id):
    if not request.user.is_authenticated:
        return HttpResponse("401 Forbidden", status=401)
    user_profile = get_user_profile(request.user)
    project_title = get_project_title(project_id)
    task_list = Task.objects.filter(project__id=project_id).order_by('due_date')
    subtask_list = Subtask.objects.filter(task__project__id=project_id)
    resource_list = Resource.objects.filter(project__id=project_id)
    message_list = TaskMessage.objects.filter(task__project__id=project_id)
    categories_with_duplicates = [task.category for task in task_list]
    categories = remove_duplicates_from_list(categories_with_duplicates)
    return render(request, "PMS/tasks.html", {
        "user_profile": user_profile,
        "project_id": project_id,
        "project_title": project_title,
        "new_task_form": NewTaskForm(),
        "task_list": task_list,
        "subtask_list": subtask_list,
        "resource_list": resource_list,
        "message_list": message_list,
        "categories": categories
    })

def add_task(request):
    if request.method == "GET":
        return HttpResponse("404 Not Found", status=404)
    else:
        project_id = request.POST.get("project_id", "")
        title = request.POST.get("title", "")
        category = request.POST.get("category", "")
        start_date = request.POST.get("start_date", "")
        due_date = request.POST.get("due_date", "")
        description = request.POST.get("description", "")
        dependency = request.POST.get("dependency", "")
        # if all required values are truthy
        if (project_id and title and category and start_date and due_date and description):
            project = Project.objects.get(id=project_id)
            if dependency:
                dependency_task = Task.objects.get(id=dependency)
            else:
                dependency_task = None
            task = Task(project=project, title=title, category=category, start_date=start_date, due_date=due_date, description=description, dependency=dependency_task, completed=False)
            task.save()
            # creating a notification for the other party
            student_profile = StudentProfile.objects.get(project=project)
            if request.user.role == "SUPERVISOR":
                student = student_profile.user
                notification = Notification(user=student, type="NEW_TASK", new_task=task)
                notification.save()
            elif request.user.role == "STUDENT":
                supervisor = student_profile.supervisor.user
                notification = Notification(user=supervisor, type="NEW_TASK", new_task=task)
                notification.save()
            return HttpResponse("Success")
        else:
            return HttpResponse("Bad request", status=400)
        
def add_subtask(request):
    if request.method == "GET":
        return HttpResponse("404 Not Found", status=404)
    else:
        task_id = request.POST.get("task_id", "")
        subtask_title = request.POST.get("subtask_title", "")
        due_date = request.POST.get("due_date", "")
        # if all values are truthy
        if (task_id and subtask_title and due_date):
            task = Task.objects.get(id=task_id)
            subtask = Subtask(task=task, title=subtask_title, due_date=due_date, completed=False)
            subtask.save()
            return HttpResponse(subtask.id)
        else:
            return HttpResponse("Bad request", status=400)
        
def toggle_task_completion(request):
    if request.method == "GET":
        return HttpResponse("404 Not Found", status=404)
    else:
        task_id = request.POST.get("task_id", "")
        # if all values are truthy
        if (task_id):
            task = Task.objects.get(id=task_id)
            task.completed = not task.completed
            task.save()
            return HttpResponse("Success")
        else:
            return HttpResponse("Bad request", status=400)
        
def toggle_subtask_completion(request):
    if request.method == "GET":
        return HttpResponse("404 Not Found", status=404)
    else:
        subtask_id = request.POST.get("subtask_id", "")
        # if value is truthy
        if (subtask_id):
            subtask = Subtask.objects.get(id=subtask_id)
            subtask.completed = not subtask.completed
            subtask.save()
            return HttpResponse("Success")
        else:
            return HttpResponse("Bad request", status=400)
        
def send_task_message(request):
    if request.method == "GET":
        return HttpResponse("404 Not Found", status=404)
    else:
        task_id = request.POST.get("task_id", "")
        task = Task.objects.get(id=task_id)
        message = request.POST.get("message", "")
        user = request.user
        timestamp = datetime.now()
        # if value is truthy
        if (task and message and user and timestamp):
            task_message = TaskMessage(task=task, user=user, text=message, timestamp=timestamp)
            task_message.save()
            student_profile = StudentProfile.objects.get(project=task.project)
            if request.user.role == "SUPERVISOR":
                student = student_profile.user
                notification = Notification(user=student, type="CHAT_TASK", chat_task=task)
                notification.save()
            elif request.user.role == "STUDENT":
                supervisor = student_profile.supervisor.user
                notification = Notification(user=supervisor, type="CHAT_TASK", chat_task=task)
                notification.save()
            return HttpResponse("Success")
        else:
            return HttpResponse("Bad request", status=400)

def gantt(request, project_id):
    if not request.user.is_authenticated:
        return HttpResponse("401 Forbidden", status=401)
    user_profile = get_user_profile(request.user)
    project_title = get_project_title(project_id)
    task_list = Task.objects.filter(project__id=project_id)
    return render(request, "PMS/gantt.html", {
        "user_profile": user_profile,
        "project_id": project_id,
        "project_title": project_title,
        "task_list": task_list
    })

def meeting_records(request, project_id):
    if not request.user.is_authenticated:
        return HttpResponse("401 Forbidden", status=401)
    submitted = request.GET.get('submitted', '')
    status_updated = request.GET.get('statusUpdate', '')
    user_profile = get_user_profile(request.user)
    project_title = get_project_title(project_id)
    meeting_record_list = MeetingRecord.objects.filter(project__id=project_id).order_by('date')
    return render(request, "PMS/meeting_records.html", {
        "submitted": submitted,
        "status_updated": status_updated,
        "user_profile": user_profile,
        "project_id": project_id,
        "project_title": project_title,
        "meeting_records": meeting_record_list
    })

def add_meeting_record(request, project_id):
    if not request.user.is_authenticated:
        return HttpResponse("401 Forbidden", status=401)
    if not request.user.role == "STUDENT":
        return HttpResponse("403 Unauthorized", status=403)
    user_profile = get_user_profile(request.user)
    project_title = get_project_title(project_id)
    
    if request.method == "POST":
        form = NewMeetingRecordForm(request.POST)
        new_meeting_record= form.save(commit=False)
        supervisor = user_profile.supervisor
        new_meeting_record.student = f"{user_profile.first_name} {user_profile.last_name}"
        new_meeting_record.supervisor = f"{supervisor.first_name} {supervisor.last_name}"
        new_meeting_record.project = user_profile.project
        new_meeting_record.save()
        # generate notification for supervisor
        student_profile = user_profile
        supervisor = student_profile.supervisor.user
        notification = Notification(user=supervisor, type="NEW_MEETING_RECORD", new_meeting_record=new_meeting_record)
        notification.save()
        return HttpResponseRedirect(reverse(meeting_records, kwargs={"project_id": project_id}) + "?submitted=True")

    return render(request, "PMS/add_view_meeting_record.html", {
        "form": NewMeetingRecordForm(),
        "user_profile": user_profile,
        "project_id": project_id,
        "project_title": project_title
    })

def view_edit_meeting_records(request, project_id, meeting_record_id):
    if not request.user.is_authenticated:
        return HttpResponse("401 Forbidden", status=401)
    user_profile = get_user_profile(request.user)
    project_title = get_project_title(project_id)
    meeting_record = MeetingRecord.objects.get(id=meeting_record_id)
    meeting_record_form = NewMeetingRecordForm(instance=meeting_record)

    if request.method == "GET":
        return render(request, "PMS/add_view_meeting_record.html", {
            "form": meeting_record_form,
            "meeting_record": meeting_record,
            "user_profile": user_profile,
            "project_id": project_id,
            "project_title": project_title
        })
    elif request.method == "POST":
        form = NewMeetingRecordForm(request.POST)
        new_meeting_record= form.save(commit=False)
        supervisor = user_profile.supervisor
        new_meeting_record.student = f"{user_profile.first_name} {user_profile.last_name}"
        new_meeting_record.supervisor = f"{supervisor.first_name} {supervisor.last_name}"
        new_meeting_record.project = user_profile.project
        new_meeting_record.save()
        meeting_record.delete()
        # generate notification for supervisor
        student_profile = user_profile
        supervisor = student_profile.supervisor.user
        notification = Notification(user=supervisor, type="NEW_MEETING_RECORD", new_meeting_record=new_meeting_record)
        notification.save()
        return HttpResponseRedirect(reverse(meeting_records, kwargs={"project_id": project_id}) + "?statusUpdate=True")

def approve_meeting_record(request, project_id):
    if request.method == "GET":
        return HttpResponse("404 not found", status=404)
    if request.user.role != "SUPERVISOR":
        # TODO: add logic to check if project is under supervisor
        return HttpResponse("401 Forbidden", status=401)
    
    meeting_record_id = request.POST.get("id", "")
    meeting_record = MeetingRecord.objects.get(id=meeting_record_id)
    meeting_record.approved = True
    meeting_record.save()
    # generate notification for students
    student = StudentProfile.objects.get(project=meeting_record.project).user
    notification = Notification(user=student, type="UPDATED_MEETING_RECORD", updated_meeting_record=meeting_record)
    notification.save()
    return HttpResponseRedirect(reverse(meeting_records, kwargs={"project_id": project_id}) + "?statusUpdate=True")

def reject_meeting_record(request, project_id):
    if request.method == "GET":
        return HttpResponse("404 not found", status=404)
    if request.user.role != "SUPERVISOR":
        # TODO: add logic to check if project is under supervisor
        return HttpResponse("401 Forbidden", status=401)
    
    meeting_record_id = request.POST.get("id", "")
    reject_reason = request.POST.get("reject_reason", "")
    meeting_record = MeetingRecord.objects.get(id=meeting_record_id)
    meeting_record.approved = False
    meeting_record.reject_reason = reject_reason
    meeting_record.save()
    # generate notification for students
    student = StudentProfile.objects.get(project=meeting_record.project).user
    notification = Notification(user=student, type="UPDATED_MEETING_RECORD", updated_meeting_record=meeting_record)
    notification.save()
    return HttpResponseRedirect(reverse(meeting_records, kwargs={"project_id": project_id}) + "?statusUpdate=True")

def resources(request, project_id):
    if not request.user.is_authenticated:
        return HttpResponse("401 Forbidden", status=401)
    user_profile = get_user_profile(request.user)
    project_title = get_project_title(project_id)
    resource_list = Resource.objects.filter(project__id=project_id)
    message_list = ResourceMessage.objects.filter(resource__project__id=project_id)
    categories_with_duplicates = [resource.category for resource in resource_list]
    categories = remove_duplicates_from_list(categories_with_duplicates)
    task_list = Task.objects.filter(project__id=project_id)
    return render(request, "PMS/resources.html", {
        "user_profile": user_profile,
        "project_id": project_id,
        "project_title": project_title,
        "resource_list": resource_list,
        "message_list": message_list,
        "categories": categories,
        "task_list": task_list,
        "new_resource_form": NewResourceForm(),
    })

def add_resource(request):
    if request.method == "GET":
        return HttpResponse("404 Not Found", status=404)
    else:
        project_id = request.POST.get("project_id", "")
        title = request.POST.get("title", "")
        category = request.POST.get("category", "")
        description = request.POST.get("description", "")
        file_name = request.FILES.get("file_name", "")
        file_URL = request.POST.get("file_URL", "")
        task_id = request.POST.get("task_id", "")
        # if all values are truthy
        if (project_id and title and category and description):
            task = Task.objects.get(id=task_id) if task_id else None
            project = Project.objects.get(id=project_id)
            resource = Resource(project=project, task=task, title=title, category=category, description=description, file_name=file_name, file_URL=file_URL)
            resource.save()
            # generate notification for other party
            student_profile = StudentProfile.objects.get(project=project)
            if request.user.role == "SUPERVISOR":
                student = student_profile.user
                notification = Notification(user=student, type="NEW_RESOURCE", new_resource=resource)
                notification.save()
            elif request.user.role == "STUDENT":
                supervisor = student_profile.supervisor.user
                notification = Notification(user=supervisor, type="NEW_RESOURCE", new_resource=resource)
                notification.save()
            return HttpResponse(resource.id)
        else:
            return HttpResponse("Bad request", status=400)
        
def send_resource_message(request):
    if request.method == "GET":
        return HttpResponse("404 Not Found", status=404)
    else:
        resource_id = request.POST.get("resource_id", "")
        resource = Resource.objects.get(id=resource_id)
        message = request.POST.get("message", "")
        user = request.user
        timestamp = datetime.now()
        # if value is truthy
        if (resource and message and user and timestamp):
            resource_message = ResourceMessage(resource=resource, user=user, text=message, timestamp=timestamp)
            resource_message.save()
            student_profile = StudentProfile.objects.get(project=resource.project)
            if request.user.role == "SUPERVISOR":
                student = student_profile.user
                notification = Notification(user=student, type="CHAT_RESOURCE", chat_resource=resource)
                notification.save()
            elif request.user.role == "STUDENT":
                supervisor = student_profile.supervisor.user
                notification = Notification(user=supervisor, type="CHAT_RESOURCE", chat_resource=resource)
                notification.save()
            return HttpResponse("Success")
        else:
            return HttpResponse("Bad request", status=400)