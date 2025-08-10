from django.contrib.auth.views import LogoutView
from django.urls import path
from .views import (RegistrationView, LoginView, MilestoneCreateView, ProjectDetailView, DocumentCreateView,
                    DashboardView, HomeView, JoinProjectView, MyProjectsView, MyTasksView, MyChangeLogView,
                    MyCalendarView, CreateProjectView, MilestoneDetailView)

urlpatterns =    [
    path('', HomeView.as_view(), name='home'),
    path('register/', RegistrationView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='home'), name='logout'),
    path('projects/join/', JoinProjectView.as_view(), name='join-project'),
    path('create-project/', CreateProjectView.as_view(), name='create-project'),
    path('my-projects/', MyProjectsView.as_view(), name='my-projects'),
    path('my-tasks/', MyTasksView.as_view(), name='my-tasks'),
    path('milestone/<int:pk>/', MilestoneDetailView.as_view(), name='milestone_detail'),
    path('my-changelogs/', MyChangeLogView.as_view(), name='my-changelogs'),
    path('calendar/', MyCalendarView.as_view(), name='calendar'),
    path('projects/<int:pk>/', ProjectDetailView.as_view(), name='project-detail'),
    path('milestones/new/', MilestoneCreateView.as_view(), name='milestone_create'),
    path('projects/<int:pk>/documents/add/', DocumentCreateView.as_view(), name='document-add'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    ]
