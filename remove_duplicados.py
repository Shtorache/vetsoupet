from django.db.models import Count
from app.models import Agendamento

duplicados = (
    Agendamento.objects
    .values("cliente", "animal", "data", "hora")
    .annotate(total=Count("id"))
    .filter(total__gt=1)
)

print(f"🔍 {duplicados.count()} grupos de agendamentos duplicados encontrados.\n")

total_removidos = 0

for dup in duplicados:
    registros = Agendamento.objects.filter(
        cliente=dup["cliente"],
        animal=dup["animal"],
        data=dup["data"],
        hora=dup["hora"]
    ).order_by("id")

    if registros.exists():
        manter = registros.first()
        apagar = registros.exclude(id=manter.id)
        total_removidos += apagar.delete()[0]
        print(f"✅ Mantido: {manter.id} | Removidos: {[r.id for r in apagar]}")
    else:
        print(f"⚠️ Nenhum duplicado encontrado para {dup}")

print(f"\n🧹 Total de registros removidos: {total_removidos}")
