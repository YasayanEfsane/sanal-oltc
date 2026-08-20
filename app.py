import streamlit as st
import pandas as pd
import json
import plotly.graph_objects as go
from src.models import TransformerParams
from src.controller import ControllerParams
from src.simulation import run_simulation
from src.metrics import calculate_kpis
from src.reporting import generate_html_report

st.set_page_config(page_title="Sanal OLTC", layout="wide")

st.title("Sanal OLTC: Otomatik Kademe Değiştiricili Trafo Gerilim Regülatörü")

# Sidebar
st.sidebar.header("Transformatör Parametreleri")
nom_power = st.sidebar.number_input("Nominal Güç (kVA)", value=100.0)
nom_pri_v = st.sidebar.number_input("Primer Gerilimi (V)", value=34500.0)
nom_sec_v = st.sidebar.number_input("Sekonder Gerilimi (V)", value=400.0)
freq = st.sidebar.number_input("Frekans (Hz)", value=50.0)
r_pu = st.sidebar.number_input("Eşdeğer Direnç (pu)", value=0.01, format="%.4f")
x_pu = st.sidebar.number_input("Eşdeğer Reaktans (pu)", value=0.04, format="%.4f")
target_v = st.sidebar.number_input("Hedef Çıkış Gerilimi (pu)", value=1.00, format="%.2f")
tap_min = st.sidebar.number_input("Minimum Kademe", value=-8, step=1)
tap_max = st.sidebar.number_input("Maksimum Kademe", value=8, step=1)
tap_step = st.sidebar.number_input("Kademe Adımı (pu)", value=0.0125, format="%.4f")

st.sidebar.header("Denetleyici Parametreleri")
deadband = st.sidebar.number_input("Ölü Bant (±%)", value=1.5, format="%.2f")
delay_time = st.sidebar.number_input("Zaman Gecikmesi (s)", value=2.0)
min_time_taps = st.sidebar.number_input("Minimum Bekleme Süresi (s)", value=1.0)

st.sidebar.header("Senaryo Ayarları")
v_scenario = st.sidebar.selectbox("Giriş Gerilimi Senaryosu", ["Sabit", "Basamak", "Rampa", "Sinüzoidal", "Rastgele"], index=1)
l_scenario = st.sidebar.selectbox("Yük Senaryosu", ["Sabit", "Basamak", "Rampa", "TEİAŞ Günlük (Ölçekli)", "Rastgele"], index=0)
pf = st.sidebar.number_input("Güç Faktörü", value=0.90, min_value=0.0, max_value=1.0)
is_ind_str = st.sidebar.radio("Yük Tipi", ["Endüktif", "Kapasitif"])
is_inductive = (is_ind_str == "Endüktif")

st.sidebar.header("İşletme Modu")
parallel_mode = st.sidebar.selectbox("Çalışma Modu", ["Tek Trafo", "Bağımsız Paralel", "Lider-Takipçi Paralel"], index=0)

st.sidebar.header("Simülasyon Ayarları")
sim_time = st.sidebar.number_input("Simülasyon Süresi (s)", value=60.0)
dt_s = st.sidebar.number_input("Zaman Adımı (s)", value=0.1)

t_params = TransformerParams(
    nominal_power_kVA=nom_power, nominal_primary_V=nom_pri_v, nominal_secondary_V=nom_sec_v,
    frequency_Hz=freq, r_pu=r_pu, x_pu=x_pu, target_voltage_pu=target_v,
    tap_min=tap_min, tap_max=tap_max, tap_step_pu=tap_step
)
c_params = ControllerParams(deadband_percent=deadband, delay_time_s=delay_time, min_time_between_taps_s=min_time_taps)

df_results, df_events, events = run_simulation(
    t_params, c_params, sim_time, dt_s, v_scenario, l_scenario, pf, is_inductive, parallel_mode
)

kpis = calculate_kpis(df_results, target_v, deadband)
params_dict = {
    "transformer": t_params.__dict__,
    "controller": c_params.__dict__,
    "scenario": {"v_scenario": v_scenario, "l_scenario": l_scenario, "pf": pf, "is_inductive": is_inductive, "parallel_mode": parallel_mode}
}

df = df_results
p_mode = parallel_mode
    
tab1, tab2, tab3, tab4, tab5 = st.tabs(["Simülasyon", "Sonuçların Karşılaştırılması", "Olay Günlüğü", "Teorik Açıklama", "Proje Hakkında"])

