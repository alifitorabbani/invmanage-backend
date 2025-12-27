from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password, check_password
from django.utils import timezone

def validate_pesan_not_empty(value):
    """Validate that feedback message is not empty after stripping whitespace"""
    if not value or len(value.strip()) == 0:
        raise ValidationError('Feedback message cannot be empty.')

class Users(models.Model):
    ROLE_CHOICES = [
        ('user', 'User'),
        ('admin', 'Admin'),
    ]

    nama = models.CharField(max_length=100, db_index=True)
    username = models.CharField(max_length=100, blank=True, null=True, unique=True, db_index=True)
    email = models.EmailField(blank=True, null=True, unique=True, db_index=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    password = models.CharField(max_length=128, blank=True, null=True)  # Increased for hashed passwords
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user', db_index=True)
    departemen = models.CharField(max_length=100, blank=True, null=True, db_index=True)
    foto = models.TextField(blank=True, null=True)  # Base64 encoded image

    class Meta:
        indexes = [
            models.Index(fields=['nama', 'role']),
            models.Index(fields=['email', 'role']),
            models.Index(fields=['departemen', 'role']),
        ]
        constraints = [
            models.CheckConstraint(check=models.Q(role__in=['user', 'admin']), name='valid_role'),
        ]

    def __str__(self):
        return f"{self.nama} ({self.role})"

    def set_password(self, raw_password):
        """Hash and set password"""
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        """Check password against hash"""
        return check_password(raw_password, self.password)

    @property
    def is_admin(self):
        return self.role == 'admin'

    @property
    def is_user(self):
        return self.role == 'user'


class Barang(models.Model):
    nama = models.CharField(max_length=100, db_index=True, unique=True)
    stok = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    harga = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    minimum = models.IntegerField(default=5, validators=[MinValueValidator(0)])  # Stok minimum untuk alert

    class Meta:
        indexes = [
            models.Index(fields=['nama']),
            models.Index(fields=['stok']),
            models.Index(fields=['harga']),
            models.Index(fields=['stok', 'minimum']),  # For low stock queries
        ]
        constraints = [
            models.CheckConstraint(check=models.Q(stok__gte=0), name='stok_non_negative'),
            models.CheckConstraint(check=models.Q(harga__gte=0), name='harga_non_negative'),
            models.CheckConstraint(check=models.Q(minimum__gte=0), name='minimum_non_negative'),
        ]

    def __str__(self):
        return f"{self.nama} (Stok: {self.stok})"

    @property
    def is_low_stock(self):
        """Check if item is low on stock"""
        return self.stok <= self.minimum

    @property
    def is_out_of_stock(self):
        """Check if item is out of stock"""
        return self.stok <= 0

    @property
    def stock_status(self):
        """Get stock status"""
        if self.stok <= 0:
            return 'out_of_stock'
        elif self.stok <= self.minimum:
            return 'low_stock'
        else:
            return 'available'

    def save(self, *args, **kwargs):
        """Override save to ensure data integrity"""
        if self.stok < 0:
            self.stok = 0
        if self.harga < 0:
            self.harga = 0
        if self.minimum < 0:
            self.minimum = 0
        super().save(*args, **kwargs)


class Feedback(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='feedbacks')
    pesan = models.TextField(validators=[validate_pesan_not_empty])
    tanggal = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['tanggal']),
            models.Index(fields=['user', 'tanggal']),
        ]
        ordering = ['-tanggal']

    def __str__(self):
        return f"{self.user.nama} - {self.pesan[:20]}"


class RiwayatTransaksi(models.Model):
    TIPE_CHOICES = [
        ('masuk', 'Masuk'),
        ('keluar', 'Keluar'),
    ]

    barang = models.ForeignKey(Barang, on_delete=models.CASCADE, related_name='transaksi')
    user = models.ForeignKey(Users, on_delete=models.SET_NULL, null=True, blank=True, related_name='transaksi')
    jumlah = models.IntegerField(validators=[MinValueValidator(1)])
    tipe = models.CharField(max_length=10, choices=TIPE_CHOICES, default='masuk', db_index=True)
    catatan = models.TextField(blank=True, null=True)
    tanggal = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['tanggal']),
            models.Index(fields=['tipe', 'tanggal']),
            models.Index(fields=['barang', 'tanggal']),
            models.Index(fields=['user', 'tanggal']),
        ]
        constraints = [
            models.CheckConstraint(check=models.Q(tipe__in=['masuk', 'keluar']), name='valid_tipe'),
            models.CheckConstraint(check=models.Q(jumlah__gt=0), name='jumlah_positive'),
        ]
        ordering = ['-tanggal']

    def __str__(self):
        return f"{self.barang.nama} - {self.tipe} - {self.jumlah}"


class Peminjaman(models.Model):
    STATUS_CHOICES = [
        ('dipinjam', 'Dipinjam'),
        ('dikembalikan', 'Dikembalikan'),
    ]

    barang = models.ForeignKey(Barang, on_delete=models.CASCADE, related_name='peminjaman')
    user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='peminjaman')
    jumlah = models.IntegerField(validators=[MinValueValidator(1)])
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='dipinjam', db_index=True)
    catatan = models.TextField(blank=True, null=True)
    tanggal_pinjam = models.DateTimeField(auto_now_add=True)
    tanggal_kembali = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['tanggal_pinjam']),
            models.Index(fields=['status', 'tanggal_pinjam']),
            models.Index(fields=['barang', 'status']),
            models.Index(fields=['user', 'status']),
            models.Index(fields=['user', 'tanggal_pinjam']),
        ]
        constraints = [
            models.CheckConstraint(check=models.Q(status__in=['dipinjam', 'dikembalikan']), name='valid_status'),
            models.CheckConstraint(check=models.Q(jumlah__gt=0), name='peminjaman_jumlah_positive'),
        ]
        ordering = ['-tanggal_pinjam']

    def __str__(self):
        return f"{self.user.nama} - {self.barang.nama} ({self.status})"

    @property
    def is_overdue(self):
        """Check if loan is overdue (more than 7 days)"""
        if self.status == 'dipinjam':
            from datetime import timedelta
            return self.tanggal_pinjam < timezone.now() - timedelta(days=7)
        return False

    @property
    def days_borrowed(self):
        """Calculate days since borrowed"""
        if self.tanggal_kembali:
            return (self.tanggal_kembali - self.tanggal_pinjam).days
        return (timezone.now() - self.tanggal_pinjam).days
