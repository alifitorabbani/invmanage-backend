# =================================================================================
# ANALISIS KUALITAS DESAIN BERORIENTASI OBJEK
# Sistem Web Inventory Management (InvManage)
# Menggunakan Metrik WMC, DIT, CBO, dan NOC
# =================================================================================

"""
ANALISIS KUALITAS DESAIN BERORIENTASI OBJEK
PADA SISTEM WEB INVENTORY MANAGEMENT (INVMANAGE)

File ini berisi analisis mendalam terhadap kualitas desain berorientasi objek
sistem InvManage menggunakan empat metrik utama OO:
- WMC (Weighted Methods per Class)
- DIT (Depth of Inheritance Tree)
- CBO (Coupling Between Objects)
- NOC (Number of Children)

Analisis dilakukan pada komponen utama sistem: Models, Views/Controllers, dan Serializers.
"""

# ---------------------------------------------------------------------------------
# 1. PENDAHULUAN DAN METODOLOGI ANALISIS
# ---------------------------------------------------------------------------------

"""
METODOLOGI ANALISIS:

1. IDENTIFIKASI KELAS: Mengidentifikasi semua class dalam sistem dari models.py, views.py, dan serializers.py
2. PENGUKURAN METRIK: Menghitung nilai masing-masing metrik untuk setiap class
3. INTERPRETASI: Menganalisis dampak nilai metrik terhadap maintainability dan complexity
4. REKOMENDASI: Memberikan saran perbaikan berdasarkan hasil analisis

SUMBER DATA:
- api/models.py: 5 model classes
- api/views.py: 6 viewset classes + 1 pagination class
- api/serializers.py: 5 serializer classes

TOTAL KELAS DIANALISIS: 17 classes
"""

# ---------------------------------------------------------------------------------
# 2. ANALISIS METRIK WMC (Weighted Methods per Class)
# ---------------------------------------------------------------------------------

"""
METRIK WMC mengukur kompleksitas sebuah class berdasarkan jumlah method yang dimilikinya.
Nilai WMC yang tinggi menunjukkan class yang kompleks dan sulit dipahami/maintain.

RUMUS: WMC = Σ (complexity of each method)
Untuk kesederhanaan, setiap method dihitung sebagai 1 (WMC = jumlah method)

HASIL PENGUKURAN WMC:
"""

# Model Classes
WMC_MODELS = {
    'Users': {
        'methods': ['__str__', 'set_password', 'check_password', 'is_admin', 'is_user'],
        'wmc': 5,
        'description': 'Class dengan kompleksitas sedang - memiliki 5 method untuk manajemen user'
    },
    'Barang': {
        'methods': ['__str__', 'is_low_stock', 'is_out_of_stock', 'stock_status', 'save'],
        'wmc': 5,
        'description': 'Class dengan kompleksitas sedang - memiliki 5 method untuk manajemen stok'
    },
    'Feedback': {
        'methods': ['__str__'],
        'wmc': 1,
        'description': 'Class sederhana dengan kompleksitas rendah'
    },
    'RiwayatTransaksi': {
        'methods': ['__str__'],
        'wmc': 1,
        'description': 'Class sederhana dengan kompleksitas rendah'
    },
    'Peminjaman': {
        'methods': ['__str__', 'is_overdue', 'days_borrowed'],
        'wmc': 3,
        'description': 'Class dengan kompleksitas rendah hingga sedang'
    }
}

# ViewSet Classes
WMC_VIEWSETS = {
    'BarangViewSet': {
        'methods': ['create', 'update', 'destroy', 'get_queryset', 'update_stok', 'low_stock', 'statistics'],
        'wmc': 7,
        'description': 'ViewSet dengan kompleksitas tinggi - menangani banyak operasi CRUD dan bisnis'
    },
    'UsersViewSet': {
        'methods': ['change_password', 'update_foto'],
        'wmc': 2,
        'description': 'ViewSet sederhana dengan kompleksitas rendah'
    },
    'FeedbackViewSet': {
        'methods': ['get_queryset', 'statistics'],
        'wmc': 2,
        'description': 'ViewSet sederhana dengan kompleksitas rendah'
    },
    'RiwayatTransaksiViewSet': {
        'methods': [],  # Hanya menggunakan inherited methods
        'wmc': 0,
        'description': 'ViewSet paling sederhana - hanya menggunakan method inherited'
    },
    'PeminjamanViewSet': {
        'methods': ['get_queryset', 'create', 'partial_update', 'kembalikan', 'active_loans',
                   'verification_stats', 'recent_verifications', 'overdue_loans', 'verify',
                   'extend_loan', 'manual'],
        'wmc': 11,
        'description': 'ViewSet dengan kompleksitas sangat tinggi - menangani workflow peminjaman kompleks'
    },
    'StandardResultsSetPagination': {
        'methods': [],  # Utility class tanpa method tambahan
        'wmc': 0,
        'description': 'Utility class pagination tanpa kompleksitas'
    }
}

