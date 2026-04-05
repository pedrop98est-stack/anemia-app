import streamlit as st

st.set_page_config(page_title="Classificador de Anemia", layout="wide")

st.title("🩸 Classificador Inteligente de Anemia")
st.markdown("Ferramenta de apoio ao raciocínio clínico. Não substitui avaliação médica.")

# -----------------------
# INPUTS
# -----------------------

st.sidebar.header("📥 Dados do Paciente")

sexo = st.sidebar.selectbox("Sexo", ["Masculino", "Feminino"])

Hb = st.sidebar.number_input("Hemoglobina (g/dL)", 0.0, 20.0, 12.0)
Ht = st.sidebar.number_input("Hematócrito (%)", 0.0, 60.0, 40.0)
VCM = st.sidebar.number_input("VCM (fL)", 50.0, 150.0, 90.0)
RDW = st.sidebar.number_input("RDW (%)", 10.0, 25.0, 13.0)

retic = st.sidebar.number_input("Reticulócitos (%)", 0.0, 20.0, 1.0)

ferritina = st.sidebar.number_input("Ferritina (ng/mL)", 0.0, 1000.0, 100.0)
ferro = st.sidebar.number_input("Ferro sérico", 0.0, 300.0, 80.0)
TIBC = st.sidebar.number_input("TIBC", 100.0, 500.0, 300.0)

B12 = st.sidebar.number_input("Vitamina B12", 0.0, 2000.0, 400.0)
folato = st.sidebar.number_input("Ácido fólico", 0.0, 20.0, 8.0)

LDH = st.sidebar.number_input("LDH", 0.0, 2000.0, 200.0)
BI = st.sidebar.number_input("Bilirrubina indireta", 0.0, 10.0, 0.8)
haptoglobina = st.sidebar.number_input("Haptoglobina", 0.0, 300.0, 100.0)

creatinina = st.sidebar.number_input("Creatinina", 0.0, 10.0, 1.0)
TSH = st.sidebar.number_input("TSH", 0.0, 20.0, 2.0)

coombs = st.sidebar.selectbox("Coombs direto", ["Negativo", "Positivo"])

# -----------------------
# CÁLCULOS
# -----------------------

anemia = False

if sexo == "Masculino" and Hb < 13:
    anemia = True
elif sexo == "Feminino" and Hb < 12:
    anemia = True

retic_corr = retic * (Ht / 45)

if Ht >= 40:
    fator = 1
elif Ht >= 30:
    fator = 1.5
elif Ht >= 20:
    fator = 2
else:
    fator = 2.5

RPI = retic_corr / fator

IST = (ferro / TIBC) * 100 if TIBC > 0 else 0

# -----------------------
# PROCESSAMENTO
# -----------------------

if not anemia:
    st.success("✅ Sem anemia")
else:
    st.error("⚠️ Anemia detectada")

    if VCM < 80:
        tipo = "Microcítica"
    elif 80 <= VCM <= 100:
        tipo = "Normocítica"
    else:
        tipo = "Macrocítica"

    if RPI < 2:
        mecanismo = "Hipoproliferativa"
    else:
        mecanismo = "Hiperproliferativa"

    st.subheader("📊 Classificação")
    st.write(f"Tipo: **{tipo}**")
    st.write(f"Mecanismo: **{mecanismo}**")

    diagnostico = "Indefinido"
    conduta = []

    # MICROCÍTICA
    if tipo == "Microcítica":
        if ferritina < 30:
            diagnostico = "Anemia ferropriva"
            conduta = ["Investigar sangramento", "Iniciar ferro oral"]
        elif IST < 20:
            diagnostico = "Deficiência de ferro provável"
        elif RDW < 14:
            diagnostico = "Talassemia"
            conduta = ["Solicitar eletroforese de hemoglobina"]
        else:
            diagnostico = "Anemia de doença crônica"

    # NORMOCÍTICA
    elif tipo == "Normocítica":
        if RPI >= 3:
            if LDH > 250 and BI > 1.2 and haptoglobina < 50:
                if coombs == "Positivo":
                    diagnostico = "Anemia hemolítica autoimune"
                else:
                    diagnostico = "Hemólise não imune"
                conduta = ["Investigar causa da hemólise"]
            else:
                diagnostico = "Sangramento agudo"
        else:
            if ferritina < 30:
                diagnostico = "Ferropriva inicial"
            elif creatinina > 1.5:
                diagnostico = "Anemia da doença renal"
            elif TSH > 4:
                diagnostico = "Hipotireoidismo"
            else:
                diagnostico = "Doença crônica / inflamatória"

    # MACROCÍTICA
    elif tipo == "Macrocítica":
        if B12 < 200:
            diagnostico = "Deficiência de vitamina B12"
            conduta = ["Reposição de B12"]
        elif folato < 4:
            diagnostico = "Deficiência de ácido fólico"
        elif RPI >= 3:
            diagnostico = "Hemólise"
        else:
            diagnostico = "Hepatopatia / álcool / SMD"

    st.subheader("🧠 Diagnóstico provável")
    st.success(diagnostico)

    st.subheader("📌 Dados interpretados")
    st.write(f"RPI: {round(RPI,2)}")
    st.write(f"IST: {round(IST,2)}%")

    if conduta:
        st.subheader("📋 Conduta sugerida")
        for c in conduta:
            st.write(f"- {c}")

    st.subheader("🚨 Alertas")

    if Hb < 7:
        st.error("Anemia grave - considerar transfusão")

    if RPI >= 3 and LDH > 300:
        st.warning("Possível hemólise ativa")

    if VCM > 110:
        st.warning("Macrocitose importante - investigar B12 urgente")
