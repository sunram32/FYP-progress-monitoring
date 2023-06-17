from django.contrib import admin
from django.urls import path, include
from . import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('', views.index, name="index"),
    path('login', views.login_view, name="login"),
    path('logout', views.logout_handler, name="logout"),
    path('home', views.home, name="home"),
    path('projects', views.projects, name="projects"),
    path('notifications' ,views.notifications, name="notifications"),
    path('project/<int:project_id>', views.project, name="project"),
    path('project/<int:project_id>/tasks', views.tasks, name="tasks"),
    path('project/tasks/add_task', views.add_task, name="add_task"),
    path('project/tasks/add_subtask', views.add_subtask, name="add_task"),
    path('project/tasks/toggle_task_completion', views.toggle_task_completion, name="toggle_task_completion"),
    path('project/tasks/toggle_subtask_completion', views.toggle_subtask_completion, name="toggle_subtask_completion"),
    path('project/tasks/send_message', views.send_task_message, name="send_task_message"),
    path('project/<int:project_id>/gantt', views.gantt, name="gantt"),
    path('project/<int:project_id>/meeting_records', views.meeting_records, name="meeting_records"),
    path('project/<int:project_id>/meeting_records/<int:meeting_record_id>', views.view_edit_meeting_records, name="view_edit_meeting_records"),
    path('api/approve_meeting_record/<int:project_id>', views.approve_meeting_record, name="approve_meeting_record"),
    path('api/reject_meeting_record/<int:project_id>', views.reject_meeting_record, name="reject_meeting_record"),
    path('project/<int:project_id>/meeting_records/add', views.add_meeting_record, name="add_meeting_record"),
    path('project/<int:project_id>/resources', views.resources, name="resources"),
    path('project/resources/add_resource', views.add_resource, name="add_resource"),
    path('project/resources/send_message', views.send_resource_message, name="send_resource_message"),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)