import streamlit as st
import pandas as pd
import string
import os

def main():
    st.set_page_config(page_title="Gestión de Archivos Excel", layout="centered")

    st.title("📂 Gestión de Archivos Excel")

    # Subir archivo Excel
    uploaded_file = st.file_uploader("📤 Sube tu archivo Excel", type=["xlsx", "xls"])

    if uploaded_file is not None:
        # Leer el archivo Excel
        try:
            df = pd.read_excel(uploaded_file)
            st.success("✅ Archivo cargado correctamente")

            # Crear encabezados al estilo Excel sin eliminar nombres originales
            original_headers = df.columns.tolist()
            excel_headers = [f"{chr(65 + i)} ({name})" for i, name in enumerate(original_headers)]
            df.columns = excel_headers

            # Variables para mantener cambios
            st.session_state.modified_df = df.copy()
            st.session_state.deleted_columns = []
            st.session_state.prefixed_columns = {}

            # Mostrar previsualización
            st.header("📋 Previsualización del archivo")
            st.dataframe(st.session_state.modified_df, use_container_width=True)

            # Eliminar columnas
            st.header("🗑️ Opciones de eliminación de columnas")
            column_to_delete = st.selectbox("Selecciona la columna a eliminar", options=st.session_state.modified_df.columns)
            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button("Eliminar columna"):
                    st.session_state.deleted_columns.append((column_to_delete, st.session_state.modified_df[column_to_delete].copy()))
                    st.session_state.modified_df = st.session_state.modified_df.drop(columns=[column_to_delete])
                    st.success(f"✅ Columna '{column_to_delete}' eliminada")
                    st.dataframe(st.session_state.modified_df, use_container_width=True)  # Actualizar previsualización
            with col2:
                if st.button("Revertir última eliminación de columna"):
                    if st.session_state.deleted_columns:
                        last_deleted = st.session_state.deleted_columns.pop()
                        st.session_state.modified_df.insert(len(st.session_state.modified_df.columns), last_deleted[0], last_deleted[1])
                        st.success(f"✅ Columna '{last_deleted[0]}' restaurada")
                        st.dataframe(st.session_state.modified_df, use_container_width=True)  # Actualizar previsualización
                    else:
                        st.warning("⚠️ No hay columnas para restaurar.")

            # Agregar o quitar prefijo a una columna
            st.header("🔗 Opciones para agregar o quitar prefijo")
            column_to_modify = st.selectbox("Selecciona la columna para modificar prefijo", options=st.session_state.modified_df.columns)
            prefix = st.text_input("Escribe el prefijo a agregar o quitar")

            col3, col4, col5 = st.columns([1, 1, 1])
            with col3:
                if st.button("Agregar prefijo"):
                    try:
                        if column_to_modify not in st.session_state.prefixed_columns:
                            st.session_state.prefixed_columns[column_to_modify] = st.session_state.modified_df[column_to_modify].copy()
                        st.session_state.modified_df[column_to_modify] = prefix + st.session_state.modified_df[column_to_modify].astype(str)
                        st.success(f"✅ Prefijo '{prefix}' agregado a la columna '{column_to_modify}'")
                        st.dataframe(st.session_state.modified_df, use_container_width=True)  # Actualizar previsualización
                    except Exception as e:
                        st.error(f"❌ Error al agregar prefijo: {e}")

            with col4:
                if st.button("Quitar prefijo"):
                    try:
                        if column_to_modify in st.session_state.modified_df.columns:
                            current_values = st.session_state.modified_df[column_to_modify].astype(str)
                            if all(val.startswith(prefix) for val in current_values):
                                st.session_state.modified_df[column_to_modify] = current_values.str[len(prefix):]
                                st.success(f"✅ Prefijo '{prefix}' eliminado de la columna '{column_to_modify}'")
                            else:
                                st.warning(f"⚠️ No todos los valores en la columna '{column_to_modify}' tienen el prefijo '{prefix}'.")
                        st.dataframe(st.session_state.modified_df, use_container_width=True)  # Actualizar previsualización
                    except Exception as e:
                        st.error(f"❌ Error al quitar prefijo: {e}")

            with col5:
                if st.button("Revertir prefijo"):
                    if column_to_modify in st.session_state.prefixed_columns:
                        st.session_state.modified_df[column_to_modify] = st.session_state.prefixed_columns.pop(column_to_modify)
                        st.success(f"✅ Prefijo revertido para la columna '{column_to_modify}'")
                        st.dataframe(st.session_state.modified_df, use_container_width=True)  # Actualizar previsualización
                    else:
                        st.warning("⚠️ No hay prefijos para revertir en esta columna.")

            # Guardar archivo CSV en el mismo directorio del script sin encabezados personalizados
            st.header("💾 Guardar archivo")
            if st.button("Guardar archivo CSV en el directorio del script"):
                file_path = os.path.join(os.getcwd(), "archivo_modificado.csv")
                # Restaurar los encabezados originales antes de guardar
                st.session_state.modified_df.columns = original_headers[:len(st.session_state.modified_df.columns)]
                st.session_state.modified_df.to_csv(file_path, index=False)
                st.success(f"✅ Archivo CSV guardado en: {file_path}")

        except Exception as e:
            st.error(f"❌ Error al procesar el archivo: {e}")

    else:
        # Reiniciar el estado al no haber archivo cargado
        if 'modified_df' in st.session_state:
            del st.session_state.modified_df
        if 'deleted_columns' in st.session_state:
            del st.session_state.deleted_columns
        if 'prefixed_columns' in st.session_state:
            del st.session_state.prefixed_columns

if __name__ == "__main__":
    main()
