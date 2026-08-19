import json
from typing import Dict, Any

def generate_html_report(params: Dict[str, Any], kpis: Dict[str, float]) -> str:
    html = f"""
    <html>
    <head>
        <meta charset="utf-8">
        <title>Sanal OLTC Simülasyon Raporu</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
            h1, h2 {{ color: #2c3e50; }}
            table {{ border-collapse: collapse; width: 100%; margin-bottom: 20px; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background-color: #f2f2f2; }}
            .summary {{ background-color: #e8f4f8; padding: 15px; border-radius: 5px; }}
        </style>
    </head>
    <body>
        <h1>Sanal OLTC: Otomatik Kademe Değiştiricili Trafo Gerilim Regülatörü</h1>
        
        <h2>Simülasyon Parametreleri</h2>
        <pre>{json.dumps(params, indent=4, ensure_ascii=False)}</pre>
        
        <h2>Performans Ölçütleri (KPIs)</h2>
        <table>
            <tr><th>Ölçüt</th><th>Değer</th></tr>
            <tr><td>Kontrolsüz Maks. Sapma</td><td>{kpis['uncontrolled_max_dev']:.4f} pu</td></tr>
            <tr><td>Kontrollü Maks. Sapma</td><td>{kpis['controlled_max_dev']:.4f} pu</td></tr>
            <tr><td>Kontrolsüz Ortalama Mutlak Hata</td><td>{kpis['uncontrolled_mae']:.4f} pu</td></tr>
            <tr><td>Kontrollü Ortalama Mutlak Hata</td><td>{kpis['controlled_mae']:.4f} pu</td></tr>
            <tr><td>Regülasyon İyileşmesi</td><td>% {kpis['improvement_percent']:.2f}</td></tr>
            <tr><td>Toplam Kademe Hareketi</td><td>{kpis['total_tap_changes']}</td></tr>
            <tr><td>Ölü Bant Dışında Kalma Süresi</td><td>{kpis['time_out_of_deadband']:.2f} s</td></tr>
            <tr><td>Min/Maks Çıkış Gerilimi</td><td>{kpis['min_v_out']:.4f} / {kpis['max_v_out']:.4f} pu</td></tr>
        </table>
        
        <h2>Otomatik Değerlendirme</h2>
        <div class="summary">
    """
    
    if kpis['improvement_percent'] > 0:
        html += f"<p>Otomatik kademe denetleyicisi, gerilim regülasyonunu %{kpis['improvement_percent']:.2f} oranında iyileştirmiştir.</p>"
    else:
        html += "<p>Otomatik kademe denetleyicisi gerilim regülasyonunda anlamlı bir iyileşme sağlayamamıştır. Parametreleri veya senaryoyu gözden geçirin.</p>"
        
    if kpis['time_out_of_deadband'] > 0:
        html += f"<p>Sistem toplamda {kpis['time_out_of_deadband']:.2f} saniye boyunca ölü bant dışında kalmıştır. Bu durum aşırı hızlı değişimlerden veya yetersiz kademe aralığından kaynaklanabilir.</p>"
        
    html += f"<p>Simülasyon boyunca toplam {kpis['total_tap_changes']} kez kademe değiştirilmiştir.</p>"
    
    html += """
        </div>
    </body>
    </html>
    """
    return html
