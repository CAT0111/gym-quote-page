"""
Batch 2: Fill Malay translations for RF-001~RF-006, BN-001~BN-006, FW-001~FW-007, FT-001~FT-012, AC-001~AC-004
Run: python3 fill_ms_batch2.py
"""
import re

MS_TRANSLATIONS = {

"RF-001": {
    "badge_text_ms": "Kit penjagaan rel panduan dihantar bersama peralatan",
    "spare_parts": [
        {"name_ms":"Galas Linear/Sesendal","qty_ms":"1 set (4 biji)","cycle_ms":"24-36 bulan"},
        {"name_ms":"Kunci Keselamatan Putar","qty_ms":"1 pasang","cycle_ms":"18-24 bulan"},
        {"name_ms":"Galas Pelapik Bar","qty_ms":"2 biji","cycle_ms":"36 bulan"},
        {"name_ms":"Gris Rel Panduan","qty_ms":"Termasuk dalam pek pelincir universal","cycle_ms":"Bahan guna habis"},
    ],
    "schedule": [
        {"interval_ms":"Sebelum setiap penggunaan","action_ms":"Periksa penguncian kunci keselamatan putar (KRITIKAL KESELAMATAN!)"},
        {"interval_ms":"Setiap minggu","action_ms":"Lap rel panduan dan sapukan lapisan nipis gris"},
        {"interval_ms":"Setiap bulan","action_ms":"Periksa kelancaran putaran pelapik bar"},
        {"interval_ms":"Setiap suku tahun","action_ms":"Periksa kehausan galas linear/sesendal"},
        {"interval_ms":"Setiap setengah tahun","action_ms":"Ketatkan semua bolt"},
    ],
    "durability_note_ms": "Teras Smith machine ialah dua rel panduannya — disalut krom keras dengan kekerasan permukaan HRC65+. Dengan penyelenggaraan normal, rel itu sendiri pada dasarnya tidak akan haus. Yang haus ialah sesendal — mengganti sesendal semudah menukar mentol lampu.",
},

"RF-002": {
    "badge_text_ms": "Kimpalan keluli sepenuhnya · Tiada alat ganti haus",
    "spare_parts": [
        {"name_ms":"J-Hook","qty_ms":"Stok universal dikongsi","cycle_ms":"36+ bulan"},
        {"name_ms":"Pelapik Getah J-Hook","qty_ms":"Stok universal dikongsi","cycle_ms":"12 bulan"},
        {"name_ms":"Lengan Keselamatan/Spotter","qty_ms":"1 pasang dari stok universal","cycle_ms":"Jarang rosak"},
    ],
    "schedule": [
        {"interval_ms":"Setiap bulan","action_ms":"Periksa kehausan lubang pengunci J-Hook dan lengan keselamatan"},
        {"interval_ms":"Setiap suku tahun","action_ms":"Periksa titik kimpalan, ketatkan bolt lantai"},
        {"interval_ms":"Setiap tahun","action_ms":"Baiki cat (jika tercalar atau berkarat)"},
    ],
    "durability_note_ms": "Tiub keluli dikimpal bersama tanpa sebarang bahagian bergerak. Ini adalah benda yang paling tidak mungkin rosak di gim. Gim hardcore berusia 20 tahun yang anda lihat? Rak squat sentiasa yang asal.",
},

"RF-003": {
    "badge_text_ms": "Kayu pepejal + getah · Hanya perlu pemeriksaan sekali-sekala",
    "spare_parts": [],
    "schedule": [
        {"interval_ms":"Setiap bulan","action_ms":"Periksa permukaan getah untuk retakan atau terangkat"},
        {"interval_ms":"Setiap suku tahun","action_ms":"Periksa papan kayu untuk melengkung"},
        {"interval_ms":"Setiap tahun","action_ms":"Ganti permukaan getah jika sangat haus (beli tikar getah secara tempatan)"},
    ],
    "durability_note_ms": "Satu papan kayu ditambah dua tikar getah — tiada bahagian mekanikal langsung. Tugasnya ialah berbaring di lantai dan dipijak, dan ia boleh melakukannya seumur hidup.",
},

"RF-004": {
    "badge_text_ms": "Keluli sepenuhnya · Hampir tanpa penyelenggaraan",
    "spare_parts": [
        {"name_ms":"Pad Getah Penyangga","qty_ms":"1 set","cycle_ms":"18-24 bulan"},
    ],
    "schedule": [
        {"interval_ms":"Setiap bulan","action_ms":"Periksa titik kimpalan dan kestabilan kaki"},
        {"interval_ms":"Setiap setengah tahun","action_ms":"Periksa kehausan pad getah penyangga, baiki cat"},
    ],
    "durability_note_ms": "Rak kimpalan tiub keluli dengan kapasiti beban jauh melebihi penggunaan sebenar. Satu-satunya yang rosak ialah pad getah penyangga dilekukkan oleh dumbbell — ganti pad sahaja.",
},

"RF-005": {
    "badge_text_ms": "Keluli sepenuhnya · Hampir tanpa penyelenggaraan",
    "spare_parts": [
        {"name_ms":"Pad Getah Penyangga","qty_ms":"1 set","cycle_ms":"18-24 bulan"},
    ],
    "schedule": [
        {"interval_ms":"Setiap bulan","action_ms":"Periksa titik kimpalan dan kaki"},
        {"interval_ms":"Setiap setengah tahun","action_ms":"Periksa pad getah, baiki cat"},
    ],
    "durability_note_ms": "Sama seperti RF-004 — rak tiub keluli, beli dan lupakan sahaja.",
},

"RF-006": {
    "badge_text_ms": "Tiada alat ganti haus · Penggunaan seumur hidup",
    "spare_parts": [],
    "schedule": [
        {"interval_ms":"Setiap setengah tahun","action_ms":"Periksa titik kimpalan dan kestabilan kaki"},
        {"interval_ms":"Setiap tahun","action_ms":"Baiki cat di tempat tercalar untuk mengelak karat"},
    ],
    "durability_note_ms": "Beberapa tiub keluli dikimpal menjadi bentuk pokok untuk memegang plat berat. Benda ini tiada sebarang sebab untuk rosak.",
},

"BN-001": {
    "badge_text_ms": "Keluli + upholsteri · Struktur minimalis",
    "spare_parts": [
        {"name_ms":"Pad Upholsteri Tempat Duduk","qty_ms":"Tidak dihantar — upholsteri semula tempatan lebih jimat","cycle_ms":"18-24 bulan"},
    ],
    "schedule": [
        {"interval_ms":"Setiap hari","action_ms":"Lap peluh dari upholsteri (peluh adalah musuh utama kulit PU)"},
        {"interval_ms":"Setiap bulan","action_ms":"Periksa keketatan bolt dan pad kaki"},
        {"interval_ms":"Apabila retak","action_ms":"Kedai upholsteri sofa tempatan, ~RM50-80 setiap pad"},
    ],
    "durability_note_ms": "Bangku rata mempunyai sifar mekanisme boleh laras — satu rangka keluli, satu pad. Rangka tidak akan rosak. Apabila pad retak, upholsteri semula tempatan kos sepuluh kali lebih murah daripada menghantar yang baru dari China.",
},

"BN-002": {
    "badge_text_ms": "Struktur ringkas · Penyelenggaraan minimum",
    "spare_parts": [
        {"name_ms":"Upholsteri Pad","qty_ms":"Upholsteri semula tempatan","cycle_ms":"18-24 bulan"},
        {"name_ms":"Span Cangkuk Kaki","qty_ms":"1 pasang","cycle_ms":"12-18 bulan"},
    ],
    "schedule": [
        {"interval_ms":"Setiap hari","action_ms":"Lap peluh dari upholsteri"},
        {"interval_ms":"Setiap bulan","action_ms":"Periksa kunci pelarasan sudut dan bolt"},
    ],
    "durability_note_ms": "Papan ab mempunyai beban satu arah dan struktur ringkas. Span cangkuk kaki adalah satu-satunya bahagian haus — alat ganti dihantar bersama peralatan.",
},

"BN-003": {
    "badge_text_ms": "Boleh laras · Fokus pada pemeriksaan pin kunci",
    "spare_parts": [
        {"name_ms":"Pin Laras/Kunci Spring","qty_ms":"4 biji dari stok universal","cycle_ms":"12-18 bulan"},
        {"name_ms":"Upholsteri Pad","qty_ms":"Upholsteri semula tempatan","cycle_ms":"18-24 bulan"},
    ],
    "schedule": [
        {"interval_ms":"Setiap hari","action_ms":"Lap peluh dari upholsteri"},
        {"interval_ms":"Setiap minggu","action_ms":"Periksa pemulangan spring pin kunci sudut"},
        {"interval_ms":"Setiap bulan","action_ms":"Periksa keketatan semua bolt"},
    ],
    "durability_note_ms": "Masalah paling biasa dengan bangku boleh laras ialah kelesuan spring pin kunci — stok universal mempunyai pin gantian yang mencukupi. Penggantian sendiri 30 saat.",
},

"BN-004": {
    "badge_text_ms": "Sudut tetap · Tiada bahagian boleh laras",
    "spare_parts": [
        {"name_ms":"Upholsteri Pad","qty_ms":"Upholsteri semula tempatan","cycle_ms":"18-24 bulan"},
    ],
    "schedule": [
        {"interval_ms":"Setiap hari","action_ms":"Lap peluh dari upholsteri"},
        {"interval_ms":"Setiap suku tahun","action_ms":"Periksa titik kimpalan dan bolt"},
    ],
    "durability_note_ms": "Sudut tetap 75 darjah tanpa mekanisme pelarasan — menghapuskan satu-satunya titik kerosakan yang terdapat pada bangku boleh laras. Rangka keluli untuk penggunaan seumur hidup, upholsteri diupholsteri semula secara tempatan.",
},

"BN-005": {
    "badge_text_ms": "Boleh laras · Fokus pada pemeriksaan pin kunci",
    "spare_parts": [
        {"name_ms":"Pin Laras/Kunci Spring","qty_ms":"Stok universal dikongsi","cycle_ms":"12-18 bulan"},
        {"name_ms":"Upholsteri Pad","qty_ms":"Upholsteri semula tempatan","cycle_ms":"18-24 bulan"},
    ],
    "schedule": [
        {"interval_ms":"Setiap hari","action_ms":"Lap peluh dari upholsteri"},
        {"interval_ms":"Setiap minggu","action_ms":"Periksa semua spring pin kunci sudut"},
        {"interval_ms":"Setiap bulan","action_ms":"Ketatkan bolt"},
    ],
    "durability_note_ms": "FID pelbagai sudut boleh laras — pin kunci adalah satu-satunya bahagian bergerak, stok penuh dalam inventori universal. Harian hanya perlu lap peluh, mingguan tekan-tekan pin kunci.",
},

"BN-006": {
    "badge_text_ms": "Keluli + upholsteri · Struktur minimalis",
    "spare_parts": [
        {"name_ms":"Pad Pinggul/Kaki","qty_ms":"1 biji","cycle_ms":"18-24 bulan"},
    ],
    "schedule": [
        {"interval_ms":"Setiap hari","action_ms":"Lap peluh dari permukaan sentuhan"},
        {"interval_ms":"Setiap bulan","action_ms":"Periksa lubang pelarasan ketinggian dan pin kunci"},
        {"interval_ms":"Setiap suku tahun","action_ms":"Ketatkan bolt"},
    ],
    "durability_note_ms": "Struktur seringkas papan ab. Berat sendiri 96kg memastikan ahli paling berat sekalipun tidak akan menggerakkannya semasa ekstensi belakang.",
},

"FW-001": {
    "badge_text_ms": "Besi tuang pepejal · Tiada bahagian mekanikal",
    "spare_parts": [],
    "schedule": [
        {"interval_ms":"Setiap bulan","action_ms":"Periksa salutan getah/penyaduran krom untuk mengelupas, ketatkan kepala dumbbell yang longgar"},
        {"interval_ms":"Setiap suku tahun","action_ms":"Bersihkan dengan kain lembap, simpan kering"},
    ],
    "durability_note_ms": "Seketul besi. Ia wujud sebelum gim anda dan akan terus wujud selepasnya. Tiada jadual penyelenggaraan kerana besi tidak luput.",
},

"FW-002": {
    "badge_text_ms": "Besi tuang pepejal · Tiada bahagian mekanikal",
    "spare_parts": [],
    "schedule": [
        {"interval_ms":"Setiap bulan","action_ms":"Periksa salutan getah/penyaduran krom"},
        {"interval_ms":"Setiap suku tahun","action_ms":"Bersihkan, ketatkan ulir"},
    ],
    "durability_note_ms": "Sama seperti FW-001. Seketul besi yang lebih berat.",
},

"FW-003": {
    "badge_text_ms": "Plat besi tuang · Tiada bahagian mekanikal",
    "spare_parts": [],
    "schedule": [
        {"interval_ms":"Setiap suku tahun","action_ms":"Periksa retakan (plat besi tuang boleh retak dalam kes ekstrem), bersihkan permukaan"},
    ],
    "durability_note_ms": "Plat berat besi tuang dari abad lepas masih digunakan di mana-mana. Pastikan kering untuk mengelak karat. Jika berkarat, gosok dengan kertas pasir dan teruskan.",
},

"FW-004": {
    "badge_text_ms": "Plat besi tuang · Tiada bahagian mekanikal",
    "spare_parts": [],
    "schedule": [
        {"interval_ms":"Setiap suku tahun","action_ms":"Periksa retakan, bersihkan permukaan"},
    ],
    "durability_note_ms": "Sama seperti FW-003.",
},

"FW-005": {
    "badge_text_ms": "Galas & sesendal disertakan",
    "spare_parts": [
        {"name_ms":"Galas","qty_ms":"4 biji untuk 4 bar","cycle_ms":"24-36 bulan"},
        {"name_ms":"Sesendal Gangsa","qty_ms":"4 biji untuk 4 bar","cycle_ms":"24-36 bulan"},
        {"name_ms":"Gelang Snap","qty_ms":"8 biji","cycle_ms":"12 bulan"},
    ],
    "schedule": [
        {"interval_ms":"Setiap minggu","action_ms":"Lap aci bar dengan minyak 3-IN-ONE untuk mengelak karat"},
        {"interval_ms":"Setiap bulan","action_ms":"Putar pelapik untuk periksa kelancaran galas"},
        {"interval_ms":"Setiap suku tahun","action_ms":"Buka pelapik, bersihkan gris lama, sapukan semula gris galas"},
    ],
    "durability_note_ms": "Bar keluli 45# mengimbangi kekerasan dan keanjalan — aci bar pada dasarnya tidak akan bengkok atau berubah bentuk dalam penggunaan komersial. Galas dan sesendal adalah satu-satunya bahan guna habis, stok penuh. Kesukaran penggantian sendiri setara dengan menukar tayar basikal.",
},

"FW-006": {
    "badge_text_ms": "Galas & sesendal disertakan",
    "spare_parts": [
        {"name_ms":"Galas","qty_ms":"2 biji","cycle_ms":"24-36 bulan"},
        {"name_ms":"Sesendal Gangsa","qty_ms":"2 biji","cycle_ms":"24-36 bulan"},
        {"name_ms":"Gelang Snap","qty_ms":"2 biji","cycle_ms":"12 bulan"},
    ],
    "schedule": [
        {"interval_ms":"Setiap minggu","action_ms":"Lap aci bar untuk mengelak karat"},
        {"interval_ms":"Setiap suku tahun","action_ms":"Bersihkan pelapik, sapukan semula gris"},
    ],
    "durability_note_ms": "Reka bentuk galas berkembar + sesendal gangsa berkembar — lebih lancar dan lebih tahan lama daripada bar galas tunggal.",
},

"FW-007": {
    "badge_text_ms": "Galas & sesendal disertakan",
    "spare_parts": [
        {"name_ms":"Galas","qty_ms":"2 biji","cycle_ms":"24-36 bulan"},
        {"name_ms":"Sesendal Gangsa","qty_ms":"2 biji","cycle_ms":"24-36 bulan"},
        {"name_ms":"Gelang Snap","qty_ms":"2 biji","cycle_ms":"12 bulan"},
    ],
    "schedule": [
        {"interval_ms":"Setiap minggu","action_ms":"Lap aci bar untuk mengelak karat"},
        {"interval_ms":"Setiap suku tahun","action_ms":"Bersihkan pelapik, sapukan semula gris"},
    ],
    "durability_note_ms": "Sama seperti FW-006. Bahagian melengkung EZ curl bar ditempa satu keping, bukan dibengkokkan kemudian — tiada risiko patah tekanan.",
},

"FT-001": {
    "badge_text_ms": "Tuangan satu keping · Tiada bahagian boleh tanggal",
    "spare_parts": [],
    "schedule": [
        {"interval_ms":"Setiap bulan","action_ms":"Periksa titik kimpalan pemegang dan salutan serbuk"},
        {"interval_ms":"Setiap suku tahun","action_ms":"Bersihkan permukaan, simpan kering"},
    ],
    "durability_note_ms": "Seketul besi dengan pemegang. Tidak boleh dipecahkan, tidak boleh dihancurkan, tidak boleh dihabiskan.",
},

"FT-002": {
    "badge_text_ms": "Rak keluli · Tanpa penyelenggaraan",
    "spare_parts": [],
    "schedule": [
        {"interval_ms":"Setiap setengah tahun","action_ms":"Periksa kestabilan dan titik kimpalan"},
    ],
    "durability_note_ms": "Rak untuk memegang kettlebell — lebih susah rosak daripada kettlebell itu sendiri.",
},

"FT-003": {
    "badge_text_ms": "Bahan guna habis · Ganti mengikut jadual",
    "spare_parts": [],
    "schedule": [
        {"interval_ms":"Setiap bulan","action_ms":"Periksa kulit untuk retakan atau penyahlamaan"},
        {"interval_ms":"12-24 bulan","action_ms":"Ganti sepenuhnya apabila kulit retak teruk (boleh didapati secara tempatan atau dari China)"},
    ],
    "durability_note_ms": "Medicine ball adalah satu-satunya alat latihan yang benar-benar mempunyai \"hayat.\" Kulit retak adalah normal — ia bermakna ahli anda berlatih dengan bersungguh-sungguh. Boleh didapati di mana-mana kedai sukan tempatan, tiada perlu import dari China.",
},

"FT-004": {
    "badge_text_ms": "Rak keluli · Tanpa penyelenggaraan",
    "spare_parts": [],
    "schedule": [
        {"interval_ms":"Setiap setengah tahun","action_ms":"Periksa kestabilan"},
    ],
    "durability_note_ms": "Sama seperti rak kettlebell — rak untuk memegang barang tiada sebab untuk rosak.",
},

"FT-005": {
    "badge_text_ms": "Bahan guna habis · Ganti mengikut jadual",
    "spare_parts": [
        {"name_ms":"Bolt Sauh Dinding","qty_ms":"2 set","cycle_ms":"Periksa setiap suku tahun"},
    ],
    "schedule": [
        {"interval_ms":"Setiap bulan","action_ms":"Periksa ikatan hujung tali untuk kelonggaran"},
        {"interval_ms":"Setiap suku tahun","action_ms":"Periksa keketatan bolt sauh dinding"},
        {"interval_ms":"12-18 bulan","action_ms":"Ganti keseluruhan tali apabila berbulu (boleh dibeli secara tempatan)"},
    ],
    "durability_note_ms": "Hayat battle rope bergantung pada lantai — lantai gim yang lebih tebal dan licin bermakna kehausan tali lebih perlahan. Bolt sauh adalah alat ganti kritikal keselamatan, stok penuh. Tali itu sendiri murah dan boleh didapati di Decathlon pada bila-bila masa.",
},

"FT-006": {
    "badge_text_ms": "Produk tali anyaman · Pemeriksaan jahitan berkala",
    "spare_parts": [
        {"name_ms":"Sauh Siling + Karabiner","qty_ms":"3 set","cycle_ms":"Periksa setiap suku tahun"},
    ],
    "schedule": [
        {"interval_ms":"Setiap bulan","action_ms":"Periksa jahitan untuk kelonggaran, tali anyaman untuk kehausan"},
        {"interval_ms":"Setiap suku tahun","action_ms":"Periksa bolt sauh siling dan karabiner"},
        {"interval_ms":"12-18 bulan","action_ms":"Ganti sepenuhnya apabila tali anyaman haus atau jahitan longgar"},
    ],
    "durability_note_ms": "TRX adalah tali anyaman yang menanggung beban — berat badan penuh ahli bergantung padanya. Keselamatan diutamakan. Periksa jahitan dengan teliti setiap bulan. Penggunaan normal tahan 1+ tahun dengan mudah. Bolt sauh stok penuh.",
},

"FT-007": {
    "badge_text_ms": "Produk getah · Penggantian berkala",
    "spare_parts": [],
    "schedule": [
        {"interval_ms":"Setiap bulan","action_ms":"Periksa retakan, kehilangan keanjalan"},
        {"interval_ms":"6-12 bulan","action_ms":"Ganti keseluruhan set apabila keanjalan menurun ketara atau retakan muncul"},
    ],
    "durability_note_ms": "Resistance band adalah produk getah yang secara semula jadi menua. Berita baiknya: ia antara alat latihan paling murah — satu set di bawah RM30. Pesan di Shopee untuk penghantaran esok. Tidak berbaloi dihantar dari China.",
},

"FT-008": {
    "badge_text_ms": "Bahan guna habis · Ganti mengikut standard kebersihan",
    "spare_parts": [],
    "schedule": [
        {"interval_ms":"Setiap hari","action_ms":"Semburkan disinfektan dan lap selepas penggunaan (peluh + bakteria adalah pembunuh utama tikar)"},
        {"interval_ms":"12-18 bulan","action_ms":"Ganti apabila permukaan retak atau bau tidak boleh dihilangkan"},
    ],
    "durability_note_ms": "Tikar senaman adalah bahan guna habis kebersihan — tikar terbaik sekalipun patut diganti selepas setahun lebih. Boleh didapati di Mr. DIY / Decathlon pada bila-bila masa, di bawah RM20 setiap satu.",
},

"FT-009": {
    "badge_text_ms": "Bahan guna habis · Ganti apabila berubah bentuk",
    "spare_parts": [],
    "schedule": [
        {"interval_ms":"Setiap bulan","action_ms":"Periksa kerosakan atau perubahan bentuk"},
        {"interval_ms":"12-18 bulan","action_ms":"Ganti apabila daya lantunan menurun ketara"},
    ],
    "durability_note_ms": "Foam roller akan kemek rata dari semasa ke semasa — itu normal. Cari \"foam roller\" di Shopee — RM15-30 setiap satu. Tidak berbaloi penghantaran antarabangsa.",
},

"FT-010": {
    "badge_text_ms": "Pembinaan papan lapis · Tahan hentaman",
    "spare_parts": [
        {"name_ms":"Permukaan Anti-gelincir","qty_ms":"Boleh diganti dengan pita anti-gelincir tempatan","cycle_ms":"12-18 bulan"},
    ],
    "schedule": [
        {"interval_ms":"Setiap bulan","action_ms":"Periksa pinggir dan integriti permukaan anti-gelincir"},
        {"interval_ms":"12-18 bulan","action_ms":"Sapukan semula permukaan anti-gelincir apabila haus (beli pita kertas pasir anti-gelincir di kedai perkakasan tempatan)"},
    ],
    "durability_note_ms": "Kotak plyo 3-dalam-1 diperbuat daripada papan lapis 18mm — menampung hentaman lompatan berulang. Kayu itu sendiri tidak akan rosak. Permukaan anti-gelincir adalah satu-satunya bahan guna habis — RM10 segulung pita anti-gelincir di mana-mana kedai perkakasan.",
},

"FT-011": {
    "badge_text_ms": "Keluli dinding · Fokus pada pemeriksaan bolt",
    "spare_parts": [
        {"name_ms":"Bolt Dinding","qty_ms":"1 set","cycle_ms":"Periksa setiap suku tahun"},
        {"name_ms":"Sarung Genggaman","qty_ms":"1 biji","cycle_ms":"12 bulan"},
    ],
    "schedule": [
        {"interval_ms":"Setiap bulan","action_ms":"Periksa bolt dinding untuk kelonggaran (KRITIKAL KESELAMATAN!)"},
        {"interval_ms":"Setiap suku tahun","action_ms":"Ketatkan semua bolt"},
        {"interval_ms":"12 bulan","action_ms":"Ganti sarung genggaman apabila haus"},
    ],
    "durability_note_ms": "Rangka keluli itu sendiri tidak akan rosak — kuncinya ialah sauh dinding. Mesti dipasang pada dinding galas beban/konkrit dengan bolt pengembangan M12+. Setelah dipasang, hanya perlu periksa bolt secara berkala.",
},

"FT-012": {
    "badge_text_ms": "Tayar getah · Penggunaan seumur hidup",
    "spare_parts": [],
    "schedule": [],
    "durability_note_ms": "Ini adalah tayar. Ia terselamat ratusan ribu kilometer di atas lori dalam kehidupan terdahulunya. Diterbalikkan di gim anda adalah persaraan. Tiada penyelenggaraan diperlukan.",
},

"AC-001": {
    "badge_text_ms": "Getah EPDM · Hayat 5+ tahun",
    "spare_parts": [],
    "schedule": [
        {"interval_ms":"Setiap hari","action_ms":"Sapu habuk, mop basah bersihkan"},
        {"interval_ms":"Setiap bulan","action_ms":"Periksa sambungan saling kunci untuk terangkat"},
        {"interval_ms":"Setiap tahun","action_ms":"Ganti jubin rosak secara individu (disyorkan beli 5% lebihan semasa pembukaan sebagai alat ganti)"},
    ],
    "durability_note_ms": "Lantai getah EPDM tahan UV, tahan haus, dan tahan kakisan peluh. Hayat normal 5-8 tahun. Beli secara tempatan — disyorkan beli 5% lebihan sebagai stok penggantian masa depan.",
},

"AC-002": {
    "badge_text_ms": "20mm tugas berat · Direka untuk jatuhan barbell",
    "spare_parts": [],
    "schedule": [
        {"interval_ms":"Setiap bulan","action_ms":"Periksa kawasan deadlift/squat untuk lekukan atau retakan"},
        {"interval_ms":"Setiap tahun","action_ms":"Ganti bahagian rosak teruk secara individu"},
    ],
    "durability_note_ms": "Getah berketumpatan tinggi 20mm direka khas untuk hentaman jatuhan barbell deadlift. Hayat lebih pendek daripada lantai standard 10mm (3-5 tahun), tetapi ia melindungi lantai anda dan siling jiran bawah anda.",
},

"AC-003": {
    "badge_text_ms": "Cermin keselamatan · Filem kalis pecah",
    "spare_parts": [],
    "schedule": [
        {"interval_ms":"Setiap hari","action_ms":"Bersihkan cap jari dan peluh dengan pencuci kaca"},
        {"interval_ms":"Setiap bulan","action_ms":"Periksa pemasangan sudut untuk kelonggaran"},
    ],
    "durability_note_ms": "Cermin keselamatan 5mm dengan filem kalis pecah — walaupun terkena dumbbell, ia hanya retak tanpa serpihan bertaburan. Tidak akan pecah dalam penggunaan normal. Musuh satu-satunya ialah dumbbell terbang — pastikan cermin sekurang-kurangnya 3 meter dari rak dumbbell.",
},

"AC-004": {
    "badge_text_ms": "Keluli gelek sejuk · Penyelenggaraan minimum",
    "spare_parts": [],
    "schedule": [
        {"interval_ms":"Setiap bulan","action_ms":"Periksa engsel pintu dan kunci"},
        {"interval_ms":"Setiap suku tahun","action_ms":"Sapukan sedikit pelincir pada engsel untuk mengelak karat (kelembapan tinggi di Malaysia)"},
    ],
    "durability_note_ms": "Loker keluli memerlukan perhatian pencegahan karat dalam persekitaran lembap Malaysia. Sedikit WD-40 pada engsel setiap suku tahun sudah memadai — badan kabinet itu sendiri tahan 10+ tahun.",
},

}  # end MS_TRANSLATIONS


