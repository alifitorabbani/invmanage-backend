# Inventory Management System - MVC Implementation
# Based on class diagram conversion to Django MVC pattern

from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password, check_password
from django.utils import timezone
from rest_framework import viewsets, status, serializers
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from django.db.models import Count, Sum, Q, F, Prefetch
from django.core.cache import cache
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)

# =============================================================================
# MODELS (M in MVC) - Business Entities
# =============================================================================

def validate_pesan_not_empty(value):
    """Validate that feedback message is not empty after stripping whitespace"""
    if not value or len(value.strip()) == 0:
        raise ValidationError('Feedback message cannot be empty.')

class Users(models.Model):
    """Users Model - Authentication and Profile Management"""
    ROLE_CHOICES = [
        ('user', 'User'),
        ('admin', 'Admin'),
    ]

    # Authentication fields
    nama = models.CharField(max_length=100, db_index=True)
    username = models.CharField(max_length=100, blank=True, null=True, unique=True)
    email = models.EmailField(blank=True, null=True, unique=True)
    password = models.CharField(max_length=128, blank=True, null=True)

    # Profile fields
    phone = models.CharField(max_length=20, blank=True, null=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')
    departemen = models.CharField(max_length=100, blank=True, null=True)
    foto = models.TextField(blank=True, null=True)  # Base64 encoded

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

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

    # Methods
    def set_password(self, raw_password):
        """Hash and set password"""
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        """Check password against hash"""
        return check_password(raw_password, self.password)

    # Properties
    @property
    def is_admin(self):
        return self.role == 'admin'

    @property
    def is_user(self):
        return self.role == 'user'


class Barang(models.Model):
    """Barang (Item) Model - Inventory Management"""
    nama = models.CharField(max_length=100, db_index=True, unique=True)
    stok = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    harga = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    minimum = models.IntegerField(default=5, validators=[MinValueValidator(0)])

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['nama']),
            models.Index(fields=['stok']),
            models.Index(fields=['harga']),
            models.Index(fields=['stok', 'minimum']),
        ]
        constraints = [
            models.CheckConstraint(check=models.Q(stok__gte=0), name='stok_non_negative'),
            models.CheckConstraint(check=models.Q(harga__gte=0), name='harga_non_negative'),
            models.CheckConstraint(check=models.Q(minimum__gte=0), name='minimum_non_negative'),
        ]

    def __str__(self):
        return f"{self.nama} (Stok: {self.stok})"

    # Properties
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

    # Methods
    def save(self, *args, **kwargs):
        """Override save to ensure data integrity"""
        if self.stok < 0:
            self.stok = 0
        if self.harga < 0:
            self.harga = 0
        if self.minimum < 0:
            self.minimum = 0
        super().save(*args, **kwargs)


class Peminjaman(models.Model):
    """Peminjaman (Loan) Model - Loan Management"""
    STATUS_CHOICES = [
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('dipinjam', 'Dipinjam'),
        ('dikembalikan', 'Dikembalikan'),
    ]

    # Relationships
    barang = models.ForeignKey(Barang, on_delete=models.CASCADE, related_name='peminjaman')
    user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='peminjaman')

    # Loan details
    jumlah = models.IntegerField(validators=[MinValueValidator(1)])
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending', db_index=True)
    alasan_peminjaman = models.TextField(blank=True, null=True)
    alasan_reject = models.TextField(blank=True, null=True)
    admin_verifier = models.ForeignKey(Users, on_delete=models.SET_NULL, null=True, blank=True, related_name='verified_loans')
    catatan = models.TextField(blank=True, null=True)

    # Dates
    tanggal_pinjam = models.DateTimeField(auto_now_add=True)
    tanggal_kembali = models.DateTimeField(null=True, blank=True)
    tanggal_verifikasi = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['tanggal_pinjam']),
            models.Index(fields=['status', 'tanggal_pinjam']),
            models.Index(fields=['barang', 'status']),
            models.Index(fields=['user', 'status']),
            models.Index(fields=['user', 'tanggal_pinjam']),
            models.Index(fields=['admin_verifier', 'tanggal_verifikasi']),
        ]
        constraints = [
            models.CheckConstraint(check=models.Q(status__in=['pending', 'approved', 'rejected', 'dipinjam', 'dikembalikan']), name='valid_status'),
            models.CheckConstraint(check=models.Q(jumlah__gt=0), name='peminjaman_jumlah_positive'),
        ]
        ordering = ['-tanggal_pinjam']

    def __str__(self):
        return f"{self.user.nama} - {self.barang.nama} ({self.status})"

    # Properties
    @property
    def is_overdue(self):
        """Check if loan is overdue (more than 7 days)"""
        if self.status == 'dipinjam':
            return self.tanggal_pinjam < timezone.now() - timedelta(days=7)
        return False

    @property
    def days_borrowed(self):
        """Calculate days since borrowed"""
        if self.tanggal_kembali:
            return (self.tanggal_kembali - self.tanggal_pinjam).days
        return (timezone.now() - self.tanggal_pinjam).days


