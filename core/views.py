from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from .forms import MilestoneForm, DocumentForm, RegistrationForm, JoinProjectForm, LoginForm, ProjectForm
from .models import Project, Milestone, Document, ProjectMembership, SubTask, ProjectChangeLog
from django.utils import timezone

class HomeView(View):
    def get(self, request):
        return render(request, 'core/home.html')


class RegistrationView(View):
    def get(self, request):
        form = RegistrationForm()
        return render(request, 'core/registration/register_form.html', {'form': form})

    def post(self, request):
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
        return render(request, 'core/registration/register_form.html', {'form': form})


class LoginView(View):
    def get(self, request):
        form = LoginForm()
        return render(request, 'core/registration/login_form.html', {'form': form})

    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password']
            )
            if user:
                login(request, user)
                next_url = request.GET.get('next')
                return redirect(next_url or 'dashboard')
            form.add_error(None, "Nieprawidłowa nazwa użytkownika lub hasło")
        return render(request, 'core/registration/login_form.html', {'form': form})


class JoinProjectView(LoginRequiredMixin, View):
    def get(self, request):
        form = JoinProjectForm(user=request.user)
        return render(request, 'core/dashboard/join_project.html', {'form': form})

    def post(self, request):
        form = JoinProjectForm(request.POST, user=request.user)
        if form.is_valid():
            project = form.cleaned_data['project']
            role = form.cleaned_data['role']
            note = form.cleaned_data['note']
            if not ProjectMembership.objects.filter(user=request.user, project=project).exists():
                ProjectMembership.objects.create(
                    user=request.user,
                    project=project,
                    role=role,
                    note=note,
                    is_approved=False
                )
            return redirect('dashboard')
        return render(request, 'core/dashboard/join_project.html', {'form': form})


class CreateProjectView(LoginRequiredMixin, View):
    def get(self, request):
        form = ProjectForm()
        return render(request, "core/project/create_project.html", {"form": form})

    def post(self, request):
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.created_by = request.user
            project.save()
            ProjectMembership.objects.create(
                user=request.user,
                project=project,
                role="role",
                is_approved=False
            )
            return redirect("dashboard")
        return render(request, "core/project/create_project.html", {"form": form})



class DashboardView(LoginRequiredMixin, View):
    def get(self, request):
        user = request.user
        today = timezone.now().date()

        form = JoinProjectForm(user=user)

        user_projects = Project.objects.filter(
            id__in=ProjectMembership.objects.filter(user=user).values("project")
        )
        active_projects = user_projects.filter(is_active=True)

        project_data = []
        for project in active_projects.order_by("end_date")[:5]:
            membership = ProjectMembership.objects.filter(user=user, project=project).first()
            project_data.append({
                "project": project,
                "role": membership.role if membership else "Brak"
            })

        recent_documents = Document.objects.filter(
            project__in=user_projects
        ).order_by("-uploaded_at")[:6]

        upcoming_milestones = Milestone.objects.filter(
            project__in=user_projects,
            due_date__gte=today
        ).order_by("due_date")[:6]

        upcoming_tasks = SubTask.objects.filter(
            assigned_to=user,
            due_date__range=(today, today + timezone.timedelta(days=7)),
            status__in=["open", "in_progress"]
        ).order_by("due_date")

        recent_changelogs = ProjectChangeLog.objects.filter(
            project__in=user_projects
        ).order_by("-created_at")[:5]

        context = {
            "form": form,
            "project_count": active_projects.count(),
            "projects": project_data,
            "recent_documents": recent_documents,
            "upcoming_milestones": upcoming_milestones,
            "upcoming_tasks": upcoming_tasks,
            "recent_changelogs": recent_changelogs
        }

        return render(request, "core/dashboard/dashboard.html", context)


class MyProjectsView(LoginRequiredMixin, View):
    def get(self, request):
        user_projects = ProjectMembership.objects.filter(user=request.user).values("project")
        projects = Project.objects.filter(id__in=user_projects)
        return render(request, "core/dashboard/my_projects.html", {"projects": projects})


class ProjectDetailView(LoginRequiredMixin, View):
    def get(self, request, pk):
        project = get_object_or_404(Project, pk=pk)
        milestones = Milestone.objects.filter(project=project).order_by('due_date')
        days_remaining = (project.end_date - project.start_date)
        context = {
            'project': project,
            'milestones': milestones,
            'days_remaining': days_remaining
        }
        return render(request, 'core/project_detail.html', context)


class MilestoneCreateView(LoginRequiredMixin, View):
    def get(self, request):
        form = MilestoneForm()
        return render(request, 'core/create_milestone.html', {'form': form})

    def post(self, request):
        form = MilestoneForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('milestone_list')
        return render(request, 'core/create_milestone.html', {'form': form})

class MyTasksView(LoginRequiredMixin, View):
    def get(self, request):
        tasks = SubTask.objects.filter(assigned_to=request.user).order_by('due_date')
        return render(request, 'core/milestones/my_tasks.html', {'tasks': tasks})

class MilestoneDetailView(View):
    template_name = 'milestone_detail.html'

    def get(self, request, pk):
        milestone = get_object_or_404(Milestone, pk=pk)
        main_tasks = SubTask.objects.filter(
            milestone=milestone,
            parent__isnull=True
        ).prefetch_related('children', 'assigned_to')

        context = {
            'milestone': milestone,
            'main_tasks': main_tasks
        }
        return render(request, self.template_name, context)


class MyChangeLogView(LoginRequiredMixin, View):
    def get(self, request):
        user_projects = ProjectMembership.objects.filter(user=request.user).values('project')
        changelogs = ProjectChangeLog.objects.filter(project__in=user_projects).order_by('-created_at')
        return render(request, 'core/change_log/my_changelogs.html', {'change_log': changelogs})


class MyCalendarView(LoginRequiredMixin, View):
    def get(self, request):
        user = request.user
        today = timezone.now().date()
        user_projects = ProjectMembership.objects.filter(user=user).values("project")

        milestones = Milestone.objects.filter(
            project_id__in=user_projects,
            due_date__gte=today
        ).order_by("due_date")

        tasks = SubTask.objects.filter(
            assigned_to=user,
            due_date__gte=today
        ).order_by("due_date")

        context = {
            "milestones": milestones,
            "tasks": tasks
        }
        return render(request, 'core/calendar/my_calendar.html', context)


class DocumentCreateView(LoginRequiredMixin, View):
    def get(self, request, pk):
        form = DocumentForm()
        return render(request, 'core/document_form.html', {'form': form})

    def post(self, request, pk):
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.uploaded_by = request.user
            document.project_id = pk
            document.save()
            return redirect('project_detail', pk=pk)
        return render(request, 'core/document_form.html', {'form': form})
