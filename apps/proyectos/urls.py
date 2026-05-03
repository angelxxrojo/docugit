from django.urls import path

from . import views

app_name = 'proyectos'

urlpatterns = [
    path('', views.ProyectoListView.as_view(), name='proyecto_list'),
    path('nuevo/', views.ProyectoCreateView.as_view(), name='proyecto_create'),
    path('<int:pk>/', views.ProyectoDetailView.as_view(), name='proyecto_detail'),
    path('<int:pk>/editar/', views.ProyectoUpdateView.as_view(), name='proyecto_update'),
    path('<int:pk>/eliminar/', views.ProyectoDeleteView.as_view(), name='proyecto_delete'),
    path('<int:pk>/estado/', views.ProyectoEstadoView.as_view(), name='proyecto_estado'),
    path('<int:pk>/contrato/', views.ProyectoContratoView.as_view(), name='proyecto_contrato'),
    path('<int:pk>/gantt-pdf/', views.ProyectoGanttPDFView.as_view(), name='proyecto_gantt_pdf'),
    path('<int:pk>/gantt-pdf/descargar/', views.ProyectoGanttPDFDownloadView.as_view(), name='proyecto_gantt_pdf_download'),
    # Desde proforma (HU13)
    path('desde-proforma/<int:proforma_pk>/', views.ProyectoFromProformaView.as_view(), name='desde_proforma'),
    # Técnicos (HTMX)
    path('<int:proyecto_pk>/tecnicos/', views.TecnicoCreateView.as_view(), name='tecnico_create'),
    path('<int:proyecto_pk>/tecnicos/<int:asig_pk>/eliminar/', views.TecnicoDeleteView.as_view(), name='tecnico_delete'),
    # Documentos (HTMX)
    path('<int:proyecto_pk>/documentos/', views.DocumentoCreateView.as_view(), name='documento_create'),
    path('<int:proyecto_pk>/documentos/<int:doc_pk>/eliminar/', views.DocumentoDeleteView.as_view(), name='documento_delete'),
    # HTMX helpers
    path('htmx/contactos/', views.ContactosByEmpresaView.as_view(), name='htmx_contactos'),
    path('htmx/proforma/', views.ProformaDataView.as_view(), name='htmx_proforma'),

    # Kanban — Actividades
    path('<int:proyecto_pk>/actividades/', views.ActividadCreateView.as_view(), name='actividad_create'),
    path('<int:proyecto_pk>/actividades/<int:pk>/', views.ActividadUpdateView.as_view(), name='actividad_update'),
    path('<int:proyecto_pk>/actividades/<int:pk>/eliminar/', views.ActividadDeleteView.as_view(), name='actividad_delete'),
    path('<int:proyecto_pk>/actividades/<int:pk>/mover/', views.ActividadMoverView.as_view(), name='actividad_mover'),
    path('<int:proyecto_pk>/actividades/<int:actividad_pk>/comentarios/', views.ComentarioCreateView.as_view(), name='comentario_create'),
    # Columnas Kanban
    path('<int:proyecto_pk>/columnas/', views.ColumnaKanbanCreateView.as_view(), name='columna_create'),
    path('<int:proyecto_pk>/columnas/<int:pk>/eliminar/', views.ColumnaKanbanDeleteView.as_view(), name='columna_delete'),
    # Gantt (Fase 2)
    path('<int:proyecto_pk>/gantt/', views.GanttDataView.as_view(), name='gantt_data'),
    path('<int:proyecto_pk>/actividades/<int:pk>/fechas/', views.ActividadFechasView.as_view(), name='actividad_fechas'),
    # Registro de tiempo (Fase 2)
    path('<int:proyecto_pk>/actividades/<int:actividad_pk>/tiempo/', views.RegistroTiempoCreateView.as_view(), name='tiempo_create'),
    path('<int:proyecto_pk>/actividades/<int:actividad_pk>/tiempo/<int:pk>/eliminar/', views.RegistroTiempoDeleteView.as_view(), name='tiempo_delete'),
]
