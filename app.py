import streamlit as st
import streamlit.components.v1 as components
import numpy as np
import sympy as sp
from scipy import integrate
import plotly.graph_objects as go
import json

# Configuración inicial de la página
st.set_page_config(
    page_title="Simulador Sólidos de Revolución - UTS",
    page_icon="🧮",
    layout="wide"
)

st.title("🧮 Simulador Computacional de Sólidos de Revolución")
st.markdown("**Unidades Tecnológicas de Santander (UTS)** | Cálculo Integral — Ingeniería de Sistemas")

# Barra lateral: Selección de ejemplo
st.sidebar.header("⚙️ Selección de Caso de Estudio")
caso = st.sidebar.selectbox(
    "Elige el método a simular:",
    [
        "1. Método de Discos (Fibra Óptica)",
        "2. Método de Arandelas (Disipador - Eje y=1)",
        "3. Método de Cascarones (Carcasa Servidor)"
    ]
)

st.sidebar.markdown("---")
st.sidebar.subheader("🎛️ Parámetros del Modelo")

x = sp.Symbol('x')

# Configuración según el caso seleccionado
if "Discos" in caso:
    st.sidebar.info("**Eje de rotación:** Eje X ($y = 0$)")
    expr_f = st.sidebar.text_input("Función superior f(x):", value="sqrt(x)")
    a = st.sidebar.number_input("Límite inferior (a):", value=0.0, step=0.5)
    b = st.sidebar.number_input("Límite superior (b):", value=4.0, step=0.5)
    eje_y = 0.0
    contexto = "**Micro-lente acopladora de fibra óptica:** En redes de telecomunicaciones, alinea el haz láser para evitar atenuación de datos. Calcular su volumen determina la cantidad exacta de material dieléctrico y su índice de refracción."
    
    u_expr = expr_f.replace('x', 'u')
    ggb_cmds = [
        f"f(x) = If({a} <= x <= {b}, {expr_f})",
        f"Solido = Surface(u, ({u_expr})*cos(v), ({u_expr})*sin(v), u, {a}, {b}, v, 0, 2*pi)"
    ]

elif "Arandelas" in caso:
    st.sidebar.info("**Eje de rotación desplazado:** $y = c$")
    expr_sup = st.sidebar.text_input("Curva exterior y_sup(x):", value="4 - x**2")
    expr_inf = st.sidebar.text_input("Curva interior y_inf(x):", value="2")
    eje_y = st.sidebar.number_input("Eje de giro horizontal (y = c):", value=1.0, step=0.5)
    a = st.sidebar.number_input("Límite inferior (a):", value=-1.41421356, format="%.4f")
    b = st.sidebar.number_input("Límite superior (b):", value=1.41421356, format="%.4f")
    contexto = "**Disipador térmico hueco para CPU:** En arquitectura de hardware, permite el flujo central de refrigeración. Su volumen determina la masa térmica de aluminio necesaria para evitar el sobrecalentamiento del procesador."
    
    R_ggb = f"(({expr_sup.replace('x', 'u')}) - ({eje_y}))"
    r_ggb = f"(({expr_inf.replace('x', 'u')}) - ({eje_y}))"
    ggb_cmds = [
        f"EjeGiro: y = {eje_y}",
        f"Exterior = Surface(u, {eje_y} + {R_ggb}*cos(v), {R_ggb}*sin(v), u, {a}, {b}, v, 0, 2*pi)",
        f"Interior = Surface(u, {eje_y} + {r_ggb}*cos(v), {r_ggb}*sin(v), u, {a}, {b}, v, 0, 2*pi)"
    ]

else:  # Cascarones Cilíndricos
    st.sidebar.info("**Eje de rotación:** Eje Y ($x = 0$)")
    expr_f = st.sidebar.text_input("Altura del cascarón f(x):", value="2*x - x**2")
    a = st.sidebar.number_input("Límite inferior (a):", value=0.0, step=0.5)
    b = st.sidebar.number_input("Límite superior (b):", value=2.0, step=0.5)
    contexto = "**Carcasa aerodinámica de servidor:** En centros de datos, redirige el flujo de aire en racks reduciendo turbulencia. El volumen permite estimar el material exacto requerido para su fabricación por impresión 3D o moldeado."
    
    u_expr = expr_f.replace('x', 'u')
    ggb_cmds = [
        f"f(x) = If({a} <= x <= {b}, {expr_f})",
        f"Solido = Surface(u*cos(v), {u_expr}, u*sin(v), u, {a}, {b}, v, 0, 2*pi)"
    ]