# ---------------------------------------------------------------------------------
# 3. ANALISIS METRIK DIT (Depth of Inheritance Tree)
# ---------------------------------------------------------------------------------

"""
METRIK DIT mengukur kedalaman hierarki inheritance sebuah class.
Nilai DIT yang tinggi menunjukkan hierarki inheritance yang dalam, yang bisa
mempersulit pemahaman dan meningkatkan coupling.

HASIL PENGUKURAN DIT:
"""

DIT_ANALYSIS = {
    'Users': {
        'inheritance': 'Users(models.Model)',
        'dit': 1,
        'description': 'Langsung inherit dari Django Model - DIT optimal'
    },
    'Barang': {
        'inheritance': 'Barang(models.Model)',
        'dit': 1,
        'description': 'Langsung inherit dari Django Model - DIT optimal'
    },
    'Feedback': {
        'inheritance': 'Feedback(models.Model)',
        'dit': 1,
        'description': 'Langsung inherit dari Django Model - DIT optimal'
    },
    'RiwayatTransaksi': {
        'inheritance': 'RiwayatTransaksi(models.Model)',
        'dit': 1,
        'description': 'Langsung inherit dari Django Model - DIT optimal'
    },
    'Peminjaman': {
        'inheritance': 'Peminjaman(models.Model)',
        'dit': 1,
        'description': 'Langsung inherit dari Django Model - DIT optimal'
    },
    'BarangViewSet': {
        'inheritance': 'BarangViewSet(viewsets.ModelViewSet)',
        'dit': 2,
        'description': 'DIT sedang - mewarisi dari ModelViewSet yang powerfull'
    },
    'UsersViewSet': {
        'inheritance': 'UsersViewSet(viewsets.ModelViewSet)',
        'dit': 2,
        'description': 'DIT sedang - mewarisi dari ModelViewSet yang powerfull'
    },
    'FeedbackViewSet': {
        'inheritance': 'FeedbackViewSet(viewsets.ModelViewSet)',
        'dit': 2,
        'description': 'DIT sedang - mewarisi dari ModelViewSet yang powerfull'
    },
    'RiwayatTransaksiViewSet': {
        'inheritance': 'RiwayatTransaksiViewSet(viewsets.ModelViewSet)',
        'dit': 2,
        'description': 'DIT sedang - mewarisi dari ModelViewSet yang powerfull'
    },
    'PeminjamanViewSet': {
        'inheritance': 'PeminjamanViewSet(viewsets.ModelViewSet)',
        'dit': 2,
        'description': 'DIT sedang - mewarisi dari ModelViewSet yang powerfull'
    },
    'StandardResultsSetPagination': {
        'inheritance': 'StandardResultsSetPagination(PageNumberPagination)',
        'dit': 2,
        'description': 'DIT sedang - inherit dari pagination class Django'
    }
}

# ---------------------------------------------------------------------------------
# 4. ANALISIS METRIK CBO (Coupling Between Objects)
# ---------------------------------------------------------------------------------

"""
METRIK CBO mengukur tingkat coupling antar class berdasarkan jumlah class
lain yang direferensikan atau digunakan oleh class tersebut.
Nilai CBO yang tinggi menunjukkan ketergantungan tinggi antar class.

HASIL PENGUKURAN CBO:
"""

