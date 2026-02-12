import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.calculations import calculate_top_materials, calculate_distribucion_origen

def show(df, estado_cob):
    """
    Página de Evolución Futura del Inventario - Replica la tercera vista del PBI
    Similar a Estado de Coberturas pero con proyección
    """
    st.header("📈 Evolución Futura del Inventario")
    
    if df.empty:
        st.warning("No hay datos para mostrar con los filtros seleccionados")
        return
    
    # Aplicar filtro de estado si está seleccionado
    if estado_cob != "Todas" and 'Estado_Cobertura' in df.columns:
        df = df[df['Estado_Cobertura'] == estado_cob]
        st.info(f"Proyección para: **{estado_cob}**")
    
    # Filtrar por meses futuros (marzo 2026 en adelante)
    if 'Fecha' in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df['Fecha']):
            fecha_actual = pd.Timestamp.now()
            df_futuro = df[df['Fecha'] >= fecha_actual]
            
            if df_futuro.empty:
                st.warning("No hay datos futuros disponibles. Mostrando todos los datos.")
                df_futuro = df
        else:
            df_futuro = df
    else:
        df_futuro = df
    
    # Fila 1: Material por Estado + Evolución del Inventario + Distribución por Origen
    col1, col2, col3 = st.columns([2, 3, 2])
    
    with col1:
        st.subheader("Material por Estado")
        # Proyección de estados por mes
        if 'Estado_Cobertura' in df_futuro.columns and 'Fecha' in df_futuro.columns:
            estado_mes = df_futuro.groupby(['Fecha', 'Estado_Cobertura']).size().reset_index(name='Cantidad')
            
            total_por_mes = estado_mes.groupby('Fecha')['Cantidad'].transform('sum')
            estado_mes['Porcentaje'] = (estado_mes['Cantidad'] / total_por_mes * 100).round(1)
            
            fig = px.bar(
                estado_mes,
                x='Fecha',
                y='Porcentaje',
                color='Estado_Cobertura',
                orientation='v',
                color_discrete_map={
                    'Cob < 45': '#EF5350',
                    'Cob < 90': '#FFA726',
                    'Cob > 90': '#66BB6A'
                }
            )
            
            fig.update_layout(
                barmode='stack',
                height=350,
                showlegend=False,
                yaxis=dict(range=[0, 100], title="Material")
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Evolución del Inventario (Proyección)")
        # Proyección de inventario con tendencia
        if 'Fecha' in df_futuro.columns:
            evolucion = df_futuro.groupby('Fecha').agg({
                'Inv Kg-L': 'sum' if 'Inv Kg-L' in df_futuro.columns else 'count',
                'Cob(D)': 'mean' if 'Cob(D)' in df_futuro.columns else 'count'
            }).reset_index()
            
            if pd.api.types.is_datetime64_any_dtype(evolucion['Fecha']):
                evolucion['Mes_Numero'] = evolucion['Fecha'].dt.month
                evolucion['Fecha_Str'] = evolucion['Fecha'].dt.strftime('%Y-%m')
            else:
                evolucion['Fecha_Str'] = evolucion['Fecha'].astype(str)
                evolucion['Mes_Numero'] = range(1, len(evolucion) + 1)
            
            fig = go.Figure()
            
            # Barras de inventario proyectado (rojo)
            fig.add_trace(
                go.Bar(
                    x=evolucion['Mes_Numero'],
                    y=evolucion['Inv Kg-L'],
                    name='Inventario Proyectado',
                    marker_color='#EF5350',
                    text=evolucion['Inv Kg-L'].round(0),
                    textposition='outside'
                )
            )
            
            # Línea de tendencia de cobertura
            if 'Cob(D)' in evolucion.columns:
                fig.add_trace(
                    go.Scatter(
                        x=evolucion['Mes_Numero'],
                        y=evolucion['Cob(D)'],
                        name='Cobertura Proyectada',
                        mode='lines+markers',
                        line=dict(color='#FF6B00', width=3, dash='dash'),
                        marker=dict(size=10),
                        yaxis='y2'
                    )
                )
            
            fig.update_layout(
                height=350,
                showlegend=True,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                xaxis=dict(title="Mes", tickmode='array', tickvals=evolucion['Mes_Numero'], 
                          ticktext=evolucion['Fecha_Str']),
                yaxis=dict(title="Inventario MUsd"),
                yaxis2=dict(title="Cobertura (Días)", overlaying='y', side='right'),
                hovermode='x unified'
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    with col3:
        st.subheader("Distribución por Origen")
        # Distribución proyectada por origen
        if 'Origen' in df_futuro.columns:
            distribucion = calculate_distribucion_origen(df_futuro)
            
            if not distribucion.empty:
                fig = px.bar(
                    distribucion,
                    y='Origen',
                    x='N_SKU',
                    orientation='h',
                    text='N_SKU',
                    color='Origen',
                    color_discrete_map={
                        'LAMPA': '#9E9E9E',
                        'TERCEROS': '#5C6BC0',
                        'LEA': '#42A5F5',
                        'LAMPA (M)': '#90CAF9'
                    }
                )
                
                fig.update_traces(textposition='outside')
                fig.update_layout(
                    height=350,
                    showlegend=False,
                    xaxis_title="N° SKU",
                    yaxis_title=""
                )
                
                st.plotly_chart(fig, use_container_width=True)
    
    # Fila 2: Top 15 + Planificación futura
    st.markdown("---")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        # Top 15 de mayor valor proyectado
        st.subheader("Top 15 de mayor valor (Proyección)")
        
        value_col = 'Inv (M/Usd)' if 'Inv (M/Usd)' in df_futuro.columns else 'Inv Kg-L'
        top_mayor = calculate_top_materials(df_futuro, value_col=value_col, top_n=15, ascending=False)
        
        if not top_mayor.empty:
            st.dataframe(
                top_mayor,
                use_container_width=True,
                height=300,
                hide_index=True
            )
        else:
            st.info("No hay datos disponibles")
        
        st.markdown("---")
        
        # Total proyectado
        st.subheader("Total Proyectado")
        
        if value_col in df_futuro.columns:
            total_value = df_futuro[value_col].sum()
            st.metric("Inventario Total Proyectado", f"{total_value:,.2f}")
        
        if 'FCST' in df_futuro.columns:
            total_fcst = df_futuro['FCST'].sum()
            st.metric("FCST Total Proyectado", f"{total_fcst:,.2f}")
    
    with col2:
        st.subheader("Planificación por SKU (Proyección Futura)")
        
        # Tabla detallada con proyección
        if 'Material' in df_futuro.columns and 'Fecha' in df_futuro.columns:
            columnas = ['Material', 'Fecha']
            
            # Columnas de métricas
            metricas = ['F (MKL)', 'Inv (MKL)', 'Inv (M/Usd)', 'Cob (D)', 'FCST', 'Inv Kg-L', 'Cob(D)']
            
            for metrica in metricas:
                if metrica in df_futuro.columns:
                    columnas.append(metrica)
            
            df_planif = df_futuro[columnas].copy()
            
            # Ordenar por fecha y material
            df_planif = df_planif.sort_values(['Fecha', 'Material'])
            
            # Aplicar colores según estado
            cob_col = None
            for col in ['Cob (D)', 'Cob(D)', 'Cobertura']:
                if col in df_planif.columns:
                    cob_col = col
                    break
            
            if cob_col:
                def highlight_cobertura(val):
                    if pd.isna(val):
                        return ''
                    elif val < 45:
                        return 'background-color: #FFCDD2'
                    elif val < 90:
                        return 'background-color: #FFE082'
                    else:
                        return 'background-color: #C8E6C9'
                
                st.dataframe(
                    df_planif.head(30).style.applymap(
                        highlight_cobertura,
                        subset=[cob_col]
                    ),
                    use_container_width=True,
                    height=650
                )
            else:
                st.dataframe(
                    df_planif.head(30),
                    use_container_width=True,
                    height=650
                )
            
            # Botón de descarga
            csv = df_planif.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Descargar proyección completa",
                data=csv,
                file_name=f'proyeccion_futura_{estado_cob}.csv',
                mime='text/csv',
            )
    
    # KPIs de proyección
    st.markdown("---")
    st.subheader("📊 Resumen de Proyección")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_sku = df_futuro['Material'].nunique() if 'Material' in df_futuro.columns else 0
        st.metric("SKUs Proyectados", f"{total_sku:,}")
    
    with col2:
        if 'Estado_Cobertura' in df_futuro.columns:
            criticos = len(df_futuro[df_futuro['Estado_Cobertura'] == 'Cob < 45'])
            st.metric("SKUs Críticos Proyectados", f"{criticos:,}", delta=f"{-criticos if criticos > 0 else 0}")
    
    with col3:
        if 'Cob(D)' in df_futuro.columns:
            cob_promedio = df_futuro['Cob(D)'].mean()
            st.metric("Cobertura Promedio", f"{cob_promedio:.1f} días")
    
    with col4:
        if 'Inv Kg-L' in df_futuro.columns and 'FCST' in df_futuro.columns:
            ratio = (df_futuro['Inv Kg-L'].sum() / df_futuro['FCST'].sum()) if df_futuro['FCST'].sum() > 0 else 0
            st.metric("Ratio Inv/FCST", f"{ratio:.2f}")
