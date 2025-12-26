import requests
from django.utils import timezone
from django.db.models import Count, Sum, Q, F, Prefetch
from django.core.cache import cache
from django.conf import settings
from rest_framework import viewsets, status, serializers
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from .models import Barang, Users, Feedback, RiwayatTransaksi, Peminjaman
from .serializers import BarangSerializer, UsersSerializer, FeedbackSerializer, RiwayatTransaksiSerializer, PeminjamanSerializer
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)

# Custom pagination class
class StandardResultsSetPagination(PageNumberPagination):
    page_size = 25
    page_size_query_param = 'page_size'
    max_page_size = 100


class BarangViewSet(viewsets.ModelViewSet):
    queryset = Barang.objects.all()
    serializer_class = BarangSerializer
    pagination_class = None  # Disable pagination for direct array response
    throttle_classes = [UserRateThrottle, AnonRateThrottle]

    def create(self, request, *args, **kwargs):
        """Create new item with validation and cache clearing"""
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            # Additional validation
            nama = serializer.validated_data.get('nama', '').strip()
            if Barang.objects.filter(nama__iexact=nama).exists():
                return Response({'error': 'Nama barang sudah digunakan'}, status=status.HTTP_400_BAD_REQUEST)

            self.perform_create(serializer)

            # Clear related caches
            cache.delete('reports_dashboard')
            cache.delete('reports_item_status_overview')
            cache.delete('reports_item_usage_over_time')
            cache.delete('reports_item_stock_levels')
            cache.delete('reports_item_categories')
            cache.delete('reports_most_borrowed_items')
            cache.delete('reports_item_transaction_trends')
            cache.delete('reports_low_stock_alerts')
            cache.delete('barang_statistics')

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
            partial = kwargs.pop('partial', False)
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)

            # Check for duplicate name (excluding current instance)
            nama = serializer.validated_data.get('nama', '').strip()
            if Barang.objects.filter(nama__iexact=nama).exclude(id=instance.id).exists():
                return Response({'error': 'Nama barang sudah digunakan'}, status=status.HTTP_400_BAD_REQUEST)

            self.perform_update(serializer)

            # Clear related caches
            cache.delete('reports_dashboard')
            cache.delete('reports_item_status_overview')
            cache.delete('reports_item_usage_over_time')
            cache.delete('reports_item_stock_levels')
            cache.delete('reports_item_categories')
            cache.delete('reports_most_borrowed_items')
            cache.delete('reports_item_transaction_trends')
            cache.delete('reports_low_stock_alerts')
            cache.delete('barang_statistics')

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

            # Check if item is referenced in loans or transactions
            active_loans = Peminjaman.objects.filter(barang=instance, status='dipinjam').count()
            if active_loans > 0:
                return Response({
                    'error': f'Barang tidak dapat dihapus karena masih dipinjam ({active_loans} peminjaman aktif)'
                }, status=status.HTTP_400_BAD_REQUEST)

            total_transactions = RiwayatTransaksi.objects.filter(barang=instance).count()
            if total_transactions > 0:
                return Response({
                    'error': f'Barang tidak dapat dihapus karena memiliki riwayat transaksi ({total_transactions} transaksi)'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Safe to delete
            self.perform_destroy(instance)

            # Clear related caches
            cache.delete('reports_dashboard')
            cache.delete('reports_item_status_overview')
            cache.delete('reports_item_usage_over_time')
            cache.delete('reports_item_stock_levels')
            cache.delete('reports_item_categories')
            cache.delete('reports_most_borrowed_items')
            cache.delete('reports_item_transaction_trends')
            cache.delete('reports_low_stock_alerts')
            cache.delete('barang_statistics')

            return Response({'success': True, 'message': 'Barang berhasil dihapus'}, status=status.HTTP_204_NO_CONTENT)

        except Exception as e:
            logger.error(f"Error deleting item: {str(e)}")
            return Response({'error': 'Gagal menghapus barang'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get_queryset(self):
        queryset = Barang.objects.select_related().order_by('nama')
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
        """Update stok barang dan catat ke riwayat transaksi"""
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

            # Catat ke riwayat
            RiwayatTransaksi.objects.create(
                barang=barang,
                user=user,
                jumlah=jumlah,
                tipe=tipe,
                catatan=catatan
            )

            # Clear cache
            cache.delete('reports_dashboard')
            cache.delete('reports_item_status_overview')
            cache.delete('reports_item_usage_over_time')
            cache.delete('reports_item_stock_levels')
            cache.delete('reports_item_categories')
            cache.delete('reports_most_borrowed_items')
            cache.delete('reports_item_transaction_trends')
            cache.delete('reports_low_stock_alerts')
            cache.delete('barang_statistics')

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
    queryset = Users.objects.all()
    serializer_class = UsersSerializer
    pagination_class = None  # Disable pagination for direct array response
    
    @action(detail=True, methods=['post'])
    def change_password(self, request, pk=None):
        """Ganti password user"""
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
        """Update foto profil (base64)"""
        user = self.get_object()
        foto = request.data.get('foto', '')
        user.foto = foto
        user.save()
        return Response({'success': True, 'user': UsersSerializer(user).data})


class FeedbackViewSet(viewsets.ModelViewSet):
    queryset = Feedback.objects.all().order_by('-tanggal')
    serializer_class = FeedbackSerializer
    pagination_class = None  # Disable pagination for direct array response


class RiwayatTransaksiViewSet(viewsets.ModelViewSet):
    queryset = RiwayatTransaksi.objects.all().order_by('-tanggal')
    serializer_class = RiwayatTransaksiSerializer
    pagination_class = None  # Disable pagination for direct array response


class PeminjamanViewSet(viewsets.ModelViewSet):
    queryset = Peminjaman.objects.all()
    serializer_class = PeminjamanSerializer
    pagination_class = None  # Disable pagination for direct array response
    throttle_classes = [UserRateThrottle, AnonRateThrottle]

    def get_queryset(self):
        queryset = Peminjaman.objects.select_related('barang', 'user').order_by('-tanggal_pinjam')
        user_id = self.request.query_params.get('user')
        status_filter = self.request.query_params.get('status')
        overdue = self.request.query_params.get('overdue')

        if user_id:
            queryset = queryset.filter(user_id=user_id)

        if status_filter:
            queryset = queryset.filter(status=status_filter)

        if overdue == 'true':
            # Filter overdue loans (borrowed more than 7 days ago and not returned)
            seven_days_ago = timezone.now() - timedelta(days=7)
            queryset = queryset.filter(
                status='dipinjam',
                tanggal_pinjam__lt=seven_days_ago
            )

        return queryset
    
    def create(self, request, *args, **kwargs):
        """Buat peminjaman baru dan kurangi stok barang"""
        barang_id = request.data.get('barang')
        jumlah = int(request.data.get('jumlah', 0))
        user_id = request.data.get('user')

        try:
            barang = Barang.objects.get(pk=barang_id)
            if barang.stok < jumlah:
                return Response({'error': 'Stok tidak mencukupi'}, status=status.HTTP_400_BAD_REQUEST)

            user = None
            if user_id:
                try:
                    user = Users.objects.get(pk=user_id)
                except Users.DoesNotExist:
                    pass

            # Kurangi stok
            barang.stok -= jumlah
            barang.save()

            # Catat ke riwayat transaksi
            RiwayatTransaksi.objects.create(
                barang=barang,
                user=user,
                jumlah=jumlah,
                tipe='keluar',
                catatan=f'Peminjaman oleh {user.nama if user else "Unknown"}'
            )

            # Buat peminjaman dengan data yang dimodifikasi
            data = request.data.copy()
            data['user'] = user_id
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
        """Update peminjaman dengan logic stok"""
        peminjaman = self.get_object()
        old_status = peminjaman.status
        new_status = request.data.get('status', old_status)
        new_jumlah = int(request.data.get('jumlah', peminjaman.jumlah))
        
        # Jika status berubah dari dipinjam ke dikembalikan
        if old_status == 'dipinjam' and new_status == 'dikembalikan':
            peminjaman.barang.stok += peminjaman.jumlah
            peminjaman.barang.save()
            peminjaman.tanggal_kembali = timezone.now()
        
        # Jika status berubah dari dikembalikan ke dipinjam
        elif old_status == 'dikembalikan' and new_status == 'dipinjam':
            if peminjaman.barang.stok < new_jumlah:
                return Response({'error': 'Stok tidak mencukupi'}, status=status.HTTP_400_BAD_REQUEST)
            peminjaman.barang.stok -= new_jumlah
            peminjaman.barang.save()
            peminjaman.tanggal_kembali = None
        
        # Jika jumlah berubah saat masih dipinjam
        elif old_status == 'dipinjam' and new_status == 'dipinjam' and new_jumlah != peminjaman.jumlah:
            diff = new_jumlah - peminjaman.jumlah
            if diff > 0 and peminjaman.barang.stok < diff:
                return Response({'error': 'Stok tidak mencukupi'}, status=status.HTTP_400_BAD_REQUEST)
            peminjaman.barang.stok -= diff
            peminjaman.barang.save()
        
        return super().partial_update(request, *args, **kwargs)
    
    @action(detail=True, methods=['post'])
    def kembalikan(self, request, pk=None):
        """Kembalikan barang dan tambah stok"""
        peminjaman = self.get_object()

        if peminjaman.status == 'dikembalikan':
            return Response({'error': 'Barang sudah dikembalikan'}, status=status.HTTP_400_BAD_REQUEST)

        # Tambah stok kembali
        peminjaman.barang.stok += peminjaman.jumlah
        peminjaman.barang.save()

        # Catat ke riwayat transaksi
        RiwayatTransaksi.objects.create(
            barang=peminjaman.barang,
            user=peminjaman.user,
            jumlah=peminjaman.jumlah,
            tipe='masuk',
            catatan=f'Pengembalian oleh {peminjaman.user.nama}'
        )

        # Update status peminjaman
        peminjaman.status = 'dikembalikan'
        peminjaman.tanggal_kembali = timezone.now()
        peminjaman.save()

        return Response(PeminjamanSerializer(peminjaman).data)


@api_view(['POST'])
def login_view(request):
    """Login khusus user"""
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
    """Register user baru dengan pilihan role"""
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

    # Cek nama sudah digunakan
    if Users.objects.filter(nama=nama).exists():
        return Response({'error': 'Nama sudah digunakan'}, status=status.HTTP_400_BAD_REQUEST)

    # Cek email sudah digunakan untuk role lain
    if Users.objects.filter(email=email).exists():
        existing = Users.objects.get(email=email)
        if existing.role != role:
            return Response({'error': 'Email sudah digunakan untuk role lain'}, status=status.HTTP_400_BAD_REQUEST)

    # Register dengan role yang dipilih
    user = Users.objects.create(nama=nama, email=email, password=password, role=role)
    redirect_to = 'admin_dashboard' if role == 'admin' else 'user_dashboard'
    return Response({
        'success': True,
        'user': UsersSerializer(user).data,
        'redirect_to': redirect_to
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
def reset_password_view(request):
    """Reset password user berdasarkan email"""
    email = request.data.get('email', '').strip()
    new_password = request.data.get('new_password', '')

    if not email or not new_password:
        return Response({'error': 'Email dan password baru wajib diisi'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = Users.objects.get(email=email)
        user.password = new_password
        user.save()
        return Response({
            'success': True,
            'message': 'Password berhasil direset'
        })
    except Users.DoesNotExist:
        return Response({'error': 'User dengan email tersebut tidak ditemukan'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def google_login_view(request):
    """Login/Register dengan Google OAuth"""
    access_token = request.data.get('access_token', '')

    if not access_token:
        return Response({'error': 'Access token wajib diisi'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Verifikasi token dengan Google
        response = requests.get(f'https://www.googleapis.com/oauth2/v1/tokeninfo?access_token={access_token}')
        if response.status_code != 200:
            return Response({'error': 'Token Google tidak valid'}, status=status.HTTP_401_UNAUTHORIZED)

        google_data = response.json()
        email = google_data.get('email')
        nama = google_data.get('name')

        if not email:
            return Response({'error': 'Email tidak ditemukan dari Google'}, status=status.HTTP_400_BAD_REQUEST)

        # Cari atau buat user
        user, created = Users.objects.get_or_create(
            email=email,
            defaults={
                'nama': nama or email.split('@')[0],
                'password': '',  # Google login tidak perlu password
                'role': 'user'
            }
        )

        serializer = UsersSerializer(user)
        redirect_to = 'admin_dashboard' if user.role == 'admin' else 'user_dashboard'

        return Response({
            'success': True,
            'user': serializer.data,
            'redirect_to': redirect_to,
            'created': created,  # True jika user baru dibuat
            'login_method': 'google'
        })

    except requests.RequestException:
        return Response({'error': 'Gagal menghubungi Google'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def admin_login_view(request):
    """Login khusus admin"""
    nama = request.data.get('nama', '').strip()
    password = request.data.get('password', '')

    if not nama or not password:
        return Response({'error': 'Nama dan password wajib diisi'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = Users.objects.get(nama=nama)
        if user.password == password and user.role == 'admin':
            serializer = UsersSerializer(user)
            return Response({
                'success': True,
                'user': serializer.data,
                'redirect_to': 'admin_dashboard'
            })
        else:
            return Response({'error': 'Kredensial admin tidak valid'}, status=status.HTTP_401_UNAUTHORIZED)
    except Users.DoesNotExist:
        return Response({'error': 'Admin tidak ditemukan'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def admin_register_view(request):
    """Register admin baru"""
    nama = request.data.get('nama', '').strip()
    email = request.data.get('email', '').strip()
    password = request.data.get('password', '')
    admin_code = request.data.get('admin_code', '')

    if not nama or not email or not password:
        return Response({'error': 'Nama, email dan password wajib diisi'}, status=status.HTTP_400_BAD_REQUEST)

    # Kode khusus untuk register admin
    if admin_code != 'ADMIN2025':
        return Response({'error': 'Kode admin tidak valid'}, status=status.HTTP_403_FORBIDDEN)

    if '@' not in email.lower():
        return Response({'error': 'Email tidak bisa terdaftar karena tidak ada @'}, status=status.HTTP_400_BAD_REQUEST)

    # Cek nama sudah digunakan
    if Users.objects.filter(nama=nama).exists():
        return Response({'error': 'Nama sudah digunakan'}, status=status.HTTP_400_BAD_REQUEST)

    # Cek email sudah digunakan untuk role lain
    if Users.objects.filter(email=email).exists():
        existing = Users.objects.get(email=email)
        if existing.role != 'admin':
            return Response({'error': 'Email sudah digunakan untuk role lain'}, status=status.HTTP_400_BAD_REQUEST)

    # Register sebagai admin
    user = Users.objects.create(nama=nama, email=email, password=password, role='admin')
    return Response({
        'success': True,
        'user': UsersSerializer(user).data,
        'redirect_to': 'admin_dashboard'
    }, status=status.HTTP_201_CREATED)


# Reporting endpoints for item graphs
@api_view(['GET'])
def item_stock_levels(request):
    """Data untuk grafik level stok barang (bar chart)"""
    cache_key = 'item_stock_levels'
    data = cache.get(cache_key)

    if not data:
        items = Barang.objects.all().order_by('-stok')[:20]  # Top 20 items by stock
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
        cache.set(cache_key, data, 600)  # Cache for 10 minutes

    return Response(data)


@api_view(['GET'])
def item_categories(request):
    """Data untuk grafik kategori barang (pie chart)"""
    cache_key = 'item_categories'
    data = cache.get(cache_key)

    if not data:
        # Extract category from item name (first word before space)
        categories = {}
        for item in Barang.objects.all():
            category = item.nama.split()[0]  # Simple categorization
            if category not in categories:
                categories[category] = 0
            categories[category] += 1

        data = {
            'labels': list(categories.keys()),
            'datasets': [{
                'data': list(categories.values()),
                'backgroundColor': [
                    'rgba(255, 99, 132, 0.6)',
                    'rgba(54, 162, 235, 0.6)',
                    'rgba(255, 205, 86, 0.6)',
                    'rgba(75, 192, 192, 0.6)',
                    'rgba(153, 102, 255, 0.6)',
                    'rgba(255, 159, 64, 0.6)',
                    'rgba(199, 199, 199, 0.6)',
                    'rgba(83, 102, 255, 0.6)',
                    'rgba(255, 99, 255, 0.6)',
                    'rgba(99, 255, 132, 0.6)'
                ]
            }]
        }
        cache.set(cache_key, data, 600)  # Cache for 10 minutes

    return Response(data)


@api_view(['GET'])
def most_borrowed_items(request):
    """Data untuk grafik barang paling sering dipinjam (bar chart)"""
    cache_key = 'most_borrowed_items'
    data = cache.get(cache_key)

    if not data:
        # Count loans per item
        loans = Peminjaman.objects.values('barang__nama').annotate(
            total_loans=Count('id'),
            total_quantity=Sum('jumlah')
        ).order_by('-total_loans')[:15]  # Top 15 most borrowed

        data = {
            'labels': [loan['barang__nama'][:30] + '...' if len(loan['barang__nama']) > 30 else loan['barang__nama'] for loan in loans],
            'datasets': [{
                'label': 'Jumlah Peminjaman',
                'data': [loan['total_loans'] for loan in loans],
                'backgroundColor': 'rgba(255, 99, 132, 0.6)',
                'borderColor': 'rgba(255, 99, 132, 1)',
                'borderWidth': 1
            }, {
                'label': 'Total Quantity',
                'data': [loan['total_quantity'] for loan in loans],
                'backgroundColor': 'rgba(54, 162, 235, 0.6)',
                'borderColor': 'rgba(54, 162, 235, 1)',
                'borderWidth': 1
            }]
        }
        cache.set(cache_key, data, 600)  # Cache for 10 minutes

    return Response(data)


@api_view(['GET'])
def item_transaction_trends(request):
    """Data untuk grafik tren transaksi barang dalam 30 hari terakhir (line chart)"""
    cache_key = 'item_transaction_trends'
    data = cache.get(cache_key)

    if not data:
        end_date = timezone.now()
        start_date = end_date - timedelta(days=30)

        # Daily transaction counts
        daily_data = []
        current_date = start_date

        while current_date <= end_date:
            next_date = current_date + timedelta(days=1)
            count = RiwayatTransaksi.objects.filter(
                tanggal__gte=current_date,
                tanggal__lt=next_date
            ).count()

            daily_data.append({
                'date': current_date.strftime('%Y-%m-%d'),
                'transactions': count
            })
            current_date = next_date

        data = {
            'labels': [d['date'] for d in daily_data],
            'datasets': [{
                'label': 'Jumlah Transaksi',
                'data': [d['transactions'] for d in daily_data],
                'borderColor': 'rgba(75, 192, 192, 1)',
                'backgroundColor': 'rgba(75, 192, 192, 0.2)',
                'tension': 0.1
            }]
        }
        cache.set(cache_key, data, 1800)  # Cache for 30 minutes

    return Response(data)


@api_view(['GET'])
def low_stock_alerts(request):
    """Data untuk grafik alert stok rendah (bar chart)"""
    cache_key = 'low_stock_alerts'
    data = cache.get(cache_key)

    if not data:
        # Items with stock below minimum threshold
        low_stock_items = Barang.objects.filter(
            Q(stok__lte=5) | Q(stok__lt=F('minimum'))
        ).order_by('stok')[:15]

        data = {
            'labels': [item.nama[:30] + '...' if len(item.nama) > 30 else item.nama for item in low_stock_items],
            'datasets': [{
                'label': 'Stok Saat Ini',
                'data': [item.stok for item in low_stock_items],
                'backgroundColor': 'rgba(255, 99, 132, 0.6)',
                'borderColor': 'rgba(255, 99, 132, 1)',
                'borderWidth': 1
            }, {
                'label': 'Minimum Required',
                'data': [item.minimum for item in low_stock_items],
                'backgroundColor': 'rgba(255, 206, 86, 0.6)',
                'borderColor': 'rgba(255, 206, 86, 1)',
                'borderWidth': 1
            }]
        }
        cache.set(cache_key, data, 300)  # Cache for 5 minutes

    return Response(data)


@api_view(['GET'])
def item_usage_over_time(request):
    """Data untuk grafik penggunaan barang per bulan (line chart)"""
    cache_key = 'item_usage_over_time'
    data = cache.get(cache_key)

    if not data:
        # Monthly loan data for the last 6 months
        end_date = timezone.now()
        monthly_data = []

        for i in range(6):
            month_start = end_date.replace(day=1) - timedelta(days=i*30)
            month_end = month_start.replace(day=28) + timedelta(days=4)  # Handle month end
            month_end = month_end - timedelta(days=month_end.day)

            count = Peminjaman.objects.filter(
                tanggal_pinjam__gte=month_start,
                tanggal_pinjam__lte=month_end
            ).count()

            monthly_data.insert(0, {
                'month': month_start.strftime('%B %Y'),
                'loans': count
            })

        data = {
            'labels': [d['month'] for d in monthly_data],
            'datasets': [{
                'label': 'Jumlah Peminjaman',
                'data': [d['loans'] for d in monthly_data],
                'borderColor': 'rgba(153, 102, 255, 1)',
                'backgroundColor': 'rgba(153, 102, 255, 0.2)',
                'tension': 0.1
            }]
        }
        cache.set(cache_key, data, 3600)  # Cache for 1 hour

    return Response(data)


@api_view(['GET'])
def item_status_overview(request):
    """Data untuk grafik overview status barang (pie chart)"""
    cache_key = 'item_status_overview'
    data = cache.get(cache_key)

    if not data:
        total_items = Barang.objects.count()
        in_stock = Barang.objects.filter(stok__gt=0).count()
        out_of_stock = Barang.objects.filter(stok=0).count()
        low_stock = Barang.objects.filter(stok__gt=0, stok__lte=5).count()

        data = {
            'labels': ['Tersedia', 'Stok Rendah (1-5)', 'Habis'],
            'datasets': [{
                'data': [in_stock - low_stock, low_stock, out_of_stock],
                'backgroundColor': [
                    'rgba(75, 192, 192, 0.6)',  # Available
                    'rgba(255, 205, 86, 0.6)',  # Low stock
                    'rgba(255, 99, 132, 0.6)'   # Out of stock
                ],
                'borderColor': [
                    'rgba(75, 192, 192, 1)',
                    'rgba(255, 205, 86, 1)',
                    'rgba(255, 99, 132, 1)'
                ],
                'borderWidth': 1
            }]
        }
        cache.set(cache_key, data, 300)  # Cache for 5 minutes

    return Response(data)


@api_view(['GET'])
def reports_dashboard(request):
    """Dashboard data untuk semua grafik laporan"""
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
        cache.set(cache_key, data, 180)  # Cache for 3 minutes

    return Response(data)
