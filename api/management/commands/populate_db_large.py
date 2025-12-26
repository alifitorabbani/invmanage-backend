from django.core.management.base import BaseCommand
from django.utils import timezone
from api.models import Users, Barang, Peminjaman, RiwayatTransaksi, Feedback
import random
from datetime import timedelta, datetime
import time

class Command(BaseCommand):
    help = 'Populate database with large sample data (2000+ records)'

    def handle(self, *args, **options):
        self.stdout.write('Populating database with large sample data (2000+ records)...')

        # Create admin user
        admin, created = Users.objects.get_or_create(
            nama='admin',
            defaults={
                'email': 'admin@invmanage.com',
                'password': 'admin123',
                'role': 'admin'
            }
        )
        if created:
            self.stdout.write('Created admin user')

        # Create sample users (2000 users)
        sample_users = []
        departments = ['IT', 'HR', 'Finance', 'Marketing', 'Operations', 'Sales', 'Engineering', 'Legal', 'Procurement', 'Quality']

        first_names = ['Ahmad', 'Budi', 'Citra', 'Dewi', 'Eko', 'Fani', 'Gilang', 'Hana', 'Irfan', 'Joko',
                      'Kartika', 'Lutfi', 'Maya', 'Nanda', 'Oka', 'Putri', 'Rizki', 'Sari', 'Taufik', 'Umi',
                      'Vino', 'Wulan', 'Xander', 'Yuni', 'Zaki', 'Adi', 'Bella', 'Candra', 'Dina', 'Erik',
                      'Fira', 'Gita', 'Hadi', 'Indah', 'Joni', 'Kiki', 'Lina', 'Miko', 'Nina', 'Omar',
                      'Prita', 'Rian', 'Sinta', 'Tina', 'Udin', 'Vera', 'Widi', 'Yeni', 'Zara', 'Arif',
                      'Bayu', 'Cici', 'Dedi', 'Elsa', 'Fajar', 'Gina', 'Hendra', 'Ika', 'Juna', 'Kris',
                      'Lala', 'Mira', 'Novi', 'Oki', 'Pandu', 'Rina', 'Susi', 'Tono', 'Uli', 'Vivi',
                      'Wira', 'Yanti', 'Zidan', 'Ali', 'Bunga', 'Ciko', 'Dono', 'Elisa', 'Fikri', 'Galih',
                      'Hesti', 'Ilham', 'Jihan', 'Kemal', 'Luki', 'Meli', 'Nurul', 'Opik', 'Pia', 'Rudi',
                      'Santi', 'Tia', 'Umar', 'Vicky', 'Wanda', 'Yuda', 'Zahra']

        last_names = ['Santoso', 'Wijaya', 'Kusuma', 'Pratama', 'Setiawan', 'Hartono', 'Susanto', 'Wibowo',
                     'Saputra', 'Permana', 'Ramadhan', 'Nugroho', 'Lestari', 'Purnama', 'Aditya', 'Mahendra',
                     'Firmansyah', 'Gunawan', 'Hidayat', 'Irawan', 'Julianto', 'Kurniawan', 'Laksana', 'Mulyono',
                     'Nugraha', 'Oktavian', 'Pangestu', 'Qomaruddin', 'Rahman', 'Siregar', 'Tanjung', 'Utama',
                     'Viantoro', 'Wahyudi', 'Yusuf', 'Zulkarnain', 'Andrianto', 'Budiman', 'Cahyono', 'Darmawan',
                     'Effendi', 'Fadillah', 'Ghozali', 'Halim', 'Iskandar', 'Junaedi', 'Kusnadi', 'Liman', 'Mahmud',
                     'Nababan', 'Oktaviani', 'Prasetyo', 'Raharjo', 'Sari', 'Tampubolon', 'Utomo', 'Viantoro', 'Wahyono',
                     'Yulianto', 'Zainuddin', 'Ardiansyah', 'Baskoro', 'Cahyadi', 'Darmadi', 'Eko', 'Fauzi', 'Gunadi',
                     'Hakim', 'Indarto', 'Jatmiko', 'Kartono', 'Laksito', 'Mardiyanto', 'Nugroho', 'Prabowo', 'Raharja',
                     'Sutrisno', 'Teguh', 'Wibisono', 'Yusuf', 'Zulkifli']

        used_names = set()

        for i in range(2000):
            # Generate unique name
            while True:
                first_name = random.choice(first_names)
                last_name = random.choice(last_names)
                nama = f'{first_name} {last_name}'
                if nama not in used_names:
                    used_names.add(nama)
                    break

            email = f'{first_name.lower()}.{last_name.lower()}@company.com'
            password = 'password123'
            role = 'user'
            departemen = random.choice(departments)
            phone = f'08{random.randint(100000000, 999999999)}'
            foto = None

            user, created = Users.objects.get_or_create(
                nama=nama,
                defaults={
                    'email': email,
                    'password': password,
                    'role': role,
                    'departemen': departemen,
                    'phone': phone,
                    'foto': foto
                }
            )
            sample_users.append(user)
            if created and i % 200 == 0:  # Progress indicator every 200 users
                self.stdout.write(f'Created {i+1} sample users...')

        # Use admin and sample users for transactions
        users = [admin] + sample_users

        # Create sample items (2000 items)
        categories = {
            'Electronics': [
                'Laptop', 'Desktop PC', 'Monitor', 'Keyboard', 'Mouse', 'Printer',
                'Scanner', 'Projector', 'Webcam', 'Headset', 'Speaker', 'Microphone',
                'Router', 'Switch', 'Cable', 'Adapter', 'Power Bank', 'External HDD',
                'USB Flash Drive', 'SD Card', 'Memory Card', 'Graphics Card', 'RAM',
                'SSD', 'Hard Drive', 'Motherboard', 'CPU', 'Cooling Fan', 'UPS',
                'Surge Protector', 'Extension Cord', 'Power Strip', 'Battery',
                'Charger', 'Cable Organizer', 'Screen Protector', 'Case', 'Stand',
                'Smartphone', 'Tablet', 'Smartwatch', 'Earbuds', 'VR Headset', 'Drone',
                'Smart Home Device', 'Gaming Console', 'Controller', 'Soundbar', 'Bluetooth Speaker'
            ],
            'Furniture': [
                'Office Chair', 'Desk', 'Cabinet', 'Bookshelf', 'Whiteboard',
                'Notice Board', 'Room Divider', 'File Cabinet', 'Storage Box',
                'Shelf', 'Table', 'Stool', 'Bench', 'Locker', 'Coat Rack',
                'Conference Table', 'Meeting Room Chair', 'Reception Desk', 'Waiting Chair',
                'Cubicle Panel', 'Partition Wall', 'Storage Cabinet', 'Display Rack'
            ],
            'Supplies': [
                'Notebook', 'Pen', 'Pencil', 'Eraser', 'Sharpener', 'Ruler',
                'Calculator', 'Stapler', 'Paper Clips', 'Binder', 'Envelope',
                'Stamp Pad', 'Ink', 'Toner', 'Label', 'Tape', 'Glue', 'Scissors',
                'Cutter', 'Punch', 'Clip Board', 'Name Card', 'Badge', 'Lanyard',
                'Marker', 'Highlighter', 'Whiteboard Marker', 'Correction Tape', 'Staple Remover',
                'Paper Shredder', 'Binding Machine', 'Laminator', 'ID Card Printer'
            ],
            'Equipment': [
                'Coffee Machine', 'Water Dispenser', 'Microwave', 'Refrigerator',
                'Air Conditioner', 'Fan', 'Heater', 'Lamp', 'Light Bulb',
                'Extension', 'Socket', 'Timer', 'Remote Control', 'Battery',
                'First Aid Kit', 'Fire Extinguisher', 'Safety Sign', 'Lock',
                'Key', 'Safe', 'Alarm System', 'Camera', 'Sensor', 'Detector',
                'Projector Screen', 'Presentation Remote', 'Laser Pointer', 'Flip Chart',
                'Whiteboard Eraser', 'Cleaning Supplies', 'Maintenance Tools'
            ],
            'IT Accessories': [
                'Mouse Pad', 'Wrist Rest', 'Cable Tie', 'Cleaner', 'Screen Cleaner',
                'Keyboard Cover', 'Mouse Cover', 'Laptop Stand', 'Monitor Arm',
                'Docking Station', 'Hub', 'Card Reader', 'Optical Drive',
                'Network Cable', 'Phone Cable', 'Audio Cable', 'Video Cable',
                'USB Hub', 'Ethernet Cable', 'HDMI Cable', 'VGA Cable', 'DisplayPort Cable',
                'Thunderbolt Cable', 'Power Cable', 'Extension Cable', 'Adapter Cable'
            ],
            'Software': [
                'Operating System License', 'Office Suite License', 'Antivirus Software',
                'Design Software', 'Development Tools', 'Database Software', 'Server Software',
                'Cloud Service Subscription', 'Security Software', 'Backup Software',
                'Collaboration Tools', 'Project Management Software', 'Accounting Software'
            ],
            'Facilities': [
                'Cleaning Equipment', 'Maintenance Tools', 'Security Equipment',
                'HVAC Parts', 'Electrical Supplies', 'Plumbing Supplies', 'Building Materials',
                'Safety Equipment', 'Emergency Supplies', 'Parking Permits', 'Access Cards'
            ]
        }

        brands = ['Dell', 'HP', 'Lenovo', 'Asus', 'Acer', 'Samsung', 'LG', 'Sony',
                 'Apple', 'Microsoft', 'Logitech', 'Razer', 'Corsair', 'Kingston',
                 'WD', 'Seagate', 'Sandisk', 'TP-Link', 'D-Link', 'Cisco', 'Brother',
                 'Epson', 'Canon', 'Panasonic', 'Sharp', 'Toshiba', 'Fujitsu', 'Intel',
                 'AMD', 'NVIDIA', 'ASRock', 'Gigabyte', 'MSI', 'ASUS ROG', 'Alienware',
                 'Surface', 'iPad', 'iPhone', 'MacBook', 'iMac', 'Mac Mini', 'AirPods']

        item_data = []
        item_count = 0
        max_items = 2000

        for category, items in categories.items():
            for item in items:
                if item_count >= max_items:
                    break

                # Create variations with brands and specs
                for brand in random.sample(brands, min(5, len(brands))):
                    if item_count >= max_items:
                        break

                    # Generate item name
                    if random.random() > 0.5:
                        name = f"{brand} {item}"
                    else:
                        name = f"{item} {brand}"

                    # Add specifications for tech items
                    if category in ['Electronics', 'IT Accessories']:
                        specs_options = ['', ' 16GB', ' 32GB', ' 64GB', ' 128GB', ' 256GB', ' 512GB', ' 1TB', ' 2TB',
                                       ' i5', ' i7', ' i9', ' Ryzen 5', ' Ryzen 7', ' Ryzen 9', ' 8GB RAM', ' 16GB RAM',
                                       ' 32GB RAM', ' 4K', ' UHD', ' Wireless', ' Bluetooth', ' USB-C', ' Thunderbolt']
                        specs = random.choice(specs_options)
                        if specs:
                            name += specs

                    # Random stock and price
                    stok = random.randint(0, 500)
                    harga = random.randint(10, 2000) * 1000  # Price in thousands

                    item_data.append((name, stok, harga))
                    item_count += 1

                if item_count >= max_items:
                    break

            if item_count >= max_items:
                break

        items = []
        for i, (name, stok, harga) in enumerate(item_data):
            item, created = Barang.objects.get_or_create(
                nama=name,
                defaults={
                    'stok': stok,
                    'harga': harga,
                    'minimum': random.randint(5, 50)
                }
            )
            items.append(item)
            if created and i % 200 == 0:  # Progress indicator every 200 items
                self.stdout.write(f'Created {i+1} items...')

        # Create sample loans and transactions (2000+ records)
        loan_count = 0
        transaction_count = 0

        # Pre-generate random dates for loans (last 30 days)
        base_time = timezone.now()
        total_seconds = 30 * 24 * 60 * 60  # 30 days in seconds
        loan_dates = []
        for i in range(2000):
            random_seconds = i * (total_seconds // 2000)  # Evenly distribute dates
            random_date = base_time - timedelta(seconds=random_seconds)
            loan_dates.append(random_date)

        for i in range(2000):  # Create 2000 loan records
            user = random.choice(users)
            item = random.choice(items)

            if item.stok > 0:
                jumlah = random.randint(1, min(10, item.stok))
                status = random.choice(['dipinjam', 'dikembalikan'])

                # Use pre-generated random date
                tanggal_pinjam = loan_dates.pop(0)

                peminjaman = Peminjaman.objects.create(
                    user=user,
                    barang=item,
                    jumlah=jumlah,
                    status=status,
                    catatan=f'Peminjaman untuk departemen {user.departemen}',
                    tanggal_pinjam=tanggal_pinjam
                )

                if status == 'dikembalikan':
                    peminjaman.tanggal_kembali = peminjaman.tanggal_pinjam + timedelta(days=random.randint(1, 14))
                    peminjaman.save()

                    # Return stock
                    item.stok += jumlah
                    item.save()

                # Reduce stock for active loans
                if status == 'dipinjam':
                    item.stok -= jumlah
                    item.save()

                # Create transaction record
                RiwayatTransaksi.objects.create(
                    barang=item,
                    user=user,
                    jumlah=jumlah,
                    tipe='keluar' if status == 'dipinjam' else 'masuk',
                    catatan=f'{"Peminjaman" if status == "dipinjam" else "Pengembalian"} oleh {user.nama} ({user.departemen})'
                )

                loan_count += 1
                transaction_count += 1

            if i % 200 == 0:  # Progress indicator every 200 loans
                self.stdout.write(f'Created {i+1} loans...')

        # Create additional transactions (2000+ non-loan transactions)
        for i in range(2000):
            user = random.choice(users) if random.random() > 0.7 else None  # 30% anonymous
            item = random.choice(items)
            tipe = random.choice(['masuk', 'keluar'])
            jumlah = random.randint(1, 20)

            if tipe == 'keluar' and item.stok < jumlah:
                continue

            # Update stock
            if tipe == 'masuk':
                item.stok += jumlah
            else:
                item.stok -= jumlah
            item.save()

            RiwayatTransaksi.objects.create(
                barang=item,
                user=user,
                jumlah=jumlah,
                tipe=tipe,
                catatan=f'{"Pembelian/Penerimaan" if tipe == "masuk" else "Penjualan/Pengeluaran"} {item.nama}'
            )
            transaction_count += 1

            if i % 200 == 0:  # Progress indicator every 200 transactions
                self.stdout.write(f'Created {i+1} additional transactions...')

        # Create sample feedback (2000 entries)
        feedback_messages = [
            'Barang berkualitas baik dan sesuai kebutuhan',
            'Pelayanan sangat memuaskan dan responsif',
            'Proses peminjaman mudah dan cepat',
            'Barang dalam kondisi baik dan terawat',
            'Terima kasih atas pelayanannya yang excellent',
            'Sistem inventory sangat membantu pekerjaan',
            'Barang lengkap dan selalu tersedia saat dibutuhkan',
            'Proses pengembalian berjalan lancar',
            'Admin sangat membantu dan informatif',
            'Sangat direkomendasikan untuk rekan kerja',
            'Barang sesuai dengan deskripsi dan spesifikasi',
            'Peminjaman fleksibel sesuai kebutuhan departemen',
            'Kualitas barang excellent dan tahan lama',
            'Layanan customer service sangat baik',
            'Sistem mudah digunakan bahkan untuk pemula',
            'Barang selalu tersedia dalam jumlah memadai',
            'Proses approval berjalan cepat dan efisien',
            'Transparansi dalam manajemen inventory sangat baik',
            'Manajemen inventory profesional dan terorganisir',
            'Terima kasih tim IT atas dukungan teknisnya',
            'Barang baru dan dalam kondisi prima',
            'Peminjaman dapat dilakukan secara online dengan mudah',
            'Sistem tracking barang sangat akurat',
            'Support teknis selalu siap membantu',
            'Inventory selalu update dan akurat',
            'Proses request barang berjalan smooth',
            'Ketersediaan barang memuaskan',
            'Quality control barang sangat baik',
            'Sistem notification sangat membantu',
            'User interface yang user-friendly',
            'Proses dokumentasi lengkap dan jelas',
            'Barang dikategorikan dengan baik',
            'Search functionality sangat powerful',
            'Reporting system sangat informatif',
            'Integration dengan sistem lain berjalan baik',
            'Security dan privacy data terjaga',
            'Backup dan recovery system handal',
            'Performance system sangat responsif',
            'Scalability system sangat baik',
            'Maintenance schedule teratur'
        ]

        # Pre-generate random dates for feedback (last 60 days)
        feedback_dates = []
        total_seconds_feedback = 60 * 24 * 60 * 60  # 60 days in seconds
        for i in range(2000):
            random_seconds = i * (total_seconds_feedback // 2000)
            random_date = base_time - timedelta(seconds=random_seconds)
            feedback_dates.append(random_date)

        for i in range(2000):
            tanggal_feedback = feedback_dates.pop(0)

            Feedback.objects.create(
                user=random.choice(users),
                pesan=random.choice(feedback_messages),
                tanggal=tanggal_feedback
            )

            if i % 200 == 0:  # Progress indicator every 200 feedback
                self.stdout.write(f'Created {i+1} feedback entries...')

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully populated database with LARGE dataset:\n'
                f'✓ 1 admin user + 2000 sample users\n'
                f'✓ {len(items)} inventory items\n'
                f'✓ {loan_count} loan records\n'
                f'✓ {transaction_count} transaction records\n'
                f'✓ 2000 feedback entries\n'
                f'📊 TOTAL RECORDS: ~{2001 + len(items) + loan_count + transaction_count + 2000}\n'
                f'🎯 TARGET ACHIEVED: 2000+ records across all entities!'
            )
        )