"""
dashboard.py — Tableau de Bord DAR ELSSALEM
============================================
Structure 2×2 :
  ┌─────────────────────────────────────────┐
  │  KPI  KPI  KPI  KPI  (ligne complète)  │
  ├──────────────────┬──────────────────────┤
  │  Derniers        │  Top Clients         │
  │  Achats          │  (noms + barres)     │
  ├──────────────────┼──────────────────────┤
  │  Dernières       │  Alertes Stock       │
  │  Factures        │  Faible              │
  ├──────────────────┴──────────────────────┤
  │  Ventes — 7 derniers jours (pleine lrg) │
  └─────────────────────────────────────────┘
"""

import datetime
import json
from PyQt6.QtWidgets import (
    QProgressBar, QWidget, QVBoxLayout, QLabel, QHBoxLayout, QFrame,
    QPushButton, QHeaderView, QTableWidget, QTableWidgetItem,
    QSizePolicy, QMessageBox, QScrollArea, QGridLayout, QDialog,
    QCheckBox, QListWidget, QListWidgetItem, QAbstractItemView,
    QDateEdit, QGroupBox, QRadioButton, QButtonGroup
)
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtCore import Qt, QObject, pyqtProperty, QPropertyAnimation, QEasingCurve, pyqtSignal

from db_manager import get_database
from styles import COLORS
from currency import fmt_da, currency_manager

try:
    from sales_history import InvoiceDetailsDialog
    _DETAIL_AVAILABLE = True
except ImportError:
    _DETAIL_AVAILABLE = False


# ══════════════════════════════════════════════════════════════════════════
#  HELPERS
# ══════════════════════════════════════════════════════════════════════════

def _clear_layout(layout):
    if layout is None:
        return
    while layout.count():
        item = layout.takeAt(0)
        w = item.widget()
        if w is not None:
            w.deleteLater()
        elif item.layout() is not None:
            _clear_layout(item.layout())


def _sep():
    """Séparateur horizontal."""
    f = QFrame()
    f.setFrameShape(QFrame.Shape.HLine)
    f.setStyleSheet("background:rgba(255,255,255,0.10); border:none; max-height:1px;")
    return f


def _lbl(text, size=11, bold=False, color=""):
    l = QLabel(text)
    l.setFont(QFont("Segoe UI", size,
                    QFont.Weight.Bold if bold else QFont.Weight.Normal))
    c = color or COLORS.get("TXT_PRI", "#F0F4FF")
    l.setStyleSheet(f"color:{c}; background:transparent; border:none; padding:0;")
    return l


def _card(name="card", border_color=""):
    """Carte avec fond sombre et bordure optionnelle."""
    f = QFrame()
    f.setObjectName(name)
    bdr = border_color or "rgba(255,255,255,0.08)"
    f.setStyleSheet(f"""
        QFrame#{name} {{
            background:{COLORS.get('BG_CARD','#252535')};
            border-radius:14px;
            border:1px solid {bdr};
        }}
    """)
    return f


def _card_frame(obj_name="card"):
    f = QFrame()
    f.setObjectName(obj_name)
    f.setStyleSheet(f"""
        QFrame#{obj_name} {{
            background: {COLORS.get('BG_CARD','#252535')};
            border-radius: 16px;
            border: 1px solid {COLORS.get('BORDER','rgba(255,255,255,0.08)')};
        }}
    """)
    return f


def _icon_box(icon, color, size=32, icon_size=14):
    """Icône dans un QFrame carré arrondi."""
    frame = QFrame()
    frame.setFixedSize(size, size)
    frame.setStyleSheet(
        f"background:{color}28; border-radius:{size//4}px; border:none;")
    lay = QVBoxLayout(frame)
    lay.setContentsMargins(0, 0, 0, 0)
    lbl = QLabel(icon)
    lbl.setFont(QFont("Segoe UI", icon_size))
    lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
    lbl.setStyleSheet("background:transparent; border:none;")
    lay.addWidget(lbl)
    return frame


def divider():
    f = QFrame()
    f.setFrameShape(QFrame.Shape.HLine)
    f.setStyleSheet(f"background:{COLORS.get('BORDER','rgba(255,255,255,0.08)')}; border:none; max-height:1px;")
    return f


# ══════════════════════════════════════════════════════════════════════════
#  ANIMATEUR KPI
# ══════════════════════════════════════════════════════════════════════════

class KpiAnimator(QObject):
    def __init__(self, label, suffix=""):
        super().__init__()
        self._value = 0
        self.label = label
        self.suffix = suffix

    def get_value(self):
        return self._value

    def set_value(self, v):
        self._value = v
        self.label.setText(f"{v:,.0f}{self.suffix}")

    value = pyqtProperty(float, get_value, set_value)


def animate_value(label, target, suffix=""):
    anim = KpiAnimator(label, suffix)
    a = QPropertyAnimation(anim, b"value")
    a.setDuration(800)
    a.setStartValue(0.0)
    a.setEndValue(float(target))
    a.setEasingCurve(QEasingCurve.Type.OutCubic)
    label._anim_ref = a
    label._anim_obj = anim
    a.start()


# ══════════════════════════════════════════════════════════════════════════
#  DASHBOARD PAGE
# ══════════════════════════════════════════════════════════════════════════