class RiwayatTransaksi(models.Model):
    """RiwayatTransaksi (Transaction History) Model - Audit Trail"""
    TIPE_CHOICES = [
        ('masuk', 'Masuk'),
        ('keluar', 'Keluar'),
    ]

    # Relationships
    barang = models.ForeignKey(Barang, on_delete=models.CASCADE, related_name='transaksi')
    user = models.ForeignKey(Users, on_delete=models.SET_NULL, null=True, blank=True, related_name='transaksi')

    # Transaction details
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


class Feedback(models.Model):
    """Feedback Model - User Feedback System"""
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


# =============================================================================
# SERIALIZERS (V in MVC) - Data Transfer Objects
# =============================================================================

class UsersSerializer(serializers.ModelSerializer):
    """Users Serializer - Data transformation for Users model"""
    password = serializers.CharField(write_only=True, required=False)
    is_admin = serializers.ReadOnlyField()
    is_user = serializers.ReadOnlyField()

    class Meta:
        model = Users
        fields = ['id', 'nama', 'username', 'email', 'phone', 'password', 'role', 'departemen', 'foto', 'is_admin', 'is_user']

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = super().create(validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user

    def validate_email(self, value):
        if value and Users.objects.filter(email=value).exclude(id=self.instance.id if self.instance else None).exists():
            raise serializers.ValidationError("Email already exists")
        return value

    def validate_username(self, value):
        if value and Users.objects.filter(username=value).exclude(id=self.instance.id if self.instance else None).exists():
            raise serializers.ValidationError("Username already exists")
        return value


class BarangSerializer(serializers.ModelSerializer):
    """Barang Serializer - Data transformation for Barang model"""
    status = serializers.ReadOnlyField()
    is_low_stock = serializers.ReadOnlyField()
    is_out_of_stock = serializers.ReadOnlyField()
    stock_status = serializers.ReadOnlyField()

    class Meta:
        model = Barang
        fields = ['id', 'nama', 'stok', 'harga', 'minimum', 'status', 'is_low_stock', 'is_out_of_stock', 'stock_status']

    def validate_stok(self, value):
        if value < 0:
            raise serializers.ValidationError("Stock cannot be negative")
        return value

    def validate_harga(self, value):
        if value < 0:
            raise serializers.ValidationError("Price cannot be negative")
        return value

    def validate_minimum(self, value):
        if value < 0:
            raise serializers.ValidationError("Minimum stock cannot be negative")
        return value


class PeminjamanSerializer(serializers.ModelSerializer):
    """Peminjaman Serializer - Data transformation for Peminjaman model"""
    barang_nama = serializers.CharField(source='barang.nama', read_only=True)
    user_nama = serializers.CharField(source='user.nama', read_only=True)
    admin_verifier_nama = serializers.CharField(source='admin_verifier.nama', read_only=True, allow_null=True)
    is_overdue = serializers.ReadOnlyField()
    days_borrowed = serializers.ReadOnlyField()

    class Meta:
        model = Peminjaman
        fields = ['id', 'barang', 'barang_nama', 'user', 'user_nama', 'jumlah', 'status', 'alasan_peminjaman', 'alasan_reject', 'admin_verifier', 'admin_verifier_nama', 'catatan', 'tanggal_pinjam', 'tanggal_kembali', 'tanggal_verifikasi', 'is_overdue', 'days_borrowed']
        read_only_fields = ['tanggal_pinjam', 'tanggal_kembali', 'is_overdue', 'days_borrowed', 'admin_verifier_nama', 'tanggal_verifikasi']

    def validate_jumlah(self, value):
        if value <= 0:
            raise serializers.ValidationError("Quantity must be positive")
        return value

    def validate(self, data):
        if not self.instance:  # Creation
            barang = data.get('barang')
            jumlah = data.get('jumlah', 0)
            if barang and barang.stok < jumlah:
                raise serializers.ValidationError("Insufficient stock")
            if not data.get('alasan_peminjaman'):
                raise serializers.ValidationError("Alasan peminjaman is required")
        else:  # Update
            status = data.get('status', self.instance.status)
            if status == 'rejected' and not data.get('alasan_reject') and not self.instance.alasan_reject:
                raise serializers.ValidationError("Alasan reject is required when rejecting")
        return data


class RiwayatTransaksiSerializer(serializers.ModelSerializer):
    """RiwayatTransaksi Serializer - Data transformation for RiwayatTransaksi model"""
    barang_nama = serializers.CharField(source='barang.nama', read_only=True)
    user_nama = serializers.CharField(source='user.nama', read_only=True, allow_null=True)

    class Meta:
        model = RiwayatTransaksi
        fields = ['id', 'barang', 'barang_nama', 'user', 'user_nama', 'jumlah', 'tipe', 'catatan', 'tanggal']
        read_only_fields = ['tanggal']

    def validate_jumlah(self, value):
        if value <= 0:
            raise serializers.ValidationError("Quantity must be positive")
        return value


class FeedbackSerializer(serializers.ModelSerializer):
    """Feedback Serializer - Data transformation for Feedback model"""
    user_nama = serializers.CharField(source='user.nama', read_only=True)

    class Meta:
        model = Feedback
        fields = ['id', 'user', 'user_nama', 'pesan', 'tanggal']
        read_only_fields = ['tanggal']

    def validate_pesan(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Message cannot be empty")
        return value.strip()


# =============================================================================
# VIEWSETS/CONTROLLERS (C in MVC) - Business Logic and API Endpoints
# =============================================================================

class BarangViewSet(viewsets.ModelViewSet):
    """Barang Controller - CRUD operations for Barang model"""
    queryset = Barang.objects.all()
    serializer_class = BarangSerializer
    throttle_classes = [UserRateThrottle, AnonRateThrottle]

    def create(self, request, *args, **kwargs):
        """Create new item with validation and cache clearing"""
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            nama = serializer.validated_data.get('nama', '').strip()
            if Barang.objects.filter(nama__iexact=nama).exists():
                return Response({'error': 'Nama barang sudah digunakan'}, status=status.HTTP_400_BAD_REQUEST)

            self.perform_create(serializer)

            # Clear related caches
            cache.delete('barang_statistics')
            cache.delete('reports_dashboard')

            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

        except serializers.ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error creating item: {str(e)}")
            return Response({'error': 'Gagal menambah barang'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def update(self, request, *args, **kwargs):
        """Update item with validation and cache clearing"""
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=kwargs.pop('partial', False))
            serializer.is_valid(raise_exception=True)

            nama = serializer.validated_data.get('nama', '').strip()
            if Barang.objects.filter(nama__iexact=nama).exclude(id=instance.id).exists():
                return Response({'error': 'Nama barang sudah digunakan'}, status=status.HTTP_400_BAD_REQUEST)

            self.perform_update(serializer)

            # Clear related caches
            cache.delete('barang_statistics')
            cache.delete('reports_dashboard')

            return Response(serializer.data)

        except serializers.ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error updating item: {str(e)}")
            return Response({'error': 'Gagal mengupdate barang'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def destroy(self, request, *args, **kwargs):
        """Delete item with safety checks"""
        try:
            instance = self.get_object()

            # Check if item is referenced in active loans
            active_loans = Peminjaman.objects.filter(barang=instance, status='dipinjam').count()
            if active_loans > 0:
                return Response({
                    'error': f'Barang tidak dapat dihapus karena sedang dipinjam ({active_loans} peminjaman aktif)'
                }, status=status.HTTP_400_BAD_REQUEST)

            self.perform_destroy(instance)

            # Clear related caches
            cache.delete('barang_statistics')
            cache.delete('reports_dashboard')

            return Response({'success': True, 'message': 'Barang berhasil dihapus'}, status=status.HTTP_204_NO_CONTENT)

        except Exception as e:
            logger.error(f"Error deleting item: {str(e)}")
            return Response({'error': 'Gagal menghapus barang'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get_queryset(self):
        """Advanced filtering for items"""
        queryset = Barang.objects.order_by('nama')
        search = self.request.query_params.get('search', '')
        status_filter = self.request.query_params.get('status', '')

        if search:
            queryset = queryset.filter(
                Q(nama__icontains=search) |
                Q(stok__icontains=search)
            )

        if status_filter:
            if status_filter == 'low_stock':
                queryset = queryset.filter(stok__lte=F('minimum'))
            elif status_filter == 'out_of_stock':
                queryset = queryset.filter(stok=0)
            elif status_filter == 'available':
                queryset = queryset.filter(stok__gt=F('minimum'))

        return queryset

    @action(detail=True, methods=['post'])
    def update_stok(self, request, pk=None):
        """Update stock and create transaction record"""
        try:
            barang = self.get_object()
            jumlah = int(request.data.get('jumlah', 0))
            tipe = request.data.get('tipe', 'masuk')
            catatan = request.data.get('catatan', '')
            user_id = request.data.get('user_id')

            if jumlah <= 0:
                return Response({'error': 'Jumlah harus positif'}, status=status.HTTP_400_BAD_REQUEST)

            if tipe not in ['masuk', 'keluar']:
                return Response({'error': 'Tipe harus masuk atau keluar'}, status=status.HTTP_400_BAD_REQUEST)

            user = None
            if user_id:
                try:
                    user = Users.objects.get(pk=user_id)
                except Users.DoesNotExist:
                    return Response({'error': 'User tidak ditemukan'}, status=status.HTTP_404_NOT_FOUND)

            # Calculate new stock
            if tipe == 'masuk':
                new_stok = barang.stok + jumlah
            else:
                new_stok = barang.stok - jumlah
                if new_stok < 0:
                    return Response({'error': 'Stok tidak mencukupi'}, status=status.HTTP_400_BAD_REQUEST)

            barang.stok = new_stok
            barang.save()

            # Create transaction record
            RiwayatTransaksi.objects.create(
                barang=barang,
                user=user,
                jumlah=jumlah,
                tipe=tipe,
                catatan=catatan
            )

            # Clear caches
            cache.delete('barang_statistics')
            cache.delete('reports_dashboard')

            return Response(BarangSerializer(barang).data)

        except ValueError:
            return Response({'error': 'Jumlah harus berupa angka'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error updating stock: {str(e)}")
            return Response({'error': 'Terjadi kesalahan internal'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'])
    def low_stock(self, request):
        """Get items with low stock"""
        items = self.get_queryset().filter(stok__lte=F('minimum'))[:20]
        serializer = self.get_serializer(items, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get basic statistics"""
        cache_key = 'barang_statistics'
        data = cache.get(cache_key)

        if not data:
            data = {
                'total_items': Barang.objects.count(),
                'total_stock': Barang.objects.aggregate(total=Sum('stok'))['total'] or 0,
                'low_stock_items': Barang.objects.filter(stok__lte=F('minimum')).count(),
                'out_of_stock_items': Barang.objects.filter(stok=0).count(),
                'average_price': Barang.objects.aggregate(avg=Sum('harga') / Count('id'))['avg'] or 0,
            }
            cache.set(cache_key, data, 300)  # Cache for 5 minutes

        return Response(data)


class UsersViewSet(viewsets.ModelViewSet):
    """Users Controller - User management operations"""
    queryset = Users.objects.all()
    serializer_class = UsersSerializer

    @action(detail=True, methods=['post'])
    def change_password(self, request, pk=None):
        """Change user password"""
        user = self.get_object()
        old_password = request.data.get('old_password', '')
        new_password = request.data.get('new_password', '')

        if not old_password or not new_password:
            return Response({'error': 'Password lama dan baru wajib diisi'}, status=status.HTTP_400_BAD_REQUEST)

        if user.password != old_password:
            return Response({'error': 'Password lama salah'}, status=status.HTTP_400_BAD_REQUEST)

        user.password = new_password
        user.save()
        return Response({'success': True, 'message': 'Password berhasil diubah'})

    @action(detail=True, methods=['post'])
    def update_foto(self, request, pk=None):
        """Update user profile photo"""
        user = self.get_object()
        foto = request.data.get('foto', '')
        user.foto = foto
        user.save()
        return Response({'success': True, 'user': UsersSerializer(user).data})


class PeminjamanViewSet(viewsets.ModelViewSet):
    """Peminjaman Controller - Loan management operations"""
    queryset = Peminjaman.objects.all()
    serializer_class = PeminjamanSerializer
    throttle_classes = [UserRateThrottle, AnonRateThrottle]

    def get_queryset(self):
        """Advanced filtering with query parameters"""
        queryset = Peminjaman.objects.select_related('barang', 'user', 'admin_verifier').order_by('-tanggal_pinjam')
        user_id = self.request.query_params.get('user')
        status_filter = self.request.query_params.get('status')
        overdue = self.request.query_params.get('overdue')
        include_pending = self.request.query_params.get('include_pending', 'false').lower() == 'true'

        if user_id:
            queryset = queryset.filter(user_id=user_id)

        # Include pending for detail operations
        if self.action in ['retrieve', 'update', 'partial_update', 'destroy']:
            include_pending = True

        # Exclude pending by default for admin views
        if not include_pending:
            queryset = queryset.exclude(status='pending')

        if status_filter:
            queryset = queryset.filter(status=status_filter)

        if overdue == 'true':
            seven_days_ago = timezone.now() - timedelta(days=7)
            queryset = queryset.filter(
                status='dipinjam',
                tanggal_pinjam__lt=seven_days_ago
            )

        return queryset

    def create(self, request, *args, **kwargs):
        """Create loan request with status pending"""
        barang_id = request.data.get('barang')
        jumlah = int(request.data.get('jumlah', 0))
        user_id = request.data.get('user')

        try:
            barang = Barang.objects.get(pk=barang_id)
            user = None
            if user_id:
                try:
                    user = Users.objects.get(pk=user_id)
                except Users.DoesNotExist:
                    pass

            # Create loan with status pending
            data = request.data.copy()
            data['user'] = user_id
            data['status'] = 'pending'
            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        except Barang.DoesNotExist:
            return Response({'error': 'Barang tidak ditemukan'}, status=status.HTTP_404_NOT_FOUND)
        except ValueError:
            return Response({'error': 'Jumlah harus berupa angka'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def partial_update(self, request, *args, **kwargs):
        """Update loan with stock reconciliation"""
        peminjaman = self.get_object()
        old_status = peminjaman.status
        new_status = request.data.get('status', old_status)
        new_jumlah = int(request.data.get('jumlah', peminjaman.jumlah))

        # Status change from approved to dipinjam (user picks up item)
        if old_status == 'approved' and new_status == 'dipinjam':
            if peminjaman.barang.stok < new_jumlah:
                return Response({'error': 'Stok tidak mencukupi'}, status=status.HTTP_400_BAD_REQUEST)
            peminjaman.barang.stok -= new_jumlah
            peminjaman.barang.save()
            RiwayatTransaksi.objects.create(
                barang=peminjaman.barang,
                user=peminjaman.user,
                jumlah=new_jumlah,
                tipe='keluar',
                catatan=f'Peminjaman disetujui oleh {peminjaman.admin_verifier.nama if peminjaman.admin_verifier else "Admin"}'
            )

        # Status change from dipinjam to dikembalikan
        elif old_status == 'dipinjam' and new_status == 'dikembalikan':
            peminjaman.barang.stok += peminjaman.jumlah
            peminjaman.barang.save()
            peminjaman.tanggal_kembali = timezone.now()
            RiwayatTransaksi.objects.create(
                barang=peminjaman.barang,
                user=peminjaman.user,
                jumlah=peminjaman.jumlah,
                tipe='masuk',
                catatan=f'Pengembalian oleh {peminjaman.user.nama}'
            )

        # Quantity change while borrowed
        elif old_status == 'dipinjam' and new_status == 'dipinjam' and new_jumlah != peminjaman.jumlah:
            diff = new_jumlah - peminjaman.jumlah
            if diff > 0 and peminjaman.barang.stok < diff:
                return Response({'error': 'Stok tidak mencukupi'}, status=status.HTTP_400_BAD_REQUEST)
            peminjaman.barang.stok -= diff
            peminjaman.barang.save()

        response = super().partial_update(request, *args, **kwargs)

        # Set verification timestamp for approved/rejected status changes
        if old_status != new_status and new_status in ['approved', 'rejected']:
            peminjaman.tanggal_verifikasi = timezone.now()
            peminjaman.save(update_fields=['tanggal_verifikasi'])

        return response

    @action(detail=True, methods=['post'])
    def kembalikan(self, request, pk=None):
        """Return item and restore stock"""
        peminjaman = self.get_object()

        if peminjaman.status == 'dikembalikan':
            return Response({'error': 'Barang sudah dikembalikan'}, status=status.HTTP_400_BAD_REQUEST)

        peminjaman.barang.stok += peminjaman.jumlah
        peminjaman.barang.save()

        RiwayatTransaksi.objects.create(
            barang=peminjaman.barang,
            user=peminjaman.user,
            jumlah=peminjaman.jumlah,
            tipe='masuk',
            catatan=f'Pengembalian oleh {peminjaman.user.nama}'
        )

        peminjaman.status = 'dikembalikan'
        peminjaman.tanggal_kembali = timezone.now()
        peminjaman.save()

        cache.delete('reports_dashboard')

        return Response(PeminjamanSerializer(peminjaman).data)

    @action(detail=False, methods=['get'])
    def active_loans(self, request):
        """Get active loans"""
        user_id = request.query_params.get('user_id')
        queryset = self.get_queryset().filter(status__in=['approved', 'dipinjam'])

        if user_id:
            queryset = queryset.filter(user_id=user_id)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def overdue_loans(self, request):
        """Get all overdue loans"""
        seven_days_ago = timezone.now() - timedelta(days=7)
        queryset = self.get_queryset().filter(
            status='dipinjam',
            tanggal_pinjam__lt=seven_days_ago
        )
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def extend_loan(self, request, pk=None):
        """Extend loan duration"""
        peminjaman = self.get_object()

        if peminjaman.status != 'dipinjam':
            return Response({'error': 'Hanya peminjaman aktif yang bisa diperpanjang'}, status=status.HTTP_400_BAD_REQUEST)

        if peminjaman.is_overdue:
            return Response({'error': 'Peminjaman sudah terlambat, tidak bisa diperpanjang'}, status=status.HTTP_400_BAD_REQUEST)

        peminjaman.catatan = f"{peminjaman.catatan or ''} [Diperpanjang]".strip()
        peminjaman.save()

        return Response({
            'success': True,
            'message': 'Peminjaman berhasil diperpanjang',
            'peminjaman': PeminjamanSerializer(peminjaman).data
        })

    @action(detail=False, methods=['post'])
    def manual(self, request):
        """Create manual loan entry"""
        return self.create(request)


class RiwayatTransaksiViewSet(viewsets.ModelViewSet):
    """RiwayatTransaksi Controller - Transaction history operations"""
    queryset = RiwayatTransaksi.objects.all().order_by('-tanggal')
    serializer_class = RiwayatTransaksiSerializer


class FeedbackViewSet(viewsets.ModelViewSet):
    """Feedback Controller - User feedback operations"""
    queryset = Feedback.objects.all().order_by('-tanggal')
    serializer_class = FeedbackSerializer

    def get_queryset(self):
        queryset = Feedback.objects.select_related('user').order_by('-tanggal')
        user_id = self.request.query_params.get('user_id')
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        return queryset

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get feedback statistics"""
        total_feedback = self.get_queryset().count()
        user_feedback = self.get_queryset().values('user__nama').annotate(
            count=Count('id')
        ).order_by('-count')[:5]

        return Response({
            'total_feedback': total_feedback,
            'top_contributors': list(user_feedback)
        })


# =============================================================================
# AUTHENTICATION VIEWS (API Authentication Controllers)
# =============================================================================

@api_view(['POST'])
def login_view(request):
    """User login controller"""
    nama = request.data.get('nama', '').strip()
    password = request.data.get('password', '')

    if not nama or not password:
        return Response({'error': 'Nama dan password wajib diisi'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = Users.objects.get(nama=nama)
        if user.password == password:
            if user.role != 'user':
                return Response({'error': 'Akun ini bukan akun user. Gunakan halaman login admin.'}, status=status.HTTP_403_FORBIDDEN)
            serializer = UsersSerializer(user)
            return Response({
                'success': True,
                'user': serializer.data,
                'redirect_to': 'user_dashboard'
            })
        else:
            return Response({'error': 'Password salah'}, status=status.HTTP_401_UNAUTHORIZED)
    except Users.DoesNotExist:
        return Response({'error': 'User tidak ditemukan'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def register_view(request):
    """User registration controller"""
    nama = request.data.get('nama', '').strip()
    email = request.data.get('email', '').strip()
    password = request.data.get('password', '')
    role = request.data.get('role', 'user').strip()
    admin_code = request.data.get('admin_code', '')

    if not nama or not email or not password:
        return Response({'error': 'Nama, email dan password wajib diisi'}, status=status.HTTP_400_BAD_REQUEST)

    if role not in ['user', 'admin']:
        return Response({'error': 'Role harus user atau admin'}, status=status.HTTP_400_BAD_REQUEST)

    if role == 'admin' and admin_code != 'ADMIN2025':
        return Response({'error': 'Kode admin diperlukan untuk mendaftar sebagai admin'}, status=status.HTTP_403_FORBIDDEN)

    if '@' not in email.lower():
        return Response({'error': 'Email tidak bisa terdaftar karena tidak ada @'}, status=status.HTTP_400_BAD_REQUEST)

    if Users.objects.filter(nama=nama).exists():
        return Response({'error': 'Nama sudah digunakan'}, status=status.HTTP_400_BAD_REQUEST)

    if Users.objects.filter(email=email).exists():
        existing = Users.objects.get(email=email)
        if existing.role != role:
            return Response({'error': 'Email sudah digunakan untuk role lain'}, status=status.HTTP_400_BAD_REQUEST)

    user = Users.objects.create(nama=nama, email=email, password=password, role=role)
    redirect_to = 'admin_dashboard' if role == 'admin' else 'user_dashboard'
    return Response({
        'success': True,
        'user': UsersSerializer(user).data,
        'redirect_to': redirect_to
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
def admin_login_view(request):
    """Admin login controller"""
    identifier = request.data.get('nama', '').strip() or request.data.get('email', '').strip()
    password = request.data.get('password', '')

    if not identifier or not password:
        return Response({'error': 'Nama/Email dan password wajib diisi'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        try:
            user = Users.objects.get(nama=identifier)
        except Users.DoesNotExist:
            try:
                user = Users.objects.get(email=identifier)
            except Users.DoesNotExist:
                return Response({'error': 'Admin tidak ditemukan'}, status=status.HTTP_404_NOT_FOUND)

        if user.password == password and user.role == 'admin':
            serializer = UsersSerializer(user)
            return Response({
                'success': True,
                'user': serializer.data,
                'redirect_to': 'admin_dashboard'
            })
        else:
            return Response({'error': 'Kredensial admin tidak valid'}, status=status.HTTP_401_UNAUTHORIZED)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def admin_register_view(request):
    """Admin registration controller"""
    nama = request.data.get('nama', '').strip()
    email = request.data.get('email', '').strip()
    password = request.data.get('password', '')
    admin_code = request.data.get('admin_code', '')

    if not nama or not password:
        return Response({'error': 'Nama dan password wajib diisi'}, status=status.HTTP_400_BAD_REQUEST)

    if admin_code != 'ADMIN2025':
        return Response({'error': 'Kode admin tidak valid'}, status=status.HTTP_403_FORBIDDEN)

    if email and '@' not in email.lower():
        return Response({'error': 'Email tidak bisa terdaftar karena tidak ada @'}, status=status.HTTP_400_BAD_REQUEST)

    if Users.objects.filter(nama=nama).exists():
        return Response({'error': 'Nama sudah digunakan'}, status=status.HTTP_400_BAD_REQUEST)

    if email and Users.objects.filter(email=email).exists():
        existing = Users.objects.get(email=email)
        if existing.role != 'admin':
            return Response({'error': 'Email sudah digunakan untuk role lain'}, status=status.HTTP_400_BAD_REQUEST)

    user = Users.objects.create(nama=nama, email=email or None, password=password, role='admin')
    return Response({
        'success': True,
        'user': UsersSerializer(user).data,
        'redirect_to': 'admin_dashboard'
    }, status=status.HTTP_201_CREATED)


# =============================================================================
# REPORTING VIEWS (Chart Data Controllers)
# =============================================================================

@api_view(['GET'])
def item_stock_levels(request):
    """Controller for item stock levels chart data"""
    cache_key = 'item_stock_levels'
    data = cache.get(cache_key)

    if not data:
        items = Barang.objects.all().order_by('-stok')[:20]
        data = {
            'labels': [item.nama[:30] + '...' if len(item.nama) > 30 else item.nama for item in items],
            'datasets': [{
                'label': 'Stok',
                'data': [item.stok for item in items],
                'backgroundColor': 'rgba(54, 162, 235, 0.6)',
                'borderColor': 'rgba(54, 162, 235, 1)',
                'borderWidth': 1
            }]
        }
        cache.set(cache_key, data, 600)

    return Response(data)


@api_view(['GET'])
def reports_dashboard(request):
    """Dashboard metrics controller"""
    cache_key = 'reports_dashboard'
    data = cache.get(cache_key)

    if not data:
        data = {
            'total_items': Barang.objects.count(),
            'total_loans': Peminjaman.objects.count(),
            'active_loans': Peminjaman.objects.filter(status='dipinjam').count(),
            'total_transactions': RiwayatTransaksi.objects.count(),
            'low_stock_items': Barang.objects.filter(Q(stok__lte=5) | Q(stok__lt=F('minimum'))).count(),
            'total_users': Users.objects.filter(role='user').count(),
            'total_feedback': Feedback.objects.count()
        }
        cache.set(cache_key, data, 180)

    return Response(data)


# =============================================================================
# UTILITY CLASSES (Supporting Classes)
# =============================================================================

class StandardResultsSetPagination:
    """Pagination utility class"""
    page_size = 25
    page_size_query_param = 'page_size'
    max_page_size = 100


class Cache:
    """Cache utility class"""
    @staticmethod
    def get(key):
        return cache.get(key)

    @staticmethod
    def set(key, value, timeout):
        cache.set(key, value, timeout)

    @staticmethod
    def delete(key):
        cache.delete(key)

    @staticmethod
    def delete_pattern(pattern):
        cache.delete_pattern(pattern)


# =============================================================================
# RELATIONSHIPS SUMMARY (as per class diagram)
# =============================================================================
"""
Entity Relationships (as defined in class diagram):

Users ||--o{ Peminjaman : borrows
Users ||--o{ RiwayatTransaksi : performs
Users ||--o{ Feedback : submits

Barang ||--o{ Peminjaman : lent_out
Barang ||--o{ RiwayatTransaksi : involved_in

Peminjaman }o--|| Barang : item
Peminjaman }o--|| Users : borrower

RiwayatTransaksi }o--|| Barang : item
RiwayatTransaksi }o--o| Users : user

Feedback }o--|| Users : submitter

ViewSet to Serializer relationships:
BarangViewSet ..> BarangSerializer : uses
UsersViewSet ..> UsersSerializer : uses
PeminjamanViewSet ..> PeminjamanSerializer : uses
RiwayatTransaksiViewSet ..> RiwayatTransaksiSerializer : uses
FeedbackViewSet ..> FeedbackSerializer : uses

ViewSet to Model relationships:
BarangViewSet ..> Barang : manages
UsersViewSet ..> Users : manages
PeminjamanViewSet ..> Peminjaman : manages
RiwayatTransaksiViewSet ..> RiwayatTransaksi : manages
FeedbackViewSet ..> Feedback : manages

Cache relationships:
BarangViewSet ..> Cache : uses
PeminjamanViewSet ..> Cache : uses

API View relationships:
login_view ..> Users : authenticates
register_view ..> Users : creates
admin_login_view ..> Users : authenticates_admin
admin_register_view ..> Users : creates_admin

Reporting views relationships:
item_stock_levels ..> Barang : reads
reports_dashboard ..> Cache : caches_metrics
"""

print("MVC Implementation completed successfully!")
print("All classes, attributes, methods, and relationships from the class diagram have been converted to Django MVC code.")