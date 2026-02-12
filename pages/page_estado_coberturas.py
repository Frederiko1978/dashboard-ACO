import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.calculations import calculate_top_materials, calculate_distribucion_origen

def show(df, estado_cob):
    """
    Página de Estado de Coberturas - Replica la segunda vista del PBI
    """
    st.header("🎯 Estado de Coberturas")
    
    if df.empty:
        st.warning("No hay datos para mostrar con los filtros seleccionados")
        return
    
    # Aplicar filtro de estado si está seleccionado
    if estado_cob != "Todas" and 'Estado_Cobertura' in df.columns:
        df = df[df['Estado_Cobertura'] == estado_cob]
        st.info(f"Mostrando datos para: **{estado_cob}**")
    
    # Fila 1: Material por Estado + Evolución del Inventario + Distribución por Origen
    col1, col2, col3 = st.columns([2, 3, 2])
    
    with col1:
        st.subheader("Material por Estado")
        # Gráfico de barras 100% apiladas por mes (filtrado)
        if 'Estado_Cobertura' in df.columns and 'Fecha' in df.columns:
            estado_mes = df.groupby(['Fecha', 'Estado_Cobertura']).size().reset_index(name='Cantidad')
            
            # Calcular porcentajes
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
        st.subheader("Evolución del Inventario")
        # Gráfico combinado con barras de inventario y línea de promedio de cobertura
        if 'Fecha' in df.columns:
            evolucion = df.groupby('Fecha').agg({
                'Inv Kg-L': 'sum' if 'Inv Kg-L' in df.columns else 'count',
                'Cob(D)': 'mean' if 'Cob(D)' in df.columns else 'count'
            }).reset_index()
            
            # Convertir fecha a string para el eje X
            if pd.api.types.is_datetime64_any_dtype(evolucion['Fecha']):
                evolucion['Mes_Numero'] = evolucion['Fecha'].dt.month
                evolucion['Fecha_Str'] = evolucion['Fecha'].dt.strftime('%Y-%m')
            else:
                evolucion['Fecha_Str'] = evolucion['Fecha'].astype(str)
                evolucion['Mes_Numero'] = range(1, len(evolucion) + 1)
            
            fig = go.Figure()
            
            # Barras de inventario (rojo para estado crítico)
            fig.add_trace(
                go.Bar(
                    x=evolucion['Mes_Numero'],
                    y=evolucion['Inv Kg-L'],
                    name='Inventario',
                    marker_color='#EF5350',
                    text=evolucion['Inv Kg-L'].round(0),
                    textposition='outside'
                )
            )
            
            # Línea de promedio de cobertura
            if 'Cob(D)' in evolucion.columns:
                fig.add_trace(
                    go.Scatter(
                        x=evolucion['Mes_Numero'],
                        y=evolucion['Cob(D)'],
                        name='Promedio Cobertura (D) Final',
                        mode='lines+markers',
                        line=dict(color='#2196F3', width=3),
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
        # Gráfico de barras horizontales por origen
        if 'Origen' in df.columns:
            distribucion = calculate_distribucion_origen(df)
            
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
    
    # Fila 2: Top 15 mayor/menor valor + Planificación por SKU
    st.markdown("---")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        # Top 15 de mayor valor
        st.subheader("Top 15 de mayor valor")
        
        value_col = 'Inv (M/Usd)' if 'Inv (M/Usd)' in df.columns else 'Inv Kg-L'
        top_mayor = calculate_top_materials(df, value_col=value_col, top_n=15, ascending=False)
        
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
        
        # Top 15 de menor valor
        st.subheader("Top 15 de menor valor")
        
        top_menor = calculate_top_materials(df, value_col=value_col, top_n=15, ascending=True)
        
        if not top_menor.empty:
            st.dataframe(
                top_menor,
                use_container_width=True,
                height=300,
                hide_index=True
            )
        else:
            st.info("No hay datos disponibles")
    
    with col2:
        st.subheader("Planificación por SKU")
        
        # Tabla detallada por mes
        if 'Material' in df.columns and 'Fecha' in df.columns:
            columnas = ['Material', 'Fecha', 'F (MKL)', 'Inv (MKL)', 'Q (MKL)', 'Cob (D)']
            
            # Mapear nombres de columnas si existen variantes
            col_map = {
                'F (MKL)': ['F (MKL)', 'FCST', 'F'],
                'Inv (MKL)': ['Inv (MKL)', 'Inv Kg-L', 'Inventario'],
                'Q (MKL)': ['Q (MKL)', 'Q'],
                'Cob (D)': ['Cob (D)', 'Cob(D)', 'Cobertura']
            }
            
            columnas_reales = ['Material', 'Fecha']
            for col_objetivo, posibles in col_map.items():
                for posible in posibles:
                    if posible in df.columns:
                        columnas_reales.append(posible)
                        break
            
            df_planif = df[columnas_reales].copy()
            
            # Agregar indicador de estado con color
            if 'Cob(D)' in df.columns or 'Cob (D)' in df.columns:
                cob_col = 'Cob(D)' if 'Cob(D)' in df.columns else 'Cob (D)'
                
                # Función para aplicar color según cobertura
                def highlight_cobertura(val):
                    if pd.isna(val):
                        return ''
                    elif val < 45:
                        return 'background-color: #FFCDD2'  # Rojo claro
                    elif val < 90:
                        return 'background-color: #FFE082'  # Amarillo claro
                    else:
                        return 'background-color: #C8E6C9'  # Verde claro
                
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
                label="📥 Descargar planificación completa",
                data=csv,
                file_name=f'planificacion_por_sku_{estado_cob}.csv',
                mime='text/csv',
            )
