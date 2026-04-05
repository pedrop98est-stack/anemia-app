import streamlit as st

st.set_page_config(page_title="Algoritmo de Anemia", layout="wide")

st.title("🩸 Algoritmo Diagnóstico de Anemia")
st.caption("Ferramenta de apoio ao raciocínio clínico. Não substitui avaliação médica.")

# -----------------------------
# Estado
# -----------------------------
if "etapa" not in st.session_state:
    st.session_state.etapa = 1


def avancar():
    st.session_state.etapa += 1


def voltar():
    if st.session_state.etapa > 1:
        st.session_state.etapa -= 1


def resetar():
    for k in list(st.session_state.keys()):
        if k != "etapa":
            del st.session_state[k]
    st.session_state.etapa = 1


# -----------------------------
# Funções
# -----------------------------
def confirmar_anemia(sexo: str, hb: float) -> bool:
    if sexo == "Masculino":
        return hb < 13
    return hb < 12


def classificar_vcm(vcm: float) -> str:
    if vcm < 80:
        return "Microcítica"
    if vcm <= 100:
        return "Normocítica"
    return "Macrocítica"


def calcular_ist(ferro: float, tibc: float):
    if tibc <= 0:
        return None
    return (ferro / tibc) * 100


def calcular_retic_corr(retic: float, ht: float) -> float:
    return retic * (ht / 45)


def calcular_rpi(retic_corr: float, ht: float) -> float:
    if ht >= 40:
        fator = 1
    elif ht >= 30:
        fator = 1.5
    elif ht >= 20:
        fator = 2
    else:
        fator = 2.5
    return retic_corr / fator


def obter_ht_base():
    return st.session_state.get("ht")


def sugestao_exames_por_padrao(tipo: str):
    if tipo == "Microcítica":
        return [
            "Ferritina",
            "Índice de saturação de transferrina (ou ferro sérico + TIBC)",
            "Eletroforese de hemoglobina se não houver ferropenia",
        ]
    if tipo == "Normocítica":
        return [
            "Reticulócitos",
            "Ferritina",
            "Índice de saturação de transferrina",
            "Se reticulocitose: LDH, bilirrubina indireta, haptoglobina e Coombs direto",
        ]
    return [
        "Reticulócitos",
        "Vitamina B12",
        "Ácido fólico",
        "Se reticulocitose: LDH, bilirrubina indireta, haptoglobina e Coombs direto",
        "Se B12/folato normais: função hepática, TSH, revisão de álcool e drogas",
    ]


# -----------------------------
# Barra lateral
# -----------------------------
with st.sidebar:
    st.subheader("Navegação")
    st.write(f"Etapa atual: **{st.session_state.etapa}**")
    if st.button("🔄 Reiniciar fluxo"):
        resetar()
        st.rerun()


