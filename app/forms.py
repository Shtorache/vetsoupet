from django import forms
from .models import Agendamento, Cliente, Paciente, Profissional


from django import forms
from .models import Agendamento, Cliente, Paciente, Profissional


class AgendamentoForm(forms.ModelForm):
    especie = forms.ChoiceField(
        choices=Agendamento.ESPECIE_CHOICES,
        required=True,
        widget=forms.Select(attrs={"class": "form-control", "id": "id_especie"})
    )
    raca = forms.ChoiceField(
        choices=[],
        required=False,
        widget=forms.Select(attrs={"class": "form-control", "id": "id_raca"})
    )

    class Meta:
        model = Agendamento
        fields = [
            "cliente",
            "animal",
            "especie",
            "raca",
            "tipo_atendimento",
            "profissional",
            "data",
            "hora",
            "duracao",
            "observacoes",
            "status",
        ]
        widgets = {
            "cliente": forms.TextInput(attrs={"class": "form-control"}),
            "animal": forms.TextInput(attrs={"class": "form-control"}),
            "tipo_atendimento": forms.Select(attrs={"class": "form-control"}),
            "profissional": forms.Select(attrs={"class": "form-control"}),
            "data": forms.DateInput(attrs={"type": "date", "class": "form-control"}),  # 🔹 igual ao seu original
            "hora": forms.TimeInput(attrs={"type": "time", "class": "form-control"}),  # 🔹 igual ao seu original
            "duracao": forms.NumberInput(attrs={"class": "form-control", "min": "10", "step": "5"}),
            "observacoes": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "status": forms.Select(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        especie = None

        # 🔹 Pega a espécie enviada no POST (quando valida o form)
        if self.data and "especie" in self.data:
            especie = self.data.get("especie")
        # 🔹 Se for edição, usa a instância
        elif self.instance and self.instance.especie:
            especie = self.instance.especie

        # 🔹 Define os choices da raça dinamicamente
        if especie in Agendamento.RACAS_CHOICES:
            self.fields["raca"].choices = Agendamento.RACAS_CHOICES[especie]
        else:
            self.fields["raca"].choices = [("", "Selecione uma espécie primeiro")]

class AtendimentoDetalhadoForm(forms.ModelForm):
    class Meta:
        model = Agendamento
        fields = ["prescricao", "relato_atendimento", "violento"]

        widgets = {
            "prescricao": forms.Textarea(attrs={"rows": 2}),
            "relato_atendimento": forms.Textarea(attrs={"rows": 4}),
            "violento": forms.CheckboxInput(),
        }

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ["nome", "email", "telefone", "endereco", "foto"]
        widgets = {
            "nome": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "telefone": forms.TextInput(attrs={"class": "form-control"}),
            "endereco": forms.TextInput(attrs={"class": "form-control"}),
            "foto": forms.ClearableFileInput(attrs={"class": "form-control"}),
        }


class PacienteForm(forms.ModelForm):
    class Meta:
        model = Paciente
        fields = ["cliente", "nome", "especie", "raca", "idade", "foto"]
        widgets = {
            "cliente": forms.Select(attrs={"class": "form-control"}),
            "nome": forms.TextInput(attrs={"class": "form-control"}),
            "especie": forms.Select(attrs={"class": "form-control"}),
            "raca": forms.TextInput(attrs={"class": "form-control"}),
            "idade": forms.NumberInput(attrs={"class": "form-control"}),
            "foto": forms.ClearableFileInput(attrs={"class": "form-control"}),
        }


class ProfissionalForm(forms.ModelForm):
    class Meta:
        model = Profissional
        fields = ["nome", "especialidade"]
        widgets = {
            "nome": forms.TextInput(attrs={"class": "form-control"}),
            "especialidade": forms.TextInput(attrs={"class": "form-control"}),
        }
