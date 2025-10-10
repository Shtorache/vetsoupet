from django import forms
from .models import Agendamento, Cliente, Animal, Profissional, PlanoSaude, Medicamento

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
            "cliente": forms.Select(attrs={"class": "form-control", "id": "id_cliente"}),
            "animal": forms.Select(attrs={"class": "form-control", "id": "id_animal"}),
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

        # 🔹 LÓGICA DE FILTRO DO Animal/ANIMAL
        # 1. Inicialmente, remove todas as opções de animal.
        self.fields['animal'].queryset = Animal.objects.none()
        self.fields['animal'].choices = [("", "Selecione um cliente primeiro")]

        cliente_id = None
        
        # 2. Tenta obter o cliente selecionado (do POST ou da instância em edição)
        if self.data and "cliente" in self.data:
            cliente_id = self.data.get("cliente")
        elif self.instance and self.instance.cliente_id:
            cliente_id = self.instance.cliente_id

        # 3. Se um cliente for encontrado, filtra os Animals.
        if cliente_id:
            self.fields['animal'].queryset = Animal.objects.filter(cliente_id=cliente_id).order_by('nome')
            
            # Se já há Animals, remove a opção de "Selecione..."
            if self.fields['animal'].queryset.exists():
                self.fields['animal'].choices = [] 

        # 🔹 LÓGICA DA RAÇA (Permanece inalterada)
        especie = None
        if self.data and "especie" in self.data:
            especie = self.data.get("especie")
        elif self.instance and self.instance.especie:
            especie = self.instance.especie

        if especie in Agendamento.RACAS_CHOICES:
            self.fields["raca"].choices = Agendamento.RACAS_CHOICES[especie]
        else:
            self.fields["raca"].choices = [("", "Selecione uma espécie primeiro")]




class EditarAgendamentoForm(forms.ModelForm):
    class Meta:
        model = Agendamento
        fields = ['status', 'observacoes']



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
        fields = ["nome", "email", "telefone", "endereco"]
        widgets = {
            "nome": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "telefone": forms.TextInput(attrs={"class": "form-control"}),
            "endereco": forms.TextInput(attrs={"class": "form-control"}),
        }


class AnimalForm(forms.ModelForm):
    especie = forms.ChoiceField(
        choices=Agendamento.ESPECIE_CHOICES,
        required=True,
        widget=forms.Select(attrs={"class": "form-control", "id": "id_especie_animal"})
    )
    raca = forms.ChoiceField(
        choices=[],
        required=False,
        widget=forms.Select(attrs={"class": "form-control", "id": "id_raca_animal"})
    )

    class Meta:
        model = Animal
        fields = ["cliente", "nome", "especie", "raca", "idade", "foto"]
        widgets = {
            "cliente": forms.HiddenInput(),
            "nome": forms.TextInput(attrs={"class": "form-control"}),
            "especie": forms.Select(attrs={"class": "form-control", "id": "id_especie_animal"}),
            "raca": forms.Select(attrs={"class": "form-control", "id": "id_raca_animal"}),
            "idade": forms.NumberInput(attrs={"class": "form-control"}),
            "foto": forms.ClearableFileInput(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # preenche opções de raça de acordo com a espécie (se houver)
        especie = None
        if self.data and "especie" in self.data:
            especie = self.data.get("especie")
        elif self.instance and getattr(self.instance, "especie", None):
            especie = self.instance.especie

        if especie in Agendamento.RACAS_CHOICES:
            self.fields["raca"].choices = Agendamento.RACAS_CHOICES[especie]
        else:
            self.fields["raca"].choices = [("", "Selecione uma espécie primeiro")]


class ProfissionalForm(forms.ModelForm):
    class Meta:
        model = Profissional
        fields = ["nome", "especialidade"]
        widgets = {
            "nome": forms.TextInput(attrs={"class": "form-control"}),
            "especialidade": forms.TextInput(attrs={"class": "form-control"}),
        }

class PlanoSaudeForm(forms.ModelForm):
    class Meta:
        model = PlanoSaude
        fields = ["cliente", "animal", "nome_plano", "descricao", "valor_mensal", "validade"]
        widgets = {
            "cliente": forms.Select(attrs={"class": "form-control", "id": "id_cliente_plano"}),
            "animal": forms.Select(attrs={"class": "form-control", "id": "id_animal_plano"}),
            "nome_plano": forms.TextInput(attrs={"class": "form-control"}),
            "descricao": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "valor_mensal": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "validade": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['animal'].queryset = Animal.objects.none()

        if 'cliente' in self.data:
            try:
                cliente_id = int(self.data.get('cliente'))
                self.fields['animal'].queryset = Animal.objects.filter(cliente_id=cliente_id)
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            self.fields['animal'].queryset = self.instance.cliente.pacientes.all()

class MedicamentoForm(forms.ModelForm):
    class Meta:
        model = Medicamento
        fields = ["nome", "fabricante", "descricao", "quantidade", "unidade", "validade", "preco"]
        widgets = {
            "nome": forms.TextInput(attrs={"class": "form-control"}),
            "fabricante": forms.TextInput(attrs={"class": "form-control"}),
            "descricao": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "quantidade": forms.NumberInput(attrs={"class": "form-control"}),
            "unidade": forms.Select(attrs={"class": "form-control"}),
            "validade": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "preco": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
        }


