from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import Users, Barang, Feedback, RiwayatTransaksi, Peminjaman


class UsersSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)
    is_admin = serializers.ReadOnlyField()
    is_user = serializers.ReadOnlyField()

    class Meta:
        model = Users
        fields = ['id', 'nama', 'username', 'email', 'phone', 'password', 'role', 'departemen', 'foto', 'is_admin', 'is_user']
        extra_kwargs = {'password': {'write_only': True}}

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


class FeedbackSerializer(serializers.ModelSerializer):
    user_nama = serializers.CharField(source='user.nama', read_only=True)

    class Meta:
        model = Feedback
        fields = ['id', 'user', 'user_nama', 'pesan', 'tanggal']
        read_only_fields = ['tanggal']

    def validate_pesan(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Message cannot be empty")
        return value.strip()


class RiwayatTransaksiSerializer(serializers.ModelSerializer):
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


class PeminjamanSerializer(serializers.ModelSerializer):
    barang_nama = serializers.CharField(source='barang.nama', read_only=True)
    user_nama = serializers.CharField(source='user.nama', read_only=True)
    is_overdue = serializers.ReadOnlyField()
    days_borrowed = serializers.ReadOnlyField()

    class Meta:
        model = Peminjaman
        fields = ['id', 'barang', 'barang_nama', 'user', 'user_nama', 'jumlah', 'status', 'catatan', 'tanggal_pinjam', 'tanggal_kembali', 'is_overdue', 'days_borrowed']
        read_only_fields = ['tanggal_pinjam', 'tanggal_kembali', 'is_overdue', 'days_borrowed']

    def validate_jumlah(self, value):
        if value <= 0:
            raise serializers.ValidationError("Quantity must be positive")
        return value

    def validate(self, data):
        # Check stock availability for new loans
        if not self.instance:  # Only for creation
            barang = data.get('barang')
            jumlah = data.get('jumlah', 0)
            if barang and barang.stok < jumlah:
                raise serializers.ValidationError("Insufficient stock")
        return data
