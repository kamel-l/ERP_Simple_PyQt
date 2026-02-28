from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QHeaderView, QPushButton, QHBoxLayout, QFrame, QComboBox, QLineEdit, 
    QMessageBox, QDialog, QScrollArea
)
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtCore import Qt
from styles import COLORS, BUTTON_STYLES, INPUT_STYLE, TABLE_STYLE
from db_manager import get_database
try:
    from returns import ReturnDialog
    _RETURNS_AVAILABLE = True
except ImportError:
    _RETURNS_AVAILABLE = False
from datetime import datetime, timedelta
from PyQt6.QtWidgets import QFileDialog


class InvoiceDetailsDialog(QDialog):
    """Dialogue facture au format professionnel (style DAR ELSSALEM)"""

    # ── Palette interne ───────────────────────────────────────
    BG       = "#0F1117"
    BG_CARD  = "#1A1D27"
    BORDER   = "rgba(255,255,255,0.07)"
    TXT      = "#F1F5F9"
    TXT_MUT  = "rgba(255,255,255,0.40)"
    ACCENT   = "#1E3A5F"       # bleu marine du PDF
    GOLD     = "#C9A84C"       # or du logo
    GREEN    = "#10B981"
    AMBER    = "#F59E0B"

    def __init__(self, sale_data, parent=None):
        super().__init__(parent)
        self.sale = sale_data
        self.setWindowTitle(f"Facture {self.sale['invoice_number']}")
        self.setMinimumSize(820, 780)
        self.setStyleSheet(f"QDialog {{ background:{self.BG}; }}")
        self._build()

    # ── Construction principale ───────────────────────────────
    def _build(self):
        root = QVBoxLayout(self)
        root.setSpacing(0)
        root.setContentsMargins(0, 0, 0, 0)

        # Zone scrollable
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(f"QScrollArea{{border:none; background:{self.BG};}}")

        page = QWidget()
        page.setStyleSheet(f"background:{self.BG};")
        lay = QVBoxLayout(page)
        lay.setSpacing(0)
        lay.setContentsMargins(40, 36, 40, 36)

        lay.addWidget(self._make_top_banner())      # bande bleue supérieure
        lay.addSpacing(20)
        lay.addWidget(self._make_company_row())     # logo + infos date/n°facture
        lay.addSpacing(6)
        lay.addWidget(self._make_mid_banner())      # bande bleue milieu
        lay.addSpacing(20)
        lay.addWidget(self._make_bill_to())         # Bill To
        lay.addSpacing(16)
        lay.addWidget(self._make_items_table())     # tableau articles
        lay.addSpacing(16)
        lay.addWidget(self._make_total_row())       # total
        lay.addSpacing(20)
        lay.addWidget(self._make_footer_note())     # note de bas de page
        lay.addWidget(self._make_bot_banner())      # bande bleue inférieure

        scroll.setWidget(page)
        root.addWidget(scroll)

        # Barre d'actions
        root.addWidget(self._make_actions())

    # ── Bandes décoratives ────────────────────────────────────
    def _make_top_banner(self):
        b = QFrame()
        b.setFixedHeight(10)
        b.setStyleSheet(f"background:{self.ACCENT}; border:none; border-radius:0;")
        return b

    def _make_mid_banner(self):
        b = QFrame()
        b.setFixedHeight(6)
        b.setStyleSheet(f"""
            background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                stop:0 {self.ACCENT}, stop:0.6 {self.GOLD}, stop:1 {self.ACCENT});
            border:none;
        """)
        return b

    def _make_bot_banner(self):
        b = QFrame()
        b.setFixedHeight(10)
        b.setStyleSheet(f"background:{self.ACCENT}; border:none;")
        return b

    # ── En-tête : logo + titre + date/n° ─────────────────────
    def _make_company_row(self):
        db = get_database()
        company_name = db.get_setting('company_name', 'Ma Société')
        company_addr = db.get_setting('company_address', '')

        frame = QFrame()
        frame.setStyleSheet("background:transparent; border:none;")
        row = QHBoxLayout(frame)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(0)

        # ── Côté gauche : badge logo + nom entreprise ─────────
        left = QVBoxLayout()
        left.setSpacing(6)

        # Badge "logo" stylisé (carré bleu marine avec initiale dorée)
        badge_frame = QFrame()
        badge_frame.setFixedSize(90, 90)
        badge_frame.setStyleSheet(f"""
            background: {self.ACCENT};
            border-radius: 12px;
            border: 2px solid {self.GOLD};
        """)
        badge_lay = QVBoxLayout(badge_frame)
        badge_lay.setContentsMargins(0, 0, 0, 0)
        initial = QLabel(company_name[:3].upper() if company_name else "ERP")
        initial.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        initial.setStyleSheet(f"color:{self.GOLD}; background:transparent; border:none;")
        initial.setAlignment(Qt.AlignmentFlag.AlignCenter)
        badge_lay.addWidget(initial)
        left.addWidget(badge_frame)

        name_lbl = QLabel(company_name.upper())
        name_lbl.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        name_lbl.setStyleSheet(f"color:{self.TXT}; background:transparent; border:none;")
        left.addWidget(name_lbl)

        if company_addr:
            addr_lbl = QLabel(company_addr)
            addr_lbl.setFont(QFont("Segoe UI", 9))
            addr_lbl.setStyleSheet(f"color:{self.TXT_MUT}; background:transparent; border:none;")
            addr_lbl.setWordWrap(True)
            left.addWidget(addr_lbl)

        row.addLayout(left)
        row.addStretch()

        # ── Côté droit : titre INVOICE + date + n° ───────────
        right = QVBoxLayout()
        right.setSpacing(4)
        right.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)

        inv_title = QLabel("FACTURE")
        inv_title.setFont(QFont("Segoe UI", 28, QFont.Weight.Bold))
        inv_title.setStyleSheet(f"color:{self.TXT}; background:transparent; border:none;")
        inv_title.setAlignment(Qt.AlignmentFlag.AlignRight)
        right.addWidget(inv_title)

        # Ligne séparatrice fine
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background:{self.ACCENT}; border:none;")
        right.addWidget(sep)

        # Date
        try:
            sale_date = datetime.fromisoformat(self.sale['sale_date'])
            date_str = sale_date.strftime('%d/%m/%Y')
        except Exception:
            date_str = str(self.sale.get('sale_date', '—'))

        date_row = self._meta_row("Date :", date_str)
        right.addWidget(date_row)

        num_row = self._meta_row("N° Facture :", self.sale['invoice_number'])
        right.addWidget(num_row)

        pay_map = {
            'cash': 'Espèces', 'card': 'Carte', 'check': 'Chèque',
            'transfer': 'Virement', 'mobile': 'Mobile', 'credit': 'À Crédit'
        }
        pay = pay_map.get(self.sale.get('payment_method', 'cash'), self.sale.get('payment_method', '—'))
        pay_row = self._meta_row("Paiement :", pay)
        right.addWidget(pay_row)

        row.addLayout(right)
        return frame

    def _meta_row(self, label, value):
        """Ligne label: valeur alignée à droite"""
        w = QWidget()
        w.setStyleSheet("background:transparent;")
        rl = QHBoxLayout(w)
        rl.setContentsMargins(0, 2, 0, 2)
        rl.setSpacing(10)

        lbl = QLabel(label)
        lbl.setFont(QFont("Segoe UI", 10))
        lbl.setStyleSheet(f"color:{self.TXT_MUT}; background:transparent; border:none;")
        lbl.setMinimumWidth(100)

        val = QLabel(str(value))
        val.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        val.setStyleSheet(f"color:{self.TXT}; background:transparent; border:none;")
        val.setAlignment(Qt.AlignmentFlag.AlignRight)

        rl.addWidget(lbl)
        rl.addWidget(val)
        return w

    # ── Section Bill To ───────────────────────────────────────
    def _make_bill_to(self):
        frame = QFrame()
        frame.setStyleSheet("background:transparent; border:none;")
        lay = QVBoxLayout(frame)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(4)

        bill_lbl = QLabel("Facturé à :")
        bill_lbl.setFont(QFont("Segoe UI", 9))
        bill_lbl.setStyleSheet(f"color:{self.TXT_MUT}; background:transparent; border:none;")
        lay.addWidget(bill_lbl)

        client_name = self.sale.get('client_name', 'Client Anonyme')
        name_lbl = QLabel(client_name.upper())
        name_lbl.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        name_lbl.setStyleSheet(f"color:{self.TXT}; background:transparent; border:none;")
        lay.addWidget(name_lbl)

        # Adresse client si disponible
        client_addr = self.sale.get('client_address', '')
        if client_addr:
            addr = QLabel(client_addr)
            addr.setFont(QFont("Segoe UI", 10))
            addr.setStyleSheet(f"color:{self.TXT_MUT}; background:transparent; border:none;")
            lay.addWidget(addr)

        return frame

    # ── Tableau des articles ──────────────────────────────────
    def _make_items_table(self):
        items = self.sale.get('items', [])

        table = QTableWidget(len(items), 6)
        table.setHorizontalHeaderLabels(
            ["Qté", "Référence", "Description", "Prix Unit.", "TVA %", "Total"])

        # Largeurs des colonnes
        hdr = table.horizontalHeader()
        hdr.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        hdr.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        hdr.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        hdr.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        hdr.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        hdr.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)

        table.verticalHeader().setVisible(False)
        table.setAlternatingRowColors(True)
        table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.setShowGrid(True)

        table.setStyleSheet(f"""
            QTableWidget {{
                background: {self.BG_CARD};
                alternate-background-color: rgba(255,255,255,0.03);
                color: {self.TXT};
                border: 1px solid {self.BORDER};
                border-radius: 10px;
                gridline-color: rgba(255,255,255,0.06);
                font-size: 12px;
            }}
            QHeaderView::section {{
                background: {self.ACCENT};
                color: white;
                font-size: 11px;
                font-weight: bold;
                padding: 10px 8px;
                border: none;
                border-right: 1px solid rgba(255,255,255,0.12);
            }}
            QHeaderView::section:last {{
                border-right: none;
            }}
            QTableWidget::item {{
                padding: 10px 8px;
                border-bottom: 1px solid rgba(255,255,255,0.04);
            }}
        """)

        # Helper cellule — défini UNE FOIS avant la boucle
        def make_cell(text, align=Qt.AlignmentFlag.AlignCenter, bold=False, color=None):
            it = QTableWidgetItem(str(text))
            it.setTextAlignment(align | Qt.AlignmentFlag.AlignVCenter)
            if bold:
                it.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
            if color:
                it.setForeground(QColor(color))
            return it

        # Remplir les lignes
        tax_rate = float(self.sale.get('tax_rate', 0))
        for r, item in enumerate(items):
            try:
                qty = int(item.get('quantity', 0) or 0)
            except (ValueError, TypeError):
                qty = 0

            ref  = str(item.get('product_reference') or item.get('reference') or '')
            desc = str(item.get('product_name') or '')

            try:
                price = float(item.get('unit_price', 0) or 0)
            except (ValueError, TypeError):
                price = 0.0

            try:
                total = float(item.get('total', 0) or 0)
            except (ValueError, TypeError):
                total = 0.0

            table.setItem(r, 0, make_cell(qty))
            table.setItem(r, 1, make_cell(ref if ref else '—'))
            table.setItem(r, 2, make_cell(desc if desc else '—', Qt.AlignmentFlag.AlignLeft))
            table.setItem(r, 3, make_cell(f"{price:,.2f} DA", Qt.AlignmentFlag.AlignRight))
            table.setItem(r, 4, make_cell(f"{tax_rate:.0f}%"))
            table.setItem(r, 5, make_cell(
                f"{total:,.2f} DA",
                Qt.AlignmentFlag.AlignRight, bold=True, color=self.GREEN
            ))
            table.setRowHeight(r, 42)

        # Hauteur adaptée
        nb = max(len(items), 1)
        table.setMinimumHeight(min(42 * nb + 50, 420))
        table.setMaximumHeight(min(42 * nb + 50, 420))

        return table

    # ── Ligne de total ────────────────────────────────────────
    def _make_total_row(self):
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background: {self.BG_CARD};
                border-radius: 10px;
                border: 1px solid {self.BORDER};
            }}
        """)
        lay = QVBoxLayout(frame)
        lay.setContentsMargins(20, 16, 20, 16)
        lay.setSpacing(8)

        def total_line(label, value, color=None, big=False):
            w = QWidget()
            w.setStyleSheet("background:transparent;")
            rl = QHBoxLayout(w)
            rl.setContentsMargins(0, 0, 0, 0)
            size_lbl = 13 if big else 11
            size_val = 22 if big else 13

            lbl = QLabel(label)
            lbl.setFont(QFont("Segoe UI", size_lbl,
                QFont.Weight.Bold if big else QFont.Weight.Normal))
            lbl.setStyleSheet(f"color:{self.TXT_MUT if not big else self.TXT}; background:transparent; border:none;")
            rl.addWidget(lbl)
            rl.addStretch()

            val = QLabel(value)
            val.setFont(QFont("Segoe UI", size_val, QFont.Weight.Bold))
            val.setStyleSheet(f"color:{color or self.TXT}; background:transparent; border:none;")
            rl.addWidget(val)
            return w

        subtotal = float(self.sale.get('subtotal', 0))
        tax_amt  = float(self.sale.get('tax_amount', 0))
        total    = float(self.sale.get('total', 0))

        lay.addWidget(total_line("Sous-total HT",   f"{subtotal:,.2f} DA"))
        lay.addWidget(total_line(f"TVA ({self.sale.get('tax_rate', 0)}%)", f"{tax_amt:,.2f} DA", self.AMBER))

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background:{self.BORDER}; border:none;")
        lay.addWidget(sep)

        lay.addWidget(total_line("TOTAL TTC", f"{total:,.2f} DA", self.GREEN, big=True))
        return frame

    # ── Note de bas de page ───────────────────────────────────
    def _make_footer_note(self):
        frame = QFrame()
        frame.setStyleSheet("background:transparent; border:none;")
        lay = QVBoxLayout(frame)
        lay.setContentsMargins(0, 0, 0, 12)
        lay.setSpacing(4)

        for txt in [
            "Veuillez nous contacter pour plus d'informations sur les options de paiement.",
            "Nous vous remercions de votre confiance."
        ]:
            lbl = QLabel(txt)
            lbl.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
            lbl.setStyleSheet(f"color:{self.TXT_MUT}; background:transparent; border:none;")
            lay.addWidget(lbl)

        return frame

    # ── Barre d'actions ───────────────────────────────────────
    def _make_actions(self):
        bar = QFrame()
        bar.setStyleSheet(f"""
            QFrame {{
                background: {self.BG_CARD};
                border-top: 1px solid {self.BORDER};
            }}
        """)
        lay = QHBoxLayout(bar)
        lay.setContentsMargins(24, 12, 24, 12)
        lay.setSpacing(10)

        def btn(label, color, outlined=False):
            b = QPushButton(label)
            b.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
            b.setFixedHeight(38)
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            if outlined:
                b.setStyleSheet(f"""
                    QPushButton{{background:transparent;color:{color};
                        border:1.5px solid {color};border-radius:9px;padding:0 18px;}}
                    QPushButton:hover{{background:{color}22;}}
                """)
            else:
                b.setStyleSheet(f"""
                    QPushButton{{background:{color};color:white;
                        border:none;border-radius:9px;padding:0 18px;}}
                    QPushButton:hover{{opacity:0.85;}}
                """)
            return b

        csv_b = btn("📊  Exporter CSV", "#3B82F6", outlined=True)
        csv_b.clicked.connect(self.export_csv)

        pdf_b = btn("📄  Exporter PDF", "#8B5CF6", outlined=True)
        pdf_b.clicked.connect(self.export_pdf)

        close_b = btn("✕  Fermer", "#EF4444")
        close_b.clicked.connect(self.accept)

        lay.addWidget(csv_b)
        lay.addWidget(pdf_b)
        lay.addStretch()
        lay.addWidget(close_b)
        return bar

    # ── Export CSV (inchangé) ─────────────────────────────────
    def export_csv(self):
        try:
            import csv
            default_name = f"facture_{self.sale['invoice_number']}.csv"
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Enregistrer la facture en CSV", default_name, "CSV Files (*.csv)")
            if not file_path:
                return
            with open(file_path, mode='w', newline='', encoding='utf-8') as f:
                w = csv.writer(f)
                w.writerow(["Facture N°", self.sale['invoice_number']])
                w.writerow(["Date", self.sale['sale_date']])
                w.writerow(["Client", self.sale.get('client_name', 'Client Anonyme')])
                w.writerow([])
                w.writerow(["Qté", "Référence", "Description", "Prix Unit.", "TVA %", "Total"])
                for item in self.sale['items']:
                    w.writerow([
                        item['quantity'], item.get('reference', ''),
                        item['product_name'], item['unit_price'],
                        self.sale.get('tax_rate', 0), item['total']
                    ])
                w.writerow([])
                w.writerow(["Sous-total", self.sale['subtotal']])
                w.writerow(["TVA", self.sale['tax_amount']])
                w.writerow(["Total TTC", self.sale['total']])
            QMessageBox.information(self, "Export Réussi", f"✅ Facture exportée !\n\n{file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur CSV:\n{str(e)}")

    # ── Export PDF (inchangé) ─────────────────────────────────
    def export_pdf(self):
        try:
            from invoice_pdf import create_invoice_pdf
        except ImportError:
            QMessageBox.warning(self, "Module manquant",
                "Le module ReportLab est requis.\n\nInstallez-le avec :\npip install reportlab")
            return

        # Demander où sauvegarder
        default_name = f"facture_{self.sale['invoice_number']}.pdf"
        filename, _ = QFileDialog.getSaveFileName(
            self, "Sauvegarder la facture PDF", default_name,
            "PDF Files (*.pdf);;Tous les fichiers (*.*)"
        )
        if not filename:
            return  # Annulé par l'utilisateur

        try:
            db = get_database()

            # Construire la liste des articles de façon sécurisée
            items_list = []
            for item in self.sale.get('items', []):
                try:
                    qty      = int(item.get('quantity', 0) or 0)
                    price    = float(item.get('unit_price', 0) or 0)
                    discount = float(item.get('discount', 0) or 0)
                    total    = float(item.get('total', 0) or 0)
                    product  = str(item.get('product_name') or 'N/A')
                    ref      = str(item.get('product_reference') or item.get('reference') or '')
                except (ValueError, TypeError):
                    qty, price, discount, total = 0, 0.0, 0.0, 0.0
                    product, ref = 'N/A', ''

                items_list.append({
                    'product':   product,
                    'reference': ref,
                    'quantity':  qty,
                    'price':     price,
                    'discount':  discount,
                    'total':     total,
                })

            try:
                sale_date = datetime.fromisoformat(self.sale['sale_date']).strftime('%d/%m/%Y')
            except Exception:
                sale_date = str(self.sale.get('sale_date', ''))

            invoice_data = {
                'invoice_number': self.sale.get('invoice_number', ''),
                'date':           sale_date,
                'company': {
                    'name':    db.get_setting('company_name',    'Ma Société'),
                    'address': db.get_setting('company_address', ''),
                    'phone':   db.get_setting('company_phone',   ''),
                    'email':   db.get_setting('company_email',   ''),
                    'nif':     db.get_setting('vat_number',      ''),
                },
                'customer': {
                    'name':    self.sale.get('client_name', 'Client Anonyme'),
                    'address': self.sale.get('client_address', ''),
                    'phone':   self.sale.get('client_phone', ''),
                },
                'items':    items_list,
                'subtotal': float(self.sale.get('subtotal', 0) or 0),
                'tax':      float(self.sale.get('tax_amount', 0) or 0),
                'tax_rate': float(self.sale.get('tax_rate', 0) or 0),
                'total':    float(self.sale.get('total', 0) or 0),
            }

            pdf_file = create_invoice_pdf(invoice_data, filename)
            QMessageBox.information(
                self, "✅ PDF Créé",
                f"La facture a été exportée avec succès !\n\n📄 {pdf_file}"
            )

        except Exception as e:
            QMessageBox.critical(
                self, "Erreur",
                f"Impossible de générer le PDF :\n\n{str(e)}"
            )


class SalesHistoryPage(QWidget):
    def __init__(self):
        super().__init__()
        
        self.db = get_database()

        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)

        # Header
        title = QLabel("📊 Historique des Ventes")
        title.setFont(QFont("Segoe UI", 28, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {COLORS['text_primary']}; margin-bottom: 5px;")
        layout.addWidget(title)

        subtitle = QLabel("Consultez l'historique complet de vos ventes")
        subtitle.setFont(QFont("Segoe UI", 14))
        subtitle.setStyleSheet(f"color: {COLORS['text_tertiary']}; margin-bottom: 15px;")
        layout.addWidget(subtitle)

        # Statistics Cards
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(15)
        layout.addLayout(stats_layout)
        
        self.update_statistics()
        stats_layout.addStretch()

        # Filters Bar
        filters_card = QFrame()
        filters_card.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {COLORS['bg_card']}, stop:1 #242424);
                border-radius: 12px;
                border: 1px solid {COLORS['border']};
                padding: 20px;
            }}
        """)
        filters_layout = QHBoxLayout()
        filters_card.setLayout(filters_layout)
        filters_layout.setSpacing(15)

        # Filtre période
        period_label = QLabel("📅 Période:")
        period_label.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        period_label.setStyleSheet(f"color: {COLORS['text_primary']}; border: none;")

        self.period_combo = QComboBox()
        self.period_combo.addItems([
            "Aujourd'hui",
            "Cette semaine",
            "Ce mois",
            "3 derniers mois",
            "Cette année",
            "Tout"
        ])
        self.period_combo.setStyleSheet(INPUT_STYLE)
        self.period_combo.setMinimumHeight(45)
        self.period_combo.currentIndexChanged.connect(self.apply_filters)

        # Barre de recherche
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Rechercher par numéro de facture ou client...")
        self.search_input.setStyleSheet(INPUT_STYLE)
        self.search_input.textChanged.connect(self.apply_filters)
        self.search_input.setMinimumHeight(45)

        # Bouton rafraîchir
        refresh_btn = QPushButton("🔄 Actualiser")
        refresh_btn.setStyleSheet(BUTTON_STYLES['secondary'])
        refresh_btn.setMinimumHeight(45)
        refresh_btn.setFixedWidth(150)
        refresh_btn.clicked.connect(self.load_sales)
        refresh_btn.setCursor(Qt.CursorShape.PointingHandCursor)

        filters_layout.addWidget(period_label)
        filters_layout.addWidget(self.period_combo)
        filters_layout.addWidget(self.search_input)
        filters_layout.addWidget(refresh_btn)

        layout.addWidget(filters_card)

        # Table
        table_container = QFrame()
        table_container.setStyleSheet(f"""
            QFrame {{
                background: {COLORS['bg_card']};
                border-radius: 12px;
                border: 1px solid {COLORS['border']};
                padding: 0px;
            }}
        """)
        table_layout = QVBoxLayout()
        table_layout.setContentsMargins(15, 15, 15, 15)
        table_layout.setSpacing(10)
        table_container.setLayout(table_layout)

        table_title = QLabel("📋 Liste des Ventes")
        table_title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        table_title.setStyleSheet(f"color: {COLORS['text_primary']}; border: none;")
        table_layout.addWidget(table_title)

        self.table = QTableWidget(0, 7)
        self.table.setHorizontalHeaderLabels([
            "N° Facture", "Date", "Client", "Articles",
            "Sous-total", "TVA", "Total TTC"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.verticalHeader().setVisible(False)
        self.table.setStyleSheet(TABLE_STYLE + f"""
            QHeaderView::section {{
                background-color: {COLORS['bg_light']};
                color: {COLORS['text_primary']};
                font-size: 13px;
                font-weight: bold;
                padding: 10px 8px;
                border: none;
                border-right: 1px solid {COLORS['border']};
                border-bottom: 2px solid {COLORS['primary']};
            }}
            QHeaderView::section:last {{
                border-right: none;
            }}
        """)
        
        # Double-clic pour voir les détails
        self.table.doubleClicked.connect(self.view_sale_details)

        table_layout.addWidget(self.table)
        layout.addWidget(table_container)

        # Action Buttons
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(10)
        layout.addLayout(actions_layout)

        self.view_btn = QPushButton("👁️ Voir Détails")
        self.view_btn.setStyleSheet(BUTTON_STYLES['primary'])
        self.view_btn.clicked.connect(self.view_sale_details)
        self.view_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.view_btn.setMinimumHeight(40)

        # Bouton Créer un Avoir (Proposition 5)
        self.return_btn = QPushButton("📦 Créer un Avoir")
        self.return_btn.setStyleSheet(BUTTON_STYLES['danger'])
        self.return_btn.clicked.connect(self.create_return)
        self.return_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.return_btn.setMinimumHeight(40)
        self.return_btn.setFixedWidth(160)

        actions_layout.addStretch()
        actions_layout.addWidget(self.return_btn)
        actions_layout.addWidget(self.view_btn)

        # Charger les données
        self.load_sales()

    def build_stat_card(self, title, value, color):
        """Construit une carte de statistique"""
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {COLORS['bg_card']}, stop:1 #242424);
                border-radius: 10px;
                border: 1px solid {COLORS['border']};
               
            }}
        """)
        card.setFixedHeight(80)
        card.setMinimumWidth(200)

        card_layout = QVBoxLayout()
        card.setLayout(card_layout)
        card_layout.setSpacing(5)
        card_layout.setContentsMargins(15, 10, 15, 10)

        title_label = QLabel(title)
        title_label.setFont(QFont("Segoe UI", 11))
        title_label.setStyleSheet(f"color: {COLORS['text_tertiary']}; border: none;")
        card_layout.addWidget(title_label)

        value_label = QLabel(str(value))
        value_label.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        value_label.setStyleSheet(f"color: {color}; border: none;")
        card_layout.addWidget(value_label)

        return card

    def update_statistics(self):
        """Met à jour les statistiques"""
        # Effacer les anciennes cartes
        stats_layout = self.layout().itemAt(2)
        while stats_layout.count() > 1:
            child = stats_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        # Récupérer les stats
        stats = self.db.get_statistics()
        
        # Aujourd'hui
        today = datetime.now().strftime("%Y-%m-%d")
        today_sales = self.db.get_sales_by_date_range(today, today)
        today_total = sum(sale['total'] for sale in today_sales)
        
        # Cette semaine
        week_start = (datetime.now() - timedelta(days=datetime.now().weekday())).strftime("%Y-%m-%d")
        week_end = datetime.now().strftime("%Y-%m-%d")
        week_sales = self.db.get_sales_by_date_range(week_start, week_end)
        week_total = sum(sale['total'] for sale in week_sales)
        
        # Ajouter les cartes
        stats_layout.insertWidget(0, self.build_stat_card(
            "Ventes Aujourd'hui", f"{today_total:,.0f} DA", COLORS['primary']
        ))
        stats_layout.insertWidget(1, self.build_stat_card(
            "Ventes Cette Semaine", f"{week_total:,.0f} DA", COLORS['success']
        ))
        stats_layout.insertWidget(2, self.build_stat_card(
            "Total Ventes", f"{stats['sales_total']:,.0f} DA", COLORS['secondary']
        ))

    def load_sales(self):
        """Charge toutes les ventes"""
        self.table.setRowCount(0)
        sales = self.db.get_all_sales()
        
        for sale in sales:
            self.add_sale_to_table(sale)
        
        self.update_statistics()

    def add_sale_to_table(self, sale):
        """Ajoute une vente au tableau"""
        row = self.table.rowCount()
        self.table.insertRow(row)
        
        # N° Facture
        invoice_item = QTableWidgetItem(sale['invoice_number'])
        invoice_item.setData(Qt.ItemDataRole.UserRole, sale['id'])
        invoice_item.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        self.table.setItem(row, 0, invoice_item)
        
        # Date
        sale_date = datetime.fromisoformat(sale['sale_date'])
        date_item = QTableWidgetItem(sale_date.strftime("%d/%m/%Y %H:%M"))
        self.table.setItem(row, 1, date_item)
        
        # Client
        client_item = QTableWidgetItem(sale.get('client_name', 'Anonyme'))
        self.table.setItem(row, 2, client_item)
        
        # Nombre d'articles (nécessite une requête supplémentaire)
        sale_details = self.db.get_sale_by_id(sale['id'])
        items_count = len(sale_details['items']) if sale_details else 0
        items_item = QTableWidgetItem(f"{items_count} article(s)")
        items_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.table.setItem(row, 3, items_item)
        
        # Sous-total
        subtotal_item = QTableWidgetItem(f"{sale['subtotal']:,.2f} DA")
        subtotal_item.setTextAlignment(Qt.AlignmentFlag.AlignRight)
        self.table.setItem(row, 4, subtotal_item)
        
        # TVA
        tax_item = QTableWidgetItem(f"{sale['tax_amount']:,.2f} DA")
        tax_item.setTextAlignment(Qt.AlignmentFlag.AlignRight)
        self.table.setItem(row, 5, tax_item)
        
        # Total
        total_item = QTableWidgetItem(f"{sale['total']:,.2f} DA")
        total_item.setTextAlignment(Qt.AlignmentFlag.AlignRight)
        total_item.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        total_item.setForeground(Qt.GlobalColor.green)
        self.table.setItem(row, 6, total_item)

    def apply_filters(self):
        """Applique les filtres"""
        period = self.period_combo.currentText()
        search_text = self.search_input.text().lower()
        
        # Calculer les dates selon la période
        end_date = datetime.now().strftime("%Y-%m-%d")
        
        if period == "Aujourd'hui":
            start_date = end_date
        elif period == "Cette semaine":
            start_date = (datetime.now() - timedelta(days=datetime.now().weekday())).strftime("%Y-%m-%d")
        elif period == "Ce mois":
            start_date = datetime.now().replace(day=1).strftime("%Y-%m-%d")
        elif period == "3 derniers mois":
            start_date = (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")
        elif period == "Cette année":
            start_date = datetime.now().replace(month=1, day=1).strftime("%Y-%m-%d")
        else:  # Tout
            # Charger toutes les ventes
            self.table.setRowCount(0)
            sales = self.db.get_all_sales()
            
            for sale in sales:
                if not search_text or \
                   search_text in sale['invoice_number'].lower() or \
                   search_text in (sale.get('client_name', 'anonyme')).lower():
                    self.add_sale_to_table(sale)
            return
        
        # Charger les ventes de la période
        self.table.setRowCount(0)
        sales = self.db.get_sales_by_date_range(start_date, end_date)
        
        for sale in sales:
            if not search_text or \
               search_text in sale['invoice_number'].lower() or \
               search_text in (sale.get('client_name', 'anonyme')).lower():
                self.add_sale_to_table(sale)

    def view_sale_details(self):
        """Affiche les détails d'une vente dans un dialogue moderne"""
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "Attention", "Veuillez sélectionner une vente!")
            return

        sale_id = self.table.item(selected, 0).data(Qt.ItemDataRole.UserRole)
        sale = self.db.get_sale_by_id(sale_id)

        if not sale:
            QMessageBox.critical(self, "Erreur", "Vente introuvable!")
            return

        dialog = InvoiceDetailsDialog(sale, self)
        dialog.exec()

    def create_return(self):
        """Ouvre le dialogue de création d'un avoir (Proposition 5)."""
        if not _RETURNS_AVAILABLE:
            QMessageBox.warning(self, "Module manquant",
                "Le module de retours (returns.py) n'est pas installé.")
            return

        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "Attention",
                "Veuillez sélectionner une vente pour créer un avoir.")
            return

        sale_id = self.table.item(selected, 0).data(Qt.ItemDataRole.UserRole)
        sale = self.db.get_sale_by_id(sale_id)
        if not sale:
            QMessageBox.critical(self, "Erreur", "Vente introuvable!")
            return

        dialog = ReturnDialog(sale, self)
        dialog.return_created.connect(lambda _: self.load_sales())
        dialog.exec()