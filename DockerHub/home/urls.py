from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name="home"),
    path('projects/', views.my_projects, name="projects"),
    path('projects/<uuid:project_id>/', views.project_display, name="project_display"),
    path('project/<uuid:project_id>/edit/', views.edit_project, name='edit_project'),
    path('project/<uuid:project_id>/delete/', views.delete_project, name='delete_project'),
    path('project/<uuid:project_id>/run/', views.run_container, name='run_container'),
    path('project/<uuid:project_id>/stop/', views.stop_container, name='stop_container'),
    path('project/<uuid:project_id>/send/', views.send_file, name='send_file'),
]