with tab1:
    st.subheader("Performans Ölçütleri (KPI)")
    if p_mode == "Tek Trafo":
        c1, c2, c3, c4 = st.columns(4)
    else:
        c1, c2, c3, c4, c5 = st.columns(5)
        c5.metric("Maks. Sirkülasyon Akımı", f"{kpis['max_i_circ']:.3f} pu")
        
    c1.metric("Regülasyon İyileşmesi", f"% {kpis['improvement_percent']:.1f}")
    c2.metric("Toplam Kademe Hareketi", str(kpis['total_tap_changes']))
    c3.metric("Ölü Bant Dışında Süre", f"{kpis['time_out_of_deadband']:.1f} s")
    c4.metric("Min/Maks Çıkış (pu)", f"{kpis['min_v_out']:.3f} / {kpis['max_v_out']:.3f}")
    
    st.write("---")
    
    display_unit = st.radio("Grafik Gösterim Birimi", ["Per-Unit (pu)", "Gerçek Değer (V)"], horizontal=True)
    v_mult = nom_sec_v if display_unit == "Gerçek Değer (V)" else 1.0
    unit_label = "V" if display_unit == "Gerçek Değer (V)" else "pu"
    
    # Plotly Graphs
    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(x=df["Zaman (s)"], y=df["Kontrolsüz Çıkış (pu)"] * v_mult, name="Kontrolsüz Çıkış", line=dict(color="red", dash="dash")))
    fig1.add_trace(go.Scatter(x=df["Zaman (s)"], y=df["Kontrollü Çıkış (pu)"] * v_mult, name="Kontrollü Çıkış", line=dict(color="blue")))
    fig1.add_trace(go.Scatter(x=df["Zaman (s)"], y=[target_v * v_mult]*len(df), name="Hedef", line=dict(color="green")))
    fig1.add_trace(go.Scatter(x=df["Zaman (s)"], y=[(target_v + deadband/100)*v_mult]*len(df), name="Üst Sınır", line=dict(color="gray", dash="dot")))
    fig1.add_trace(go.Scatter(x=df["Zaman (s)"], y=[(target_v - deadband/100)*v_mult]*len(df), name="Alt Sınır", line=dict(color="gray", dash="dot")))
    fig1.update_layout(title="Çıkış Gerilimi Karşılaştırması", xaxis_title="Zaman (s)", yaxis_title=f"Gerilim ({unit_label})")
    st.plotly_chart(fig1, use_container_width=True)
    
    c_chart1, c_chart2 = st.columns(2)
    with c_chart1:
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=df["Zaman (s)"], y=df["Giriş Gerilimi (pu)"], name="Giriş Gerilimi"))
        fig2.update_layout(title="Giriş Gerilimi Profili", xaxis_title="Zaman (s)", yaxis_title="Gerilim (pu)")
        st.plotly_chart(fig2, use_container_width=True)
        
        fig4 = go.Figure()
        fig4.add_trace(go.Scatter(x=df["Zaman (s)"], y=df["Kontrollü Hata"], name="Hata", fill="tozeroy"))
        fig4.update_layout(title="Kontrollü Gerilim Hatası", xaxis_title="Zaman (s)", yaxis_title="Hata (pu)")
        st.plotly_chart(fig4, use_container_width=True)
        
        if p_mode != "Tek Trafo":
            fig6 = go.Figure()
            fig6.add_trace(go.Scatter(x=df["Zaman (s)"], y=df["Sirkülasyon Akımı (pu)"], name="Sirkülasyon Akımı", line=dict(color="orange"), fill="tozeroy"))
            fig6.update_layout(title="Trafolar Arası Sirkülasyon Akımı", xaxis_title="Zaman (s)", yaxis_title="Akım (pu)")
            st.plotly_chart(fig6, use_container_width=True)
        
    with c_chart2:
        fig3 = go.Figure()
        fig3.add_trace(go.Scatter(x=df["Zaman (s)"], y=df["Kademe 1"], name="Kademe (Trafo 1)", line_shape="hv", line=dict(width=3)))
        if p_mode != "Tek Trafo":
            fig3.add_trace(go.Scatter(x=df["Zaman (s)"], y=df["Kademe 2"], name="Kademe (Trafo 2)", line_shape="hv", line=dict(dash="dot", width=3)))
        fig3.update_layout(title="Kademe Konumu (Basamak Grafiği)", xaxis_title="Zaman (s)", yaxis_title="Konum")
        st.plotly_chart(fig3, use_container_width=True)
        
        fig5 = go.Figure()
        fig5.add_trace(go.Scatter(x=df["Zaman (s)"], y=df["Yük (pu)"], name="Yük", line_shape="hv"))
        fig5.update_layout(title="Yük Profili", xaxis_title="Zaman (s)", yaxis_title="Yük (pu)")
        st.plotly_chart(fig5, use_container_width=True)

