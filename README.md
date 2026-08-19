<h1 align="center">
  Sanal OLTC ⚡
</h1>

<p align="center">
  <b>Otomatik Kademe Değiştiricili Trafo Gerilim Regülatörü Simülasyonu</b><br>
  (On-Load Tap Changer Voltage Regulator Simulation)
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12-blue.svg" alt="Python Version">
  <img src="https://img.shields.io/badge/Streamlit-1.30+-FF4B4B.svg" alt="Streamlit">
  <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License">
</p>

---

## 📖 Proje Hakkında

**Sanal OLTC**, bir güç transformatörünün sekonder gerilimini otomatik kademe değiştirici (OLTC) kullanarak regüle etme sürecini modelleyen, tamamen yazılımsal ve eğitsel bir simülasyon projesidir.

Gerçek donanımların getirdiği riskleri ve yüksek maliyetleri ortadan kaldırarak; mühendislerin, öğrencilerin ve araştırmacıların gerilim dalgalanmalarını, yük değişimlerini ve denetleyici algoritmalarının sisteme etkilerini interaktif bir şekilde gözlemlemesine olanak tanır. 

*Not: Bu projedeki "OLTC" ifadesi fiziksel bir cihazı değil, gerilim regülasyon davranışının matematiksel ve algoritmik modelini temsil eder.*

---

## ✨ Temel Özellikler

- **Analitik Matematiksel Model:** Elektromanyetik geçici rejim (EMT) çözücülerine veya ağır iterasyonlara gerek kalmadan, Per-Unit (pu) sistemi ve tam kapalı form kuadratik denklemlerle (RMS ve quasi-steady-state) %100 kararlı hesaplama.
- **Akıllı Denetleyici Algoritması:** Gerçek bir röle mantığında çalışan; Ölü Bant (Deadband), Zaman Gecikmesi (Time Delay) ve Minimum Bekleme Süresi parametreleriyle donatılmış kontrolcü.
- **Etkileşimli Senaryolar:** Şebeke gerilimi ve yük için Sabit, Basamak, Rampa, Sinüzoidal ve Rastgele dalgalanma senaryoları.
- **Endüktif ve Kapasitif Yük Desteği:** Güç faktörünün ve yük tipinin gerilim düşümüne (veya yükselmesine) olan yönlü etkisinin simülasyonu.
- **Detaylı Analitik:** Kontrollü ve kontrolsüz (şebekeye doğrudan bağlı) durumların saniye saniye karşılaştırması, Hata (MAE) analizleri ve KPI kartları.
- **Dışa Aktarma (Export):** Simülasyon sonuçlarını `CSV`, parametreleri `JSON`, performans raporunu `HTML` olarak indirebilme.

---

## 🛠️ Kurulum

Proje Python 3.12 (veya üzeri) gerektirmektedir.

**1. Depoyu klonlayın:**
```bash
git clone https://github.com/kullaniciadi/sanal-oltc.git
cd sanal-oltc
```

**2. Sanal ortam oluşturun ve aktif edin:**
```bash
# Windows için
python -m venv .venv
.venv\Scripts\activate

# Linux / macOS için
python3 -m venv .venv
source .venv/bin/activate
```

**3. Gerekli kütüphaneleri yükleyin:**
```bash
pip install -r requirements.txt
```

---

## 🚀 Kullanım

Projeyi çalıştırmak için terminalde şu komutu girin:

```bash
streamlit run app.py
```
*Varsayılan tarayıcınızda (genellikle http://localhost:8501 adresinde) uygulama otomatik olarak açılacaktır.*

### Arayüz Kullanımı
1. Sol menüden **Transformatör Parametrelerini** (Nominal güç, eşdeğer empedans, kademe adımı vb.) ayarlayın.
2. **Denetleyici Parametrelerini** (Ölü bant genişliği, gecikme süresi vb.) belirleyin.
3. Test etmek istediğiniz gerilim ve yük **Senaryolarını** seçin.
4. **Simülasyonu Çalıştır** butonuna tıklayın ve etkileşimli grafiklerin tadını çıkarın!

---

## 🧪 Testler

Uygulamanın matematiksel altyapısı ve denetleyici mantığı `pytest` kullanılarak birim testleriyle güvence altına alınmıştır. Testleri çalıştırmak için:

```bash
pytest -v
```

---

## 🧠 Nasıl Çalışıyor? (Teorik Arka Plan)

1. **Per-Unit Sistemi:** Bütün değerler (gerilim, empedans, güç) transformatörün nominal değerlerine bölünerek (1.0 pu = %100) standardize edilir.
2. **Gerilim Düşümü:** Yükün çektiği aktif ($P$) ve reaktif ($Q$) güç ile transformatörün iç direnci ($R$) ve reaktansı ($X$) kullanılarak çıkış gerilimi analitik formülle hesaplanır:
   $$v^2 + (2(PR + QX) - V_s^2)v + (P^2 + Q^2)(R^2 + X^2) = 0$$
3. **Kontrol Mantığı:** Çıkış gerilimi sürekli ölçülür. Gerilim **Ölü Bant** ($V_{hedef} \pm \%1.5$) dışına çıktığında zamanlayıcı başlar. Eğer hata durumu **Zaman Gecikmesi** boyunca kesintisiz devam ederse, kademe bir adım yukarı/aşağı hareket ettirilir. Mekanik aşınmayı önlemek için peş peşe hareketler arasında **Minimum Bekleme Süresi** uygulanır.

*(Gelişmiş mühendislik açıklamaları için uygulama içindeki **Teorik Açıklama** sekmesini inceleyebilirsiniz.)*

---

## 📜 Lisans

Bu proje **MIT Lisansı** altında lisanslanmıştır. Daha fazla bilgi için `LICENSE` dosyasına bakabilirsiniz. Herhangi bir ticari, akademik veya kişisel projede özgürce kullanabilirsiniz.
