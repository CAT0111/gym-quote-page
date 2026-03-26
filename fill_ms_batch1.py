"""
Batch 1: Fill Malay translations for CD-001~CD-005, FS-001~FS-018, PL-001~PL-005
Run: python3 fill_ms_batch1.py
"""
import re

MS_TRANSLATIONS = {

"CD-001": {
    "badge_text_ms": "Kit alat ganti lengkap dihantar bersama peralatan",
    "spare_parts": [
        {"name_ms":"Tali Lari","qty_ms":"2 tali bagi setiap 5 unit","cycle_ms":"18-24 bulan"},
        {"name_ms":"Tali Pemacu","qty_ms":"2 tali bagi setiap 5 unit","cycle_ms":"24-36 bulan"},
        {"name_ms":"Papan Lari","qty_ms":"1 bagi setiap 5 unit","cycle_ms":"24-36 bulan"},
        {"name_ms":"Berus Karbon Motor","qty_ms":"1 pasang setiap unit","cycle_ms":"12-18 bulan"},
        {"name_ms":"Kunci Keselamatan","qty_ms":"2 setiap unit","cycle_ms":"Ganti apabila hilang/rosak"},
        {"name_ms":"Papan Kawalan Utama","qty_ms":"1 bagi setiap 5 unit","cycle_ms":"Gantian kecemasan"},
        {"name_ms":"Panel Paparan LED","qty_ms":"1 bagi setiap 5 unit","cycle_ms":"Gantian kecemasan"},
        {"name_ms":"Galas Penggelek","qty_ms":"2 set bagi setiap 5 unit","cycle_ms":"36+ bulan"},
        {"name_ms":"Jalur Anti-gelincir Rel Sisi","qty_ms":"3 pasang bagi setiap 5 unit","cycle_ms":"12 bulan"},
        {"name_ms":"Pelincir Silikon 500ml","qty_ms":"5 botol","cycle_ms":"Bahan guna habis"},
    ],
    "schedule": [
        {"interval_ms":"Setiap hari","action_ms":"Bersihkan habuk dan peluh dari permukaan tali lari"},
        {"interval_ms":"Setiap minggu","action_ms":"Lap sarung motor, uji fungsi kunci keselamatan"},
        {"interval_ms":"Setiap bulan","action_ms":"Sapukan pelincir silikon antara tali dan papan lari, periksa penjajaran dan ketegangan tali"},
        {"interval_ms":"Setiap suku tahun","action_ms":"Periksa kehausan berus karbon motor, periksa semua terminal pendawaian"},
        {"interval_ms":"Setiap setengah tahun","action_ms":"Periksa galas penggelek depan/belakang untuk bunyi bising, ketatkan semua bolt"},
    ],
    "durability_note_ms": "Motor DC 3.0HP gred komersial direka untuk operasi berterusan, mampu mengendalikan penggunaan harian 12+ jam dengan mudah. Sistem kawalan isyarat digital mencegah berhenti mengejut dan lari laju tanpa kawalan. Penggelek berdiameter besar 100mm memanjangkan hayat motor dan tali lari.",
},

"CD-002": {
    "badge_text_ms": "Kit alat ganti lengkap dihantar bersama peralatan",
    "spare_parts": [
        {"name_ms":"Tali Pemacu","qty_ms":"1 bagi setiap 2 unit","cycle_ms":"24-36 bulan"},
        {"name_ms":"Galas Pedal","qty_ms":"1 set bagi setiap 2 unit","cycle_ms":"24-36 bulan"},
        {"name_ms":"Penggelek Panduan","qty_ms":"1 set (4 biji) bagi setiap 2 unit","cycle_ms":"36 bulan"},
        {"name_ms":"Pad Anti-gelincir Pedal","qty_ms":"2 pasang","cycle_ms":"12 bulan"},
        {"name_ms":"Pad Sensor Kadar Jantung","qty_ms":"2 pasang","cycle_ms":"12-18 bulan"},
        {"name_ms":"Sarung Pemegang PU Foam","qty_ms":"1 pasang","cycle_ms":"24 bulan"},
    ],
    "schedule": [
        {"interval_ms":"Setiap hari","action_ms":"Lap peluh dari pemegang dan pedal (pemegang PU akan retak jika direndam peluh)"},
        {"interval_ms":"Setiap bulan","action_ms":"Periksa keketatan semua bolt"},
        {"interval_ms":"Setiap suku tahun","action_ms":"Sapukan gris litium pada galas pedal dan sendi penyambung"},
        {"interval_ms":"Setiap setengah tahun","action_ms":"Periksa ketegangan dan kehausan tali pemacu, periksa penggelek panduan"},
    ],
    "durability_note_ms": "Sistem rintangan magnet tanpa geseran sentuhan. Struktur pacuan roda belakang meminimumkan kehilangan transmisi. Direka untuk 8+ tahun penggunaan komersial berterusan.",
},

"CD-003": {
    "badge_text_ms": "Kit alat ganti lengkap dihantar bersama peralatan",
    "spare_parts": [
        {"name_ms":"Papan Langkah","qty_ms":"4 keping","cycle_ms":"18-24 bulan"},
        {"name_ms":"Rantai Langkah","qty_ms":"1 rantai","cycle_ms":"36 bulan"},
        {"name_ms":"Tali Pemacu","qty_ms":"1 tali","cycle_ms":"24-36 bulan"},
        {"name_ms":"Galas Aci Utama","qty_ms":"1 set (2 biji)","cycle_ms":"36 bulan"},
        {"name_ms":"Minyak Pelincir Rantai 250ml","qty_ms":"2 botol","cycle_ms":"Bahan guna habis"},
        {"name_ms":"Suis Sensor Keselamatan","qty_ms":"2 unit","cycle_ms":"Ganti apabila rosak"},
        {"name_ms":"Kit Skru Sarung","qty_ms":"2 set","cycle_ms":"Ganti apabila longgar"},
    ],
    "schedule": [
        {"interval_ms":"Setiap hari","action_ms":"Bersihkan permukaan papan langkah (habuk dalam alur anti-gelincir mengurangkan cengkaman)"},
        {"interval_ms":"Setiap bulan","action_ms":"Sapukan pelincir rantai"},
        {"interval_ms":"Setiap suku tahun","action_ms":"Periksa ketegangan tali pemacu"},
        {"interval_ms":"Setiap setengah tahun","action_ms":"Pemeriksaan penuh galas dan kehausan sproket"},
    ],
    "durability_note_ms": "Sarung acuan suntikan dibentuk satu keping, kukuh dan tahan ubah bentuk. Sistem pacuan rantai gred industri direka untuk operasi berterusan pada beban 160kg.",
},

"CD-004": {
    "badge_text_ms": "Rintangan magnet · Penyelenggaraan sangat rendah",
    "spare_parts": [
        {"name_ms":"Tali Pemacu","qty_ms":"1 tali","cycle_ms":"36 bulan"},
        {"name_ms":"Penggelek Rel Tempat Duduk","qty_ms":"1 set (4 biji)","cycle_ms":"24 bulan"},
        {"name_ms":"Sarung Tempat Duduk","qty_ms":"1 biji","cycle_ms":"18-24 bulan"},
        {"name_ms":"Tali Pengikat Pedal","qty_ms":"2 pasang","cycle_ms":"12 bulan"},
    ],
    "schedule": [
        {"interval_ms":"Setiap hari","action_ms":"Lap peluh dari tempat duduk dan sandaran"},
        {"interval_ms":"Setiap bulan","action_ms":"Periksa kelancaran rel tempat duduk"},
        {"interval_ms":"Setiap suku tahun","action_ms":"Sapukan gris pada rel dan galas pedal"},
    ],
    "durability_note_ms": "Rintangan magnet tanpa sentuhan fizikal, pelarasan rintangan tanpa kehausan. Reka bentuk berbaring menjadikan pusat graviti rendah dengan pengagihan tekanan struktur yang sekata. Hampir tiada titik kerosakan. Sesuai untuk penggunaan komersial berfrekuensi tinggi dan berpanjangan.",
},

"CD-005": {
    "badge_text_ms": "Struktur mekanikal tulen · Titik kerosakan minimum",
    "spare_parts": [
        {"name_ms":"Rantai Pemacu","qty_ms":"1 rantai","cycle_ms":"36 bulan"},
        {"name_ms":"Tali Pengikat/Klip Pedal","qty_ms":"1 pasang","cycle_ms":"12 bulan"},
        {"name_ms":"Sarung Tempat Duduk","qty_ms":"1 biji","cycle_ms":"18 bulan"},
        {"name_ms":"Minyak Rantai 250ml","qty_ms":"1 botol","cycle_ms":"Bahan guna habis"},
    ],
    "schedule": [
        {"interval_ms":"Setiap minggu","action_ms":"Bersihkan habuk dari bilah kipas (habuk terkumpul menjejaskan keseragaman rintangan angin)"},
        {"interval_ms":"Setiap bulan","action_ms":"Minyakkan rantai pemacu"},
        {"interval_ms":"Setiap suku tahun","action_ms":"Ketatkan semua bolt"},
    ],
    "durability_note_ms": "Basikal rintangan angin ini tiada elektronik, tiada motor, tiada tali — rintangan datang sepenuhnya daripada udara. Semakin ringkas strukturnya, semakin tahan lama. Kadar kerosakan basikal ini hampir sifar.",
},

"FS-001": {
    "badge_text_ms": "Kit alat ganti lengkap dihantar bersama peralatan",
    "spare_parts": [
        {"name_ms":"Kabel Keluli Bersalut","qty_ms":"Dipotong dari gulungan pukal 50m","cycle_ms":"18-24 bulan"},
        {"name_ms":"Takal dengan Galas","qty_ms":"Dari stok alat ganti universal","cycle_ms":"24-36 bulan"},
        {"name_ms":"Pin Pemilih Berat","qty_ms":"Dari stok alat ganti universal","cycle_ms":"12 bulan"},
        {"name_ms":"Sesendal Panduan","qty_ms":"Dari stok alat ganti universal","cycle_ms":"12-18 bulan"},
        {"name_ms":"Galas Sfera","qty_ms":"Dari stok alat ganti universal","cycle_ms":"24-36 bulan"},
        {"name_ms":"Sarung Span Pemegang","qty_ms":"Dari stok alat ganti universal","cycle_ms":"6-12 bulan"},
        {"name_ms":"Pad Tempat Duduk","qty_ms":"Dari stok alat ganti universal","cycle_ms":"18-24 bulan"},
    ],
    "schedule": [
        {"interval_ms":"Setiap hari","action_ms":"Lap peluh dari pad tempat duduk dan pemegang"},
        {"interval_ms":"Setiap minggu","action_ms":"Periksa spring pemulangan pin berat, periksa kabel keluli secara visual"},
        {"interval_ms":"Setiap bulan","action_ms":"Sapukan gris litium putih pada rod panduan tindanan berat"},
        {"interval_ms":"Setiap suku tahun","action_ms":"Periksa kelancaran putaran takal, griskan galas sfera"},
        {"interval_ms":"Setiap setengah tahun","action_ms":"Ketatkan semua bolt dengan sepana tork, periksa salutan kabel"},
    ],
    "durability_note_ms": "Semua alat ganti datang dari stok alat ganti universal. Sebarang kerosakan komponen tunggal boleh diganti dengan cepat di lokasi — tiada perlu menunggu penghantaran dari luar negara.",
},

"FS-002": {
    "badge_text_ms": "Kit alat ganti lengkap dihantar bersama peralatan",
    "spare_parts": [
        {"name_ms":"Kabel Keluli Bersalut","qty_ms":"Stok universal","cycle_ms":"18-24 bulan"},
        {"name_ms":"Takal dengan Galas","qty_ms":"Stok universal","cycle_ms":"24-36 bulan"},
        {"name_ms":"Pin Pemilih Berat","qty_ms":"Stok universal","cycle_ms":"12 bulan"},
        {"name_ms":"Sesendal Panduan","qty_ms":"Stok universal","cycle_ms":"12-18 bulan"},
        {"name_ms":"Galas Sfera","qty_ms":"Stok universal","cycle_ms":"24-36 bulan"},
        {"name_ms":"Sarung Span Pemegang","qty_ms":"Stok universal","cycle_ms":"6-12 bulan"},
        {"name_ms":"Pad Tempat Duduk/Sandaran","qty_ms":"Stok universal","cycle_ms":"18-24 bulan"},
    ],
    "schedule": [
        {"interval_ms":"Setiap hari","action_ms":"Lap peluh dari pad tempat duduk dan pemegang"},
        {"interval_ms":"Setiap minggu","action_ms":"Periksa spring pemulangan pin berat, periksa kabel keluli secara visual"},
        {"interval_ms":"Setiap bulan","action_ms":"Sapukan gris pada rod panduan tindanan berat"},
        {"interval_ms":"Setiap suku tahun","action_ms":"Periksa takal dan galas sfera"},
        {"interval_ms":"Setiap setengah tahun","action_ms":"Ketatkan semua bolt, pemeriksaan penuh kabel"},
    ],
    "durability_note_ms": "Struktur pin-loaded gred komersial. Rod panduan tindanan berat disalut krom keras, hayat kehausan melebihi 500,000 kitaran gerakan.",
},

"FS-003": {
    "badge_text_ms": "Kit alat ganti lengkap dihantar bersama peralatan",
    "spare_parts": [
        {"name_ms":"Kabel Keluli Bersalut","qty_ms":"Stok universal","cycle_ms":"18-24 bulan"},
        {"name_ms":"Takal dengan Galas","qty_ms":"Stok universal","cycle_ms":"24-36 bulan"},
        {"name_ms":"Pin Pemilih Berat","qty_ms":"Stok universal","cycle_ms":"12 bulan"},
        {"name_ms":"Sesendal Panduan","qty_ms":"Stok universal","cycle_ms":"12-18 bulan"},
        {"name_ms":"Galas Sfera","qty_ms":"Stok universal","cycle_ms":"24-36 bulan"},
        {"name_ms":"Sarung Span Pemegang","qty_ms":"Stok universal","cycle_ms":"6-12 bulan"},
        {"name_ms":"Pad Tempat Duduk/Sandaran","qty_ms":"Stok universal","cycle_ms":"18-24 bulan"},
    ],
    "schedule": [
        {"interval_ms":"Setiap hari","action_ms":"Lap peluh dari pad tempat duduk dan pemegang"},
        {"interval_ms":"Setiap minggu","action_ms":"Periksa pin pemilih dan kabel keluli"},
        {"interval_ms":"Setiap bulan","action_ms":"Pelinciran rod panduan"},
        {"interval_ms":"Setiap suku tahun","action_ms":"Periksa takal dan galas"},
        {"interval_ms":"Setiap setengah tahun","action_ms":"Pemeriksaan penuh pengetatan bolt"},
    ],
    "durability_note_ms": "Pemegang boleh laras menggunakan mekanisme pengunci gred industri — tiada kelonggaran selepas 100,000 pelarasan. Laluan kabel menggunakan reka bentuk jejari besar untuk mengurangkan kehausan lenturan.",
},

"FS-004": {
    "badge_text_ms": "Kit alat ganti lengkap dihantar bersama peralatan",
    "spare_parts": [
        {"name_ms":"Kabel Keluli Bersalut","qty_ms":"Stok universal","cycle_ms":"18-24 bulan"},
        {"name_ms":"Takal dengan Galas","qty_ms":"Stok universal","cycle_ms":"24-36 bulan"},
        {"name_ms":"Pin Pemilih Berat","qty_ms":"Stok universal","cycle_ms":"12 bulan"},
        {"name_ms":"Sarung Span Pemegang","qty_ms":"Stok universal","cycle_ms":"6-12 bulan"},
        {"name_ms":"Pad Siku","qty_ms":"Stok universal","cycle_ms":"18-24 bulan"},
    ],
    "schedule": [
        {"interval_ms":"Setiap hari","action_ms":"Lap peluh dari pad siku dan pemegang"},
        {"interval_ms":"Setiap minggu","action_ms":"Periksa pin pemilih"},
        {"interval_ms":"Setiap bulan","action_ms":"Pelinciran rod panduan"},
        {"interval_ms":"Setiap suku tahun","action_ms":"Periksa takal dan galas"},
        {"interval_ms":"Setiap setengah tahun","action_ms":"Ketatkan semua bolt"},
    ],
    "durability_note_ms": "Mesin pengasingan sendi tunggal dengan laluan transmisi pendek dan dinamik daya yang ringkas — salah satu jenis kadar kerosakan paling rendah antara semua peralatan pin-loaded.",
},

"FS-005": {
    "badge_text_ms": "Kit alat ganti lengkap dihantar bersama peralatan",
    "spare_parts": [
        {"name_ms":"Kabel Keluli Bersalut","qty_ms":"Stok universal","cycle_ms":"18-24 bulan"},
        {"name_ms":"Takal dengan Galas","qty_ms":"Stok universal","cycle_ms":"24-36 bulan"},
        {"name_ms":"Pin Pemilih Berat","qty_ms":"Stok universal","cycle_ms":"12 bulan"},
        {"name_ms":"Pin Spring Laras Pantas","qty_ms":"3 set dari stok universal","cycle_ms":"12 bulan"},
        {"name_ms":"Pad Penggelek PU","qty_ms":"Stok universal","cycle_ms":"12-18 bulan"},
        {"name_ms":"Pad Telungkup","qty_ms":"Stok universal","cycle_ms":"18-24 bulan"},
    ],
    "schedule": [
        {"interval_ms":"Setiap hari","action_ms":"Lap peluh dari pad telungkup"},
        {"interval_ms":"Setiap minggu","action_ms":"Periksa pin pemilih dan kunci laras pantas"},
        {"interval_ms":"Setiap bulan","action_ms":"Pelinciran rod panduan, periksa kehausan pad penggelek PU"},
        {"interval_ms":"Setiap suku tahun","action_ms":"Periksa takal dan galas"},
        {"interval_ms":"Setiap setengah tahun","action_ms":"Ketatkan semua bolt"},
    ],
    "durability_note_ms": "Kunci laras pantas menggunakan mekanisme pin kunci spring. Stok alat ganti mencukupi — penggantian hanya mengambil 30 saat apabila diperlukan.",
},

"FS-006": {
    "badge_text_ms": "Kit alat ganti lengkap dihantar bersama peralatan",
    "spare_parts": [
        {"name_ms":"Kabel Keluli Bersalut","qty_ms":"Stok universal","cycle_ms":"18-24 bulan"},
        {"name_ms":"Takal dengan Galas","qty_ms":"Stok universal","cycle_ms":"24-36 bulan"},
        {"name_ms":"Pin Pemilih Berat","qty_ms":"Stok universal","cycle_ms":"12 bulan"},
        {"name_ms":"Pin Spring Laras Pantas","qty_ms":"Stok universal","cycle_ms":"12 bulan"},
        {"name_ms":"Pad Penggelek PU","qty_ms":"Stok universal","cycle_ms":"12-18 bulan"},
        {"name_ms":"Pad Tempat Duduk/Sandaran","qty_ms":"Stok universal","cycle_ms":"18-24 bulan"},
    ],
    "schedule": [
        {"interval_ms":"Setiap hari","action_ms":"Lap peluh dari pad tempat duduk"},
        {"interval_ms":"Setiap minggu","action_ms":"Periksa pin pemilih dan kunci laras pantas"},
        {"interval_ms":"Setiap bulan","action_ms":"Pelinciran rod panduan"},
        {"interval_ms":"Setiap suku tahun","action_ms":"Periksa takal"},
        {"interval_ms":"Setiap setengah tahun","action_ms":"Ketatkan semua bolt"},
    ],
    "durability_note_ms": "Berkongsi alat ganti kunci laras pantas spesifikasi sama dengan prone leg curl — sandaran redundansi bersama.",
},

"FS-007": {
    "badge_text_ms": "Kit alat ganti lengkap dihantar bersama peralatan",
    "spare_parts": [
        {"name_ms":"Kabel Keluli Bersalut","qty_ms":"Stok universal","cycle_ms":"18-24 bulan"},
        {"name_ms":"Takal dengan Galas","qty_ms":"Stok universal","cycle_ms":"24-36 bulan"},
        {"name_ms":"Pin Pemilih Berat","qty_ms":"Stok universal","cycle_ms":"12 bulan"},
        {"name_ms":"Galas Sfera","qty_ms":"Stok universal","cycle_ms":"24-36 bulan"},
        {"name_ms":"Pad Kaki","qty_ms":"Stok universal","cycle_ms":"18-24 bulan"},
        {"name_ms":"Pad Tempat Duduk/Sandaran","qty_ms":"Stok universal","cycle_ms":"18-24 bulan"},
    ],
    "schedule": [
        {"interval_ms":"Setiap hari","action_ms":"Lap peluh dari semua permukaan sentuhan"},
        {"interval_ms":"Setiap minggu","action_ms":"Periksa pin pemilih"},
        {"interval_ms":"Setiap bulan","action_ms":"Pelinciran rod panduan, periksa mekanisme suis dalam/luar"},
        {"interval_ms":"Setiap suku tahun","action_ms":"Griskan galas sfera"},
        {"interval_ms":"Setiap setengah tahun","action_ms":"Ketatkan semua bolt"},
    ],
    "durability_note_ms": "Satu mesin bertukar antara paha dalam/luar dengan sandaran boleh laras. Mekanisme penukaran menggunakan kunci rak-dan-pinion — tiada kelonggaran selepas 100,000 penukaran.",
},

"FS-008": {
    "badge_text_ms": "Kit alat ganti lengkap dihantar bersama peralatan",
    "spare_parts": [
        {"name_ms":"Kabel Keluli Bersalut","qty_ms":"Stok universal (unit ini menggunakan kabel lebih panjang, ~4-5m)","cycle_ms":"18-24 bulan"},
        {"name_ms":"Takal dengan Galas","qty_ms":"Stok universal (unit ini menggunakan 6-8 takal)","cycle_ms":"24-36 bulan"},
        {"name_ms":"Pin Pemilih Berat","qty_ms":"Stok universal","cycle_ms":"12 bulan"},
        {"name_ms":"Pin Ratchet Laras Ketinggian","qty_ms":"2 biji","cycle_ms":"12-18 bulan"},
        {"name_ms":"Lampiran Pemegang","qty_ms":"1 set","cycle_ms":"Ganti apabila haus"},
        {"name_ms":"Pad Tempat Duduk","qty_ms":"Stok universal","cycle_ms":"18-24 bulan"},
    ],
    "schedule": [
        {"interval_ms":"Setiap hari","action_ms":"Lap peluh dari pad tempat duduk"},
        {"interval_ms":"Setiap minggu","action_ms":"Periksa pin pemilih dan kunci laras ketinggian"},
        {"interval_ms":"Setiap bulan","action_ms":"Pelinciran rod panduan, periksa kabel (laluan paling panjang — fokus pada titik lenturan)"},
        {"interval_ms":"Setiap suku tahun","action_ms":"Periksa semua takal satu per satu"},
        {"interval_ms":"Setiap setengah tahun","action_ms":"Ketatkan semua bolt"},
    ],
    "durability_note_ms": "Pelarasan takal tinggi-rendah tanpa had — peralatan tunggal paling serba guna. Laluan kabel panjang tetapi menggunakan kumpulan takal jejari besar, meminimumkan tekanan lenturan.",
},

"FS-009": {
    "badge_text_ms": "Kit alat ganti lengkap dihantar bersama peralatan",
    "spare_parts": [
        {"name_ms":"Kabel Keluli Bersalut","qty_ms":"Stok universal","cycle_ms":"18-24 bulan"},
        {"name_ms":"Takal dengan Galas","qty_ms":"Stok universal","cycle_ms":"24-36 bulan"},
        {"name_ms":"Pin Pemilih Berat","qty_ms":"Stok universal","cycle_ms":"12 bulan"},
        {"name_ms":"Galas Sfera","qty_ms":"Stok universal","cycle_ms":"24-36 bulan"},
        {"name_ms":"Sarung Span Pemegang","qty_ms":"Stok universal","cycle_ms":"6-12 bulan"},
    ],
    "schedule": [
        {"interval_ms":"Setiap hari","action_ms":"Lap peluh dari pemegang"},
        {"interval_ms":"Setiap minggu","action_ms":"Periksa pin pemilih"},
        {"interval_ms":"Setiap bulan","action_ms":"Pelinciran rod panduan"},
        {"interval_ms":"Setiap suku tahun","action_ms":"Periksa takal dan galas sfera"},
        {"interval_ms":"Setiap setengah tahun","action_ms":"Ketatkan semua bolt"},
    ],
    "durability_note_ms": "Naik taraf Gen 2, berat bersih 268kg — kestabilan sangat tinggi. Dua tindanan berat beroperasi secara bebas tanpa gangguan antara satu sama lain.",
},

"FS-010": {
    "badge_text_ms": "Kit alat ganti lengkap dihantar bersama peralatan",
    "spare_parts": [
        {"name_ms":"Kabel Keluli Bersalut","qty_ms":"Stok universal","cycle_ms":"18-24 bulan"},
        {"name_ms":"Takal dengan Galas","qty_ms":"Stok universal","cycle_ms":"24-36 bulan"},
        {"name_ms":"Pin Pemilih Berat","qty_ms":"Stok universal","cycle_ms":"12 bulan"},
        {"name_ms":"Pad Lengan","qty_ms":"Stok universal","cycle_ms":"18-24 bulan"},
    ],
    "schedule": [
        {"interval_ms":"Setiap hari","action_ms":"Lap peluh dari pad lengan"},
        {"interval_ms":"Setiap minggu","action_ms":"Periksa pin pemilih"},
        {"interval_ms":"Setiap bulan","action_ms":"Pelinciran rod panduan"},
        {"interval_ms":"Setiap suku tahun","action_ms":"Periksa takal"},
        {"interval_ms":"Setiap setengah tahun","action_ms":"Ketatkan semua bolt"},
    ],
    "durability_note_ms": "Mesin pengasingan sendi tunggal dengan laluan transmisi paling pendek dan struktur paling ringkas — kadar kerosakan sangat rendah.",
},

"FS-011": {
    "badge_text_ms": "Kit alat ganti lengkap dihantar bersama peralatan",
    "spare_parts": [
        {"name_ms":"Kabel Keluli Bersalut","qty_ms":"Stok universal (lengan berkembar, 1 kabel setiap satu)","cycle_ms":"18-24 bulan"},
        {"name_ms":"Takal dengan Galas","qty_ms":"Stok universal (unit ini mempunyai takal paling banyak)","cycle_ms":"24-36 bulan"},
        {"name_ms":"Pin Pemilih Berat","qty_ms":"Stok universal","cycle_ms":"12 bulan"},
        {"name_ms":"Galas Sfera","qty_ms":"Stok universal","cycle_ms":"24-36 bulan"},
        {"name_ms":"Sarung Span Pemegang","qty_ms":"Stok universal","cycle_ms":"6-12 bulan"},
        {"name_ms":"Pad Penahan Paha","qty_ms":"Stok universal","cycle_ms":"18-24 bulan"},
    ],
    "schedule": [
        {"interval_ms":"Setiap hari","action_ms":"Lap peluh dari tempat duduk dan pad paha"},
        {"interval_ms":"Setiap minggu","action_ms":"Periksa pin pemilih dan kabel keluli"},
        {"interval_ms":"Setiap bulan","action_ms":"Pelinciran rod panduan"},
        {"interval_ms":"Setiap suku tahun","action_ms":"Periksa semua takal satu per satu (unit ini mempunyai takal paling banyak)"},
        {"interval_ms":"Setiap setengah tahun","action_ms":"Ketatkan semua bolt"},
    ],
    "durability_note_ms": "Reka bentuk lengan bebas diverging dengan tindanan berat kiri/kanan berasingan. Ketinggian 2520mm dengan rangka utama tiub persegi tebal tambahan — kestabilan cemerlang.",
},

"FS-012": {
    "badge_text_ms": "Kit alat ganti lengkap dihantar bersama peralatan",
    "spare_parts": [
        {"name_ms":"Kabel Keluli Bersalut","qty_ms":"Stok universal","cycle_ms":"18-24 bulan"},
        {"name_ms":"Takal dengan Galas","qty_ms":"Stok universal","cycle_ms":"24-36 bulan"},
        {"name_ms":"Pin Pemilih Berat","qty_ms":"Stok universal","cycle_ms":"12 bulan"},
        {"name_ms":"Sarung Span Pemegang","qty_ms":"Stok universal","cycle_ms":"6-12 bulan"},
        {"name_ms":"Pad Tempat Duduk/Sandaran","qty_ms":"Stok universal","cycle_ms":"18-24 bulan"},
    ],
    "schedule": [
        {"interval_ms":"Setiap hari","action_ms":"Lap peluh dari pad tempat duduk"},
        {"interval_ms":"Setiap minggu","action_ms":"Periksa pin pemilih"},
        {"interval_ms":"Setiap bulan","action_ms":"Pelinciran rod panduan"},
        {"interval_ms":"Setiap suku tahun","action_ms":"Periksa takal dan galas"},
        {"interval_ms":"Setiap setengah tahun","action_ms":"Ketatkan semua bolt"},
    ],
    "durability_note_ms": "Mesin tekan bahu mempunyai arah daya menegak ke atas — kehausan rod panduan paling minimum, hayat rod panduan paling lama antara semua peralatan pin-loaded.",
},

"FS-013": {
    "badge_text_ms": "Kit alat ganti lengkap dihantar bersama peralatan",
    "spare_parts": [
        {"name_ms":"Kabel Keluli Bersalut","qty_ms":"Stok universal","cycle_ms":"18-24 bulan"},
        {"name_ms":"Takal dengan Galas","qty_ms":"Stok universal","cycle_ms":"24-36 bulan"},
        {"name_ms":"Pin Pemilih Berat","qty_ms":"Stok universal","cycle_ms":"12 bulan"},
        {"name_ms":"Galas Sfera","qty_ms":"Stok universal","cycle_ms":"24-36 bulan"},
        {"name_ms":"Sarung Span Pemegang","qty_ms":"Stok universal","cycle_ms":"6-12 bulan"},
        {"name_ms":"Pad Dada","qty_ms":"Stok universal","cycle_ms":"18-24 bulan"},
    ],
    "schedule": [
        {"interval_ms":"Setiap hari","action_ms":"Lap peluh dari pad dada"},
        {"interval_ms":"Setiap minggu","action_ms":"Periksa pin pemilih dan kabel keluli"},
        {"interval_ms":"Setiap bulan","action_ms":"Pelinciran rod panduan"},
        {"interval_ms":"Setiap suku tahun","action_ms":"Periksa takal dan galas sfera"},
        {"interval_ms":"Setiap setengah tahun","action_ms":"Ketatkan semua bolt"},
    ],
    "durability_note_ms": "Lengan bebas diverging membetulkan ketidakseimbangan kekuatan kiri/kanan. Dua tindanan berat beroperasi secara bebas — kerosakan satu sisi tidak menjejaskan sisi yang lain.",
},

"FS-014": {
    "badge_text_ms": "Kit alat ganti lengkap dihantar bersama peralatan",
    "spare_parts": [
        {"name_ms":"Kabel Keluli Bersalut","qty_ms":"Stok universal","cycle_ms":"18-24 bulan"},
        {"name_ms":"Takal dengan Galas","qty_ms":"Stok universal","cycle_ms":"24-36 bulan"},
        {"name_ms":"Pin Pemilih Berat","qty_ms":"Stok universal","cycle_ms":"12 bulan"},
        {"name_ms":"Galas Sfera","qty_ms":"Stok universal","cycle_ms":"24-36 bulan"},
        {"name_ms":"Sarung Span Pemegang","qty_ms":"Stok universal","cycle_ms":"6-12 bulan"},
        {"name_ms":"Pad Tempat Duduk/Sandaran","qty_ms":"Stok universal","cycle_ms":"18-24 bulan"},
    ],
    "schedule": [
        {"interval_ms":"Setiap hari","action_ms":"Lap peluh dari pad tempat duduk"},
        {"interval_ms":"Setiap minggu","action_ms":"Periksa pin pemilih"},
        {"interval_ms":"Setiap bulan","action_ms":"Pelinciran rod panduan"},
        {"interval_ms":"Setiap suku tahun","action_ms":"Periksa takal dan galas"},
        {"interval_ms":"Setiap setengah tahun","action_ms":"Ketatkan semua bolt"},
    ],
    "durability_note_ms": "Sudut super-incline dikunci dengan tepat. Rak pelarasan sudut dikarburkan ke kekerasan HRC58+ — tiada kehausan selepas berpuluh ribu pelarasan.",
},

"FS-015": {
    "badge_text_ms": "Kit alat ganti lengkap dihantar bersama peralatan",
    "spare_parts": [
        {"name_ms":"Kabel Keluli Bersalut","qty_ms":"Stok universal","cycle_ms":"18-24 bulan"},
        {"name_ms":"Takal dengan Galas","qty_ms":"Stok universal","cycle_ms":"24-36 bulan"},
        {"name_ms":"Pin Pemilih Berat","qty_ms":"Stok universal","cycle_ms":"12 bulan"},
        {"name_ms":"Galas Sfera","qty_ms":"Stok universal","cycle_ms":"24-36 bulan"},
        {"name_ms":"Sarung Span Pemegang","qty_ms":"Stok universal","cycle_ms":"6-12 bulan"},
        {"name_ms":"Pad Tempat Duduk/Sandaran","qty_ms":"Stok universal","cycle_ms":"18-24 bulan"},
    ],
    "schedule": [
        {"interval_ms":"Setiap hari","action_ms":"Lap peluh dari pad tempat duduk"},
        {"interval_ms":"Setiap minggu","action_ms":"Periksa pin pemilih"},
        {"interval_ms":"Setiap bulan","action_ms":"Pelinciran rod panduan"},
        {"interval_ms":"Setiap suku tahun","action_ms":"Periksa takal dan galas"},
        {"interval_ms":"Setiap setengah tahun","action_ms":"Ketatkan semua bolt"},
    ],
    "durability_note_ms": "Trajektori gerakan sudut lebar mengenakan daya sisi yang lebih tinggi pada galas sfera. Galas sfera tambahan telah disimpan dalam inventori alat ganti universal untuk jenis ini.",
},

"FS-016": {
    "badge_text_ms": "Kit alat ganti lengkap dihantar bersama peralatan",
    "spare_parts": [
        {"name_ms":"Kabel Keluli Bersalut","qty_ms":"Stok universal","cycle_ms":"18-24 bulan"},
        {"name_ms":"Takal dengan Galas","qty_ms":"Stok universal","cycle_ms":"24-36 bulan"},
        {"name_ms":"Pin Pemilih Berat","qty_ms":"Stok universal","cycle_ms":"12 bulan"},
        {"name_ms":"Sarung Span Pemegang","qty_ms":"Stok universal","cycle_ms":"6-12 bulan"},
        {"name_ms":"Pad Tempat Duduk","qty_ms":"Stok universal","cycle_ms":"18-24 bulan"},
    ],
    "schedule": [
        {"interval_ms":"Setiap hari","action_ms":"Lap peluh dari pad tempat duduk dan pemegang"},
        {"interval_ms":"Setiap minggu","action_ms":"Periksa pin pemilih"},
        {"interval_ms":"Setiap bulan","action_ms":"Pelinciran rod panduan"},
        {"interval_ms":"Setiap suku tahun","action_ms":"Periksa takal"},
        {"interval_ms":"Setiap setengah tahun","action_ms":"Ketatkan semua bolt"},
    ],
    "durability_note_ms": "Tricep dip mempunyai julat gerakan pendek dan beban berat ringan. Kabel dan takal mengalami tekanan paling sedikit — salah satu mesin pin-loaded paling tahan lama di gim.",
},

"FS-017": {
    "badge_text_ms": "Kit alat ganti lengkap dihantar bersama peralatan",
    "spare_parts": [
        {"name_ms":"Kabel Keluli Bersalut","qty_ms":"Stok universal","cycle_ms":"18-24 bulan"},
        {"name_ms":"Takal dengan Galas","qty_ms":"Stok universal","cycle_ms":"24-36 bulan"},
        {"name_ms":"Pin Pemilih Berat","qty_ms":"Stok universal","cycle_ms":"12 bulan"},
        {"name_ms":"Galas Sfera","qty_ms":"Stok universal","cycle_ms":"24-36 bulan"},
        {"name_ms":"Sarung Span Pemegang","qty_ms":"Stok universal","cycle_ms":"6-12 bulan"},
        {"name_ms":"Pad Tempat Duduk/Sandaran","qty_ms":"Stok universal","cycle_ms":"18-24 bulan"},
    ],
    "schedule": [
        {"interval_ms":"Setiap hari","action_ms":"Lap peluh dari pad tempat duduk"},
        {"interval_ms":"Setiap minggu","action_ms":"Periksa pin pemilih"},
        {"interval_ms":"Setiap bulan","action_ms":"Pelinciran rod panduan"},
        {"interval_ms":"Setiap suku tahun","action_ms":"Periksa takal dan galas"},
        {"interval_ms":"Setiap setengah tahun","action_ms":"Ketatkan semua bolt"},
    ],
    "durability_note_ms": "Reka bentuk sudut decline tetap — tiada mekanisme pelarasan sudut bermakna komponen struktur lebih sedikit dan kebolehpercayaan lebih tinggi.",
},

"FS-018": {
    "badge_text_ms": "Kit alat ganti lengkap dihantar bersama peralatan",
    "spare_parts": [
        {"name_ms":"Kabel Keluli Bersalut","qty_ms":"Stok universal","cycle_ms":"18-24 bulan"},
        {"name_ms":"Takal dengan Galas","qty_ms":"Stok universal","cycle_ms":"24-36 bulan"},
        {"name_ms":"Pin Pemilih Berat","qty_ms":"Stok universal","cycle_ms":"12 bulan"},
        {"name_ms":"Galas Sfera","qty_ms":"Stok universal","cycle_ms":"24-36 bulan"},
        {"name_ms":"Sarung Span Pemegang","qty_ms":"Stok universal","cycle_ms":"6-12 bulan"},
        {"name_ms":"Pad Tempat Duduk/Sandaran","qty_ms":"Stok universal","cycle_ms":"18-24 bulan"},
    ],
    "schedule": [
        {"interval_ms":"Setiap hari","action_ms":"Lap peluh dari pad tempat duduk"},
        {"interval_ms":"Setiap minggu","action_ms":"Periksa pin pemilih"},
        {"interval_ms":"Setiap bulan","action_ms":"Pelinciran rod panduan"},
        {"interval_ms":"Setiap suku tahun","action_ms":"Periksa takal dan galas"},
        {"interval_ms":"Setiap setengah tahun","action_ms":"Ketatkan semua bolt"},
    ],
    "durability_note_ms": "Flat chest press adalah salah satu mesin yang paling kerap digunakan. Reka bentuk lengan diverging mengagihkan kehausan lebih sekata berbanding reka bentuk berpaut, sebenarnya menghasilkan hayat yang lebih panjang.",
},

"PL-001": {
    "badge_text_ms": "Kunci keselamatan telah distok khas",
    "spare_parts": [
        {"name_ms":"Galas Linear","qty_ms":"1 set (4 biji)","cycle_ms":"24-36 bulan"},
        {"name_ms":"Kunci Keselamatan/Ratchet","qty_ms":"2 biji","cycle_ms":"12-18 bulan"},
        {"name_ms":"Pelapik Tiang Plat","qty_ms":"2 biji","cycle_ms":"36 bulan"},
        {"name_ms":"Pad Bahu/Sandaran","qty_ms":"1 set","cycle_ms":"18-24 bulan"},
        {"name_ms":"Permukaan Anti-gelincir Tapak Kaki","qty_ms":"1 keping","cycle_ms":"12-18 bulan"},
    ],
    "schedule": [
        {"interval_ms":"Setiap hari","action_ms":"Lap peluh dari pad sandaran"},
        {"interval_ms":"Setiap minggu","action_ms":"Uji penguncian kunci keselamatan (KRITIKAL KESELAMATAN!)"},
        {"interval_ms":"Setiap bulan","action_ms":"Sapukan gris pada rel panduan"},
        {"interval_ms":"Setiap suku tahun","action_ms":"Ketatkan semua bolt"},
    ],
    "durability_note_ms": "Kunci keselamatan adalah satu-satunya alat ganti kehausan tinggi pada mesin ini — stok berganda telah disediakan. Rel panduan diperbuat daripada keluli 45# dengan salutan krom keras, menampung pengguna 160kg melakukan squat berulang tanpa ubah bentuk.",
},

"PL-002": {
    "badge_text_ms": "Kunci keselamatan telah distok khas",
    "spare_parts": [
        {"name_ms":"Peluncur Panduan","qty_ms":"1 set (4 biji)","cycle_ms":"24-36 bulan"},
        {"name_ms":"Kunci Keselamatan","qty_ms":"2 biji","cycle_ms":"12-18 bulan"},
        {"name_ms":"Pad Sandaran","qty_ms":"1 biji","cycle_ms":"18-24 bulan"},
        {"name_ms":"Permukaan Tapak Kaki","qty_ms":"1 keping","cycle_ms":"12-18 bulan"},
    ],
    "schedule": [
        {"interval_ms":"Setiap hari","action_ms":"Lap pad sandaran"},
        {"interval_ms":"Setiap minggu","action_ms":"Uji kunci keselamatan"},
        {"interval_ms":"Setiap bulan","action_ms":"Pelinciran rel panduan"},
        {"interval_ms":"Setiap suku tahun","action_ms":"Ketatkan semua bolt"},
    ],
    "durability_note_ms": "Berkongsi kunci keselamatan spesifikasi sama dengan hack squat — redundansi bersama. Rangka utama menggunakan tiub keluli segi empat 100×50mm, kapasiti beban jauh melebihi nilai dinilai.",
},

"PL-003": {
    "badge_text_ms": "Pembinaan keluli sepenuhnya · Ketahanan 10 tahun",
    "spare_parts": [
        {"name_ms":"J-Hook","qty_ms":"2 pasang dari stok universal","cycle_ms":"36+ bulan"},
        {"name_ms":"Pelapik Getah J-Hook","qty_ms":"4 pasang dari stok universal","cycle_ms":"12 bulan"},
        {"name_ms":"Pad Bangku","qty_ms":"1 biji","cycle_ms":"18-24 bulan"},
    ],
    "schedule": [
        {"interval_ms":"Setiap hari","action_ms":"Lap peluh dari pad bangku"},
        {"interval_ms":"Setiap bulan","action_ms":"Periksa kehausan J-Hook dan penguncian"},
        {"interval_ms":"Setiap suku tahun","action_ms":"Periksa titik kimpalan, ketatkan semua bolt"},
    ],
    "durability_note_ms": "Tiada kabel, tiada takal, tiada elektronik — pembinaan kimpalan keluli tulen. Satu-satunya yang haus ialah pad getah dan upholsteri. Pelapik getah J-Hook adalah satu-satunya bahan guna habis, stok penuh. Mesin ini akan bertahan sehingga pengubahsuaian anda yang seterusnya.",
},

"PL-004": {
    "badge_text_ms": "Pembinaan keluli sepenuhnya · Ketahanan 10 tahun",
    "spare_parts": [
        {"name_ms":"J-Hook","qty_ms":"Dikongsi dengan stok universal PL-003","cycle_ms":"36+ bulan"},
        {"name_ms":"Pelapik Getah J-Hook","qty_ms":"Stok universal dikongsi","cycle_ms":"12 bulan"},
        {"name_ms":"Pad Bangku","qty_ms":"1 biji","cycle_ms":"18-24 bulan"},
    ],
    "schedule": [
        {"interval_ms":"Setiap hari","action_ms":"Lap peluh dari pad bangku"},
        {"interval_ms":"Setiap bulan","action_ms":"Periksa J-Hook dan kunci sudut"},
        {"interval_ms":"Setiap suku tahun","action_ms":"Periksa titik kimpalan, ketatkan bolt"},
    ],
    "durability_note_ms": "Sama dengan PL-003 — kimpalan keluli tulen, sifar elektronik, sifar kabel. Berat bersih 250kg itu sendiri adalah jaminan kestabilan terbaik.",
},

"PL-005": {
    "badge_text_ms": "Semua 5 stesen dilindungi alat ganti secara bebas",
    "spare_parts": [
        {"name_ms":"Kabel Keluli Bersalut","qty_ms":"Stok universal (1 setiap stesen × 5)","cycle_ms":"18-24 bulan"},
        {"name_ms":"Takal dengan Galas","qty_ms":"Stok universal (10-12 takal untuk unit ini)","cycle_ms":"24-36 bulan"},
        {"name_ms":"Pin Pemilih Berat","qty_ms":"Stok universal (5 biji)","cycle_ms":"12 bulan"},
        {"name_ms":"Sesendal Panduan","qty_ms":"Stok universal (5 set)","cycle_ms":"12-18 bulan"},
        {"name_ms":"Galas Sfera","qty_ms":"Stok universal (10 biji)","cycle_ms":"24-36 bulan"},
        {"name_ms":"Sarung Span Pemegang","qty_ms":"Stok universal (5 set)","cycle_ms":"6-12 bulan"},
        {"name_ms":"Pad Setiap Stesen","qty_ms":"Stok universal (5 biji)","cycle_ms":"18-24 bulan"},
    ],
    "schedule": [
        {"interval_ms":"Setiap hari","action_ms":"Lap pad tempat duduk di setiap stesen"},
        {"interval_ms":"Setiap minggu","action_ms":"Periksa semua 5 pin pemilih satu per satu"},
        {"interval_ms":"Setiap bulan","action_ms":"Pelinciran semua 5 rod panduan satu per satu"},
        {"interval_ms":"Setiap suku tahun","action_ms":"Periksa semua takal dan galas satu per satu"},
        {"interval_ms":"Setiap setengah tahun","action_ms":"Pengetatan bolt sepenuhnya (unit 660kg — disyorkan operasi 2 orang)"},
    ],
    "durability_note_ms": "Stesen 5-orang pada dasarnya adalah 5 mesin bebas berkongsi satu rangka. Mana-mana satu stesen bermasalah tidak menjejaskan empat yang lain. Berat sendiri 660kg — kukuh seperti batu.",
},

}  # end MS_TRANSLATIONS


