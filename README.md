# E-Commerce API Data Ingestion & ETL Pipeline

## Disclaimer / Sorumluluk Reddi

### English
This project was developed strictly for **educational, practical, and non-commercial portfolio purposes**. 
* **No Commercial Intent:** This repository and script are not intended for commercial gain, resale, or profit-making activities.
* **No Data Distribution:** No scraped or extracted data from third-party platforms is hosted, redistributed, or publicly shared within this repository.
* **No Copyright Infringement:** All product names, trademarks, registered trademarks, and API structures mentioned or referenced belong to their respective owners. 
* **Liability:** The author assumes no liability for any misuse of this software or for any breaches of third-party terms of service by end users.

---

### Türkçe
Bu proje yalnızca **eğitim, kişisel gelişim ve ticari olmayan portföy amaçlarıyla** geliştirilmiştir.
* **Ticari Amac Bulunmamaktadır:** Bu depo (repository) ve kaynak kodları herhangi bir ticari kazanç, satış veya kâr amacı taşımamaktadır.
* **Veri Paylaşımı Yapılmamaktadır:** Üçüncü taraf platformlardan çekilen veya işlenen hiçbir veri bu depoda saklanmamakta, dağıtılmamakta ve kamuoyuyla paylaşılmamaktadır.
* **Telif Hakları:** Adı geçen veya referans gösterilen tüm ürün, marka ve API yapıları ilgili hak sahiplerine aittir.
* **Sorumluluk Reddi:** Yazılımın üçüncü şahıslar tarafından kullanımından veya kullanım koşullarının ihlalinden doğabilecek yasal sorumluluklar tamamen kullanıcıya aittir; proje sahibi hiçbir sorumluluk kabul etmez.

---

## Technical Overview / Teknik Özet

This script demonstrates a Python-based ETL (Extract, Transform, Load) pipeline that fetches product listing data via paginated REST API endpoints, parses metadata using regular expressions (Regex), normalizes floating-point numerical values (e.g., currency formatting), and dynamically ingests the structured output into a MySQL database.

Bu betik, sayfalanmış (paginated) REST API uç noktalarından ürün verilerini çeken, düzenli ifadeler (Regex) ile meta verileri ayrıştıran, sayısal değerleri (fiyat/ondalık) dönüştüren ve veriyi dinamik olarak MySQL veritabanına aktaran Python tabanlı bir ETL mimarisini sergilemektedir.
