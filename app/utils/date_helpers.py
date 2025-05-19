"""
Utilidades para el manejo de fechas en la aplicación.
"""
from datetime import timedelta, date
from typing import List, Dict, Any, Iterator, Tuple

def daterange(start_date: date, end_date: date) -> Iterator[date]:
    """
    Genera un rango de fechas entre start_date y end_date, ambos inclusive.
    
    Args:
        start_date (date): Fecha de inicio
        end_date (date): Fecha final
        
    Yields:
        date: Cada fecha en el rango
    """
    # Incluir el día final en el rango (+1)
    for n in range(int((end_date - start_date).days) + 1):
        yield start_date + timedelta(n)

def group_consecutive_dates(dates: List[date]) -> List[Dict[str, Any]]:
    """
    Agrupa fechas consecutivas en rangos.
    
    Args:
        dates (List[date]): Lista de fechas a agrupar
        
    Returns:
        List[Dict[str, Any]]: Lista de diccionarios con fechas de inicio,
                              fin y cantidad de días para cada rango
    """
    if not dates:
        return []
    
    # Ordenar las fechas
    sorted_dates = sorted(dates)
    ranges = []
    
    # Inicializar el primer rango
    current_range = {
        'start': sorted_dates[0],
        'end': sorted_dates[0],
        'days': 1
    }
    
    # Agrupar fechas consecutivas
    for i in range(1, len(sorted_dates)):
        current_date = sorted_dates[i]
        prev_date = sorted_dates[i-1]
        
        # Si es el día siguiente, extender el rango actual
        if (current_date - prev_date).days == 1:
            current_range['end'] = current_date
            current_range['days'] += 1
        else:
            # Si hay un salto, guardar el rango actual y comenzar uno nuevo
            ranges.append(current_range)
            current_range = {
                'start': current_date,
                'end': current_date,
                'days': 1
            }
    
    # Añadir el último rango
    ranges.append(current_range)
    
    return ranges

def group_date_ranges_by_people(dates_with_people: List[Tuple[date, int]]) -> Dict[int, List[Dict[str, Any]]]:
    """
    Agrupa fechas por cantidad de personas y luego las agrupa en rangos consecutivos.
    
    Args:
        dates_with_people (List[Tuple[date, int]]): Lista de tuplas (fecha, personas)
        
    Returns:
        Dict[int, List[Dict[str, Any]]]: Diccionario donde las claves son la cantidad de personas
                                       y los valores son listas de rangos de fechas
    """
    # Agrupar por cantidad de personas
    people_groups = {}
    for date_obj, people in dates_with_people:
        if people not in people_groups:
            people_groups[people] = []
        people_groups[people].append(date_obj)
    
    # Para cada grupo de personas, agrupar fechas consecutivas
    result = {}
    for people, dates in people_groups.items():
        result[people] = group_consecutive_dates(dates)
    
    return result