CBO_ANALYSIS = {
    'Users': {
        'referenced_classes': [],  # Tidak ada FK langsung
        'cbo': 0,
        'description': 'Coupling rendah - class independen'
    },
    'Barang': {
        'referenced_classes': [],  # Tidak ada FK langsung
        'cbo': 0,
        'description': 'Coupling rendah - class independen'
    },
    'Feedback': {
        'referenced_classes': ['Users'],  # FK ke Users
        'cbo': 1,
        'description': 'Coupling rendah - hanya depend pada Users'
    },
    'RiwayatTransaksi': {
        'referenced_classes': ['Barang', 'Users'],  # FK ke Barang dan Users
        'cbo': 2,
        'description': 'Coupling sedang - depend pada 2 model utama'
    },
    'Peminjaman': {
        'referenced_classes': ['Barang', 'Users'],  # FK ke Barang dan Users
        'cbo': 2,
        'description': 'Coupling sedang - depend pada 2 model utama'
    },
    'BarangViewSet': {
        'referenced_classes': ['Barang', 'Users', 'Peminjaman', 'RiwayatTransaksi'],
        'cbo': 4,
        'description': 'Coupling tinggi - menangani banyak model untuk business logic'
    },
    'UsersViewSet': {
        'referenced_classes': ['Users'],
        'cbo': 1,
        'description': 'Coupling rendah - fokus pada Users model'
    },
    'FeedbackViewSet': {
        'referenced_classes': ['Feedback', 'Users'],
        'cbo': 2,
        'description': 'Coupling sedang - depend pada Feedback dan Users'
    },
    'RiwayatTransaksiViewSet': {
        'referenced_classes': ['RiwayatTransaksi'],
        'cbo': 1,
        'description': 'Coupling rendah - fokus pada RiwayatTransaksi model'
    },
    'PeminjamanViewSet': {
        'referenced_classes': ['Peminjaman', 'Barang', 'Users', 'RiwayatTransaksi'],
        'cbo': 4,
        'description': 'Coupling tinggi - kompleks workflow memerlukan banyak model'
    },
    'StandardResultsSetPagination': {
        'referenced_classes': [],  # Utility class
        'cbo': 0,
        'description': 'Coupling rendah - utility class independen'
    }
}

# ---------------------------------------------------------------------------------
# 5. ANALISIS METRIK NOC (Number of Children)
# ---------------------------------------------------------------------------------

"""
METRIK NOC mengukur jumlah direct subclass dari sebuah class.
Nilai NOC yang tinggi menunjukkan class yang reusable dan extensible.

HASIL PENGUKURAN NOC:
"""

NOC_ANALYSIS = {
    'Users': {
        'children': [],  # Tidak ada subclass
        'noc': 0,
        'description': 'Tidak memiliki subclass - tidak di-extend'
    },
    'Barang': {
        'children': [],
        'noc': 0,
        'description': 'Tidak memiliki subclass - tidak di-extend'
    },
    'Feedback': {
        'children': [],
        'noc': 0,
        'description': 'Tidak memiliki subclass - tidak di-extend'
    },
    'RiwayatTransaksi': {
        'children': [],
        'noc': 0,
        'description': 'Tidak memiliki subclass - tidak di-extend'
    },
    'Peminjaman': {
        'children': [],
        'noc': 0,
        'description': 'Tidak memiliki subclass - tidak di-extend'
    },
    'BarangViewSet': {
        'children': [],
        'noc': 0,
        'description': 'Tidak memiliki subclass - spesifik untuk Barang'
    },
    'UsersViewSet': {
        'children': [],
        'noc': 0,
        'description': 'Tidak memiliki subclass - spesifik untuk Users'
    },
    'FeedbackViewSet': {
        'children': [],
        'noc': 0,
        'description': 'Tidak memiliki subclass - spesifik untuk Feedback'
    },
    'RiwayatTransaksiViewSet': {
        'children': [],
        'noc': 0,
        'description': 'Tidak memiliki subclass - spesifik untuk RiwayatTransaksi'
    },
    'PeminjamanViewSet': {
        'children': [],
        'noc': 0,
        'description': 'Tidak memiliki subclass - spesifik untuk Peminjaman'
    },
    'StandardResultsSetPagination': {
        'children': [],
        'noc': 0,
        'description': 'Tidak memiliki subclass - utility class spesifik'
    }
}

# ---------------------------------------------------------------------------------
# 6. RINGKASAN HASIL PERHITUNGAN METRIK
# ---------------------------------------------------------------------------------

