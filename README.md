# 🧮 Simulador Computacional de Sólidos de Revolución

**Proyecto Integrador — Cálculo Integral**  
**Institución:** Unidades Tecnológicas de Santander (UTS)  
**Programa:** Ingeniería de Sistemas  

## 📋 Descripción
Aplicación web interactiva desarrollada en Python para el modelado 3D, análisis simbólico y cálculo numérico del volumen de sólidos de revolución mediante tres métodos principales:
1. **Método de Discos:** Micro-lente acopladora de fibra óptica ($f(x) = \sqrt{x}$ en $[0, 4]$ alrededor del eje X).
2. **Método de Arandelas:** Disipador térmico hueco para procesador ($y_{\text{sup}} = 4 - x^2$, $y_{\text{inf}} = 2$ alrededor del eje desplazado $y = 1$).
3. **Método de Cascarones Cilíndricos:** Carcasa aerodinámica de servidor ($f(x) = 2x - x^2$ en $[0, 2]$ alrededor del eje Y).

## 🛠️ Tecnologías Utilizadas
* **Python 3**
* **Streamlit:** Interfaz web interactiva.
* **SymPy:** Resolución analítica exacta y álgebra simbólica.
* **SciPy & NumPy:** Integración numérica por cuadratura y cálculo vectorial.
* **Plotly:** Visualización 3D interactiva con secciones transversales dinámicas.
* **GeoGebra 3D API:** Renderizado paramétrico automático.

## 🚀 Instalación y Ejecución Local
1. Clonar el repositorio:
   ```bash
   git clone <https://github.com/amurillov675/Simulador_Solidos_Revolucion.git>
