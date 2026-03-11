def fmt_da(value, decimals=2):
    """Format monétaire algérien : 1,200.00 DA"""
    try:
        v = float(value)
    except (TypeError, ValueError):
        v = 0.0
    if decimals == 0:
        return f"{v:,.0f} DA"
    return f"{v:,.2f} DA"


"""
Module de gestion des paiements
Gère les différents modes de paiement et le suivi des encaissements
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QLineEdit, QFrame, QTextEdit,
    QDoubleSpinBox, QMessageBox, QTableWidget, QTableWidgetItem,
    QHeaderView, QScrollArea, QWidget
)
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtCore import Qt, pyqtSignal
from datetime import datetime
from styles import COLORS, BUTTON_STYLES, INPUT_STYLE
from db_manager import get_database


class PaymentDialog(QDialog):
    """Dialogue de paiement avec détails de facture et liste déroulante"""

    payment_completed = pyqtSignal(dict)

    def __init__(self, total_amount, invoice_number="", cart_items=None,
                 client_name="Client Anonyme", parent=None):
        super().__init__(parent)

        self.db             = get_database()
        self.total_amount   = total_amount
        self.invoice_number = invoice_number
        self.cart_items     = cart_items or []
        self.client_name    = client_name
        self.vat_rate       = self._get_vat_rate()  # Récupérer la TVA depuis les settings
        self.vat_percent    = self.vat_rate * 100   # Convertir en pourcentage pour l'affichage

        # Références widgets détails
        self.cash_received      = None
        self.change_label       = None
        self.card_transaction   = None
        self.card_type          = None
        self.check_number       = None
        self.check_bank         = None
        self.transfer_ref       = None
        self.mobile_operator    = None
        self.mobile_transaction = None
        self.credit_due_date    = None
        self.notes              = None
        self.details_layout     = None

        self.setWindowTitle("💳 Encaissement")
        self.setMinimumWidth(700)
        self.setMinimumHeight(1000)
        self.setStyleSheet(f"QDialog {{ background-color: {COLORS['bg_medium']}; }}")

        self._setup_ui()

    # ───────────────────────────── UI ────────────────────────────────────────

    def _setup_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        container = QWidget()
        container.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(container)
        layout.setSpacing(14)
        layout.setContentsMargins(24, 24, 24, 24)

        layout.addWidget(self._build_header())
        layout.addWidget(self._build_invoice_details())
        layout.addWidget(self._build_payment_selector())
        layout.addWidget(self._build_details_frame())
        layout.addWidget(self._build_notes())
        layout.addLayout(self._build_buttons())

        scroll.setWidget(container)
        root.addWidget(scroll)

        # Afficher les détails du premier mode
        self.payment_combo.setCurrentIndex(0)
        self._on_method_changed(0)

    def _get_vat_rate(self):
        """Récupère le taux de TVA depuis les settings"""
        try:
            vat_str = self.db.get_setting('vat', '19')
            return float(vat_str) / 100.0  # Convertir en décimal (ex: 19 -> 0.19)
        except:
            return 0.19  # Valeur par défaut

    # ── En-tête ───────────────────────────────────────────────────────────────
    def _build_header(self):
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {COLORS['success']}, stop:1 {COLORS['primary']});
                border-radius: 12px;
            }}
        """)
        lay = QVBoxLayout(frame)
        lay.setContentsMargins(20, 16, 20, 16)
        lay.setSpacing(4)

        t = QLabel("💳 Encaissement de la Facture")
        t.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        t.setStyleSheet("color: white; border: none;")
        lay.addWidget(t)

        sub = QHBoxLayout()
        if self.invoice_number:
            inv = QLabel(f"📄 Facture N° {self.invoice_number}")
            inv.setFont(QFont("Segoe UI", 11))
            inv.setStyleSheet("color: rgba(255,255,255,0.85); border: none;")
            sub.addWidget(inv)
        sub.addStretch()
        cli = QLabel(f"👤 {self.client_name}")
        cli.setFont(QFont("Segoe UI", 11))
        cli.setStyleSheet("color: rgba(255,255,255,0.85); border: none;")
        sub.addWidget(cli)
        lay.addLayout(sub)
        return frame

    # ── Tableau articles + sous-totaux ────────────────────────────────────────
    def _build_invoice_details(self):
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background: {COLORS['bg_card']};
                border-radius: 10px;
                border: 1px solid {COLORS['border']};
            }}
        """)
        lay = QVBoxLayout(card)
        lay.setContentsMargins(16, 14, 16, 14)
        lay.setSpacing(10)

        sec = QLabel("🧾 Détails de la Facture")
        sec.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        sec.setStyleSheet(f"color: {COLORS['text_primary']}; border: none;")
        lay.addWidget(sec)

        # --- tableau articles ---
        tbl = QTableWidget(len(self.cart_items), 5)
        tbl.setHorizontalHeaderLabels(["Produit", "Qté", "Prix Unit.", "Remise", "Total"])
        tbl.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        for col, w in [(1, 50), (2, 110), (3, 70), (4, 120)]:
            tbl.horizontalHeader().setSectionResizeMode(col, QHeaderView.ResizeMode.Fixed)
            tbl.setColumnWidth(col, w)
        tbl.verticalHeader().setVisible(False)
        tbl.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        tbl.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        tbl.setShowGrid(False)
        tbl.setAlternatingRowColors(True)
        tbl.setMaximumHeight(min(38 + len(self.cart_items) * 34, 220))
        tbl.setStyleSheet(f"""
            QTableWidget {{
                background: transparent;
                alternate-background-color: rgba(255,255,255,0.04);
                color: {COLORS['text_primary']};
                border: none; font-size: 12px;
            }}
            QHeaderView::section {{
                background: {COLORS['bg_medium']};
                color: {COLORS['text_primary']};
                font-size: 11px; font-weight: bold;
                padding: 6px 4px;
                border: none;
                border-bottom: 1px solid {COLORS['border']};
            }}
            QTableWidget::item {{ padding: 6px 4px; }}
        """)

        for r, item in enumerate(self.cart_items):
            def mk(text, align=Qt.AlignmentFlag.AlignLeft, col=None):
                it = QTableWidgetItem(text)
                it.setTextAlignment(align | Qt.AlignmentFlag.AlignVCenter)
                if col:
                    it.setForeground(QColor(col))
                return it
            tbl.setItem(r, 0, mk(item.get('product_name', '—')))
            tbl.setItem(r, 1, mk(str(item.get('quantity', 0)), Qt.AlignmentFlag.AlignCenter))
            tbl.setItem(r, 2, mk(f"{fmt_da(item.get('unit_price', 0))}", Qt.AlignmentFlag.AlignRight))
            d = item.get('discount', 0)
            tbl.setItem(r, 3, mk(f"{d:.1f}%" if d else "—", Qt.AlignmentFlag.AlignCenter,
                                 COLORS.get('danger') if d else None))
            tbl.setItem(r, 4, mk(f"{fmt_da(item.get('total', 0))}",
                                 Qt.AlignmentFlag.AlignRight, COLORS.get('success')))

        lay.addWidget(tbl)

        # --- séparateur ---
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(f"background: {COLORS['border']}; border: none;")
        sep.setFixedHeight(1)
        lay.addWidget(sep)

        # --- sous-totaux ---
        subtotal = sum(i.get('total', 0) for i in self.cart_items)
        tax      = subtotal * self.vat_rate
        total    = subtotal + tax

        totals_row = QHBoxLayout()
        totals_row.addStretch()

        tf = QFrame()
        tf.setStyleSheet("background: transparent; border: none;")
        tv = QVBoxLayout(tf)
        tv.setSpacing(4)
        tv.setContentsMargins(0, 0, 0, 0)

        def tline(label, value, color, bold=False):
            h = QHBoxLayout()
            lb = QLabel(label)
            lb.setFont(QFont("Segoe UI", 11))
            lb.setStyleSheet(f"color: {COLORS['text_tertiary']}; border: none;")
            lb.setMinimumWidth(140)
            vl = QLabel(value)
            vl.setFont(QFont("Segoe UI", 13 if bold else 11, QFont.Weight.Bold))
            vl.setStyleSheet(f"color: {color}; border: none;")
            vl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            vl.setMinimumWidth(130)
            h.addWidget(lb)
            h.addWidget(vl)
            tv.addLayout(h)

        tline("Sous-total HT :", f"{fmt_da(subtotal)}", COLORS['text_primary'])
        tline(f"TVA ({self.vat_percent:.0f}%) :",     f"{fmt_da(tax)}",      COLORS.get('warning', '#F59E0B'))
        tline("TOTAL TTC :",     f"{fmt_da(total)}",    COLORS['success'], bold=True)

        totals_row.addWidget(tf)
        lay.addLayout(totals_row)
        return card

    # ── Sélecteur mode paiement — liste déroulante ────────────────────────────
    def _build_payment_selector(self):
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background: {COLORS['bg_card']};
                border-radius: 10px;
                border: 1px solid {COLORS['border']};
            }}
        """)
        lay = QHBoxLayout(card)
        lay.setContentsMargins(16, 14, 16, 14)
        lay.setSpacing(16)

        lbl = QLabel("💰 Mode de Paiement :")
        lbl.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        lbl.setStyleSheet(f"color: {COLORS['text_primary']}; border: none;")
        lay.addWidget(lbl)

        self._methods = [
            ("💵  Espèces",        "cash"),
            ("💳  Carte Bancaire", "card"),
            ("📝  Chèque",         "check"),
            ("🏦  Virement",       "transfer"),
            ("📱  Mobile Money",   "mobile"),
            ("🔄  Crédit",         "credit"),
        ]
        self.payment_combo = QComboBox()
        self.payment_combo.setMinimumHeight(42)
        self.payment_combo.setFont(QFont("Segoe UI", 12))
        self.payment_combo.setStyleSheet(f"""
            QComboBox {{
                background: {COLORS['bg_medium']};
                color: {COLORS['text_primary']};
                border: 2px solid {COLORS['border']};
                border-radius: 8px;
                padding: 6px 14px;
            }}
            QComboBox:focus {{ border: 2px solid {COLORS['primary']}; }}
            QComboBox::drop-down {{ border: none; width: 30px; }}
            QComboBox QAbstractItemView {{
                background: {COLORS['bg_card']};
                color: {COLORS['text_primary']};
                selection-background-color: {COLORS['primary']};
                border: 1px solid {COLORS['border']};
                font-size: 12px;
            }}
            QComboBox QAbstractItemView::item {{
                padding: 8px 14px;
                min-height: 32px;
            }}
        """)
        for label, _ in self._methods:
            self.payment_combo.addItem(label)
        self.payment_combo.currentIndexChanged.connect(self._on_method_changed)
        lay.addWidget(self.payment_combo, 1)
        return card

    # ── Zone détails dynamique ────────────────────────────────────────────────
    def _build_details_frame(self):
        self.details_outer = QFrame()
        self.details_outer.setStyleSheet(f"""
            QFrame {{
                background: {COLORS['bg_card']};
                border-radius: 10px;
                border: 1px solid {COLORS['border']};
            }}
        """)
        self.details_layout = QVBoxLayout(self.details_outer)
        self.details_layout.setContentsMargins(16, 14, 16, 14)
        self.details_layout.setSpacing(10)
        return self.details_outer

    # ── Notes ─────────────────────────────────────────────────────────────────
    def _build_notes(self):
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background: {COLORS['bg_card']};
                border-radius: 10px;
                border: 1px solid {COLORS['border']};
            }}
        """)
        lay = QVBoxLayout(card)
        lay.setContentsMargins(16, 14, 16, 14)
        lay.setSpacing(6)
        lbl = QLabel("📝 Notes (optionnel)")
        lbl.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        lbl.setStyleSheet(f"color: {COLORS['text_primary']}; border: none;")
        lay.addWidget(lbl)
        self.notes = QTextEdit()
        self.notes.setPlaceholderText("Ajoutez des notes sur ce paiement...")
        self.notes.setMaximumHeight(70)
        self.notes.setStyleSheet(INPUT_STYLE)
        lay.addWidget(self.notes)
        return card

    # ── Boutons ───────────────────────────────────────────────────────────────
    def _build_buttons(self):
        lay = QHBoxLayout()
        lay.setSpacing(10)
        cancel = QPushButton("❌ Annuler")
        cancel.setStyleSheet(BUTTON_STYLES['secondary'])
        cancel.setMinimumHeight(48)
        cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel.clicked.connect(self.reject)
        validate = QPushButton("✅ Valider l'Encaissement")
        validate.setStyleSheet(BUTTON_STYLES['success'])
        validate.setMinimumHeight(48)
        validate.setMinimumWidth(240)
        validate.setCursor(Qt.CursorShape.PointingHandCursor)
        validate.clicked.connect(self._validate)
        lay.addWidget(cancel)
        lay.addStretch()
        lay.addWidget(validate)
        return lay

    # ───────────────────────── Logique ───────────────────────────────────────

    def _reset_refs(self):
        self.cash_received = self.change_label = self.card_transaction = None
        self.card_type = self.check_number = self.check_bank = None
        self.transfer_ref = self.mobile_operator = self.mobile_transaction = None
        self.credit_due_date = None

    def _on_method_changed(self, index):
        self._reset_refs()
        if self.details_layout:
            while self.details_layout.count():
                child = self.details_layout.takeAt(0)
                if child.widget():
                    child.widget().setParent(None)

        _, method = self._methods[index]

        titles = {
            "cash":     "💵 Détails — Espèces",
            "card":     "💳 Détails — Carte Bancaire",
            "check":    "📝 Détails — Chèque",
            "transfer": "🏦 Détails — Virement",
            "mobile":   "📱 Détails — Mobile Money",
            "credit":   "🔄 Détails — Crédit",
        }
        t = QLabel(titles.get(method, "Détails"))
        t.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        t.setStyleSheet(f"color: {COLORS['text_primary']}; border: none;")
        self.details_layout.addWidget(t)

        getattr(self, f"_details_{method}")()

    def _irow(self, label, placeholder, attr):
        """Ligne helper label + QLineEdit"""
        h = QHBoxLayout()
        lb = QLabel(label)
        lb.setFont(QFont("Segoe UI", 11))
        lb.setStyleSheet(f"color: {COLORS['text_tertiary']}; border: none;")
        lb.setMinimumWidth(160)
        ed = QLineEdit()
        ed.setPlaceholderText(placeholder)
        ed.setStyleSheet(INPUT_STYLE)
        ed.setMinimumHeight(38)
        h.addWidget(lb)
        h.addWidget(ed, 1)
        self.details_layout.addLayout(h)
        setattr(self, attr, ed)

    def _details_cash(self):
        h = QHBoxLayout()
        lb = QLabel("💵 Montant reçu :")
        lb.setFont(QFont("Segoe UI", 11))
        lb.setStyleSheet(f"color: {COLORS['text_tertiary']}; border: none;")
        lb.setMinimumWidth(160)
        self.cash_received = QDoubleSpinBox()
        self.cash_received.setMinimum(0)
        self.cash_received.setMaximum(999_999_999)
        self.cash_received.setDecimals(2)
        self.cash_received.setValue(self.total_amount)
        self.cash_received.setSuffix(" DA")
        self.cash_received.setMinimumHeight(38)
        self.cash_received.setStyleSheet(INPUT_STYLE)
        self.cash_received.valueChanged.connect(self._calc_change)
        h.addWidget(lb)
        h.addWidget(self.cash_received, 1)
        self.details_layout.addLayout(h)

        self.change_label = QLabel()
        self.change_label.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        self.change_label.setStyleSheet(f"color: {COLORS['success']}; border: none;")
        self.details_layout.addWidget(self.change_label)
        self._calc_change()

    def _calc_change(self):
        if self.cash_received and self.change_label:
            try:
                diff = self.cash_received.value() - self.total_amount
                if diff >= 0:
                    self.change_label.setText(f"💸 Monnaie à rendre : {fmt_da(diff)}")
                    self.change_label.setStyleSheet(f"color: {COLORS['success']}; border: none; font-size: 13px; font-weight: bold;")
                else:
                    self.change_label.setText(f"⚠️ Insuffisant : {fmt_da(abs(diff))} manquants")
                    self.change_label.setStyleSheet(f"color: {COLORS['danger']}; border: none; font-size: 13px; font-weight: bold;")
            except RuntimeError:
                pass

    def _details_card(self):
        self._irow("🔢 N° Transaction :", "Ex: 123456789",          "card_transaction")
        self._irow("💳 Type de carte :",  "Ex: Visa, MasterCard",   "card_type")

    def _details_check(self):
        self._irow("📝 N° Chèque :", "Numéro du chèque", "check_number")
        self._irow("🏦 Banque :",    "Nom de la banque", "check_bank")

    def _details_transfer(self):
        self._irow("🔢 Référence :", "Référence du virement", "transfer_ref")

    def _details_mobile(self):
        self._irow("📱 Opérateur :",     "Ex: BaridiMob, CCP",    "mobile_operator")
        self._irow("🔢 N° Transaction :", "Numéro de transaction", "mobile_transaction")

    def _details_credit(self):
        w = QLabel("⚠️  Montant à recouvrer ultérieurement")
        w.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        w.setStyleSheet(f"color: {COLORS.get('warning','#F59E0B')}; border: none;")
        self.details_layout.addWidget(w)
        self._irow("📅 Date d'échéance :", "JJ/MM/AAAA", "credit_due_date")

    # ── Validation ────────────────────────────────────────────────────────────

    def _safe(self, widget, is_value=False):
        if widget is None:
            return None
        try:
            return widget.value() if is_value else widget.text()
        except RuntimeError:
            return None

    def _validate(self):
        idx = self.payment_combo.currentIndex()
        _, method = self._methods[idx]

        if method == "cash":
            v = self._safe(self.cash_received, is_value=True)
            if v is not None and v < self.total_amount:
                QMessageBox.warning(self, "Montant insuffisant",
                                    "Le montant reçu est inférieur au total !")
                return

        data = {
            'method':         method,
            'amount':         self.total_amount,
            'date':           datetime.now().strftime('%d/%m/%Y %H:%M'),
            'invoice_number': self.invoice_number,
            'notes':          self.notes.toPlainText() if self.notes else "",
            'details':        {}
        }

        if method == "cash":
            v = self._safe(self.cash_received, is_value=True)
            if v is not None:
                data['details']['received'] = v
                data['details']['change']   = v - self.total_amount
        elif method == "card":
            v = self._safe(self.card_transaction)
            if v: data['details']['transaction'] = v
            v = self._safe(self.card_type)
            if v: data['details']['card_type'] = v
        elif method == "check":
            v = self._safe(self.check_number)
            if v: data['details']['check_number'] = v
            v = self._safe(self.check_bank)
            if v: data['details']['bank'] = v
        elif method == "transfer":
            v = self._safe(self.transfer_ref)
            if v: data['details']['reference'] = v
        elif method == "mobile":
            v = self._safe(self.mobile_operator)
            if v: data['details']['operator'] = v
            v = self._safe(self.mobile_transaction)
            if v: data['details']['transaction'] = v
        elif method == "credit":
            v = self._safe(self.credit_due_date)
            if v: data['details']['due_date'] = v

        self.payment_completed.emit(data)
        QMessageBox.information(self, "Paiement enregistré",
            f"✅ Paiement de {fmt_da(self.total_amount)} enregistré avec succès !")
        self.accept()


# ──────────────────────── Fonction utilitaire ────────────────────────────────

def show_payment_dialog(total_amount, invoice_number="", cart_items=None,
                        client_name="Client Anonyme", parent=None):
    """
    Affiche le dialogue de paiement avec les détails de la facture.

    Args:
        total_amount:   Montant TTC
        invoice_number: Numéro de facture
        cart_items:     Liste des articles du panier
        client_name:    Nom du client affiché
        parent:         Widget parent Qt

    Returns:
        dict payment_data si validé, None si annulé
    """
    dialog = PaymentDialog(
        total_amount=total_amount,
        invoice_number=invoice_number,
        cart_items=cart_items or [],
        client_name=client_name,
        parent=parent,
    )
    payment_data = None

    def on_payment(d):
        nonlocal payment_data
        payment_data = d

    dialog.payment_completed.connect(on_payment)
    if dialog.exec():
        return payment_data
    return None