class PurchaseDetailsDialog(QDialog):
    """Dialogue d'affichage des détails d'un achat."""
    
    def __init__(self, purchase_data, items_data, parent=None):
        super().__init__(parent)
        self.purchase = purchase_data
        self.items = items_data
        self.setWindowTitle(f"Détails Achat #{purchase_data.get('id', '?')}")
        self.setMinimumSize(650, 550)
        self.setStyleSheet(f"background:{COLORS.get('BG_PAGE','#1E1E2E')};")
        self._build_ui()
    
    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # En-tête
        header = QFrame()
        header.setStyleSheet(f"""
            background:{COLORS.get('BG_CARD','#252535')};
            border-radius:12px;
            padding:15px;
        """)
        header_layout = QHBoxLayout(header)
        
        # Informations principales
        info_layout = QVBoxLayout()
        info_layout.setSpacing(5)
        
        purchase_date = self.purchase.get('purchase_date', '')
        if purchase_date:
            try:
                date_obj = datetime.datetime.strptime(str(purchase_date), '%Y-%m-%d %H:%M:%S')
                purchase_date = date_obj.strftime('%d/%m/%Y %H:%M')
            except:
                purchase_date = str(purchase_date)[:16]
        
        info_layout.addWidget(_lbl(f"Achat du {purchase_date}", 14, bold=True))
        
        supplier_info = f"Fournisseur: {self.purchase.get('supplier_name', '—')}"
        if self.purchase.get('supplier_phone'):
            supplier_info += f" | Tél: {self.purchase.get('supplier_phone')}"
        info_layout.addWidget(_lbl(supplier_info, 11, color=COLORS.get('TXT_SEC','#A0AACC')))
        
        if self.purchase.get('payment_method'):
            pay_text = {
                "cash": "💰 Espèces",
                "card": "💳 Carte",
                "check": "📝 Chèque",
                "transfer": "🏦 Virement"
            }.get(self.purchase.get('payment_method'), self.purchase.get('payment_method'))
            info_layout.addWidget(_lbl(f"Paiement: {pay_text}", 10, color=COLORS.get('TXT_SEC','#A0AACC')))
        
        header_layout.addLayout(info_layout)
        header_layout.addStretch()
        
        # Total
        total_label = _lbl(f"Total: {fmt_da(self.purchase.get('total', 0))}", 18, bold=True, color="#F59E0B")
        header_layout.addWidget(total_label)
        
        layout.addWidget(header)
        
        # Tableau des articles
        layout.addWidget(_lbl("📦 Articles", 12, bold=True))
        
        table = QTableWidget(0, 5)
        table.setHorizontalHeaderLabels(["Produit", "Quantité", "Prix unitaire", "Total", ""])
        table.setStyleSheet(f"""
            QTableWidget {{
                background:transparent;
                alternate-background-color:rgba(255,255,255,0.03);
                color:{COLORS.get('TXT_PRI','#F0F4FF')};
                border:none;
            }}
            QHeaderView::section {{
                background:{COLORS.get('BG_DEEP','#16161F')};
                color:{COLORS.get('primary','#3B82F6')};
                padding:10px;
                border:none;
                border-bottom:2px solid {COLORS.get('primary','#3B82F6')};
            }}
            QTableWidget::item {{
                padding:8px;
                border-bottom:1px solid rgba(255,255,255,0.04);
            }}
        """)
        
        table.setRowCount(len(self.items))
        for r, item in enumerate(self.items):
            product = item.get('product_name', item.get('name', '—'))
            qty = item.get('quantity', 0)
            price = item.get('unit_price', 0)
            total = item.get('total', 0)
            
            table.setItem(r, 0, QTableWidgetItem(str(product)))
            table.setItem(r, 1, QTableWidgetItem(str(qty)))
            
            price_item = QTableWidgetItem(fmt_da(price))
            price_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            table.setItem(r, 2, price_item)
            
            total_item = QTableWidgetItem(fmt_da(total))
            total_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            total_item.setForeground(QColor("#F59E0B"))
            total_item.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
            table.setItem(r, 3, total_item)
        
        table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        for i in range(1, 4):
            table.horizontalHeader().setSectionResizeMode(i, QHeaderView.ResizeMode.ResizeToContents)
        
        layout.addWidget(table)
        
        # Notes
        if self.purchase.get('notes'):
            layout.addWidget(_lbl("📝 Notes", 12, bold=True))
            notes = QLabel(self.purchase.get('notes'))
            notes.setStyleSheet(f"color:{COLORS.get('TXT_SEC','#A0AACC')}; background:{COLORS.get('BG_DEEP','#16161F')}; padding:12px; border-radius:8px;")
            notes.setWordWrap(True)
            layout.addWidget(notes)
        
        # Bouton fermer
        close_btn = QPushButton("Fermer")
        close_btn.setFixedHeight(38)
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background:{COLORS.get('primary','#3B82F6')};
                color:white;
                border:none;
                border-radius:8px;
                font-weight:bold;
                font-size:12px;
            }}
            QPushButton:hover {{
                background:{COLORS.get('secondary','#A855F7')};
            }}
        """)
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)


class DashboardPage(QWidget):
    """Tableau de bord principal avec tous les widgets."""

    def __init__(self):
        super().__init__()
        self.db = get_database()
        self.setStyleSheet(f"background:{COLORS.get('BG_PAGE','#1E1E2E')};")
        self._build_ui()
        self.refresh()

    # ─────────────────────────────────────────────────────────────
    #  Construction de l'interface
    # ─────────────────────────────────────────────────────────────

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea{border:none; background:transparent;}")

        container = QWidget()
        container.setStyleSheet("background:transparent;")
        self._main = QVBoxLayout(container)
        self._main.setSpacing(16)
        self._main.setContentsMargins(24, 18, 24, 20)

        # ── En-tête ──
        self._build_header()

        # ── Ligne KPI (4 cartes pleine largeur) ──
        self._build_kpi_row()

        # ── Grille 2×2 ──────────────────────────────────────────
        grid = QGridLayout()
        grid.setSpacing(14)
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)

        # Ligne 0: Derniers Achats | Top Clients
        grid.addWidget(self._build_purchases_card(), 0, 0)
        grid.addWidget(self._build_top_clients_card(), 0, 1)

        # Ligne 1: Dernières Factures | Alertes Stock
        grid.addWidget(self._build_invoices_card(), 1, 0)
        grid.addWidget(self._build_low_stock_card(), 1, 1)

        self._main.addLayout(grid)

        # ── Ventes 7 jours (pleine largeur) ──
        self._build_sales_chart_card()

        self._main.addStretch()
        scroll.setWidget(container)
        root.addWidget(scroll)

    # ─────────────────────────────────────────────────────────────
    #  En-tête
    # ─────────────────────────────────────────────────────────────

    def _build_header(self):
        row = QHBoxLayout()
        row.setSpacing(12)

        col = QVBoxLayout()
        col.setSpacing(2)
        title = QLabel("📊 Tableau de Bord")
        title.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        title.setStyleSheet(
            f"color:{COLORS.get('TXT_PRI','#F0F4FF')}; background:transparent;")
        col.addWidget(title)
        self._subtitle = QLabel("Vue d'ensemble de l'activité")
        self._subtitle.setFont(QFont("Segoe UI", 10))
        self._subtitle.setStyleSheet(
            f"color:{COLORS.get('TXT_SEC','#A0AACC')}; background:transparent;")
        col.addWidget(self._subtitle)
        row.addLayout(col)
        row.addStretch()

        self._last_update_lbl = QLabel("")
        self._last_update_lbl.setFont(QFont("Segoe UI", 9))
        self._last_update_lbl.setStyleSheet(
            "color:rgba(160,170,204,0.45); background:transparent;")
        row.addWidget(self._last_update_lbl)

        btn = QPushButton("🔄  Rafraîchir")
        btn.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        btn.setFixedHeight(36)
        btn.setFixedWidth(130)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setStyleSheet(f"""
            QPushButton {{
                background:rgba(59,130,246,0.15);
                color:{COLORS.get('primary','#3B82F6')};
                border:1.5px solid {COLORS.get('primary','#3B82F6')}88;
                border-radius:9px;
            }}
            QPushButton:hover  {{ background:rgba(59,130,246,0.28); }}
            QPushButton:pressed {{ background:rgba(59,130,246,0.42); }}
        """)
        btn.clicked.connect(self.refresh)
        row.addWidget(btn)
        self._main.addLayout(row)

    # ─────────────────────────────────────────────────────────────
    #  Ligne KPI
    # ─────────────────────────────────────────────────────────────

    def _build_kpi_row(self):
        row = QHBoxLayout()
        row.setSpacing(14)
        sym = currency_manager.primary.symbol

        self._kpi_meta = [
            ("Ventes Totales", "#6366F1", "💳", f" {sym}"),
            ("Achats", "#F59E0B", "🛒", f" {sym}"),
            ("Bénéfice Net", "#10B981", "📈", f" {sym}"),
            ("Clients", "#06B6D4", "👥", ""),
        ]
        self.kpi_cards = []
        for title, color, icon, suffix in self._kpi_meta:
            card = self._make_kpi_card(icon, title, color, suffix)
            row.addWidget(card)
            self.kpi_cards.append(card)
        self._main.addLayout(row)

    def _make_kpi_card(self, icon, title, color, suffix):
        card = QFrame()
        card.setObjectName("kpi")
        card.setFixedHeight(118)
        card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        card.setStyleSheet(f"""
            QFrame#kpi {{
                background:{COLORS.get('BG_CARD','#252535')};
                border-radius:14px; border:1px solid {color}44;
            }}
        """)
        lay = QVBoxLayout(card)
        lay.setContentsMargins(18, 13, 18, 11)
        lay.setSpacing(6)

        top = QHBoxLayout()
        top.setSpacing(10)
        top.addWidget(_icon_box(icon, color, size=38, icon_size=16))

        title_lbl = QLabel(title)
        title_lbl.setFont(QFont("Segoe UI", 11))
        title_lbl.setStyleSheet(
            f"color:{COLORS.get('TXT_SEC','#A0AACC')}; "
            "background:transparent; border:none;")
        top.addWidget(title_lbl)
        top.addStretch()

        evol = QLabel("")
        evol.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        evol.setStyleSheet("background:transparent; border:none; color:transparent;")
        top.addWidget(evol)
        lay.addLayout(top)

        val_lbl = QLabel("0")
        val_lbl.setFont(QFont("Segoe UI", 28, QFont.Weight.Bold))
        val_lbl.setStyleSheet(f"color:{color}; background:transparent; border:none;")
        lay.addWidget(val_lbl)

        bar = QFrame()
        bar.setFixedHeight(3)
        bar.setStyleSheet(
            f"background:qlineargradient(x1:0,y1:0,x2:1,y2:0,"
            f"stop:0 {color}, stop:0.55 {color}77, stop:1 transparent);"
            "border-radius:2px; border:none;")
        lay.addWidget(bar)

        card.value_label = val_lbl
        card.evol_badge = evol
        card.suffix = suffix
        card.kpi_color = color
        return card

    # ─────────────────────────────────────────────────────────────
    #  Carte Derniers Achats (avec boutons de détails)
    # ─────────────────────────────────────────────────────────────

    def _build_purchases_card(self):
        """Carte affichant les derniers achats avec boutons de détails."""
        card = _card("purchases")
        card.setMinimumHeight(280)
        lay = QVBoxLayout(card)
        lay.setContentsMargins(18, 14, 18, 14)
        lay.setSpacing(0)

        hdr = QHBoxLayout()
        hdr.addWidget(_lbl("🛒  Derniers Achats", 13, bold=True))
        hdr.addStretch()
        hdr.addWidget(_lbl("10 derniers", 9, color=COLORS.get("TXT_SEC","#A0AACC")))
        lay.addLayout(hdr)
        lay.addSpacing(8)
        lay.addWidget(_sep())
        lay.addSpacing(8)

        # Tableau des achats
        self.purchases_table = QTableWidget(0, 5)
        self.purchases_table.setHorizontalHeaderLabels(
            ["N° Achat", "Produit", "Fournisseur", "Total", ""])

        hv = self.purchases_table.horizontalHeader()
        hv.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        hv.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        hv.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        hv.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        hv.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        self.purchases_table.setColumnWidth(4, 40)

        self.purchases_table.verticalHeader().setVisible(False)
        self.purchases_table.setAlternatingRowColors(True)
        self.purchases_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.purchases_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.purchases_table.setShowGrid(False)
        self.purchases_table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self.purchases_table.setStyleSheet(f"""
            QTableWidget {{
                background:transparent;
                alternate-background-color:rgba(255,255,255,0.03);
                color:{COLORS.get('TXT_PRI','#F0F4FF')};
                border:none; font-size:11px;
            }}
            QHeaderView::section {{
                background:{COLORS.get('BG_DEEP','#16161F')};
                color:{COLORS.get('primary','#3B82F6')};
                font-size:10px; font-weight:bold;
                padding:8px 6px; border:none;
                border-bottom:2px solid {COLORS.get('primary','#3B82F6')};
            }}
            QTableWidget::item {{
                padding:8px 6px;
                border-bottom:1px solid rgba(255,255,255,0.04);
            }}
            QTableWidget::item:selected {{
                background:rgba(245,158,11,0.22); color:white;
            }}
        """)
        lay.addWidget(self.purchases_table, 1)
        return card

    # ─────────────────────────────────────────────────────────────
    #  Carte Top Clients
    # ─────────────────────────────────────────────────────────────

    def _build_top_clients_card(self):
        card = _card("tc")
        card.setMinimumHeight(280)
        lay = QVBoxLayout(card)
        lay.setContentsMargins(18, 14, 18, 14)
        lay.setSpacing(0)

        hdr = QHBoxLayout()
        hdr.addWidget(_lbl("🏆  Top Clients", 13, bold=True))
        hdr.addStretch()
        self._tc_period_lbl = _lbl("Cette année", 9, color=COLORS.get("TXT_SEC","#A0AACC"))
        hdr.addWidget(self._tc_period_lbl)
        
       
        lay.addSpacing(0)
        lay.addWidget(_sep())
        lay.addSpacing(8)

        self.top_clients_layout = QVBoxLayout()
        self.top_clients_layout.setSpacing(8)
        lay.addLayout(self.top_clients_layout)
        lay.addStretch()
        return card

    # ─────────────────────────────────────────────────────────────
    #  Carte Dernières Factures
    # ─────────────────────────────────────────────────────────────

    def _build_invoices_card(self):
        card = _card("inv")
        card.setMinimumHeight(280)
        lay = QVBoxLayout(card)
        lay.setContentsMargins(18, 14, 18, 14)
        lay.setSpacing(0)

        hdr = QHBoxLayout()
        hdr.addWidget(_lbl("🧾  Dernières Factures", 13, bold=True))
        hdr.addStretch()
        hdr.addWidget(_lbl("10 dernières", 9, color=COLORS.get("TXT_SEC","#A0AACC")))
        lay.addLayout(hdr)
        lay.addSpacing(8)
        lay.addWidget(_sep())
        lay.addSpacing(4)

        self.invoice_table = QTableWidget(0, 6)
        self.invoice_table.setHorizontalHeaderLabels(
            ["N° Facture", "Client", "Total TTC", "Date", "Paiement", ""])

        hv = self.invoice_table.horizontalHeader()
        hv.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        hv.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        hv.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        hv.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        hv.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        hv.setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)
        self.invoice_table.setColumnWidth(5, 40)

        self.invoice_table.verticalHeader().setVisible(False)
        self.invoice_table.setAlternatingRowColors(True)
        self.invoice_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.invoice_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.invoice_table.setShowGrid(False)
        self.invoice_table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self.invoice_table.setStyleSheet(f"""
            QTableWidget {{
                background:transparent;
                alternate-background-color:rgba(255,255,255,0.03);
                color:{COLORS.get('TXT_PRI','#F0F4FF')};
                border:none; font-size:12px;
            }}
            QHeaderView::section {{
                background:{COLORS.get('BG_DEEP','#16161F')};
                color:{COLORS.get('primary','#3B82F6')};
                font-size:11px; font-weight:bold;
                padding:9px 8px; border:none;
                border-bottom:2px solid {COLORS.get('primary','#3B82F6')};
            }}
            QTableWidget::item {{
                padding:9px 8px;
                border-bottom:1px solid rgba(255,255,255,0.04);
            }}
            QTableWidget::item:selected {{
                background:rgba(99,102,241,0.22); color:white;
            }}
        """)
        lay.addWidget(self.invoice_table, 1)
        return card

    # ─────────────────────────────────────────────────────────────
    #  Carte Alertes Stock Faible
    # ─────────────────────────────────────────────────────────────

    def _build_low_stock_card(self):
        card = _card("ls")
        card.setMinimumHeight(280)
        lay = QVBoxLayout(card)
        lay.setContentsMargins(18, 14, 18, 14)
        lay.setSpacing(0)

        hdr = QHBoxLayout()
        hdr.addWidget(_lbl("⚠️  Alertes Stock Faible", 13, bold=True))
        hdr.addStretch()
        self._ls_count = _lbl("", 10, color=COLORS.get("warning","#FBBF24"))
        hdr.addWidget(self._ls_count)
        lay.addLayout(hdr)
        lay.addSpacing(8)
        lay.addWidget(_sep())
        lay.addSpacing(10)

        # === AJOUT SCROLLBAR ===
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        scroll_area.setStyleSheet("""
            QScrollArea { background: transparent; border: none; }
            QScrollBar:vertical {
                background: #1E1E2E;
                width: 6px;
                border-radius: 3px;
            }
            QScrollBar::handle:vertical {
                background: #F59E0B;
                border-radius: 3px;
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover {
                background: #FBBF24;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        
        container = QWidget()
        self.low_stock_layout = QVBoxLayout(container)
        self.low_stock_layout.setSpacing(8)
        self.low_stock_layout.setContentsMargins(0, 0, 5, 0)
        
        scroll_area.setWidget(container)
        lay.addWidget(scroll_area, 1)
        # === FIN AJOUT ===

        return card

    # ─────────────────────────────────────────────────────────────
    #  Graphique Ventes 7 jours
    # ─────────────────────────────────────────────────────────────

    def _build_sales_chart_card(self):
        card = _card("chart")
        card.setMinimumHeight(190)
        lay = QVBoxLayout(card)
        lay.setContentsMargins(18, 14, 18, 14)
        lay.setSpacing(0)

        hdr = QHBoxLayout()
        hdr.addWidget(_lbl("📈  Ventes — 7 derniers jours", 13, bold=True))
        hdr.addStretch()
        self._chart_total = _lbl("", 11, bold=True, color=COLORS.get("success","#22C55E"))
        hdr.addWidget(self._chart_total)
        lay.addLayout(hdr)
        lay.addSpacing(8)
        lay.addWidget(_sep())
        lay.addSpacing(10)

        self.sales_chart_layout = QVBoxLayout()
        self.sales_chart_layout.setSpacing(6)
        lay.addLayout(self.sales_chart_layout)
        self._main.addWidget(card)

    # ─────────────────────────────────────────────────────────────
    #  showEvent
    # ─────────────────────────────────────────────────────────────

    def showEvent(self, event):
        super().showEvent(event)
        self.refresh()

    # ─────────────────────────────────────────────────────────────
    #  Rafraîchissement
    # ─────────────────────────────────────────────────────────────

    def refresh(self):
        self._load_kpis()
        self._load_purchases()
        self._load_invoices()
        self._load_low_stock()
        self._load_top_clients()
        self._load_sales_chart()
        now = datetime.datetime.now().strftime("%d/%m/%Y  %H:%M")
        self._last_update_lbl.setText(f"Mis à jour le  {now}")

    # ─────────────────────────────────────────────────────────────
    #  KPI
    # ─────────────────────────────────────────────────────────────

    def _load_kpis(self):
        stats = self.db.get_statistics() or {}
        sales = float(stats.get("sales_total", 0))
        pur = float(stats.get("purchases_total", 0))
        prof = sales - pur
        cli = int(stats.get("total_clients", 0))
        sym = currency_manager.primary.symbol

        prev_sales = prev_pur = 0.0
        try:
            today = datetime.date.today()
            first_this = today.replace(day=1)
            last_prev = first_this - datetime.timedelta(days=1)
            first_prev = last_prev.replace(day=1)
            self.db.cursor.execute(
                "SELECT COALESCE(SUM(total),0) FROM sales "
                "WHERE DATE(sale_date) BETWEEN ? AND ?",
                (str(first_prev), str(last_prev)))
            prev_sales = float(self.db.cursor.fetchone()[0] or 0)
            self.db.cursor.execute(
                "SELECT COALESCE(SUM(total),0) FROM purchases "
                "WHERE DATE(purchase_date) BETWEEN ? AND ?",
                (str(first_prev), str(last_prev)))
            prev_pur = float(self.db.cursor.fetchone()[0] or 0)
        except Exception:
            pass

        prev_prof = prev_sales - prev_pur
        values = [sales, pur, prof, float(cli)]
        prevs = [prev_sales, prev_pur, prev_prof, None]
        suffixes = [f" {sym}", f" {sym}", f" {sym}", ""]

        for card, val, prev, suf in zip(self.kpi_cards, values, prevs, suffixes):
            if card is self.kpi_cards[2]:
                c = "#10B981" if val >= 0 else "#EF4444"
                card.value_label.setStyleSheet(
                    f"color:{c}; background:transparent; border:none;")
                card.setStyleSheet(f"""
                    QFrame#kpi {{
                        background:{COLORS.get('BG_CARD','#252535')};
                        border-radius:14px; border:1px solid {c}55;
                    }}
                """)

            animate_value(card.value_label, val, suf)

            if prev is not None and prev > 0:
                evol = ((val - prev) / prev) * 100
                if evol > 0.5:
                    txt, fg, bg = f"▲ +{evol:.0f}%", "#FFF", "#16A34A"
                elif evol < -0.5:
                    txt, fg, bg = f"▼ {evol:.0f}%", "#FFF", "#DC2626"
                else:
                    txt, fg, bg = "→ stable", "#F0F4FF", "rgba(160,170,204,0.22)"
                card.evol_badge.setText(txt)
                card.evol_badge.setStyleSheet(
                    f"color:{fg}; background:{bg}; border-radius:5px; "
                    "padding:2px 8px; font-size:10px; font-weight:bold; border:none;")
            else:
                card.evol_badge.setText("")
                card.evol_badge.setStyleSheet(
                    "background:transparent; border:none; color:transparent;")

    # ─────────────────────────────────────────────────────────────
    #  Derniers Achats (avec détails)
    # ─────────────────────────────────────────────────────────────

    def _load_purchases(self):
        """Charge les derniers achats avec bouton de détails."""
        try:
            self.db.cursor.execute("""
                SELECT 
                    pi.id,
                    pi.purchase_id,
                    pi.product_name,
                    pi.quantity,
                    pi.unit_price,
                    pi.total,
                    pi.created_at,
                    s.name as supplier_name,
                    pu.payment_method,
                    pu.notes
                FROM purchase_items pi
                LEFT JOIN purchases pu ON pi.purchase_id = pu.id
                LEFT JOIN suppliers s ON pu.supplier_id = s.id
                ORDER BY pi.created_at DESC
                LIMIT 10
            """)
            purchases = [dict(row) for row in self.db.cursor.fetchall()]
        except Exception as e:
            print(f"❌ Erreur chargement achats: {e}")
            purchases = []

        self.purchases_table.setRowCount(len(purchases))

        for r, purchase in enumerate(purchases):
            # Numéro d'achat
            purchase_num = f"ACH-{purchase.get('purchase_id', '?')}"

            # Nom du produit avec quantité
            product_name = purchase.get('product_name', '—')
            qty = purchase.get('quantity', 0)
            if qty > 1:
                product_name += f" ×{qty}"

            # Fournisseur
            supplier = purchase.get('supplier_name', '—')

            # Total
            total = float(purchase.get('total', 0))

            cells = [
                (str(purchase_num), "#F0F4FF"),
                (str(product_name), "#F0F4FF"),
                (str(supplier), "#A0AACC"),
                (fmt_da(total), "#F59E0B"),
            ]

            for col, (val, color) in enumerate(cells):
                item = QTableWidgetItem(str(val))
                item.setForeground(QColor(color))
                item.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
                if col == 3:
                    item.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight)
                    item.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
                self.purchases_table.setItem(r, col, item)

            # Bouton de détails
            btn = QPushButton("👁")
            btn.setFixedSize(30, 30)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet("""
                QPushButton {
                    background:rgba(245,158,11,0.20);
                    border-radius:8px; font-size:13px; border:none;
                }
                QPushButton:hover { background:rgba(245,158,11,0.42); }
            """)
            purchase_id = purchase.get('purchase_id')
            btn.clicked.connect(lambda _, pid=purchase_id: self._open_purchase_detail(pid))
            self.purchases_table.setCellWidget(r, 4, btn)
            self.purchases_table.setRowHeight(r, 40)

    def _open_purchase_detail(self, purchase_id: int):
        """Ouvre une boîte de dialogue avec les détails de l'achat."""
        try:
            # Récupérer les détails de l'achat
            self.db.cursor.execute("""
                SELECT 
                    p.*,
                    s.name as supplier_name,
                    s.phone as supplier_phone,
                    s.email as supplier_email
                FROM purchases p
                LEFT JOIN suppliers s ON p.supplier_id = s.id
                WHERE p.id = ?
            """, (purchase_id,))
            
            purchase_row = self.db.cursor.fetchone()
            if not purchase_row:
                QMessageBox.warning(self, "Introuvable", "Cet achat n'existe pas.")
                return
            
            purchase = dict(purchase_row)

            # Récupérer les articles de l'achat
            self.db.cursor.execute("""
                SELECT 
                    pi.*,
                    COALESCE(p.name, pi.product_name) as product_name
                FROM purchase_items pi
                LEFT JOIN products p ON pi.product_id = p.id
                WHERE pi.purchase_id = ?
            """, (purchase_id,))
            
            items = [dict(row) for row in self.db.cursor.fetchall()]

            # Afficher la boîte de dialogue
            dialog = PurchaseDetailsDialog(purchase, items, self)
            dialog.exec()

        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Impossible d'ouvrir les détails:\n{e}")

    # ─────────────────────────────────────────────────────────────
    #  Tableau Factures
    # ─────────────────────────────────────────────────────────────

    def _load_invoices(self):
        PAY = {
            "cash": "💵 Espèces", "card": "💳 Carte",
            "check": "📝 Chèque", "transfer": "🏦 Virement",
            "mobile": "📱 Mobile", "credit": "🔄 Crédit",
        }
        STATUS_COLOR = {
            "paid": "#22C55E", "pending": "#FBBF24", "cancelled": "#EF4444"
        }

        try:
            data = self.db.get_all_sales(limit=10) or []
        except Exception:
            data = []

        self.invoice_table.setRowCount(len(data))
        for r, sale in enumerate(data):
            client = sale.get("client_name") or "—"
            date = str(sale.get("sale_date") or "—").split(" ")[0]
            pay = PAY.get(sale.get("payment_method", ""), sale.get("payment_method") or "—")
            total = float(sale.get("total") or 0)
            status = sale.get("payment_status", "paid")
            tc = STATUS_COLOR.get(status, "#F0F4FF")

            cells = [
                (str(sale.get("invoice_number", "—")), "#F0F4FF", Qt.AlignmentFlag.AlignLeft),
                (str(client), "#F0F4FF", Qt.AlignmentFlag.AlignLeft),
                (fmt_da(total), tc, Qt.AlignmentFlag.AlignRight),
                (date, "#A0AACC", Qt.AlignmentFlag.AlignCenter),
                (pay, "#D1D5DB", Qt.AlignmentFlag.AlignLeft),
            ]
            for col, (val, color, align) in enumerate(cells):
                it = QTableWidgetItem(val)
                it.setForeground(QColor(color))
                it.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | align)
                if col == 2:
                    it.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
                self.invoice_table.setItem(r, col, it)

            btn = QPushButton("👁")
            btn.setFixedSize(30, 30)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet("""
                QPushButton {
                    background:rgba(99,102,241,0.20);
                    border-radius:8px; font-size:13px; border:none;
                }
                QPushButton:hover { background:rgba(99,102,241,0.42); }
            """)
            btn.clicked.connect(lambda _, sid=sale["id"]: self._open_detail(sid))
            self.invoice_table.setCellWidget(r, 5, btn)
            self.invoice_table.setRowHeight(r, 40)

    # ─────────────────────────────────────────────────────────────
    #  Alertes Stock Faible
    # ─────────────────────────────────────────────────────────────

    def _load_low_stock(self):
        _clear_layout(self.low_stock_layout)
        try:
            products = self.db.get_low_stock_products() or []
        except Exception:
            products = []

        nb = len(products)
        self._ls_count.setText(f"{nb} alerte{'s' if nb != 1 else ''}" if nb else "")

        if not products:
            self.low_stock_layout.addWidget(
                _lbl("✅  Tous les stocks sont suffisants", 11, color="#22C55E"))
            return

        for p in products[:8]:
            stock = int(p.get("stock_quantity", 0))
            mini = int(p.get("min_stock", 0))
            name = str(p.get("name", "—"))
            is_rupture = (stock == 0)
            dot_color = "#EF4444" if is_rupture else "#FBBF24"

            row_frame = QFrame()
            row_frame.setStyleSheet(
                f"background:{'rgba(239,68,68,0.12)' if is_rupture else 'rgba(251,191,36,0.10)'};"
                "border-radius:8px; border:none;")
            rh = QHBoxLayout(row_frame)
            rh.setContentsMargins(12, 8, 12, 8)
            rh.setSpacing(10)

            dot = QFrame()
            dot.setFixedSize(13, 13)
            dot.setStyleSheet(f"background:{dot_color}; border-radius:7px; border:none;")
            rh.addWidget(dot)

            nl = QLabel(name[:34])
            nl.setFont(QFont("Segoe UI", 11, QFont.Weight.Medium))
            nl.setStyleSheet(
                f"color:#FFFFFF; "  # ← Texte BLANC pour visibilité
                "background:transparent; border:none;")
            rh.addWidget(nl, 1)

            # Affichage du stock
            if is_rupture:
                stock_text = "⚠️ RUPTURE"
                stock_color = "#FF6B6B"
            else:
                stock_text = f"📦 {stock} / {mini}"
                stock_color = dot_color
            
            sl = QLabel(stock_text)
            sl.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
            sl.setStyleSheet(f"color:{stock_color}; background:transparent; border:none;")
            sl.setAlignment(Qt.AlignmentFlag.AlignRight)
            rh.addWidget(sl)

            self.low_stock_layout.addWidget(row_frame)

    # ─────────────────────────────────────────────────────────────
    #  Top Clients
    # ─────────────────────────────────────────────────────────────

    def _load_top_clients(self, period="year"):
        """Charge le classement des top clients pour une période donnée."""
        _clear_layout(self.top_clients_layout)

        from datetime import datetime, timedelta

        today = datetime.now()
        start_date = None
        end_date = None

        if period == "year":
            start_date = today.replace(month=1, day=1).strftime('%Y-%m-%d')
            end_date = today.strftime('%Y-%m-%d')
            period_label = "Cette année"
        elif period == "month":
            start_date = today.replace(day=1).strftime('%Y-%m-%d')
            end_date = today.strftime('%Y-%m-%d')
            period_label = "Ce mois"
        elif period == "week":
            start_date = (today - timedelta(days=today.weekday())).strftime('%Y-%m-%d')
            end_date = today.strftime('%Y-%m-%d')
            period_label = "Cette semaine"
        elif period == "all":
            start_date = None
            end_date = None
            period_label = "Toutes les périodes"
        elif isinstance(period, tuple):
            start_date, end_date = period
            period_label = f"Du {start_date} au {end_date}"
        else:
            start_date = None
            end_date = None
            period_label = "Toutes les périodes"

        try:
            if start_date and end_date:
                self.db.cursor.execute("""
                    SELECT
                        c.name,
                        COUNT(s.id) as sale_count,
                        SUM(s.total) as total_amount
                    FROM sales s
                    JOIN clients c ON s.client_id = c.id
                    WHERE DATE(s.sale_date) BETWEEN ? AND ?
                    GROUP BY s.client_id
                    ORDER BY total_amount DESC
                    LIMIT 5
                """, (start_date, end_date))
            else:
                self.db.cursor.execute("""
                    SELECT
                        c.name,
                        COUNT(s.id) as sale_count,
                        SUM(s.total) as total_amount
                    FROM sales s
                    JOIN clients c ON s.client_id = c.id
                    GROUP BY s.client_id
                    ORDER BY total_amount DESC
                    LIMIT 5
                """)

            clients = [dict(row) for row in self.db.cursor.fetchall()]
        except Exception as e:
            print(f"❌ Erreur chargement top clients: {e}")
            clients = []

        # En-tête
        header_layout = QHBoxLayout()
        header_layout.addWidget(_lbl("🏆 Top Clients", 13, bold=True))
        header_layout.addStretch()
        header_layout.addWidget(_lbl(period_label, 9, color=COLORS.get("TXT_SEC","#A0AACC")))

        period_btn = QPushButton("📅 Période")
        period_btn.setFixedHeight(28)
        period_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        period_btn.setStyleSheet(f"""
            QPushButton {{
                background: rgba(99,102,241,0.15);
                color: {COLORS.get('primary','#3B82F6')};
                border: 1px solid rgba(99,102,241,0.3);
                border-radius: 6px;
                font-size: 10px;
                font-weight: bold;
                padding: 0 12px;
            }}
            QPushButton:hover {{
                background: rgba(99,102,241,0.3);
            }}
        """)
        period_btn.clicked.connect(lambda: self._open_period_selector())
        header_layout.addWidget(period_btn)

        self.top_clients_layout.addLayout(header_layout)
        self.top_clients_layout.addWidget(divider())

        if not clients:
            self.top_clients_layout.addWidget(
                _lbl(f"Aucune donnée disponible pour {period_label}", 11, color=COLORS.get('TXT_SEC','#A0AACC')))
            return

        MEDAL = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"]
        max_t = max((float(c.get('total_amount', 0)) for c in clients), default=1) or 1

        for rank, c in enumerate(clients):
            name = c.get('name', '—')[:24]
            total = float(c.get('total_amount', 0))
            sale = int(c.get('sale_count', 0))
            pct = total / max_t

            # Ligne client
            client_row = QHBoxLayout()
            client_row.setSpacing(8)

            medal_label = _lbl(MEDAL[rank], 14)
            client_row.addWidget(medal_label)

            name_label = _lbl(name, 10, bold=True)
            client_row.addWidget(name_label, 1)

            amount_label = _lbl(fmt_da(total, 0), 10, color=COLORS.get('primary','#3B82F6'))
            amount_label.setAlignment(Qt.AlignmentFlag.AlignRight)
            client_row.addWidget(amount_label)

            sales_label = _lbl(f"({sale} vente{'s' if sale != 1 else ''})", 9, color=COLORS.get('TXT_SEC','#A0AACC'))
            sales_label.setAlignment(Qt.AlignmentFlag.AlignRight)
            client_row.addWidget(sales_label)

            self.top_clients_layout.addLayout(client_row)

            # Barre de progression
            bar = QFrame()
            bar.setFixedHeight(3)
            bar.setStyleSheet(f"""
                background:qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 {COLORS.get('primary','#3B82F6')},
                    stop:{pct:.2f} {COLORS.get('primary','#3B82F6')},
                    stop:{min(pct+0.01,1):.3f} transparent,
                    stop:1 transparent);
                border-radius:2px; border:none;
            """)
            self.top_clients_layout.addWidget(bar)

        self._top_clients_period = period

    def _open_period_selector(self):
        """Ouvre un dialogue pour choisir la période des top clients."""
        from PyQt6.QtCore import QDate

        dialog = QDialog(self)
        dialog.setWindowTitle("Choisir la période - Top Clients")
        dialog.setMinimumWidth(400)
        dialog.setStyleSheet(f"""
            QDialog {{
                background: {COLORS.get('BG_PAGE','#1E1E2E')};
            }}
            QLabel {{
                color: {COLORS.get('TXT_PRI','#F0F4FF')};
            }}
            QGroupBox {{
                color: {COLORS.get('primary','#3B82F6')};
                border: 1px solid {COLORS.get('BORDER','rgba(255,255,255,0.08)')};
                border-radius: 8px;
                margin-top: 10px;
                font-weight: bold;
                padding-top: 10px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }}
            QRadioButton {{
                color: {COLORS.get('TXT_PRI','#F0F4FF')};
                spacing: 8px;
            }}
            QDateEdit {{
                background: {COLORS.get('BG_DEEP','#16161F')};
                color: {COLORS.get('TXT_PRI','#F0F4FF')};
                border: 1px solid {COLORS.get('BORDER','rgba(255,255,255,0.08)')};
                border-radius: 6px;
                padding: 6px;
            }}
        """)

        layout = QVBoxLayout(dialog)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Périodes prédéfinies
        group1 = QGroupBox("Périodes prédéfinies")
        group1_layout = QVBoxLayout(group1)

        period_radio = QButtonGroup(dialog)

        rb_year = QRadioButton("Cette année")
        rb_month = QRadioButton("Ce mois")
        rb_week = QRadioButton("Cette semaine")
        rb_all = QRadioButton("Toutes les périodes")

        current_period = getattr(self, '_top_clients_period', 'year')
        if current_period == "year":
            rb_year.setChecked(True)
        elif current_period == "month":
            rb_month.setChecked(True)
        elif current_period == "week":
            rb_week.setChecked(True)
        elif current_period == "all":
            rb_all.setChecked(True)
        else:
            rb_year.setChecked(True)

        period_radio.addButton(rb_year, 0)
        period_radio.addButton(rb_month, 1)
        period_radio.addButton(rb_week, 2)
        period_radio.addButton(rb_all, 3)

        group1_layout.addWidget(rb_year)
        group1_layout.addWidget(rb_month)
        group1_layout.addWidget(rb_week)
        group1_layout.addWidget(rb_all)

        layout.addWidget(group1)

        # Période personnalisée
        group2 = QGroupBox("Période personnalisée")
        group2_layout = QVBoxLayout(group2)

        date_layout = QHBoxLayout()
        date_layout.addWidget(QLabel("Du :"))
        start_date = QDateEdit()
        start_date.setCalendarPopup(True)
        start_date.setDate(QDate.currentDate().addDays(-30))
        date_layout.addWidget(start_date)

        date_layout.addWidget(QLabel("Au :"))
        end_date = QDateEdit()
        end_date.setCalendarPopup(True)
        end_date.setDate(QDate.currentDate())
        date_layout.addWidget(end_date)

        group2_layout.addLayout(date_layout)

        custom_radio = QRadioButton("Utiliser cette période")
        group2_layout.addWidget(custom_radio)
        period_radio.addButton(custom_radio, 4)

        layout.addWidget(group2)

        def on_radio_changed():
            if custom_radio.isChecked():
                start_date.setEnabled(True)
                end_date.setEnabled(True)
            else:
                start_date.setEnabled(False)
                end_date.setEnabled(False)

        custom_radio.toggled.connect(on_radio_changed)
        on_radio_changed()

        # Boutons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        cancel_btn = QPushButton("Annuler")
        cancel_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {COLORS.get('TXT_SEC','#A0AACC')};
                border: 1px solid {COLORS.get('BORDER','rgba(255,255,255,0.08)')};
                border-radius: 6px;
                padding: 8px 16px;
            }}
            QPushButton:hover {{
                background: rgba(255,255,255,0.05);
            }}
        """)
        cancel_btn.clicked.connect(dialog.reject)

        apply_btn = QPushButton("Appliquer")
        apply_btn.setStyleSheet(f"""
            QPushButton {{
                background: {COLORS.get('primary','#3B82F6')};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 20px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background: {COLORS.get('secondary','#A855F7')};
            }}
        """)
        apply_btn.clicked.connect(dialog.accept)

        btn_layout.addStretch()
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(apply_btn)
        layout.addLayout(btn_layout)

        if dialog.exec():
            selected_id = period_radio.checkedId()

            if selected_id == 0:
                self._load_top_clients("year")
            elif selected_id == 1:
                self._load_top_clients("month")
            elif selected_id == 2:
                self._load_top_clients("week")
            elif selected_id == 3:
                self._load_top_clients("all")
            elif selected_id == 4:
                start = start_date.date().toString("yyyy-MM-dd")
                end = end_date.date().toString("yyyy-MM-dd")
                self._load_top_clients((start, end))

    # ─────────────────────────────────────────────────────────────
    #  Graphique Ventes 7 jours
    # ─────────────────────────────────────────────────────────────

    def _load_sales_chart(self):
        _clear_layout(self.sales_chart_layout)
        try:
            self.db.cursor.execute("""
                SELECT DATE(sale_date) AS day,
                       SUM(total)      AS total,
                       COUNT(*)        AS nb
                FROM   sales
                WHERE  sale_date >= DATE('now', '-6 days')
                GROUP  BY day ORDER BY day
            """)
            rows_db = {r[0]: (float(r[1] or 0), int(r[2] or 0))
                       for r in self.db.cursor.fetchall()}
        except Exception:
            rows_db = {}

        today = datetime.date.today()
        jours = ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"]
        days = [today - datetime.timedelta(days=6-i) for i in range(7)]
        totals = [rows_db.get(str(d), (0.0, 0))[0] for d in days]
        max_val = max(totals, default=1) or 1
        grand = sum(totals)

        self._chart_total.setText(f"Total semaine : {fmt_da(grand, 0)}" if grand > 0 else "")

        for day_date, total in zip(days, totals):
            nb = rows_db.get(str(day_date), (0, 0))[1]
            dn = jours[day_date.weekday()]
            is_today = (day_date == today)

            rh = QHBoxLayout()
            rh.setSpacing(10)

            day_color = (COLORS.get("primary", "#3B82F6")
                         if is_today
                         else COLORS.get("TXT_SEC", "#A0AACC"))
            prefix = "▶ " if is_today else "   "
            dl = QLabel(f"{prefix}{dn} {day_date.strftime('%d/%m')}")
            dl.setFont(QFont("Segoe UI", 10,
                       QFont.Weight.Bold if is_today else QFont.Weight.Normal))
            dl.setFixedWidth(95)
            dl.setStyleSheet(
                f"color:{day_color}; background:transparent; border:none;")
            rh.addWidget(dl)

            bar = QProgressBar()
            bar.setRange(0, 1000)
            bar.setValue(int((total / max_val) * 1000) if total > 0 else 0)
            bar.setTextVisible(False)
            bar.setFixedHeight(14)

            if total == 0:
                chunk = "background:rgba(255,255,255,0.06); border-radius:5px;"
            elif is_today:
                chunk = (
                    f"background:qlineargradient(x1:0,y1:0,x2:1,y2:0,"
                    f"stop:0 {COLORS.get('primary','#3B82F6')},"
                    f"stop:1 {COLORS.get('secondary','#A855F7')});"
                    "border-radius:5px;")
            else:
                chunk = (
                    f"background:qlineargradient(x1:0,y1:0,x2:1,y2:0,"
                    f"stop:0 {COLORS.get('primary','#3B82F6')}99,"
                    f"stop:1 {COLORS.get('secondary','#A855F7')}99);"
                    "border-radius:5px;")

            bar.setStyleSheet(f"""
                QProgressBar {{
                    background:{COLORS.get('BG_DEEP','#16161F')};
                    border-radius:5px; border:none;
                }}
                QProgressBar::chunk {{ {chunk} }}
            """)
            rh.addWidget(bar, 1)

            amt_color = (COLORS.get("success", "#22C55E")
                         if total > 0
                         else "rgba(160,170,204,0.35)")
            al = QLabel(fmt_da(total, 0) if total > 0 else "—")
            al.setFont(QFont("Segoe UI", 11,
                       QFont.Weight.Bold if total > 0 else QFont.Weight.Normal))
            al.setFixedWidth(135)
            al.setAlignment(
                Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            al.setStyleSheet(
                f"color:{amt_color}; background:transparent; border:none;")
            rh.addWidget(al)

            nbl = QLabel(f"({nb})" if nb > 0 else "")
            nbl.setFont(QFont("Segoe UI", 9))
            nbl.setFixedWidth(40)
            nbl.setAlignment(
                Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            nbl.setStyleSheet(
                "color:rgba(160,170,204,0.60); background:transparent; border:none;")
            rh.addWidget(nbl)

            self.sales_chart_layout.addLayout(rh)

    # ─────────────────────────────────────────────────────────────
    #  Détail facture
    # ─────────────────────────────────────────────────────────────

    def _open_detail(self, sale_id: int):
        if not _DETAIL_AVAILABLE:
            QMessageBox.warning(self, "Module manquant",
                                "Le module sales_history.py est introuvable.")
            return
        try:
            sale = self.db.get_sale_by_id(sale_id)
            if sale:
                InvoiceDetailsDialog(sale, self).exec()
            else:
                QMessageBox.warning(self, "Introuvable",
                                    "Cette vente n'existe plus en base.")
        except Exception as e:
            QMessageBox.critical(self, "Erreur",
                                 f"Impossible d'ouvrir la facture :\n{e}")