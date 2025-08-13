from datetime import date

from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

PROJECT_TYPE_CHOICES = [
    ('IND', 'Projekt indywidualny'),
    ('GR', 'Projekt wielopodmiotowy'),
]

class Project(models.Model):
    is_active = models.BooleanField(default=True, verbose_name='Projekt aktywny?')
    internal_number = models.CharField("Nr wewnętrzny projektu", max_length=50, unique=True)
    title = models.CharField(max_length=250)
    description = models.TextField("Opis projektu", max_length=1000)

    principal_investigator = models.ForeignKey(User, on_delete=models.PROTECT, related_name='led_projects',
                                               verbose_name="Kierownik projektu")
    pi_email = models.EmailField("Email Kierownika projektu")
    pi_phone = models.CharField("Telefon Kierownika projektu", max_length=20)


    contact_person = models.CharField("Osoba do kontaktu", max_length=150, null=True, blank=True)
    contact_email = models.EmailField("Email kontaktowy", null=True, blank=True)
    contact_phone = models.CharField("Telefon kontaktowy", null=True, blank=True)

    project_type = models.CharField("Typ projektu", max_length=20, choices=PROJECT_TYPE_CHOICES)
    project_leader = models.CharField("Lider projektu", max_length=200, null=True, blank=True)
    domestic_partners = models.TextField("Partnerzy krajowi", max_length=500, null=True, blank=True)
    foreign_partners = models.TextField("Partnerzy zagraniczni", max_length=500, null=True, blank=True)


    funding_agency = models.CharField("Instytucja finansująca", max_length=200)
    call_name = models.CharField("Nazwa i edycja konkursu", max_length=150)
    funding_decision_date = models.DateField("Data decyzji o finansowaniu")
    funding_number = models.CharField("Nr projektu w instytucji finansującej", max_length=100)
    agreement_number = models.CharField("Numer umowy o finansowanie", max_length=100, default='')
    agreement_sign_date = models.DateField("Data podpisania umowy")
    start_date = models.DateField("Data rozpoczęcia projektu")
    end_date = models.DateField("Data zakończenia projektu")

    executing_unit = models.CharField("Jednostka realizująca", max_length=200)
    budget_total = models.DecimalField("Budżet całkowity", max_digits=12, decimal_places=2)

    project_support = models.ForeignKey(User, on_delete=models.PROTECT, related_name='supported_projects',
                                        verbose_name="Opiekun Projektu")

    def __str__(self):
        return f"Projekt: {self.title} ({self.internal_number})"

    def clean(self):
        super().clean()

        if self.contact_person:
            if not self.contact_email:
                raise ValidationError({'contact_email': 'Podaj Email kontaktowy, jeśli wskazano osobę do kontaktu'})
            if not self.contact_phone:
                raise ValidationError({'contact_phone': 'Podaj telefon kontaktowy, jeśli wskazano osobę do kontaktu'})

        if self.project_type == 'GR':
            errors = {}

            if not self.project_leader:
                errors['project_leader'] = 'Wymagane dla projektów wielopodmiotowych.'
            if not self.domestic_partners and not self.foreign_partners:
                errors['domestic_partners'] = 'Należy uzupełnić partnerów kajrowych lub partnerów zagranicznych dla projektu wielopodmiotowego'
                errors['foreign_partners'] = 'Należy uzupełnić partnerów kajrowych lub partnerów zagranicznych dla projektu wielopodmiotowego'

        if self.funding_decision_date and self.agreement_sign_date:
            if self.funding_decision_date > self.agreement_sign_date:
                raise ValidationError({
                    'funding_decision_date': "Data decyzji o finansowaniu nie może być późniejsza niż data podpisania umowy.",
                    'agreement_sign_date': "Data podpisania umowy nie może być wcześniejsza niż decyzja o finansowaniu."})

        if self.start_date and self.funding_decision_date:
            if self.start_date < self.funding_decision_date:
                errors['start_date'] = "Projekt nie może rozpocząć się przed decyzją o finansowaniu."
                errors['funding_decision_date'] = "Decyzja musi poprzedzać rozpoczęcie projektu."

        if self.start_date and self.end_date:
            if self.start_date > self.end_date:
                errors['start_date'] = "Data rozpoczęcia nie może być późniejsza niż data zakończenia."
                errors['end_date'] = "Data zakończenia nie może być wcześniejsza niż data rozpoczęcia."

        if errors:
            raise ValidationError(errors)

    def get_status(self):
        today = date.today()
        if today < self.start_date:
            return "Nie rozpoczęty"
        elif self.start_date <= today <= self.end_date:
            return "Projekt w trakcie"
        else:
            return "Projekt zakończony"

    def get_days_remaining(self):
        today = date.today()
        if self.end_date < today:
            return "Koniec projektu"
        return (self.end_date - today).days

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

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='milestones')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    start_date = models.DateField(null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)

    responsible = models.ManyToManyField(User, blank=True)
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
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="planned")
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

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='changelogs')
    title = models.CharField(max_length=255)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.project.title} - {self.title}"

class Expenses(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='expenses')
    description = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateField()

    def __str__(self):
        return f"Wydatek: {self.amount} PLN na „{self.project.title}” ({self.date})"