# Control interactivo del elemento diferencial
pos_elem = st.sidebar.slider(
    "🔍 Posición de la sección transversal (dx):",
    min_value=float(a),
    max_value=float(b),
    value=float((a + b) / 2),
    step=0.02
)

# Procesamiento matemático (Simbólico Exacto y Numérico)
try:
    a_sym = sp.nsimplify(a, tolerance=1e-4)
    b_sym = sp.nsimplify(b, tolerance=1e-4)

    if "Discos" in caso:
        f_sym = sp.sympify(expr_f)
        f_num = sp.lambdify(x, f_sym, "numpy")
        integrando_sym = sp.pi * (f_sym**2)
        antiderivada = sp.integrate(integrando_sym, x)
        vol_exacto = sp.integrate(integrando_sym, (x, a_sym, b_sym))
        vol_numerico, _ = integrate.quad(lambda val: np.pi * (float(f_num(val))**2), a, b)
        expr_sin_simp = r"\pi \left(" + sp.latex(f_sym) + r"\right)^2"

    elif "Arandelas" in caso:
        sup_sym = sp.sympify(expr_sup)
        inf_sym = sp.sympify(expr_inf)
        eje_sym = sp.nsimplify(eje_y, tolerance=1e-4)
        R_sym = sup_sym - eje_sym
        r_sym = inf_sym - eje_sym
        sup_num = sp.lambdify(x, sup_sym, "numpy")
        inf_num = sp.lambdify(x, inf_sym, "numpy")
        
        integrando_sym = sp.pi * sp.expand(R_sym**2 - r_sym**2)
        antiderivada = sp.integrate(integrando_sym, x)
        
        if np.isclose(abs(a), np.sqrt(2)) and np.isclose(abs(b), np.sqrt(2)):
            a_sym, b_sym = -sp.sqrt(2), sp.sqrt(2)
            
        vol_exacto = sp.simplify(sp.integrate(integrando_sym, (x, a_sym, b_sym)))
        vol_numerico, _ = integrate.quad(
            lambda val: np.pi * ((float(sup_num(val)) - eje_y)**2 - (float(inf_num(val)) - eje_y)**2),
            a, b
        )
        expr_sin_simp = r"\pi \left[ \left(" + sp.latex(R_sym) + r"\right)^2 - \left(" + sp.latex(r_sym) + r"\right)^2 \right]"

    else:  # Cascarones
        f_sym = sp.sympify(expr_f)
        f_num = sp.lambdify(x, f_sym, "numpy")
        integrando_sym = sp.expand(2 * sp.pi * x * f_sym)
        antiderivada = sp.integrate(integrando_sym, x)
        vol_exacto = sp.integrate(integrando_sym, (x, a_sym, b_sym))
        vol_numerico, _ = integrate.quad(lambda val: 2 * np.pi * val * float(f_num(val)), a, b)
        expr_sin_simp = r"2\pi x \left(" + sp.latex(f_sym) + r"\right)"

    # Panel superior: Contexto y Resultados
    st.info(contexto)
    
    c1, c2, c3 = st.columns(3)
    vol_str = str(vol_exacto).replace("**", "^").replace("*", "·").replace("sqrt", "√").replace("pi", "π")
    c1.metric("Volumen Exacto (Simbólico)", f"{vol_str} u³")
    c2.metric("Aproximación Numérica (SciPy)", f"{vol_numerico:.6f} u³")
    err = abs(float(vol_exacto.evalf()) - vol_numerico)
    c3.metric("Error Absoluto (Punto Flotante)", f"{err:.2e}")

    st.latex(r"V = \int_{" + sp.latex(a_sym) + r"}^{" + sp.latex(b_sym) + r"} " + expr_sin_simp + r"\,dx = " + sp.latex(vol_exacto))

    # Pestañas de visualización y análisis
    tab_analisis, tab_2d, tab_3d, tab_ggb = st.tabs([
        "📝 Desarrollo Analítico Paso a Paso",
        "📈 Región Plana 2D",
        "🧊 Simulador 3D (Sólido y Sección)",
        "📐 GeoGebra 3D Renderizado"
    ])

    # --- PESTAÑA 1: GRÁFICO 3D ---
    with tab_3d:
        u = np.linspace(a, b, 70)
        v = np.linspace(0, 2 * np.pi, 70)
        U, V = np.meshgrid(u, v)
        fig3d = go.Figure()

        if "Discos" in caso:
            R_vals = np.broadcast_to(f_num(U), U.shape)
            fig3d.add_trace(go.Surface(
                x=U, y=R_vals * np.cos(V), z=R_vals * np.sin(V),
                opacity=0.45, colorscale="Viridis", showscale=False, name="Sólido"
            ))
            r_elem = float(f_num(pos_elem))
            rad = np.linspace(0, r_elem, 20)
            theta = np.linspace(0, 2 * np.pi, 40)
            RAD, THETA = np.meshgrid(rad, theta)
            fig3d.add_trace(go.Surface(
                x=np.full_like(RAD, pos_elem),
                y=RAD * np.cos(THETA),
                z=RAD * np.sin(THETA),
                colorscale=[[0, '#FF4B4B'], [1, '#FF4B4B']], showscale=False, opacity=0.95, name="Disco dx"
            ))

        elif "Arandelas" in caso:
            R_ext = np.broadcast_to(sup_num(U) - eje_y, U.shape)
            R_int = np.broadcast_to(inf_num(U) - eje_y, U.shape)
            
            fig3d.add_trace(go.Surface(
                x=U, y=eje_y + R_ext * np.cos(V), z=R_ext * np.sin(V),
                opacity=0.35, colorscale="Blues", showscale=False, name="Pared Exterior"
            ))
            fig3d.add_trace(go.Surface(
                x=U, y=eje_y + R_int * np.cos(V), z=R_int * np.sin(V),
                opacity=0.55, colorscale="Teal", showscale=False, name="Cavidad Interior"
            ))
            fig3d.add_trace(go.Scatter3d(
                x=[a - 0.3, b + 0.3], y=[eje_y, eje_y], z=[0, 0],
                mode="lines", line=dict(color="red", width=5, dash="dash"), name=f"Eje y={eje_y}"
            ))
            r_out = float(sup_num(pos_elem)) - eje_y
            r_in = float(inf_num(pos_elem)) - eje_y
            rad = np.linspace(min(r_in, r_out), max(r_in, r_out), 20)
            theta = np.linspace(0, 2 * np.pi, 40)
            RAD, THETA = np.meshgrid(rad, theta)
            fig3d.add_trace(go.Surface(
                x=np.full_like(RAD, pos_elem),
                y=eje_y + RAD * np.cos(THETA),
                z=RAD * np.sin(THETA),
                colorscale=[[0, '#FFA500'], [1, '#FFA500']], showscale=False, opacity=0.95, name="Arandela dx"
            ))

        else:  # Cascarones Cilíndricos
            H_vals = np.broadcast_to(f_num(U), U.shape)
            fig3d.add_trace(go.Surface(
                x=U * np.cos(V), y=H_vals, z=U * np.sin(V),
                opacity=0.45, colorscale="Plasma", showscale=False, name="Sólido"
            ))
            h_elem = float(f_num(pos_elem))
            h_grid = np.linspace(0, h_elem, 20)
            theta = np.linspace(0, 2 * np.pi, 40)
            H_G, THETA = np.meshgrid(h_grid, theta)
            fig3d.add_trace(go.Surface(
                x=pos_elem * np.cos(THETA),
                y=H_G,
                z=pos_elem * np.sin(THETA),
                colorscale=[[0, '#00F0FF'], [1, '#00F0FF']], showscale=False, opacity=0.95, name="Cascarón dx"
            ))

        fig3d.update_layout(
            scene=dict(xaxis_title="Eje X", yaxis_title="Eje Y", zaxis_title="Eje Z", aspectmode="data"),
            height=580, margin=dict(l=0, r=0, b=0, t=20)
        )
        st.plotly_chart(fig3d, use_container_width=True)

  # --- PESTAÑA 2: DESARROLLO ANALÍTICO PASO A PASO ---
    with tab_analisis:
        st.subheader("Resolución Analítica Detallada Paso a Paso")

        # Desglose de antiderivada término a término y sustitución explícita
        terminos_integrando = sp.Add.make_args(sp.expand(integrando_sym))
        pasos_antiderivada = [sp.integrate(t, x) for t in terminos_integrando]
        antiderivada_desglosada = sp.Add(*pasos_antiderivada)

        # Construir cadenas LaTeX mostrando el reemplazo explícito de b y a en la antiderivada
        antiderivada_latex = sp.latex(antiderivada_desglosada)
        sust_b_latex = antiderivada_latex.replace("x", f"\\left({sp.latex(b_sym)}\\right)")
        sust_a_latex = antiderivada_latex.replace("x", f"\\left({sp.latex(a_sym)}\\right)")

        val_b = sp.simplify(antiderivada_desglosada.subs(x, b_sym))
        val_a = sp.simplify(antiderivada_desglosada.subs(x, a_sym))

        if "Discos" in caso:
            st.markdown("### 1. Comprensión del Problema y Fórmula del Método")
            st.write(
                "Queremos calcular el volumen de la micro-lente dieléctrica que se forma al girar la curva "
                f"$f(x) = {sp.latex(f_sym)}$ alrededor del **eje horizontal X** ($y = 0$). "
                "Como la figura no tiene ningún hueco en su interior, si la cortamos en rebanadas verticales muy delgadas "
                "de grosor $dx$, cada rebanada es un **disco sólido** cuyo radio es la altura de la curva: $R(x) = f(x)$."
            )
            st.latex(r"V = \pi \int_{a}^{b} [R(x)]^2 \, dx = \pi \int_{a}^{b} [f(x)]^2 \, dx")

            st.markdown("### 2. Hallar los Límites de Integración ($a$ y $b$)")
            if expr_f.strip() == "sqrt(x)" and np.isclose(a, 0.0) and np.isclose(b, 4.0):
                st.write("Necesitamos saber desde qué punto en $x$ empieza la lente hasta dónde termina:")
                st.latex(r"\text{Inicio } (a): \text{ La curva toca el eje } X \ (y = 0) \implies \sqrt{x} = 0 \implies x = 0^2 \implies a = 0")
                st.latex(r"\text{Fin } (b): \text{ El diseño establece una longitud de } 4\text{ mm} \implies b = 4")
                st.latex(r"\text{Por lo tanto, integramos desde } x = 0 \text{ hasta } x = 4.")
            else:
                st.latex(r"\text{Integramos en el intervalo definido: } x \in [" + sp.latex(a_sym) + r", " + sp.latex(b_sym) + r"]")

            st.markdown("### 3. Armar y Simplificar la Integral")
            st.write(f"Reemplazamos la función $f(x) = {sp.latex(f_sym)}$ y los límites $a = {sp.latex(a_sym)}$ y $b = {sp.latex(b_sym)}$ en la fórmula:")
            st.latex(r"V = \int_{" + sp.latex(a_sym) + r"}^{" + sp.latex(b_sym) + r"} " + expr_sin_simp + r" \, dx")
            st.write("Como elevar una raíz cuadrada al cuadrado cancela la raíz ($(\\sqrt{x})^2 = x$), la integral se simplifica a:")
            st.latex(r"V = \int_{" + sp.latex(a_sym) + r"}^{" + sp.latex(b_sym) + r"} " + sp.latex(integrando_sym) + r" \, dx")

        elif "Arandelas" in caso:
            st.markdown("### 1. Comprensión del Problema y Fórmula del Método")
            st.write(
                f"Este disipador térmico tiene un agujero en el centro porque la región entre la curva superior "
                f"$y_{{\\text{{sup}}}}(x) = {sp.latex(sup_sym)}$ y la curva inferior $y_{{\\text{{inf}}}}(x) = {sp.latex(inf_sym)}$ "
                f"gira alrededor de la recta horizontal **$y = {sp.latex(eje_sym)}$** (que está por debajo de la figura). "
                "Al hacer cortes verticales de grosor $dx$, obtenemos **arandelas** (discos con un hueco circular en el medio)."
            )
            st.latex(r"V = \pi \int_{a}^{b} \left( [R(x)]^2 - [r(x)]^2 \right) dx")

            st.markdown("### 2. Hallar los Límites de Integración ($a$ y $b$)")
            st.write("La región comienza y termina exactamente donde las dos curvas se cruzan. Para hallar esos puntos, igualamos ambas ecuaciones:")
            st.latex(sp.latex(sup_sym) + r" = " + sp.latex(inf_sym) + r" \implies " + sp.latex(sp.Eq(sup_sym - inf_sym, 0)))
            raices = sp.solve(sp.Eq(sup_sym, inf_sym), x)
            if raices:
                raices_latex = r" \quad \text{y} \quad ".join([f"x = {sp.latex(r_val)}" for r_val in raices])
                st.latex(r"\text{Al despejar } x \text{ obtenemos los cortes: } " + raices_latex)
            st.latex(r"\text{Por lo tanto, integramos desde } a = " + sp.latex(a_sym) + r" \text{ hasta } b = " + sp.latex(b_sym) + r".")

            st.markdown(f"### 3. Calcular el Radio Exterior $R(x)$ y el Radio Interior $r(x)$")
            st.write(f"Como el eje de giro está en $y = {sp.latex(eje_sym)}$ y no en $y = 0$, medimos la distancia desde cada curva hasta la recta $y = {sp.latex(eje_sym)}$:")
            st.latex(r"\text{Radio exterior } R(x) = \left(" + sp.latex(sup_sym) + r"\right) - \left(" + sp.latex(eje_sym) + r"\right) = " + sp.latex(R_sym))
            st.latex(r"\text{Radio interior } r(x) = \left(" + sp.latex(inf_sym) + r"\right) - \left(" + sp.latex(eje_sym) + r"\right) = " + sp.latex(r_sym))

            st.markdown("### 4. Armar y Expandir la Integral")
            st.write("Sustituimos ambos radios en la fórmula de arandelas:")
            st.latex(r"V = \int_{" + sp.latex(a_sym) + r"}^{" + sp.latex(b_sym) + r"} " + expr_sin_simp + r" \, dx")
            st.write("Desarrollamos los cuadrados (recordando que $(a - b)^2 = a^2 - 2ab + b^2$) y restamos los términos semejantes:")
            st.latex(r"V = \int_{" + sp.latex(a_sym) + r"}^{" + sp.latex(b_sym) + r"} " + sp.latex(integrando_sym) + r" \, dx")

        else:  # Cascarones Cilíndricos
            st.markdown("### 1. Comprensión del Problema y Fórmula del Método")
            st.write(
                f"La región bajo la parábola $f(x) = {sp.latex(f_sym)}$ gira alrededor del **eje vertical Y** ($x = 0$). "
                "Si dividimos la figura en tiras verticales paralelas al eje Y, cada tira genera un tubo cilíndrico delgado "
                "(un **cascarón cilíndrico**) cuyo radio es la distancia al eje Y ($x$) y cuya altura es $f(x)$."
            )
            st.latex(r"V = 2\pi \int_{a}^{b} (\text{Radio}) \cdot (\text{Altura}) \, dx = 2\pi \int_{a}^{b} x \cdot f(x) \, dx")
            st.info(
                "💡 **¿Por qué usamos Cascarones y no Arandelas?** Si usáramos arandelas (cortes horizontales), "
                "tendríamos que despejar $x$ de $y = 2x - x^2$, obteniendo $x = 1 \\pm \\sqrt{1-y}$, lo que genera dos raíces complicadas. "
                "Con cascarones integramos directamente respecto a $x$ usando un polinomio sencillo."
            )

            st.markdown("### 2. Hallar los Límites de Integración ($a$ y $b$)")
            st.write("La región está limitada abajo por el eje X ($y = 0$). Igualamos la función a cero y factorizamos para ver dónde corta al eje X:")
            st.latex(sp.latex(f_sym) + r" = 0 \implies " + sp.latex(sp.factor(f_sym)) + r" = 0")
            raices = sp.solve(sp.Eq(f_sym, 0), x)
            if raices:
                raices_latex = r" \quad \text{y} \quad ".join([f"x = {sp.latex(r_val)}" for r_val in raices])
                st.latex(r"\text{Igualando cada factor a cero: } " + raices_latex)
            st.latex(r"\text{Por lo tanto, integramos desde } a = " + sp.latex(a_sym) + r" \text{ hasta } b = " + sp.latex(b_sym) + r".")

            st.markdown("### 3. Armar y Expandir la Integral")
            st.write(f"Sustituimos $f(x) = {sp.latex(f_sym)}$ en la fórmula de cascarones:")
            st.latex(r"V = \int_{" + sp.latex(a_sym) + r"}^{" + sp.latex(b_sym) + r"} " + expr_sin_simp + r" \, dx")
            st.write("Multiplicamos $x$ por cada término dentro del paréntesis:")
            st.latex(r"V = \int_{" + sp.latex(a_sym) + r"}^{" + sp.latex(b_sym) + r"} " + sp.latex(integrando_sym) + r" \, dx")

        # Paso final común: Integración explícita y sustitución numérica directa
        st.markdown("### 4. Resolver la Integral (Regla de la Potencia)")
        st.write(
            "Para integrar cada término polinómico, sumamos $1$ al exponente de $x$ y dividimos entre ese nuevo exponente "
            "($\\int x^n \\, dx = \\frac{x^{n+1}}{n+1}$):"
        )
        st.latex(r"V = \left[ " + antiderivada_latex + r" \right]_{" + sp.latex(a_sym) + r"}^{" + sp.latex(b_sym) + r"}")

        st.markdown("### 5. Evaluar los Límites Superior e Inferior")
        st.write(
            f"Aplicamos el **Teorema Fundamental del Cálculo**: primero reemplazamos todas las $x$ por el límite superior "
            f"($x = {sp.latex(b_sym)}$) y luego le restamos el resultado de reemplazar todas las $x$ por el límite inferior "
            f"($x = {sp.latex(a_sym)}$):"
        )
        st.latex(
            r"V = \underbrace{\left[ " + sust_b_latex + r" \right]}_{\text{Evaluando } x = " + sp.latex(b_sym) + r"}"
            r" - \underbrace{\left[ " + sust_a_latex + r" \right]}_{\text{Evaluando } x = " + sp.latex(a_sym) + r"}"
        )
        st.write("Simplificamos las potencias y operaciones dentro de cada corchete:")
        st.latex(r"V = \left( " + sp.latex(val_b) + r" \right) - \left( " + sp.latex(val_a) + r" \right)")

        st.success("**Resultado Final Exacto y Aproximación Decimal:**")
        st.latex(r"V = " + sp.latex(vol_exacto) + r" \approx " + f"{vol_numerico:.6f}" + r" \text{ u}^3")
        
    # --- PESTAÑA 3: REGIÓN PLANA 2D ---
    with tab_2d:
        x_vals = np.linspace(a, b, 200)
        fig2d = go.Figure()
        
        if "Arandelas" in caso:
            y_s = np.broadcast_to(sup_num(x_vals), x_vals.shape)
            y_i = np.broadcast_to(inf_num(x_vals), x_vals.shape)
            fig2d.add_trace(go.Scatter(x=x_vals, y=y_s, mode='lines', name='Curva Exterior', line=dict(color='blue')))
            fig2d.add_trace(go.Scatter(x=x_vals, y=y_i, mode='lines', fill='tonexty', name='Región a Rotar', line=dict(color='green')))
            fig2d.add_hline(y=eje_y, line_dash="dash", line_color="red", annotation_text=f"Eje de giro y = {eje_y}")
        else:
            y_vals = np.broadcast_to(f_num(x_vals), x_vals.shape)
            fig2d.add_trace(go.Scatter(x=x_vals, y=y_vals, mode='lines', fill='tozeroy', name='Región a Rotar', line=dict(color='purple')))
            if "Discos" in caso:
                fig2d.add_hline(y=0, line_dash="dash", line_color="red", annotation_text="Eje X (Giro)")
            else:
                fig2d.add_vline(x=0, line_dash="dash", line_color="red", annotation_text="Eje Y (Giro)")

        fig2d.update_layout(title="Región Transversal en el Plano XY", xaxis_title="x", yaxis_title="y", height=450)
        st.plotly_chart(fig2d, use_container_width=True)

    # --- PESTAÑA 4: GEOGEBRA 3D RENDERIZADO AUTOMÁTICAMENTE ---
    with tab_ggb:
        st.markdown("### Visualización Paramétrica Renderizada en GeoGebra 3D")
        st.caption("El sólido se dibuja automáticamente mediante la API de GeoGebra 3D. Puedes rotarlo con el ratón o hacer zoom.")
        
        cmds_json = json.dumps(ggb_cmds)
        ggb_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <script src="https://www.geogebra.org/apps/deployggb.js"></script>
        </head>
        <body style="margin:0; padding:0; overflow:hidden;">
            <div id="ggb-element" style="width: 100%; height: 600px;"></div>
            <script>
                var comandos = {cmds_json};
                var params = {{
                    "appName": "3d",
                    "width": 1100,
                    "height": 600,
                    "showToolBar": true,
                    "showAlgebraInput": true,
                    "showMenuBar": false,
                    "language": "es",
                    "appletOnLoad": function(api) {{
                        comandos.forEach(function(cmd) {{
                            api.evalCommand(cmd);
                        }});
                    }}
                }};
                var applet = new GGBApplet(params, true);
                window.addEventListener("load", function() {{
                    applet.inject('ggb-element');
                }});
            </script>
        </body>
        </html>
        """
        components.html(ggb_html, height=610)

except Exception as e:
    st.error(f"Revisa la expresión matemática ingresada. Detalle técnico: {e}")
