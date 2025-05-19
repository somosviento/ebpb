"""
Script para testear las funciones de manejo de fechas.
Para ejecutar:
python tests/test_dates.py
"""
from datetime import date, timedelta
import os
import sys

# Añadir el directorio raíz al path para poder importar app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.utils.date_helpers import daterange, group_consecutive_dates, group_date_ranges_by_people

# Test 1: daterange
print("\n=== Test daterange ===")
start_date = date(2025, 5, 15)
end_date = date(2025, 5, 20)
print(f"Rango de fechas del {start_date} al {end_date}:")
dates = list(daterange(start_date, end_date))
print(f"Total de fechas: {len(dates)}")
print(f"Fechas: {[d.strftime('%Y-%m-%d') for d in dates]}")

# Test 2: Agrupar fechas consecutivas
print("\n=== Test group_consecutive_dates ===")
# Fechas consecutivas
consecutive_dates = [date(2025, 5, 15), date(2025, 5, 16), date(2025, 5, 17), date(2025, 5, 18)]
# Fechas con saltos
non_consecutive_dates = [date(2025, 5, 15), date(2025, 5, 16), date(2025, 5, 18), date(2025, 5, 19), 
                          date(2025, 5, 22), date(2025, 5, 25)]

print("Fechas consecutivas:")
ranges1 = group_consecutive_dates(consecutive_dates)
for r in ranges1:
    print(f"Del {r['start'].strftime('%Y-%m-%d')} al {r['end'].strftime('%Y-%m-%d')} - {r['days']} días")

print("\nFechas con saltos:")
ranges2 = group_consecutive_dates(non_consecutive_dates)
for r in ranges2:
    print(f"Del {r['start'].strftime('%Y-%m-%d')} al {r['end'].strftime('%Y-%m-%d')} - {r['days']} días")

# Test 3: Agrupar por cantidad de personas
print("\n=== Test group_date_ranges_by_people ===")
dates_with_people = [
    (date(2025, 5, 15), 5),
    (date(2025, 5, 16), 5),
    (date(2025, 5, 17), 5),
    (date(2025, 5, 18), 10),
    (date(2025, 5, 19), 10),
    (date(2025, 5, 22), 5),
    (date(2025, 5, 23), 5),
]

result = group_date_ranges_by_people(dates_with_people)
print("Agrupaciones por número de personas:")
for people, ranges in result.items():
    print(f"\nGrupo de {people} personas:")
    for r in ranges:
        print(f"Del {r['start'].strftime('%Y-%m-%d')} al {r['end'].strftime('%Y-%m-%d')} - {r['days']} días")

print("\nTest completado.")
