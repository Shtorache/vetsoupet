from django.db import models
from django.contrib.auth.models import User


class Animal(models.Model):
    nome = models.CharField(max_length=100)

    def __str__(self):
        return self.nome


class TipoAtendimento(models.Model):
    nome = models.CharField(max_length=100)

    def __str__(self):
        return self.nome


class Profissional(models.Model):
    nome = models.CharField(max_length=100)
    especialidade = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.nome


class Agendamento(models.Model):
    STATUS_CHOICES = [
        ("pendente", "Pendente"),
        ("confirmado", "Confirmado"),
        ("cancelado", "Cancelado"),
        ("realizado", "Realizado"),

    ]

    PROFISSIONAL_CHOICES = [
        ("nathan", "Nathan Esnácio"),
        ("yago", "Yago Cabral"),
        ("matheus", "Matheus Corrêa"),
        ("carlos", "Carlos Alberto"),

    ]

    ESPECIE_CHOICES = [
        ("", "---------"),
        ("canino", "Canino"),
        ("felino", "Felino"),
        ("equino", "Equino"),
        ("bovino", "Bovino"),
        ("ave", "Ave"),
    ]

    ATENDIMENTO_CHOICES = [
        ("consulta", "Consulta"),
        ("ultrasonografia", "Ultrasonografia"),
        ("cirurgia", "Cirurgia"),
        ("especial", "Especial"),
    ]

    RACAS_CHOICES = {
        "canino": [
            ("labrador", "Labrador"),
            ("pastor_alemao", "Pastor Alemão"),
            ("poodle", "Poodle"),
            ("bulldog", "Bulldog"),
        ],
        "felino": [
            ("siames", "Siamês"),
            ("persa", "Persa"),
            ("maine_coon", "Maine Coon"),
            ("sphynx", "Sphynx"),
        ],
        "equino": [
            ("mangalarga", "Mangalarga"),
            ("quarto_de_milha", "Quarto de Milha"),
            ("andaluz", "Andaluz"),
        ],
        "bovino": [
            ("nelore", "Nelore"),
            ("angus", "Angus"),
            ("girolando", "Girolando"),
        ],
        "ave": [
            ("calopsita", "Calopsita"),
            ("periquito", "Periquito"),
            ("papagaio", "Papagaio"),
            ("canario", "Canário"),
        ],
    }


    cliente = models.CharField(max_length=100)
    animal = models.CharField(max_length=100)

    especie = models.CharField(max_length=100, choices=ESPECIE_CHOICES, default=None)
    raca = models.CharField(max_length=100, blank=True, null=True)
    prescricao = models.TextField(blank=True, null=True)
    relato_atendimento = models.TextField(blank=True, null=True)
    violento = models.BooleanField(default=False)
    tipo_atendimento = models.CharField(max_length=100, choices=ATENDIMENTO_CHOICES)
    profissional = models.CharField(max_length=100, choices=PROFISSIONAL_CHOICES)
    data = models.DateField()
    hora = models.TimeField()
    duracao = models.IntegerField(default=30)
    observacoes = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=[
        ("pendente", "Pendente"),
        ("confirmado", "Confirmado"),
        ("cancelado", "Cancelado"),
        ("realizado", "Realizado"),
    ], default="pendente")

    usuario = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="agendamentos"
    )

    def __str__(self):
        return f"{self.cliente} - {self.animal} ({self.data} {self.hora})"

def upload_tutor(instance, filename):
    return f"tutores/{instance.id}/{filename}"

def upload_paciente(instance, filename):
    return f"pacientes/{instance.cliente.id}/{filename}"

class Cliente(models.Model):
    nome = models.CharField(max_length=150)
    email = models.EmailField(blank=True, null=True)
    telefone = models.CharField(max_length=20, blank=True, null=True)
    endereco = models.CharField(max_length=255, blank=True, null=True)
    foto = models.ImageField(upload_to=upload_tutor, blank=True, null=True)

    def __str__(self):
        return self.nome


class Paciente(models.Model):
    cliente = models.ForeignKey(Cliente, related_name="pacientes", on_delete=models.CASCADE)
    nome = models.CharField(max_length=150)
    especie = models.CharField(max_length=50, choices=[("Cachorro", "Cachorro"), ("Gato", "Gato"), ("Outro", "Outro")])
    raca = models.CharField(max_length=100, blank=True, null=True)
    idade = models.PositiveIntegerField(blank=True, null=True)
    foto = models.ImageField(upload_to=upload_paciente, blank=True, null=True)

    def __str__(self):
        return f"{self.nome} ({self.cliente.nome})"