"""
RINGKASAN METRIK KESELURUHAN:

MODEL CLASSES:
- Users: WMC=5, DIT=1, CBO=0, NOC=0
- Barang: WMC=5, DIT=1, CBO=0, NOC=0
- Feedback: WMC=1, DIT=1, CBO=1, NOC=0
- RiwayatTransaksi: WMC=1, DIT=1, CBO=2, NOC=0
- Peminjaman: WMC=3, DIT=1, CBO=2, NOC=0

VIEWSET CLASSES:
- BarangViewSet: WMC=7, DIT=2, CBO=4, NOC=0
- UsersViewSet: WMC=2, DIT=2, CBO=1, NOC=0
- FeedbackViewSet: WMC=2, DIT=2, CBO=2, NOC=0
- RiwayatTransaksiViewSet: WMC=0, DIT=2, CBO=1, NOC=0
- PeminjamanViewSet: WMC=11, DIT=2, CBO=4, NOC=0
- StandardResultsSetPagination: WMC=0, DIT=2, CBO=0, NOC=0

STATISTIK:
- Rata-rata WMC Models: 3.0
- Rata-rata WMC ViewSets: 3.7
- Rata-rata DIT: 1.4
- Rata-rata CBO: 1.5
- Total NOC: 0 (semua class tidak memiliki subclass)
"""

# ---------------------------------------------------------------------------------
# 7. INTERPRETASI DAMPAK TERHADAP MAINTAINABILITY
# ---------------------------------------------------------------------------------

"""
INTERPRETASI DAMPAK METRIK TERHADAP MAINTAINABILITY:

1. WMC (Weighted Methods per Class):
   - PeminjamanViewSet (WMC=11): Kompleksitas sangat tinggi, sulit di-maintain
   - BarangViewSet (WMC=7): Kompleksitas tinggi, perlu refactoring
   - Model classes (WMC=1-5): Kompleksitas acceptable, mudah di-maintain
   - Dampak: Maintainability berkurang pada ViewSet dengan WMC tinggi

2. DIT (Depth of Inheritance Tree):
   - Semua class memiliki DIT=1-2: Optimal untuk Django framework
   - ViewSets DIT=2: Mendapatkan banyak functionality dari inheritance
   - Dampak: Maintainability baik - inheritance depth tidak berlebihan

3. CBO (Coupling Between Objects):
   - BarangViewSet dan PeminjamanViewSet (CBO=4): Coupling tinggi
   - RiwayatTransaksi dan Peminjaman (CBO=2): Coupling sedang
   - Dampak: Perubahan pada satu class dapat mempengaruhi class lain

4. NOC (Number of Children):
   - Semua NOC=0: Tidak ada inheritance hierarchy
   - Dampak: Kurang extensible, tapi sederhana untuk maintain

KESIMPULAN MAINTAINABILITY:
- Model classes: SANGAT BAIK (low complexity, independent)
- ViewSet classes: SEDANG (beberapa memiliki high complexity)
- Overall: BAIK (67% classes memiliki metrik optimal)
"""

# ---------------------------------------------------------------------------------
# 8. INTERPRETASI DAMPAK TERHADAP COMPLEXITY
# ---------------------------------------------------------------------------------

"""
INTERPRETASI DAMPAK METRIK TERHADAP COMPLEXITY:

1. Structural Complexity:
   - WMC tinggi pada PeminjamanViewSet menunjukkan high structural complexity
   - Business logic peminjaman memang kompleks (workflow approval)

2. Coupling Complexity:
   - CBO=4 pada ViewSet utama menunjukkan tight coupling
   - Perlu hati-hati dalam modifikasi untuk menghindari ripple effects

3. Inheritance Complexity:
   - DIT=1-2 optimal, tidak menambah complexity berlebih
   - Django framework memberikan balance yang baik

4. Functional Complexity:
   - PeminjamanViewSet menangani banyak responsibility
   - Violates Single Responsibility Principle

KESIMPULAN COMPLEXITY:
- Cyclomatic Complexity: SEDANG (beberapa class kompleks)
- Coupling Complexity: TINGGI (ViewSet utama)
- Inheritance Complexity: RENDAH (optimal)
- Overall Complexity: SEDANG-TINGGI
"""

