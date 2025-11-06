# app/admin.py

from django.contrib import admin
from .models import Cliente, Animal, Agendamento, PlanoSaude, Medicamento, ProcedimentoRealizado

# O comando admin.site.register() diz ao Django:
# "Ei, mostre este modelo na página de administração."

admin.site.register(Cliente)
admin.site.register(Animal)
admin.site.register(Agendamento)
admin.site.register(PlanoSaude)
admin.site.register(Medicamento)
admin.site.register(ProcedimentoRealizado)