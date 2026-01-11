from django.core.management.base import BaseCommand
from django.utils import timezone
from api.models import Users, Feedback
import random
from datetime import timedelta

class Command(BaseCommand):
    help = 'Populate database with sample feedback'

    def handle(self, *args, **options):
        self.stdout.write('Populating database with sample feedback...')

        # Get existing users
        users = list(Users.objects.all())
        if not users:
            self.stdout.write(self.style.ERROR('No users found. Run populate_db first.'))
            return

        # Create sample feedback
        feedback_messages = [
            'Barang berkualitas baik dan sesuai dengan yang diharapkan',
            'Pelayanan sangat memuaskan, tim admin sangat membantu',
            'Proses peminjaman mudah dan tidak ribet',
            'Barang dalam kondisi baik, tidak ada kerusakan',
            'Terima kasih atas pelayanannya yang profesional',
            'Sistem inventory sangat membantu dalam mengelola barang',
            'Barang lengkap dan terawat dengan baik',
            'Proses pengembalian cepat dan efisien',
            'Admin responsif terhadap pertanyaan saya',
            'Rekomendasi untuk teman-teman di departemen',
            'Barang sesuai deskripsi, tidak ada perbedaan',
            'Peminjaman fleksibel sesuai kebutuhan',
            'Kualitas barang excellent, worth it',
            'Layanan customer service baik dan ramah',
            'Sistem mudah digunakan bahkan untuk pemula',
            'Barang selalu tersedia saat dibutuhkan',
            'Proses approval cepat, tidak menunggu lama',
            'Transparansi yang baik dalam proses peminjaman',
            'Manajemen inventory profesional dan terorganisir',
            'Terima kasih tim IT atas sistem yang bagus',
            'Barang yang dipinjam sangat berguna untuk pekerjaan',
            'Proses dokumentasi lengkap dan jelas',
            'Admin memberikan panduan yang mudah dipahami',
            'Ketersediaan barang memudahkan produktivitas',
            'Sistem notifikasi membantu mengingatkan pengembalian',
            'Barang dikembalikan dalam kondisi sama seperti dipinjam',
            'Tim support teknis sangat kompeten',
            'Proses verifikasi admin cepat dan akurat',
            'Variasi barang lengkap untuk berbagai kebutuhan',
            'Interface sistem user-friendly dan intuitif',
            'Barang selalu dalam kondisi prima',
            'Pelayanan 24/7 melalui sistem online',
            'Proses peminjaman dapat dilakukan dari mana saja',
            'Admin memberikan alternatif barang jika yang diminta tidak tersedia',
            'Sistem tracking peminjaman sangat membantu',
            'Barang dikategorikan dengan baik untuk pencarian mudah',
            'Proses pengajuan peminjaman sederhana',
            'Tim admin memberikan feedback konstruktif',
            'Barang disimpan dengan rapi dan terorganisir',
            'Sistem memiliki fitur reminder yang berguna',
            'Proses approval dilakukan dengan pertimbangan matang',
            'Barang yang dipinjam sesuai standar kualitas',
            'Layanan pengembalian dapat dilakukan di berbagai lokasi',
            'Admin memberikan informasi tambahan tentang barang',
            'Sistem memiliki fitur pencarian yang advanced',
            'Barang selalu diperiksa kondisinya sebelum peminjaman',
            'Proses peminjaman terintegrasi dengan sistem HR',
            'Admin memberikan training singkat untuk penggunaan barang',
            'Sistem memiliki dashboard yang informatif',
            'Barang dikembalikan dengan prosedur yang jelas',
            'Tim admin responsif terhadap feedback pengguna',
            'Proses peminjaman mendukung workflow perusahaan',
            'Barang memiliki dokumentasi yang lengkap',
            'Sistem memiliki fitur reporting yang baik',
            'Admin memberikan prioritas untuk kebutuhan urgent',
            'Barang disimpan di lokasi yang mudah diakses',
            'Proses verifikasi dilakukan dengan teliti',
            'Sistem memiliki fitur notifikasi email',
            'Barang selalu diperbaharui dengan yang terbaru',
            'Admin memberikan panduan penggunaan yang detail',
            'Proses peminjaman terintegrasi dengan kalender',
            'Barang memiliki garansi dan dukungan teknis',
            'Sistem memiliki fitur request custom',
            'Admin memberikan alternatif solusi yang kreatif',
            'Barang dikategorikan berdasarkan departemen',
            'Proses pengembalian memiliki checklist yang lengkap',
            'Sistem memiliki fitur analytics untuk admin',
            'Barang selalu dalam kondisi siap pakai',
            'Admin memberikan update status secara real-time',
            'Proses peminjaman mendukung mobile device',
            'Barang memiliki label identifikasi yang jelas',
            'Sistem memiliki fitur auto-approval untuk item tertentu',
            'Admin memberikan feedback tentang penggunaan barang',
            'Proses peminjaman terintegrasi dengan sistem keamanan',
            'Barang disimpan dengan sistem inventory yang akurat',
            'Sistem memiliki fitur reminder otomatis',
            'Admin memberikan training reguler untuk pengguna',
            'Barang selalu diperiksa sebelum dan sesudah peminjaman',
            'Proses approval memiliki escalation matrix',
            'Sistem memiliki fitur search yang powerful',
            'Barang dikembalikan dengan konfirmasi digital',
            'Admin memberikan support untuk troubleshooting',
            'Proses peminjaman mendukung workflow approval',
            'Barang memiliki dokumentasi penggunaan yang lengkap',
            'Sistem memiliki dashboard analytics',
            'Admin memberikan prioritas berdasarkan urgency',
            'Barang disimpan dengan sistem FIFO',
            'Proses verifikasi dilakukan dengan biometrik',
            'Sistem memiliki fitur integration dengan ERP',
            'Barang selalu di-update dengan teknologi terbaru',
            'Admin memberikan konsultasi sebelum peminjaman',
            'Proses peminjaman terintegrasi dengan sistem absensi',
            'Barang memiliki tracking GPS untuk item berharga',
            'Sistem memiliki fitur predictive analytics',
            'Admin memberikan report penggunaan berkala',
            'Proses pengembalian memiliki validasi otomatis',
            'Barang dikategorikan berdasarkan frekuensi penggunaan',
            'Sistem memiliki fitur auto-restock alert',
            'Admin memberikan training khusus untuk equipment',
            'Barang selalu dalam kondisi steril dan bersih',
            'Proses peminjaman mendukung multi-location',
            'Sistem memiliki fitur blockchain untuk tracking',
            'Admin memberikan support 24/7 untuk emergency',
            'Proses approval memiliki workflow yang kompleks',
            'Barang memiliki sensor IoT untuk monitoring',
            'Sistem memiliki AI untuk rekomendasi barang',
            'Admin memberikan feedback loop untuk improvement',
            'Proses peminjaman terintegrasi dengan AI assistant',
            'Barang selalu di-maintain secara preventif',
            'Sistem memiliki fitur VR untuk preview barang',
            'Admin memberikan personalized service',
            'Proses pengembalian memiliki auto-checkout',
            'Barang dikategorikan dengan AI clustering',
            'Sistem memiliki predictive maintenance',
            'Admin memberikan consulting untuk procurement',
            'Proses peminjaman mendukung augmented reality',
            'Barang memiliki digital twin untuk monitoring',
            'Sistem memiliki machine learning untuk forecasting',
            'Admin memberikan strategic advice untuk inventory',
            'Proses approval menggunakan AI decision making',
            'Barang selalu di-upgrade dengan teknologi baru',
            'Sistem memiliki quantum computing untuk optimization',
            'Admin memberikan visionary leadership untuk asset management'
        ]

        # Pre-generate random dates for feedback
        base_time = timezone.now()
        total_seconds = 30 * 24 * 60 * 60  # 30 days in seconds
        feedback_dates = []
        for i in range(500):
            random_seconds = random.randint(0, total_seconds)
            random_date = base_time - timedelta(seconds=random_seconds)
            feedback_dates.append(random_date)

        created_count = 0
        for _ in range(500):
            tanggal_feedback = random.choice(feedback_dates)

            Feedback.objects.create(
                user=random.choice(users),
                pesan=random.choice(feedback_messages),
                tanggal=tanggal_feedback
            )
            created_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {created_count} feedback entries with {len(feedback_messages)} different messages'
            )
        )