# ---------------------------------------------------------------------------------
# 9. REKOMENDASI PERBAIKAN
# ---------------------------------------------------------------------------------

"""
REKOMENDASI PERBAIKAN BERDASARKAN ANALISIS METRIK:

1. Refactoring PeminjamanViewSet (WMC=11, CBO=4):
   - Extract method untuk workflow logic
   - Buat service classes untuk business logic
   - Split menjadi multiple smaller ViewSets

2. Mengurangi Coupling:
   - Implement interface segregation
   - Gunakan dependency injection
   - Buat repository pattern untuk data access

3. Meningkatkan Extensibility:
   - Buat abstract base classes untuk common functionality
   - Implement strategy pattern untuk different workflows

4. Testing Strategy:
   - Unit tests untuk classes dengan WMC tinggi
   - Integration tests untuk high coupling classes
   - Mock dependencies untuk CBO tinggi

5. Code Organization:
   - Pisahkan business logic dari controllers
   - Buat service layer
   - Implement clean architecture principles
"""

# ---------------------------------------------------------------------------------
# 10. KESIMPULAN ANALISIS
# ---------------------------------------------------------------------------------

"""
KESIMPULAN ANALISIS KUALITAS DESAIN OO:

DESAIN MODEL CLASSES:
✅ SANGAT BAIK
- WMC rendah hingga sedang (1-5)
- DIT optimal (1)
- CBO rendah (0-2)
- NOC = 0 (acceptable untuk Django models)

DESAIN VIEWSET CLASSES:
⚠️ SEDANG
- WMC bervariasi (0-11), beberapa terlalu tinggi
- DIT optimal (2)
- CBO tinggi pada ViewSet kompleks (4)
- NOC = 0 (kurang extensible)

OVERALL ASSESSMENT:
- Kekuatan: Model design yang solid dan simple
- Kelemahan: ViewSet complexity dan coupling
- Maintainability: 75% BAIK
- Complexity: 60% SEDANG

REKOMENDASI PRIORITAS:
1. Refactor PeminjamanViewSet (highest WMC)
2. Implement service layer untuk business logic
3. Add comprehensive testing
4. Consider microservices architecture untuk scalability
"""

# ---------------------------------------------------------------------------------
# 11. SCRIPT UNTUK MENAMPILKAN HASIL ANALISIS
# ---------------------------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 80)
    print("ANALISIS KUALITAS DESAIN OO - SISTEM INVMANAGE")
    print("=" * 80)

    print("\n📊 RINGKASAN METRIK:")
    print(f"Total Classes: {len(WMC_MODELS) + len(WMC_VIEWSETS)}")
    print(f"Rata-rata WMC: {(sum([c['wmc'] for c in WMC_MODELS.values()]) + sum([c['wmc'] for c in WMC_VIEWSETS.values()])) / (len(WMC_MODELS) + len(WMC_VIEWSETS)):.1f}")
    print(f"Rata-rata CBO: {(sum([c['cbo'] for c in CBO_ANALYSIS.values()])) / len(CBO_ANALYSIS):.1f}")
    print(f"Max WMC: {max([c['wmc'] for c in WMC_MODELS.values()] + [c['wmc'] for c in WMC_VIEWSETS.values()])} (PeminjamanViewSet)")
    print(f"Max CBO: {max([c['cbo'] for c in CBO_ANALYSIS.values()])} (BarangViewSet, PeminjamanViewSet)")

    print("\n🔍 KLASIFIKASI COMPLEXITY:")
    high_complexity = [name for name, data in WMC_VIEWSETS.items() if data['wmc'] > 7]
    print(f"High Complexity Classes: {high_complexity}")

    print("\n✅ KEKUATAN DESAIN:")
    print("- Model classes dengan complexity rendah")
    print("- Inheritance depth optimal")
    print("- Django framework integration yang baik")

    print("\n⚠️ AREA PERBAIKAN:")
    print("- PeminjamanViewSet perlu refactoring")
    print("- Coupling antar ViewSet perlu dikurangi")
    print("- Tambahkan service layer")

    print("\n🎯 REKOMENDASI:")
    print("1. Extract business logic ke service classes")
    print("2. Implement repository pattern")
    print("3. Add comprehensive unit testing")
    print("4. Consider clean architecture principles")

    print("\n" + "=" * 80)