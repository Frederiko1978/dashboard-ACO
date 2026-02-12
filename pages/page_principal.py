import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from utils.calculations import calculate_estado_stats, calculate_evolucion_inventario

def show(df, estado_cob):
    """
    Página principal del dashboard - Replica la primera vista del PBI
    """
    st.header("📊 Vista Principal - Planificación y Cobertura")
    
    if df.empty:
        st.warning("No hay datos para mostrar con los filtros seleccionados")
        return
    
    # Fila 1: Tabla de materiales + Material por Estados + Evolutivo Cobertura
    col1, col2, col3 = st.columns([1, 2, 3])
    
    with col1:
        st.subheader("Materiales")
        # Tabla resumida de materiales
        if 'Material' in df.columns:
            # Construir diccionario de agregación dinámicamente
            agg_dict = {}
            if 'Q' in df.columns:
                agg_dict['Q'] = 'sum'
            if 'CG' in df.columns:
                agg_dict['CG'] = 'first'
                
            # Si no hay columnas extra para agregar, solo listamos materiales únicos
            if not agg_dict:
                 materiales_summary = pd.DataFrame(df['Material'].unique(), columns=['Material'])
            else:
                 materiales_summary = df.groupby('Material').agg(agg_dict).reset_index()
            
            # Limitar a 10 registros para la vista
            st.dataframe(
                materiales_summary.head(10),
                use_container_width=True,
                height=300
            )
    
    with col2:
        st.subheader("Material por Estados")
        # Gráfico de barras 100% apiladas por mes
        if 'Estado_Cobertura' in df.columns and 'Fecha' in df.columns:
            # Agrupar por fecha y estado
            estado_mes = df.groupby(['Fecha', 'Estado_Cobertura']).size().reset_index(name='Cantidad')
            
            # Calcular porcentajes
            total_por_mes = estado_mes.groupby('Fecha')['Cantidad'].transform('sum')
            estado_mes['Porcentaje'] = (estado_mes['Cantidad'] / total_por_mes * 100).round(1)
            
            # Crear gráfico de barras apiladas
            fig = px.bar(
                estado_mes,
                x='Fecha',
                y='Porcentaje',
                color='Estado_Cobertura',
                text='Porcentaje',
                color_discrete_map={
                    'Cob < 45': '#EF5350',
                    'Cob < 90': '#FFA726',
                    'Cob > 90': '#66BB6A'
                },
                labels={'Porcentaje': '%', 'Fecha': 'Mes 2026'}
            )
            
            fig.update_traces(texttemplate='%{text:.0f}%', textposition='inside')
            fig.update_layout(
                barmode='stack',
                height=300,
                showlegend=True,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                yaxis=dict(range=[0, 100])
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No hay datos de estado de cobertura disponibles")
    
    with col3:
        st.subheader("Evolutivo Cobertura")
        # Gráfico combinado de líneas y barras
        if 'Fecha' in df.columns:
            evolucion = calculate_evolucion_inventario(df)
            
            if not evolucion.empty:
                # Crear figura con eje secundario
                fig = make_subplots(specs=[[{"secondary_y": True}]])
                
                # Barras de Despachos KL
                if 'Despachos KL' in evolucion.columns:
                    fig.add_trace(
                        go.Bar(
                            x=evolucion['Fecha'],
                            y=evolucion['Despachos KL'],
                            name='Despachos KL',
                            marker_color='#FF6B9D'
                        ),
                        secondary_y=False
                    )
                
                # Barras de FCST Act
                if 'FCST' in evolucion.columns:
                    fig.add_trace(
                        go.Bar(
                            x=evolucion['Fecha'],
                            y=evolucion['FCST'],
                            name='FCST Act',
                            marker_color='#4A90E2'
                        ),
                        secondary_y=False
                    )
                
                # Línea de Inventario
                if 'Inv Kg-L' in evolucion.columns:
                    fig.add_trace(
                        go.Scatter(
                            x=evolucion['Fecha'],
                            y=evolucion['Inv Kg-L'],
                            name='Inventario',
                            mode='lines+markers',
                            line=dict(color='#FFA726', width=3),
                            marker=dict(size=8)
                        ),
                        secondary_y=False
                    )
                
                # Calcular cobertura en días si hay datos
                if 'Inv Kg-L' in evolucion.columns and 'FCST' in evolucion.columns:
                    evolucion['Cobertura_Dias'] = (evolucion['Inv Kg-L'] / evolucion['FCST'].replace(0, 1)) * 30
                    
                    fig.add_trace(
                        go.Scatter(
                            x=evolucion['Fecha'],
                            y=evolucion['Cobertura_Dias'],
                            name='Cobertura (Días)',
                            mode='lines+markers',
                            line=dict(color='#66BB6A', width=2, dash='dash'),
                            marker=dict(size=6)
                        ),
                        secondary_y=True
                    )
                
                fig.update_xaxes(title_text="Mes")
                fig.update_yaxes(title_text="KL", secondary_y=False)
                fig.update_yaxes(title_text="Cobertura (Días)", secondary_y=True)
                
                fig.update_layout(
                    height=300,
                    showlegend=True,
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                    hovermode='x unified'
                )
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No hay datos de evolución disponibles")
    
    # Fila 2: Planificación x SKU KL
    st.markdown("---")
    st.subheader("Planificación x SKU KL")
    
    # Crear tabla detallada pivoteada por mes
    if 'Material' in df.columns and 'Fecha' in df.columns:
        # Columnas a mostrar
        columnas_base = ['Material', 'Fecha', 'FCST', 'Prod Kg-L', 'Inv Kg-L', 'Q', 'Cob(D)', 'Cobertura']
        columnas_disponibles = [col for col in columnas_base if col in df.columns]
        
        # Filtrar y preparar datos
        df_planificacion = df[columnas_disponibles].copy()
        
        # Convertir fecha a nombre de mes
        if pd.api.types.is_datetime64_any_dtype(df_planificacion['Fecha']):
            df_planificacion['Mes'] = df_planificacion['Fecha'].dt.strftime('%B %Y')
        else:
            df_planificacion['Mes'] = df_planificacion['Fecha']
        
        # Pivot para mostrar meses como columnas
        try:
            # Agrupar por Material y Mes
            metrics = ['FCST', 'Prod Kg-L', 'Inv Kg-L', 'Q', 'Cob(D)']
            available_metrics = [m for m in metrics if m in df_planificacion.columns]
            
            if available_metrics:
                df_pivot = df_planificacion.groupby(['Material', 'Mes'])[available_metrics].sum().reset_index()
                
                # Mostrar tabla con formato
                st.dataframe(
                    df_pivot.head(20),
                    use_container_width=True,
                    height=400
                )
                
                # Botón para descargar datos completos
                csv = df_pivot.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Descargar tabla completa (CSV)",
                    data=csv,
                    file_name='planificacion_sku.csv',
                    mime='text/csv',
                )
        except Exception as e:
            st.error(f"Error al crear la tabla de planificación: {str(e)}")
            st.dataframe(df_planificacion.head(20), use_container_width=True)
    else:
        st.warning("No hay suficientes datos para mostrar la planificación por SKU")
    
    # KPIs resumen
    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_sku = df['Material'].nunique() if 'Material' in df.columns else 0
        st.metric("Total SKUs", f"{total_sku:,}")
    
    with col2:
        inv_total = df['Inv Kg-L'].sum() if 'Inv Kg-L' in df.columns else 0
        st.metric("Inventario Total (KL)", f"{inv_total:,.0f}")
    
    with col3:
        fcst_total = df['FCST'].sum() if 'FCST' in df.columns else 0
        st.metric("FCST Total (KL)", f"{fcst_total:,.0f}")
    
    with col4:
        if 'Estado_Cobertura' in df.columns:
            criticos = len(df[df['Estado_Cobertura'] == 'Cob < 45'])
            pct_criticos = (criticos / len(df) * 100) if len(df) > 0 else 0
            st.metric("SKUs Críticos", f"{criticos:,} ({pct_criticos:.1f}%)")
