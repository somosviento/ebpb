# Guía de Estilos - Formulario de Reservas EBPB

Este documento proporciona una descripción detallada de los estilos utilizados en el sistema de formularios de reservas para la Estación Biológica Puerto Blest (EBPB).

## Índice

1. [Configuración General](#configuración-general)
2. [Framework y Dependencias](#framework-y-dependencias)
3. [Tipografía](#tipografía)
4. [Colores](#colores)
5. [Componentes de Formulario](#componentes-de-formulario)
   - [Secciones del Formulario](#secciones-del-formulario)
   - [Campos de Entrada](#campos-de-entrada)
   - [Botones](#botones)
   - [Entradas Especiales](#entradas-especiales)
6. [Tarjetas y Contenedores](#tarjetas-y-contenedores)
7. [Navegación](#navegación)
8. [Alertas y Mensajes](#alertas-y-mensajes)
9. [Efectos y Animaciones](#efectos-y-animaciones)
10. [Diseño Responsivo](#diseño-responsivo)

## Configuración General

El diseño sigue un enfoque minimalista, limpio y moderno con énfasis en la usabilidad.

```css
body {
    font-family: 'Inter', 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif;
    background-color: #fff;
    color: #555;
    line-height: 1.4;
    font-size: 0.85rem;
}
```

## Framework y Dependencias

El sistema utiliza las siguientes bibliotecas de CSS y JavaScript:

1. **Bootstrap 5.3.0**
   - Framework principal de CSS para la estructura y componentes básicos
   - CDN: `https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css`

2. **Bootstrap Icons 1.8.0**
   - Set de iconos vectoriales
   - CDN: `https://cdn.jsdelivr.net/npm/bootstrap-icons@1.8.0/font/bootstrap-icons.css`

3. **Fuente Inter**
   - Tipografía principal
   - CDN: `https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap`

4. **Flatpickr**
   - Para los selectores de fecha
   - CDN: `https://cdn.jsdelivr.net/npm/flatpickr/dist/flatpickr.min.css`

5. **jQuery 3.6.0**
   - Usado para manipulaciones DOM y AJAX
   - CDN: `https://code.jquery.com/jquery-3.6.0.min.js`

## Tipografía

La aplicación utiliza principalmente la fuente Inter con varias alternativas:

```css
h1, h2, h3, h4, h5, h6 {
    letter-spacing: -0.01em;
    color: #444;
    font-weight: 500;
}

h1 { font-size: 1.6rem; }
h2 { font-size: 1.4rem; }
h3 { font-size: 1.25rem; }
h4 { font-size: 1.1rem; }
h5 { font-size: 0.95rem; }
h6 { font-size: 0.85rem; }

.text-muted {
    color: #888 !important;
    font-size: 0.8rem;
}
```

## Colores

La paleta de colores principal incluye:

### Colores Primarios
- **Azul primario**: `#4285f4` (Usado en botones, enlaces y elementos destacados)
- **Azul hover**: `#3b78e7` (Estado hover para elementos azules)

### Colores de Fondo
- **Blanco**: `#fff` (Fondo principal)
- **Gris claro**: `#f8f9fa` (Fondo de campos de formulario y tarjetas)
- **Gris más claro**: `#fafafa` (Fondo de las cabeceras de tarjetas)

### Colores de Borde
- **Gris muy claro**: `#eee` (Bordes de tarjetas y separadores)
- **Gris claro**: `#ddd` (Bordes en estado hover)

### Colores de Texto
- **Gris oscuro**: `#555` (Texto principal)
- **Gris medio**: `#888` (Texto secundario/muted)
- **Gris oscuro para títulos**: `#444` (Títulos)

### Colores de Estado
- **Verde**: `#34a853` (Éxito/mensajes positivos)
- **Rojo**: `#ea4335` (Error/alertas)
- **Amarillo**: `#fbbc05` (Advertencias)
- **Azul claro**: `#4fc3f7` (Información)

## Componentes de Formulario

### Secciones del Formulario

Las secciones del formulario tienen un estilo distintivo:

```css
.form-section {
    margin-bottom: 2rem;
    padding-bottom: 1.5rem;
    border-bottom: 1px solid #f0f0f0;
}

.form-section:last-child {
    border-bottom: none;
    padding-bottom: 0;
}

.form-section-title {
    display: flex;
    align-items: center;
    margin-bottom: 1.2rem;
    padding-bottom: 0.5rem;
    border-bottom: 2px solid rgba(66, 133, 244, 0.1);
    color: #4285f4;
    font-weight: 500;
    font-size: 1.1rem;
}

.form-section-title i {
    margin-right: 0.6rem;
    opacity: 0.8;
}
```

### Campos de Entrada

Los campos de entrada tienen un estilo minimalista con efectos sutiles:

```css
.form-control, .form-select {
    font-size: 0.85rem;
    background-color: #f8f9fa;
}

.form-control:hover, .form-select:hover {
    box-shadow: 0 0 0 0.1rem rgba(66, 133, 244, 0.1);
}

.form-control:focus, .form-select:focus {
    border-color: rgba(66, 133, 244, 0.5);
    box-shadow: 0 0 0 0.15rem rgba(66, 133, 244, 0.15);
}

.form-label {
    font-size: 0.75rem;
    margin-bottom: 0.3rem;
}

.form-text {
    font-size: 0.7rem;
    color: #999;
}

.input-group-text {
    color: #607d8b;
}
```

### Botones

Los botones siguen un diseño limpio con transiciones suaves:

```css
.btn {
    border-radius: 4px;
    font-weight: 400;
    padding: 0.4rem 0.8rem;
    transition: all 0.15s ease;
    font-size: 0.8rem;
}

.btn-primary {
    background-color: #4285f4;
    border-color: #4285f4;
    box-shadow: none;
}

.btn-primary:hover {
    background-color: #3b78e7;
    border-color: #3b78e7;
    box-shadow: none;
}

.btn-outline-primary {
    color: #4285f4;
    border-color: #d6e3fa;
    background-color: transparent;
}

.btn-outline-primary:hover {
    background-color: #f4f7fd;
    border-color: #4285f4;
    color: #3b78e7;
}

.btn-danger {
    background-color: #ea4335;
    border-color: #ea4335;
    box-shadow: none;
}

.btn-danger:hover {
    background-color: #d33426;
    border-color: #d33426;
    box-shadow: none;
}
```

### Entradas Especiales

#### Campos Requeridos

Los campos obligatorios se indican con un asterisco rojo:

```css
.form-required::after {
    content: " *";
    color: #ea4335;
    font-weight: bold;
}
```

#### Entrada de Fechas

El formulario utiliza Flatpickr para los selectores de fecha:

```css
.flatpickr-day.selected {
    background-color: #0d6efd;
    border-color: #0d6efd;
}
```

#### Entradas de Participantes y Fechas

Estilos especiales para estas secciones dinámicas:

```css
.date-entry, .participant-entry {
    transition: all 0.2s ease;
    border-radius: 3px;
    border: 1px solid #eee;
    margin-bottom: 0.75rem;
    padding: 0.6rem;
}

.date-entry:hover, .participant-entry:hover {
    border-color: #ddd;
    background-color: #fafafa;
}
```

## Tarjetas y Contenedores

Las tarjetas tienen un estilo minimalista:

```css
.card {
    border: 1px solid #eee;
    border-radius: 4px;
    box-shadow: none;
    margin-bottom: 1rem;
    transition: all 0.15s ease-in-out;
}

.card:hover {
    border-color: #ddd;
}

.card-header {
    font-weight: 500;
    font-size: 0.85rem;
    border-bottom: 1px solid #eee;
    background-color: #fafafa;
    border-radius: 4px 4px 0 0 !important;
    padding: 0.6rem 0.8rem;
}

.card-header.bg-primary {
    background-color: #4285f4 !important;
    color: white;
    border-bottom: none;
}

.card-body {
    padding: 0.8rem;
}
```

## Navegación

La barra de navegación tiene un estilo limpio:

```css
.navbar {
    box-shadow: none;
    padding: 0.5rem 0.8rem;
    background-color: #607d8b !important;
    border-bottom: 1px solid #f0f0f0;
}

.navbar-brand {
    font-weight: 600;
    font-size: 1rem;
    letter-spacing: -0.2px;
    color: #c0ccd6 !important;
}

.nav-link {
    font-weight: 400;
    color: #c0ccd6;
    padding: 0.3rem 0.5rem;
    margin: 0 0.1rem;
    border-radius: 3px;
    font-size: 0.8rem;
}
```

## Alertas y Mensajes

Los mensajes de alerta y confirmación tienen estilos específicos:

```css
.alert {
    padding: 0.4rem 0.75rem;
    font-size: 0.8rem;
    border-radius: 3px;
}

.confirmation-msg {
    color: #34a853;
    font-size: 0.8rem;
    padding: 0.3rem 0;
    opacity: 0.9;
    animation: fadeIn 0.5s ease-in;
}
```

## Efectos y Animaciones

Se usan animaciones sutiles para mejorar la experiencia:

```css
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(-5px); }
    to { opacity: 0.9; transform: translateY(0); }
}

/* Transiciones suaves para todos los elementos */
.form-control, .form-select, .btn, .input-group-text,
.card, .alert, .date-entry, .participant-entry {
    transition: all 0.2s ease-in-out;
}
```

## Diseño Responsivo

El diseño es responsivo con ajustes específicos para dispositivos móviles:

```css
@media (max-width: 767.98px) {
    .btn-group {
        display: flex;
        flex-direction: column;
    }
    
    .btn-group .btn {
        margin-bottom: 0.5rem;
        border-radius: 0.25rem !important;
    }
}
```

## Estructura Específica de Formularios

### Formulario de Reserva de Cátedras
El formulario para reservas de Cátedras incluye campos específicos:
- Departamento
- Asignatura
- Lista de participantes con roles (docente/estudiante)
- Campos de cada participante:
  - Nombre y Apellido
  - DNI/Pasaporte
  - CUIL
  - Rol (docente/estudiante)
  - Email (opcional)
  - Teléfono (opcional)
  - Fecha de nacimiento (opcional)

### Formulario de Equipo de Investigación
El formulario para equipos de investigación tiene campos diferentes:
- Nombre del Proyecto
- Código del Proyecto
- Director del Proyecto
- Lista de participantes con formato específico:
  - **Campos por participante organizados en 2 columnas:**
    - Nombre y Apellido | DNI/Pasaporte
    - Institución | Cargo
    - Nacionalidad | (espacio vacío)
    - Email | Teléfono
    - Fecha de nacimiento | (espacio vacío)
  - El campo CUIL fue intencionalmente omitido para este tipo de formulario
  - El diseño de dos columnas optimiza el espacio y mejora la legibilidad

### Diferencias entre Formularios de Participantes

**Para Cátedras:**
```html
<div class="row g-3">
    <div class="col-md-6">Nombre y Apellido</div>
    <div class="col-md-6">DNI/Pasaporte</div>
    <div class="col-md-4">Rol</div>
    <div class="col-md-4">CUIL</div>
    <div class="col-md-4">Email</div>
    <div class="col-md-4">Teléfono</div>
    <div class="col-md-4">Fecha de nacimiento</div>
</div>
```

**Para Equipos de Investigación:**
```html
<div class="row g-3">
    <div class="col-md-6">Nombre y Apellido</div>
    <div class="col-md-6">DNI/Pasaporte</div>
    <div class="col-md-6">Institución</div>
    <div class="col-md-6">Cargo</div>
    <div class="col-md-6">Nacionalidad</div>
    <div class="col-md-6">(vacío para mantener 2 columnas)</div>
    <div class="col-md-6">Email</div>
    <div class="col-md-6">Teléfono</div>
    <div class="col-md-6">Fecha de nacimiento</div>
    <div class="col-md-6">(vacío para mantener 2 columnas)</div>
</div>
```

## Clases de Utilidad Personalizadas

La aplicación incluye varias clases de utilidad para espaciado y presentación:

```css
.mb-4 { margin-bottom: 1rem !important; }
.mb-3 { margin-bottom: 0.75rem !important; }
.py-3 { padding-top: 0.75rem !important; padding-bottom: 0.75rem !important; }
.py-2 { padding-top: 0.5rem !important; padding-bottom: 0.5rem !important; }
.mt-4 { margin-top: 1rem !important; }
.mt-3 { margin-top: 0.75rem !important; }
```

---

© EBPB 2025 - Documentación de Estilos
