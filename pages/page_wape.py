import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from plotly.subplots import make_subplots
from utils.calculations import calculate_wape, calculate_wape_evolution

def show(df):
    """
    Página de WAPE (Weighted Absolute Percentage Error) - Replica la cuarta vista del PBI
    Análisis de precisión del forecast
    """
    st.header("📉 WAPE (Kg-L) - Análisis de Precisión del Forecast")
    
    if df.empty:
        st.warning("No hay datos para mostrar")
        return
    
    # Verificar que existan las columnas necesarias para WAPE
    has_fcst = 'FCST' in df.columns or 'F (MKL)' in df.columns
    has_desp = 'Despachos KL' in df.columns or 'Desp (MKL)' in df.columns
    
    if not (has_fcst and has_desp):
        st.warning("⚠️ No hay suficientes datos para calcular WAPE. Se requieren columnas de FCST y Despachos.")
        st.info("Columnas disponibles: " + ", ".join(df.columns.tolist()))
        return
    
    # Mapear columnas
    fcst_col = 'FCST' if 'FCST' in df.columns else 'F (MKL)'
    desp_col = 'Despachos KL' if 'Despachos KL' in df.columns else 'Desp (MKL)'
    
    # Fila 1: WAPE por origen + Tablas de mayores/menores WAPE
    col1, col2, col3 = st.columns([2, 2, 2])
    
    with col1:
        st.subheader("WAPE % por Origen")
        # Calcular WAPE por origen
        df_wape_origen = pd.DataFrame()
        if 'Origen' in df.columns:
            # Optimización: Usar groupby en lugar de un bucle for para mayor rendimiento
            df_wape_origen = df.groupby('Origen').agg(
                fcst_total=(fcst_col, 'sum'),
                desp_total=(desp_col, 'sum')
            ).reset_index()

            # Filtrar donde los despachos son 0 para evitar división por cero y calcular WAPE
            df_wape_origen = df_wape_origen[df_wape_origen['desp_total'] > 0].copy()
            if not df_wape_origen.empty:
                df_wape_origen['Wape_%'] = calculate_wape(df_wape_origen['fcst_total'], df_wape_origen['desp_total'])

            if not df_wape_origen.empty:
                # Gráfico de dona
                fig = px.pie(
                    df_wape_origen,
                    values='Wape_%',
                    names='Origen',
                    color='Origen',
                    color_discrete_map={
                        'LAMPA': '#9E9E9E',
                        'LAMPA (M)': '#FFA726',
                        'LEA': '#42A5F5',
                        'TERCEROS': '#AB47BC'
                    },
                    hole=0.4
                )
                
                fig.update_traces(textposition='inside', textinfo='percent+label')
                fig.update_layout(height=350, showlegend=True)
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Tabla de cálculo WAPE
                st.markdown("##### Cálculo WAPE")
                st.dataframe(
                    df_wape_origen,
                    column_config={"Wape_%": st.column_config.ProgressColumn(format="%.1f%%", min_value=0, max_value=100)},
                    use_container_width=True,
                    hide_index=True
                )
        else:
            st.info("No hay datos de origen disponibles")

    # Optimización: Calcular WAPE por material una sola vez usando groupby
    df_wape_mat = pd.DataFrame()
    if 'Material' in df.columns:
        group_cols = ['Material']
        if 'Origen' in df.columns:
            group_cols.append('Origen')

        df_wape_mat = df.groupby(group_cols).agg(
            fcst_total=(fcst_col, 'sum'),
            desp_total=(desp_col, 'sum')
        ).reset_index()

        df_wape_mat = df_wape_mat[df_wape_mat['desp_total'] > 0].copy()
        if not df_wape_mat.empty:
            df_wape_mat['Wape (%)'] = calculate_wape(df_wape_mat['fcst_total'], df_wape_mat['desp_total'])
            df_wape_mat['Dif Wape Abs(MKL)'] = (df_wape_mat['desp_total'] - df_wape_mat['fcst_total']).abs()
            # Seleccionar y reordenar columnas para mantener consistencia
            df_wape_mat = df_wape_mat[group_cols + ['Wape (%)', 'Dif Wape Abs(MKL)']]

    with col2:
        st.subheader("Mes en curso: Mayores 15")
        if not df_wape_mat.empty:
            top_15_mayor = df_wape_mat.nlargest(15, 'Wape (%)')
            st.dataframe(
                top_15_mayor, use_container_width=True, height=350, hide_index=True
            )
        else:
            st.info("No hay datos de material para calcular WAPE.")
    
    with col3:
        st.subheader("Mes en curso: Menores 15")
        # Top 15 materiales con menor WAPE (mejor precisión)
        
        if 'Material' in df.columns and not df_wape_mat.empty:
            top_15_menor = df_wape_mat.nsmallest(15, 'Wape (%)')
            
            st.dataframe(
                top_15_menor,
                use_container_width=True,
                height=350,
                hide_index=True
            )
        else:
            st.info("Sin datos")
    
    # Fila 2: Cálculo WAPE detallado + Evolución WAPE mensual
    st.markdown("---")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Cálculo WAPE")
        
        # Tabla de cálculo WAPE por fecha
        if 'Fecha' in df.columns:
            wape_mensual = calculate_wape_evolution(df, 'Fecha')
            
            if not wape_mensual.empty:
                # Formatear columnas
                wape_mensual['FCST'] = wape_mensual['FCST'].round(2)
                wape_mensual['Despachos'] = wape_mensual['Despachos'].round(2)
                wape_mensual['Dif_Wape_Abs'] = wape_mensual['Dif_Wape_Abs'].round(2)
                wape_mensual['Wape_%'] = wape_mensual['Wape_%'].round(1)
                
                # Optimización: Usar np.where en lugar de .apply() para mayor rendimiento
                wape_mensual['+Wape (MKL)'] = np.where(
                    wape_mensual['FCST'] < wape_mensual['Despachos'],
                    wape_mensual['Dif_Wape_Abs'],
                    0
                )
                wape_mensual['-Wape (MKL)'] = np.where(
                    wape_mensual['FCST'] > wape_mensual['Despachos'],
                    -wape_mensual['Dif_Wape_Abs'],
                    0
                )
                
                st.dataframe(
                    wape_mensual,
                    use_container_width=True,
                    height=400,
                    hide_index=True
                )
        else:
            st.info("No hay datos de fecha para calcular WAPE mensual")
    
    with col2:
        st.subheader("Evolución WAPE Mensual")
        
        # Gráfico de cascada (waterfall) mostrando evolución del WAPE
        if 'Fecha' in df.columns and not wape_mensual.empty:
            # Preparar datos para gráfico de cascada
            
            # Crear gráfico combinado con barras y línea
            fig = make_subplots(specs=[[{"secondary_y": True}]])
            
            # Barras de -Wape (azul, negativo)
            fig.add_trace(
                go.Bar(
                    x=wape_mensual['Fecha'],
                    y=wape_mensual['-Wape (MKL)'],
                    name='-Wape',
                    marker_color='#42A5F5',
                    text=wape_mensual['-Wape (MKL)'].round(0),
                    textposition='outside'
                ),
                secondary_y=False
            )
            
            # Barras de +Wape (azul oscuro, positivo)
            fig.add_trace(
                go.Bar(
                    x=wape_mensual['Fecha'],
                    y=wape_mensual['+Wape (MKL)'],
                    name='+Wape',
                    marker_color='#1565C0',
                    text=wape_mensual['+Wape (MKL)'].round(0),
                    textposition='outside'
                ),
                secondary_y=False
            )
            
            # Línea de Wape%
            fig.add_trace(
                go.Scatter(
                    x=wape_mensual['Fecha'],
                    y=wape_mensual['Wape_%'],
                    name='Wape%',
                    mode='lines+markers',
                    line=dict(color='#FF6B00', width=3),
                    marker=dict(size=10, symbol='circle'),
                    text=wape_mensual['Wape_%'].round(1).astype(str) + '%',
                    textposition='top center'
                ),
                secondary_y=True
            )
            
            fig.update_xaxes(title_text="Mes")
            fig.update_yaxes(title_text="-Wape y +Wape", secondary_y=False)
            fig.update_yaxes(title_text="Wape%", secondary_y=True)
            
            fig.update_layout(
                height=450,
                showlegend=True,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                hovermode='x unified',
                barmode='relative'
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No hay suficientes datos para mostrar la evolución")
    
    # KPIs de WAPE
    st.markdown("---")
    st.subheader("📊 Métricas Clave de WAPE")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        fcst_total = df[fcst_col].sum()
        st.metric("FCST Total", f"{fcst_total:,.0f} KL")
    
    with col2:
        desp_total = df[desp_col].sum()
        st.metric("Despachos Total", f"{desp_total:,.0f} KL")
    
    with col3:
        wape_global = calculate_wape(fcst_total, desp_total)
        
        # Determinar si es bueno o malo
        delta_color = "normal" if wape_global < 15 else "inverse"
        st.metric("WAPE Global", f"{wape_global:.1f}%", delta=f"{'Bueno' if wape_global < 15 else 'Revisar'}")
    
    with col4:
        dif_abs = abs(desp_total - fcst_total)
        bias = "Sobre-forecast" if fcst_total > desp_total else "Sub-forecast"
        st.metric("Diferencia Absoluta", f"{dif_abs:,.0f} KL", delta=bias)
    
    # Información adicional
    st.info("""
    **Interpretación de WAPE:**
    - WAPE < 15%: Excelente precisión del forecast
    - WAPE 15-25%: Precisión aceptable
    - WAPE > 25%: Se requiere mejorar el proceso de forecasting
    
    **+Wape**: Sobre-forecast (proyectamos más de lo que se vendió)
    **-Wape**: Sub-forecast (proyectamos menos de lo que se vendió)
    """)
