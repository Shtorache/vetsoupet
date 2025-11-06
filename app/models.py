from django.db import models
from django.contrib.auth.models import User


class Cliente(models.Model):
    nome = models.CharField(max_length=150)
    email = models.EmailField(blank=True, null=True)
    telefone = models.CharField(max_length=20, blank=True, null=True)
    endereco = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.nome

def upload_tutor(instance, filename):
    return f"tutores/{instance.id}/{filename}"

def upload_paciente(instance, filename):
    cliente_id = instance.cliente.pk if hasattr(instance, 'cliente') and instance.cliente else 'temp_upload'
    return f"pacientes/{cliente_id}/{filename}"


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

    cliente = models.ForeignKey('Cliente', on_delete=models.PROTECT, related_name="agendamentos_cliente")
    animal = models.ForeignKey('Animal', on_delete=models.PROTECT, related_name="agendamentos_paciente")

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

    # --- CAMPO NOVO ADICIONADO ABAIXO ---
    valor_total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Valor Total")

    def __str__(self):
        return f"{self.cliente.nome} - {self.animal.nome} ({self.data} {self.hora})"

# --- NOVO MODELO ADICIONADO ABAIXO ---
class ProcedimentoRealizado(models.Model):
    agendamento = models.ForeignKey(
        Agendamento, 
        on_delete=models.CASCADE, 
        related_name='procedimentos'
    )
    codigo = models.CharField(max_length=50, blank=True, null=True, verbose_name="Código")
    procedimento_descricao = models.CharField(max_length=255, verbose_name="Descrição do Procedimento")
    valor = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valor (R$)")

    def __str__(self):
        return f"{self.procedimento_descricao} (R$ {self.valor})"
        
class Animal(models.Model):
    cliente = models.ForeignKey(Cliente, related_name="pacientes", on_delete=models.CASCADE)
    nome = models.CharField(max_length=150)
    especie = models.CharField(max_length=50, choices=Agendamento.ESPECIE_CHOICES) 
    raca = models.CharField(max_length=100, blank=True, null=True)
    idade = models.PositiveIntegerField(blank=True, null=True)
    foto = models.ImageField(upload_to=upload_paciente, blank=True, null=True)
    
    # Adicionei esses campos para corresponder ao relatório que você quer gerar
    peso = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True, verbose_name="Peso (kg)")
    sexo = models.CharField(max_length=10, choices=[('macho', 'Macho'), ('femea', 'Fêmea')], blank=True, null=True)

    def __str__(self):
        return f"{self.nome} ({self.cliente.nome})"

class PlanoSaude(models.Model):
    nome_plano = models.CharField(max_length=100)
    descricao = models.TextField(blank=True, null=True)
    valor_mensal = models.DecimalField(max_digits=8, decimal_places=2)
    validade = models.DateField()
    cliente = models.ForeignKey('Cliente', on_delete=models.CASCADE, related_name="planos_cliente")
    animal = models.ForeignKey('Animal', on_delete=models.CASCADE, related_name="plano_saude")
    cobertura = models.TextField(blank=True, null=True) 
    ativo = models.BooleanField(default=True) 

    def __str__(self):
        return f"{self.nome_plano} - {self.animal.nome}"

class Medicamento(models.Model):
    nome = models.CharField(max_length=150)
    fabricante = models.CharField(max_length=150, blank=True, null=True)
    descricao = models.TextField(blank=True, null=True)
    quantidade = models.PositiveIntegerField(default=0)
    unidade = models.CharField(max_length=20, choices=[
        ('comprimidos', 'Comprimidos'),
        ('ml', 'Mililitros'),
        ('g', 'Gramas'),
        ('outro', 'Outro')
    ], default='comprimidos')
    validade = models.DateField(blank=True, null=True)
    preco = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    data_cadastro = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.nome} ({self.quantidade} {self.unidade})"

class MedicamentoUsado(models.Model):
    agendamento = models.ForeignKey(
        Agendamento,
        on_delete=models.CASCADE,
        related_name="medicamentos_usados"
    )
    medicamento = models.ForeignKey(
        Medicamento,
        on_delete=models.PROTECT,
        related_name="usos"
    )
    quantidade_usada = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.medicamento.nome} - {self.quantidade_usada} usada(s)"
