from django.db import models
from django.contrib.auth.models import User

PROJECT_TYPE_CHOICES = [
    ('IND', 'Projekt indywidualny'),
    ('GR', 'Projekt wielopodmiotowy'),
]

class Project(models.Model):
    is_active = models.BooleanField(default=True)
    internal_number = models.CharField("Nr wewnętrzny projektu", max_length=50, unique=True, default='')
    title = models.CharField(max_length=250, default='')
    description = models.TextField("Opis projektu", max_length=1000, default='')

    principal_investigator = models.ForeignKey(User, on_delete=models.PROTECT, related_name='led_projects',
                                               verbose_name="Kierownik projektu", default='')
    pi_email = models.EmailField("Email Kierownika projektu", default='')
    pi_phone = models.CharField("Telefon Kierownika projektu", max_length=20, default='')


    contact_person = models.CharField("Osoba do kontaktu", max_length=150, default='')
    contact_email = models.EmailField("Email kontaktowy", default='')
    contact_phone = models.CharField("Telefon kontaktowy", max_length=20, default='')


    project_type = models.CharField("Typ projektu", max_length=20, choices=PROJECT_TYPE_CHOICES, default='')
    project_leader = models.CharField("Lider projektu", max_length=200, default='')
    domestic_partners = models.TextField("Partnerzy krajowi", blank=True, max_length=500, default='')
    foreign_partners = models.TextField("Partnerzy zagraniczni", max_length=500, blank=True, default='')


    funding_agency = models.CharField("Instytucja finansująca", max_length=200, default='')
    call_name = models.CharField("Nazwa i edycja konkursu", max_length=150, default='')
    funding_decision_date = models.DateField("Data decyzji o finansowaniu", default=None)
    funding_number = models.CharField("Nr projektu w instytucji finansującej", max_length=100, default='')
    agreement_number = models.CharField("Numer umowy o finansowanie", max_length=100, default='')
    agreement_sign_date = models.DateField("Data podpisania umowy", default=None)
    start_date = models.DateTimeField("Data rozpoczęcia projektu", default=None)
    end_date = models.DateTimeField("Data zakończenia projektu", default=None)

    executing_unit = models.CharField("Jednostka realizująca", max_length=200)
    budget_total = models.DecimalField("Budżet całkowity", max_digits=12, decimal_places=2)

    project_support = models.ForeignKey(User, on_delete=models.PROTECT, related_name='supported_projects',
                                        verbose_name="Opiekun Projektu", default='')

    class Meta:
        ordering = ['start_date']
        verbose_name = "Projekt"
        verbose_name_plural = "Projekty"

ROLE_CHOICES = [
        ('PI', 'Kierownik projektu'),
        ('PS', 'Opiekun projektu'),
        ('CO', 'Współpracownik'),
        ('AD', 'Administrator'),
    ]

class ProjectMembership(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='project_roles', verbose_name="Użytkownik")
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='memberships', verbose_name="Projekt")
    role = models.CharField(choices=ROLE_CHOICES, max_length=2)
    assigned_at = models.DateTimeField("Data przypisania", auto_now_add=True)
    is_active = models.BooleanField("Aktywny członek zespołu", default = True)
    note = models.TextField("Notatka (np. zakres obowiązków)", blank = True, max_length = 500)

    class Meta:
        verbose_name = "Członek zespołu"
        verbose_name_plural = "Członkowie zespołu"
        unique_together = ('project', 'role', 'user')
        ordering = ['project', 'role', 'user']

    def __str__(self):
        return f"{self.user.get_full_name()} jako {self.get_role_display()} w projekcie „{self.project.title}”"


class Milestone(models.Model):
    STATUS_CHOICES = [
        ('planned', 'Zaplanowany'),
        ('in_progress', 'W trakcie'),
        ('completed', 'Zakończony'),
        ('delayed', 'Opóźniony'),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    start_date = models.DateField(null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)

    responsible = models.ManyToManyField(User, blank=True, related_name='milestones')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planned')

    def __str__(self):
        return f"{self.title} ({self.project.title})"

    class Meta:
        ordering = ['start_date']

class SubTask(models.Model):
    STATUS_CHOICES = [
        ('planned', 'Zaplanowany'),
        ('in_progress', 'W trakcie'),
        ('completed', 'Zakończony'),
        ('delayed', 'Opóźniony'),
    ]

    milestone = models.ForeignKey(Milestone, on_delete=models.CASCADE, related_name='subtasks')
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='children')

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    assigned_to = models.ManyToManyField(User, blank=True, related_name='subtasks')

    start_date = models.DateField(null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    completed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.title} ({'Zakończone' if self.completed else 'W trakcie'})"

    class Meta:
        ordering = ['due_date']

class Document(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='documents')
    name = models.CharField(max_length=200)
    file = models.FileField(upload_to='documents/')

    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.name} ({self.project.title})"

class ProjectChangeLog(models.Model):
    STATUS_CHOICES = [
        ("draft", "W przygotowaniu"),
        ("pending", "W rozpatrywaniu"),
        ("approved", "Zatwierdzony"),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.project.name} - {self.title}"

class Expenses(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    description = models.TextField(max_length=255)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateField()