def apply_translations():
    """Read maintenance_data.py, fill in _ms fields, write back."""
    filepath = "maintenance_data.py"

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    changes = 0

    for sku, trans in MS_TRANSLATIONS.items():
        # 1) badge_text_ms
        bt = trans["badge_text_ms"]
        # Find pattern: "SKU": { ... badge_text_ms": "" ...
        # We use a targeted approach: find the SKU block, then replace empty _ms fields
        pass

    # Strategy: line-by-line stateful replacement
    lines = content.split('\n')
    new_lines = []
    current_sku = None
    spare_idx = 0
    sched_idx = 0
    in_spare_parts = False
    in_schedule = False

    for line in lines:
        # Detect SKU block start
        sku_match = re.match(r'^"((?:CD|FS|PL)-\d+)":\s*\{', line)
        if sku_match:
            current_sku = sku_match.group(1)
            spare_idx = 0
            sched_idx = 0
            in_spare_parts = False
            in_schedule = False
            new_lines.append(line)
            continue

        if current_sku and current_sku in MS_TRANSLATIONS:
            trans = MS_TRANSLATIONS[current_sku]

            # Detect spare_parts list
            if '"spare_parts": [' in line:
                in_spare_parts = True
                in_schedule = False
                new_lines.append(line)
                continue
            if '"schedule": [' in line:
                in_schedule = True
                in_spare_parts = False
                sched_idx = 0
                new_lines.append(line)
                continue
            if in_spare_parts and line.strip() == '],':
                in_spare_parts = False
                new_lines.append(line)
                continue
            if in_schedule and line.strip() == '],':
                in_schedule = False
                new_lines.append(line)
                continue

            # Replace badge_text_ms
            if '"badge_text_ms": ""' in line:
                line = line.replace('"badge_text_ms": ""', f'"badge_text_ms": "{trans["badge_text_ms"]}"')
                changes += 1

            # Replace durability_note_ms
            if '"durability_note_ms": ""' in line:
                line = line.replace('"durability_note_ms": ""', f'"durability_note_ms": "{trans["durability_note_ms"]}"')
                changes += 1

            # Replace spare_parts fields
            if in_spare_parts and spare_idx < len(trans.get("spare_parts", [])):
                sp = trans["spare_parts"][spare_idx]
                if '"name_ms":""' in line or '"name_ms": ""' in line:
                    # This line has a spare part entry - replace all _ms fields
                    line = re.sub(r'"name_ms":\s*""', f'"name_ms":"{sp["name_ms"]}"', line)
                    line = re.sub(r'"qty_ms":\s*""', f'"qty_ms":"{sp["qty_ms"]}"', line)
                    line = re.sub(r'"cycle_ms":\s*""', f'"cycle_ms":"{sp["cycle_ms"]}"', line)
                    spare_idx += 1
                    changes += 3

            # Replace schedule fields
            if in_schedule and sched_idx < len(trans.get("schedule", [])):
                sc = trans["schedule"][sched_idx]
                if '"interval_ms":""' in line or '"interval_ms": ""' in line:
                    line = re.sub(r'"interval_ms":\s*""', f'"interval_ms":"{sc["interval_ms"]}"', line)
                    line = re.sub(r'"action_ms":\s*""', f'"action_ms":"{sc["action_ms"]}"', line)
                    sched_idx += 1
                    changes += 2

        new_lines.append(line)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write('\n'.join(new_lines))

    print(f"✅ Batch 1 done: {changes} fields filled for {len(MS_TRANSLATIONS)} SKUs")
    # Verify
    remaining = '\n'.join(new_lines)
    empty_count = 0
    for sku in MS_TRANSLATIONS:
        # Count remaining empty _ms in each SKU block
        pass
    # Quick check: count all remaining empty _ms
    b1_skus = list(MS_TRANSLATIONS.keys())
    print(f"   SKUs processed: {', '.join(b1_skus)}")


if __name__ == "__main__":
    import os
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    apply_translations()