with tab2:
    st.subheader("İstatistiksel Karşılaştırma")
    c1, c2 = st.columns(2)
    c1.metric("Kontrolsüz Maks. Sapma", f"{kpis['uncontrolled_max_dev']:.4f} pu")
    c1.metric("Kontrolsüz Ortalama Mutlak Hata", f"{kpis['uncontrolled_mae']:.4f} pu")
    
    c2.metric("Kontrollü Maks. Sapma", f"{kpis['controlled_max_dev']:.4f} pu", delta=f"{kpis['controlled_max_dev'] - kpis['uncontrolled_max_dev']:.4f} pu", delta_color="inverse")
    c2.metric("Kontrollü Ortalama Mutlak Hata", f"{kpis['controlled_mae']:.4f} pu", delta=f"{kpis['controlled_mae'] - kpis['uncontrolled_mae']:.4f} pu", delta_color="inverse")
    
    st.write("### Dışa Aktarma Seçenekleri")
    csv_results = df.to_csv(index=False).encode('utf-8')
    st.download_button("Sonuçları CSV İndir", data=csv_results, file_name="simulasyon_sonuclari.csv", mime="text/csv")
    
    json_params = json.dumps(params_dict, indent=4).encode('utf-8')
    st.download_button("Parametreleri JSON İndir", data=json_params, file_name="parametreler.json", mime="application/json")
    
    html_report = generate_html_report(params_dict, kpis).encode('utf-8')
    st.download_button("Raporu HTML İndir", data=html_report, file_name="sanal_oltc_rapor.html", mime="text/html")

with tab3:
    st.subheader("Kademe Değişimi Olay Günlüğü")
    if not df_events.empty:
        st.dataframe(df_events, use_container_width=True)
        csv_events = df_events.to_csv(index=False).encode('utf-8')
        st.download_button("Olay Günlüğünü CSV İndir", data=csv_events, file_name="olay_gunlugu.csv", mime="text/csv")
    else:
        st.info("Simülasyon boyunca herhangi bir kademe hareketi gerçekleşmedi.")

with tab4:
    st.subheader("Teorik Açıklama")
    st.markdown("""
    **Transformatör Dönüş Oranı & Kademe Değiştirme:** Transformatörün primer ve sekonder sargı sayılarının oranı, gerilim dönüştürme oranını belirler. Kademe (tap) değiştirici, sargı sayısını mekanik/elektriksel olarak değiştirerek dönüş oranını ayarlar. Pozitif kademe, sekonder gerilimini yükseltir.
    
    **Per-Unit (pu) Sistemi:** Elektrik güç sistemlerinde farklı gerilim seviyelerindeki ekipmanları ortak bir tabanda analiz edebilmek için büyüklüklerin nominal değerlerine bölünmesiyle elde edilen boyutsuz birim sistemidir (1.0 pu = %100).
    
    **Paralel Transformatörler ve Sirkülasyon Akımı:** İki veya daha fazla transformatör paralel bağlandığında, kademe konumları farklı olursa aralarında bir gerilim farkı oluşur. Bu fark, şebekeye veya yüke akmak yerine iki trafo arasında dönüp duran ve ısınmaya sebep olan bir "sirkülasyon akımı" (circulating current) yaratır. Master-Follower (Lider-Takipçi) kontrol modu, kademeleri senkronize ederek bunu önler. Bağımsız kontrol modunda ise tepki sürelerindeki ufak farklar bile bu akımın oluşmasına yol açar.
    
    **Ölü Bant (Deadband):** Çıkış geriliminin etrafında tanımlanan tolerans sınırıdır (örn. ±%1.5). Gerilim bu bant içindeyken denetleyici hiçbir düzeltme yapmaz. Bu, sürekli ve gereksiz kademe değişimini (chattering) önler.
    
    **Zaman Gecikmesi:** Gerilim ölü bant dışına çıktığında hemen tepki verilmez. Anlık dalgalanmaların kademe değişimine yol açmaması için beklenilen süredir.
    """)
    
with tab5:
    st.subheader("Proje Hakkında")
    st.markdown("""
    **Proje Adı:** Sanal OLTC: Otomatik Kademe Değiştiricili Trafo Gerilim Regülatörü
    
    Bu uygulama, tamamen bilgisayar ortamında çalışan eğitsel ve teorik bir simülasyondur. 
    Herhangi bir fiziksel donanıma (Arduino, sensör, röle) bağlı değildir. 
    
    **Geliştirme Amacı:** Elektrik-Elektronik Mühendisliği öğrencilerine ve ilgililerine, transformatörlerde otomatik gerilim regülasyonunun temel mantığını etkileşimli biçimde sunmaktır.
    
    **Gereksinimleri Karşılama:**
    Uygulama PEP 8 uyumlu Python kodu ile yazılmış olup Streamlit, Plotly, Pandas ve Numpy kullanılmıştır. Bütün matematiksel modeller, Unit Testler (pytest) ile doğrulanmış deterministik bir yapıdadır.
    """)
