from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    BarangViewSet, UsersViewSet, FeedbackViewSet, RiwayatTransaksiViewSet, PeminjamanViewSet,
    login_view, register_view, reset_password_view, google_login_view, admin_login_view, admin_register_view,
    item_stock_levels, item_categories, most_borrowed_items, item_transaction_trends,
    low_stock_alerts, item_usage_over_time, item_status_overview, reports_dashboard
)

router = DefaultRouter()
router.register(r"barang", BarangViewSet)
router.register(r"users", UsersViewSet)
router.register(r"feedback", FeedbackViewSet)
router.register(r"transaksi", RiwayatTransaksiViewSet)
router.register(r"peminjaman", PeminjamanViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("login/", login_view, name="login"),
    path("register/", register_view, name="register"),
    path("admin/login/", admin_login_view, name="admin_login"),
    path("admin/register/", admin_register_view, name="admin_register"),
    path("reset-password/", reset_password_view, name="reset_password"),
    path("google-login/", google_login_view, name="google_login"),

    # Reporting endpoints
    path("reports/dashboard/", reports_dashboard, name="reports_dashboard"),
    path("reports/item-stock-levels/", item_stock_levels, name="item_stock_levels"),
    path("reports/item-categories/", item_categories, name="item_categories"),
    path("reports/most-borrowed-items/", most_borrowed_items, name="most_borrowed_items"),
    path("reports/item-transaction-trends/", item_transaction_trends, name="item_transaction_trends"),
    path("reports/low-stock-alerts/", low_stock_alerts, name="low_stock_alerts"),
    path("reports/item-usage-over-time/", item_usage_over_time, name="item_usage_over_time"),
    path("reports/item-status-overview/", item_status_overview, name="item_status_overview"),
]