# -----------------------------
# ETAPA 1
# -----------------------------
if st.session_state.etapa == 1:
    st.header("Etapa 1 — Hemograma inicial")
    st.write("Preencha apenas os dados iniciais do hemograma.")

    with st.form("etapa1"):
        sexo = st.selectbox("Sexo", ["Masculino", "Feminino"], key="sexo_input")
        hb = st.number_input(
            "Hemoglobina (g/dL)",
            min_value=0.0,
            max_value=25.0,
            value=12.0,
            step=0.1,
            key="hb_input",
        )
        ht = st.number_input(
            "Hematócrito (%)",
            min_value=0.0,
            max_value=70.0,
            value=36.0,
            step=0.1,
            key="ht_input",
        )
        vcm = st.number_input(
            "VCM (fL)",
            min_value=50.0,
            max_value=150.0,
            value=90.0,
            step=0.1,
            key="vcm_input",
        )
        rdw = st.number_input(
            "RDW (%)",
            min_value=8.0,
            max_value=40.0,
            value=13.0,
            step=0.1,
            key="rdw_input",
        )
        rbc = st.number_input(
            "Hemácias (milhões/µL)",
            min_value=0.0,
            max_value=10.0,
            value=4.5,
            step=0.1,
            key="rbc_input",
        )

        enviado = st.form_submit_button("Interpretar hemograma inicial")

    if enviado:
        st.session_state["sexo"] = sexo
        st.session_state["hb"] = hb
        st.session_state["ht"] = ht
        st.session_state["vcm"] = vcm
        st.session_state["rdw"] = rdw
        st.session_state["rbc"] = rbc

        anemia = confirmar_anemia(sexo, hb)
        st.session_state["anemia"] = anemia
        st.session_state["tipo"] = classificar_vcm(vcm)

        if not anemia:
            st.success("Sem anemia pelos critérios informados.")
        else:
            st.error("Anemia detectada.")
            st.subheader("Interpretação inicial")
            st.write(f"**Classificação morfológica:** {st.session_state.tipo}")

            justificativas = [
                f"Hb = {hb:.1f} g/dL",
                f"VCM = {vcm:.1f} fL",
                f"RDW = {rdw:.1f}%",
                f"Hemácias = {rbc:.1f} milhões/µL",
            ]

            st.write("**Pistas do hemograma:**")
            for j in justificativas:
                st.write(f"- {j}")

            if st.session_state.tipo == "Microcítica":
                if rdw > 14.5:
                    st.info("Microcitose com RDW elevado: padrão compatível com ferropenia.")
                elif rdw <= 14.5 and rbc >= 5.0:
                    st.info("Microcitose com RDW normal e hemácias relativamente altas: padrão sugestivo de talassemia.")
            elif st.session_state.tipo == "Normocítica":
                st.info("Anemia normocítica exige diferenciação entre produção reduzida e perda/hemólise.")
            else:
                if rdw > 14.5:
                    st.info("Macrocitose com RDW elevado: padrão sugestivo de deficiência de B12/folato.")
                else:
                    st.info("Macrocitose com RDW não muito elevado: considerar álcool, hepatopatia, drogas, hipotireoidismo.")

            st.write("**Próximos exames sugeridos nesta fase:**")
            for exame in sugestao_exames_por_padrao(st.session_state.tipo):
                st.write(f"- {exame}")

            st.button("Avançar para exames complementares", on_click=avancar)