def apply_translations():
    """Read maintenance_data.py, fill in _ms fields for batch 2 SKUs, write back."""
    filepath = "maintenance_data.py"
    import re

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    lines = content.split('\n')
    new_lines = []
    current_sku = None
    spare_idx = 0
    sched_idx = 0
    in_spare_parts = False
    in_schedule = False
    changes = 0

    for line in lines:
        sku_match = re.match(r'^"((?:RF|BN|FW|FT|AC)-\d+)":\s*\{', line)
        if sku_match:
            current_sku = sku_match.group(1)
            spare_idx = 0
            sched_idx = 0
            in_spare_parts = False
            in_schedule = False
            new_lines.append(line)
            continue

        # Also reset on any SKU start (in case of CD/FS/PL blocks)
        other_sku = re.match(r'^"((?:CD|FS|PL)-\d+)":\s*\{', line)
        if other_sku:
            current_sku = None
            in_spare_parts = False
            in_schedule = False
            new_lines.append(line)
            continue

        if current_sku and current_sku in MS_TRANSLATIONS:
            trans = MS_TRANSLATIONS[current_sku]

            if '"spare_parts": [' in line:
                in_spare_parts = True
                in_schedule = False
                spare_idx = 0
                new_lines.append(line)
                continue
            if '"schedule": [' in line:
                in_schedule = True
                in_spare_parts = False
                sched_idx = 0
                new_lines.append(line)
                continue
            if (in_spare_parts or in_schedule) and line.strip() == '],':
                in_spare_parts = False
                in_schedule = False
                new_lines.append(line)
                continue

            # badge_text_ms
            if '"badge_text_ms": ""' in line:
                line = line.replace('"badge_text_ms": ""', f'"badge_text_ms": "{trans["badge_text_ms"]}"')
                changes += 1

            # durability_note_ms
            if '"durability_note_ms": ""' in line:
                line = line.replace('"durability_note_ms": ""', f'"durability_note_ms": "{trans["durability_note_ms"]}"')
                changes += 1

            # spare_parts
            if in_spare_parts and spare_idx < len(trans.get("spare_parts", [])):
                sp = trans["spare_parts"][spare_idx]
                if '"name_ms":""' in line or '"name_ms": ""' in line:
                    line = re.sub(r'"name_ms":\s*""', f'"name_ms":"{sp["name_ms"]}"', line)
                    line = re.sub(r'"qty_ms":\s*""', f'"qty_ms":"{sp["qty_ms"]}"', line)
                    line = re.sub(r'"cycle_ms":\s*""', f'"cycle_ms":"{sp["cycle_ms"]}"', line)
                    spare_idx += 1
                    changes += 3

            # schedule
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

    print(f"✅ Batch 2 done: {changes} fields filled for {len(MS_TRANSLATIONS)} SKUs")
    print(f"   SKUs processed: {', '.join(sorted(MS_TRANSLATIONS.keys()))}")


if __name__ == "__main__":
    import os
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    apply_translations()
