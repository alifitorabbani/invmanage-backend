from django.core.management.base import BaseCommand
from django.utils import timezone
from api.models import Users, Barang, Peminjaman, RiwayatTransaksi, Feedback
import random
from datetime import timedelta, datetime
import time

class Command(BaseCommand):
    help = 'Populate database with sample data'

    def handle(self, *args, **options):
        self.stdout.write('Populating database with sample data...')

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

        # Create sample users
        sample_users = []
        departments = ['IT', 'HR', 'Finance', 'Marketing', 'Operations', 'Sales']

        first_names = ['Ahmad', 'Budi', 'Citra', 'Dewi', 'Eko', 'Fani', 'Gilang', 'Hana', 'Irfan', 'Joko',
                      'Kartika', 'Lutfi', 'Maya', 'Nanda', 'Oka', 'Putri', 'Rizki', 'Sari', 'Taufik', 'Umi',
                      'Vino', 'Wulan', 'Xander', 'Yuni', 'Zaki', 'Adi', 'Bella', 'Candra', 'Dina', 'Erik',
                      'Fira', 'Gita', 'Hadi', 'Indah', 'Joni', 'Kiki', 'Lina', 'Miko', 'Nina', 'Omar',
                      'Prita', 'Rian', 'Sinta', 'Tina', 'Udin', 'Vera', 'Widi', 'Yeni', 'Zara', 'Arif']

        last_names = ['Santoso', 'Wijaya', 'Kusuma', 'Pratama', 'Setiawan', 'Hartono', 'Susanto', 'Wibowo',
                     'Saputra', 'Permana', 'Ramadhan', 'Nugroho', 'Lestari', 'Purnama', 'Aditya', 'Mahendra',
                     'Firmansyah', 'Gunawan', 'Hidayat', 'Irawan', 'Julianto', 'Kurniawan', 'Laksana', 'Mulyono',
                     'Nugraha', 'Oktavian', 'Pangestu', 'Qomaruddin', 'Rahman', 'Siregar', 'Tanjung', 'Utama',
                     'Viantoro', 'Wahyudi', 'Yusuf', 'Zulkarnain', 'Andrianto', 'Budiman', 'Cahyono', 'Darmawan',
                     'Effendi', 'Fadillah', 'Ghozali', 'Halim', 'Iskandar', 'Junaedi', 'Kusnadi', 'Liman', 'Mahmud']

        used_names = set()

        for i in range(200):
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
            if created:
                self.stdout.write(f'Created sample user: {nama}')

        # Use admin and sample users for transactions
        users = [admin] + sample_users

        # Create sample items (expanded to 500 items)
        categories = {
            'Electronics': [
                'Laptop', 'Desktop PC', 'Monitor', 'Keyboard', 'Mouse', 'Printer',
                'Scanner', 'Projector', 'Webcam', 'Headset', 'Speaker', 'Microphone',
                'Router', 'Switch', 'Cable', 'Adapter', 'Power Bank', 'External HDD',
                'USB Flash Drive', 'SD Card', 'Memory Card', 'Graphics Card', 'RAM',
                'SSD', 'Hard Drive', 'Motherboard', 'CPU', 'Cooling Fan', 'UPS',
                'Surge Protector', 'Extension Cord', 'Power Strip', 'Battery',
                'Charger', 'Cable Organizer', 'Screen Protector', 'Case', 'Stand'
            ],
            'Furniture': [
                'Office Chair', 'Desk', 'Cabinet', 'Bookshelf', 'Whiteboard',
                'Notice Board', 'Room Divider', 'File Cabinet', 'Storage Box',
                'Shelf', 'Table', 'Stool', 'Bench', 'Locker', 'Coat Rack'
            ],
            'Supplies': [
                'Notebook', 'Pen', 'Pencil', 'Eraser', 'Sharpener', 'Ruler',
                'Calculator', 'Stapler', 'Paper Clips', 'Binder', 'Envelope',
                'Stamp Pad', 'Ink', 'Toner', 'Label', 'Tape', 'Glue', 'Scissors',
                'Cutter', 'Punch', 'Clip Board', 'Name Card', 'Badge', 'Lanyard'
            ],
            'Equipment': [
                'Coffee Machine', 'Water Dispenser', 'Microwave', 'Refrigerator',
                'Air Conditioner', 'Fan', 'Heater', 'Lamp', 'Light Bulb',
                'Extension', 'Socket', 'Timer', 'Remote Control', 'Battery',
                'First Aid Kit', 'Fire Extinguisher', 'Safety Sign', 'Lock',
                'Key', 'Safe', 'Alarm System', 'Camera', 'Sensor', 'Detector'
            ],
            'IT Accessories': [
                'Mouse Pad', 'Wrist Rest', 'Cable Tie', 'Cleaner', 'Screen Cleaner',
                'Keyboard Cover', 'Mouse Cover', 'Laptop Stand', 'Monitor Arm',
                'Docking Station', 'Hub', 'Card Reader', 'Optical Drive',
                'Network Cable', 'Phone Cable', 'Audio Cable', 'Video Cable'
            ]
        }

        brands = ['Dell', 'HP', 'Lenovo', 'Asus', 'Acer', 'Samsung', 'LG', 'Sony',
                 'Apple', 'Microsoft', 'Logitech', 'Razer', 'Corsair', 'Kingston',
                 'WD', 'Seagate', 'Sandisk', 'TP-Link', 'D-Link', 'Cisco', 'Brother',
                 'Epson', 'Canon', 'Panasonic', 'Sharp', 'Toshiba', 'Fujitsu']

        item_data = []
        item_count = 0
        max_items = 500

        for category, items in categories.items():
            for item in items:
                if item_count >= max_items:
                    break

                # Create variations with brands and specs
                for brand in random.sample(brands, min(3, len(brands))):
                    if item_count >= max_items:
                        break

                    # Generate item name
                    if random.random() > 0.5:
                        name = f"{brand} {item}"
                    else:
                        name = f"{item} {brand}"

                    # Add specifications for tech items
                    if category == 'Electronics':
                        specs = random.choice(['', ' 16GB', ' 32GB', ' 64GB', ' 128GB', ' 256GB', ' 512GB', ' 1TB'])
                        name += specs

                    # Random stock and price
                    stok = random.randint(0, 200)
                    harga = random.randint(10, 500) * 1000  # Price in thousands

                    item_data.append((name, stok, harga))
                    item_count += 1

                if item_count >= max_items:
                    break

            if item_count >= max_items:
                break

        items = []
        for name, stok, harga in item_data:
            item, created = Barang.objects.get_or_create(
                nama=name,
                defaults={
                    'stok': stok,
                    'harga': harga,
                    'minimum': random.randint(5, 20)
                }
            )
            items.append(item)
            if created:
                self.stdout.write(f'Created item: {name}')

        # Create sample loans and transactions
        loan_count = 0
        transaction_count = 0

        # Pre-generate random dates for loans
        base_time = timezone.now()  # Fixed base time for all randomizations
        total_seconds = 14 * 24 * 60 * 60  # 14 days in seconds
        loan_dates = []
        for i in range(1500):
            random_seconds = i * (total_seconds // 1500)  # Evenly distribute dates
            random_date = base_time - timedelta(seconds=random_seconds)
            loan_dates.append(random_date)

        for _ in range(1500):  # Create 1500 loan records
            user = random.choice(users)  # Use random user for loans
            item = random.choice(items)

            if item.stok > 0:
                jumlah = random.randint(1, min(5, item.stok))
                status = random.choice(['dipinjam', 'dikembalikan'])

                # Use pre-generated random date
                tanggal_pinjam = loan_dates.pop(0)

                peminjaman = Peminjaman.objects.create(
                    user=user,
                    barang=item,
                    jumlah=jumlah,
                    status=status,
                    catatan=f'Peminjaman untuk {user.departemen}',
                    tanggal_pinjam=tanggal_pinjam
                )

                if status == 'dikembalikan':
                    peminjaman.tanggal_kembali = peminjaman.tanggal_pinjam + timedelta(days=random.randint(1, 7))
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
                    catatan=f'{"Peminjaman" if status == "dipinjam" else "Pengembalian"} oleh {user.nama}'
                )

                loan_count += 1
                transaction_count += 1

        # Create additional transactions (non-loan)
        for _ in range(1000):
            user = random.choice(users) if random.random() > 0.3 else None
            item = random.choice(items)
            tipe = random.choice(['masuk', 'keluar'])
            jumlah = random.randint(1, 10)

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
                catatan=f'{"Pembelian" if tipe == "masuk" else "Penjualan"} {item.nama}'
            )
            transaction_count += 1

        # Create sample feedback
        feedback_messages = [
            'Barang berkualitas baik',
            'Pelayanan sangat memuaskan',
            'Proses peminjaman mudah',
            'Barang dalam kondisi baik',
            'Terima kasih atas pelayanannya',
            'Sistem inventory sangat membantu',
            'Barang lengkap dan terawat',
            'Proses pengembalian cepat',
            'Admin responsif',
            'Rekomendasi untuk teman',
            'Barang sesuai deskripsi',
            'Peminjaman fleksibel',
            'Kualitas barang excellent',
            'Layanan customer service baik',
            'Sistem mudah digunakan',
            'Barang selalu tersedia',
            'Proses approval cepat',
            'Transparansi yang baik',
            'Manajemen inventory profesional',
            'Terima kasih tim IT'
        ]

        # Pre-generate random dates for feedback
        feedback_dates = []
        for i in range(1000):
            random_seconds = i * (total_seconds // 1000)  # Evenly distribute dates
            random_date = base_time - timedelta(seconds=random_seconds)
            feedback_dates.append(random_date)

        for _ in range(1000):
            tanggal_feedback = feedback_dates.pop(0)

            Feedback.objects.create(
                user=random.choice(users),  # Use random user for feedback
                pesan=random.choice(feedback_messages),
                tanggal=tanggal_feedback
            )

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully populated database:\n'
                f'- 1 admin user + 200 sample users\n'
                f'- {len(items)} items\n'
                f'- {loan_count} loans\n'
                f'- {transaction_count} transactions\n'
                f'- 1000 feedback entries\n'
                f'Total records: ~{201 + len(items) + loan_count + transaction_count + 1000}'
            )
        )