# -----------------------------
# ETAPA 2
# -----------------------------
elif st.session_state.etapa == 2:
    st.header("Etapa 2 — Refinamento com exames dirigidos")
    tipo = st.session_state.get("tipo")

    if not st.session_state.get("anemia", False):
        st.warning("Não há anemia confirmada na etapa anterior.")
    else:
        st.write(f"**Padrão em investigação:** {tipo}")

        if tipo == "Microcítica":
            with st.form("micro"):
                ferritina = st.number_input("Ferritina (ng/mL)", 0.0, 3000.0, 30.0, 0.1)
                ferro = st.number_input("Ferro sérico", 0.0, 500.0, 80.0, 0.1)
                tibc = st.number_input("TIBC", 0.0, 600.0, 300.0, 0.1)
                eletroforese_alterada = st.selectbox("Eletroforese de hemoglobina alterada?", ["Não realizada", "Não", "Sim"])
                enviar = st.form_submit_button("Refinar diagnóstico")

            if enviar:
                ist = calcular_ist(ferro, tibc)
                st.subheader("Resultado do refinamento")

                if ferritina < 30:
                    st.success("Diagnóstico provável: anemia por deficiência de ferro.")
                    st.write("- Ferritina baixa favorece ferropenia.")
                    if ist is not None:
                        st.write(f"- IST calculado: {ist:.1f}%")
                    st.write("**Próximos passos:**")
                    st.write("- Investigar sangramento menstrual ou gastrointestinal")
                    st.write("- Considerar ferro oral se indicado clinicamente")
                elif ist is not None and ist < 20:
                    st.success("Diagnóstico provável: deficiência de ferro, mesmo com ferritina não claramente baixa.")
                    st.write(f"- IST calculado: {ist:.1f}%")
                    st.write("- Lembrar que ferritina pode subir em inflamação.")
                elif eletroforese_alterada == "Sim":
                    st.success("Diagnóstico provável: hemoglobinopatia/talassemia.")
                    st.write("- Correlacionar com laudo da eletroforese.")
                else:
                    st.success("Padrão compatível com anemia de doença crônica/inflamatória.")
                    st.write("- Correlacionar com contexto clínico.")
                    st.write("- Considerar investigação inflamatória, infecciosa, renal ou neoplásica.")

        elif tipo == "Normocítica":
            with st.form("normo"):
                retic = st.number_input("Reticulócitos (%)", 0.0, 30.0, 1.0, 0.1)
                ferritina = st.number_input("Ferritina (ng/mL)", 0.0, 3000.0, 30.0, 0.1)
                ferro = st.number_input("Ferro sérico", 0.0, 500.0, 80.0, 0.1)
                tibc = st.number_input("TIBC", 0.0, 600.0, 300.0, 0.1)
                ldh = st.number_input("LDH", 0.0, 5000.0, 200.0, 1.0)
                bi = st.number_input("Bilirrubina indireta", 0.0, 20.0, 0.8, 0.1)
                haptoglobina = st.number_input("Haptoglobina", 0.0, 500.0, 100.0, 0.1)
                coombs = st.selectbox("Coombs direto", ["Negativo", "Positivo"])
                creatinina = st.number_input("Creatinina", 0.0, 15.0, 1.0, 0.1)
                tsh = st.number_input("TSH", 0.0, 50.0, 2.0, 0.1)
                enviar = st.form_submit_button("Refinar diagnóstico")

            if enviar:
                ht_base = obter_ht_base()

                if ht_base is None:
                    st.error("Hematócrito da etapa 1 não encontrado. Volte e preencha o hemograma inicial novamente.")
                else:
                    retic_corr = calcular_retic_corr(retic, ht_base)
                    rpi = calcular_rpi(retic_corr, ht_base)
                    ist = calcular_ist(ferro, tibc)

                    st.subheader("Resultado do refinamento")
                    st.write(f"- Reticulócito corrigido: {retic_corr:.2f}")
                    st.write(f"- RPI: {rpi:.2f}")
                    if ist is not None:
                        st.write(f"- IST: {ist:.1f}%")

                    if rpi >= 3:
                        if ldh > 250 and bi > 1.2 and haptoglobina < 50:
                            if coombs == "Positivo":
                                st.success("Diagnóstico provável: anemia hemolítica autoimune.")
                            else:
                                st.success("Diagnóstico provável: hemólise não imune.")
                            st.write("- Padrão laboratorial compatível com hemólise.")
                        else:
                            st.success("Padrão hiperproliferativo: considerar sangramento agudo/recente ou hemólise em investigação.")
                    else:
                        if ferritina < 30:
                            st.success("Diagnóstico provável: deficiência de ferro em fase inicial.")
                        elif ist is not None and ist < 20:
                            st.success("Diagnóstico provável: deficiência de ferro ou anemia inflamatória com ferropenia funcional.")
                        elif creatinina > 1.5:
                            st.success("Diagnóstico provável: anemia da doença renal crônica.")
                        elif tsh > 4:
                            st.success("Diagnóstico provável: anemia associada a hipotireoidismo.")
                        else:
                            st.success("Padrão compatível com anemia de doença crônica/inflamatória ou outra causa hipoproliferativa.")

        elif tipo == "Macrocítica":
            with st.form("macro"):
                retic = st.number_input("Reticulócitos (%)", 0.0, 30.0, 1.0, 0.1)
                b12 = st.number_input("Vitamina B12", 0.0, 5000.0, 400.0, 1.0)
                folato = st.number_input("Ácido fólico", 0.0, 50.0, 8.0, 0.1)
                ldh = st.number_input("LDH", 0.0, 5000.0, 200.0, 1.0)
                bi = st.number_input("Bilirrubina indireta", 0.0, 20.0, 0.8, 0.1)
                haptoglobina = st.number_input("Haptoglobina", 0.0, 500.0, 100.0, 0.1)
                coombs = st.selectbox("Coombs direto", ["Negativo", "Positivo"])
                alcool = st.checkbox("Uso importante de álcool")
                drogas = st.checkbox("Uso de drogas que causam macrocitose")
                tsh = st.number_input("TSH", 0.0, 50.0, 2.0, 0.1)
                enviar = st.form_submit_button("Refinar diagnóstico")

            if enviar:
                ht_base = obter_ht_base()

                if ht_base is None:
                    st.error("Hematócrito da etapa 1 não encontrado. Volte e preencha o hemograma inicial novamente.")
                else:
                    retic_corr = calcular_retic_corr(retic, ht_base)
                    rpi = calcular_rpi(retic_corr, ht_base)

                    st.subheader("Resultado do refinamento")
                    st.write(f"- Reticulócito corrigido: {retic_corr:.2f}")
                    st.write(f"- RPI: {rpi:.2f}")

                    if rpi >= 3:
                        if ldh > 250 and bi > 1.2 and haptoglobina < 50:
                            if coombs == "Positivo":
                                st.success("Diagnóstico provável: hemólise com macrocitose secundária à reticulocitose.")
                            else:
                                st.success("Diagnóstico provável: hemólise não imune com macrocitose secundária.")
                        else:
                            st.success("Macrocitose com padrão hiperproliferativo: considerar hemólise ou recuperação medular.")
                    else:
                        if b12 < 200:
                            st.success("Diagnóstico provável: deficiência de vitamina B12.")
                        elif folato < 4:
                            st.success("Diagnóstico provável: deficiência de ácido fólico.")
                        elif alcool:
                            st.success("Padrão compatível com macrocitose associada ao álcool.")
                        elif drogas:
                            st.success("Padrão compatível com macrocitose relacionada a medicação.")
                        elif tsh > 4:
                            st.success("Padrão compatível com macrocitose associada a hipotireoidismo.")
                        else:
                            st.success("Considerar hepatopatia, síndrome mielodisplásica ou outras causas de macrocitose.")

    col1, col2 = st.columns(2)
    with col1:
        st.button("⬅️ Voltar", on_click=voltar)
    with col2:
        st.button("Ir para resumo final ➡️", on_click=avancar)


# -----------------------------
# ETAPA 3
# -----------------------------
elif st.session_state.etapa == 3:
    st.header("Etapa 3 — Resumo do raciocínio")
    st.write("Resumo do que foi definido ao longo do fluxo.")

    if "sexo" in st.session_state:
        st.write(f"- Sexo: {st.session_state.sexo}")
    if "hb" in st.session_state:
        st.write(f"- Hb: {st.session_state.hb:.1f} g/dL")
    if "ht" in st.session_state:
        st.write(f"- Ht: {st.session_state.ht:.1f}%")
    if "vcm" in st.session_state:
        st.write(f"- VCM: {st.session_state.vcm:.1f} fL")
    if "tipo" in st.session_state:
        st.write(f"- Classificação morfológica: {st.session_state.tipo}")

    if st.session_state.get("anemia", False):
        st.info("Use este fluxo como apoio ao raciocínio. Correlacione sempre com clínica, esfregaço periférico e contexto do paciente.")
    else:
        st.success("Não houve anemia pelos critérios informados na etapa inicial.")

    col1, col2 = st.columns(2)
    with col1:
        st.button("⬅️ Voltar", on_click=voltar)
    with col2:
        st.button("🔄 Reiniciar caso", on_click=resetar)
