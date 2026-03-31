from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QHeaderView, QPushButton, QHBoxLayout, QFrame, QComboBox, QLineEdit,
    QMessageBox, QDialog, QScrollArea, QFileDialog
)
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtCore import Qt
from db_manager import get_database
try:
    from returns import ReturnDialog
    _RETURNS_AVAILABLE = True
except ImportError:
    _RETURNS_AVAILABLE = False
from datetime import datetime, timedelta

# ── Palette Midnight Amber ────────────────────────────────────────────────
C = {
    'bg':        '#0D0D0F',
    'bg_card':   '#1C1C23',
    'bg_input':  '#12121A',
    'bg_row':    '#141418',
    'amber':     '#F5A623',
    'amber_d':   '#C4841A',
    'amber_l':   '#FFD080',
    'teal':      '#4ECDC4',
    'coral':     '#FF6B6B',
    'yellow':    '#FFE66D',
    'txt':       '#F0EDE8',
    'txt_sec':   '#B0A99A',
    'txt_dim':   '#6B6460',
    'border':    '#2A2A35',
}

BTN = {
    'primary': f"""
        QPushButton {{
            background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
                stop:0 {C['amber']}, stop:1 {C['amber_d']});
            color: #0D0D0F; border: none; border-radius: 6px;
            padding: 10px 20px; font-size: 13px; font-weight: bold; min-height: 36px;
        }}
        QPushButton:hover {{ background: {C['amber_l']}; }}
        QPushButton:pressed {{ background: {C['amber_d']}; }}
    """,
    'success': f"""
        QPushButton {{
            background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
                stop:0 {C['teal']}, stop:1 #3AAA9F);
            color: #0D0D0F; border: none; border-radius: 6px;
            padding: 10px 20px; font-size: 13px; font-weight: bold; min-height: 36px;
        }}
        QPushButton:hover {{ background: #7EDBD5; }}
    """,
    'danger': f"""
        QPushButton {{
            background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
                stop:0 {C['coral']}, stop:1 #CC4444);
            color: {C['txt']}; border: none; border-radius: 6px;
            padding: 10px 20px; font-size: 13px; font-weight: bold; min-height: 36px;
        }}
        QPushButton:hover {{ background: #FF9090; }}
    """,
    'secondary': f"""
        QPushButton {{
            background: transparent; color: {C['amber']};
            border: 1.5px solid rgba(245,166,35,0.4); border-radius: 6px;
            padding: 10px 20px; font-size: 13px; font-weight: bold; min-height: 36px;
        }}
        QPushButton:hover {{ background: rgba(245,166,35,0.10); border-color:{C['amber']}; }}
    """,
}

INPUT_STYLE = f"""
    QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QTextEdit {{
        background-color: {C['bg_input']}; border: 1.5px solid {C['border']};
        border-radius: 6px; padding: 8px 12px;
        color: {C['txt']}; font-size: 13px; min-height: 36px;
    }}
    QLineEdit:focus, QComboBox:focus {{
        border: 1.5px solid {C['amber']}; background-color: {C['bg_card']};
    }}
    QLineEdit:hover, QComboBox:hover {{ border: 1.5px solid rgba(245,166,35,0.40); }}
    QComboBox::drop-down {{ border:none; width:30px; }}
    QComboBox::down-arrow {{
        image:none; border-left:5px solid transparent; border-right:5px solid transparent;
        border-top:5px solid {C['amber']}; margin-right:10px;
    }}
    QComboBox QAbstractItemView {{
        background-color: {C['bg_card']}; border:1px solid rgba(245,166,35,0.25);
        selection-background-color: rgba(245,166,35,0.18); color: {C['txt']};
    }}
"""

TABLE_STYLE = f"""
    QTableWidget {{
        background-color: {C['bg_card']}; alternate-background-color: {C['bg_row']};
        border: 1px solid {C['border']}; border-radius: 8px;
        gridline-color: rgba(255,255,255,0.04); color: {C['txt']};
        selection-background-color: rgba(245,166,35,0.18); font-size: 13px;
    }}
    QTableWidget::item {{ padding: 10px 8px; border:none; }}
    QTableWidget::item:selected {{ background-color:rgba(245,166,35,0.22); color:{C['txt']}; }}
    QTableWidget::item:hover {{ background-color:rgba(245,166,35,0.08); }}
    QHeaderView::section {{
        background: {C['bg']}; color: {C['amber']};
        padding: 10px 8px; border:none;
        border-bottom: 2px solid rgba(245,166,35,0.30);
        font-weight:bold; font-size:11px; letter-spacing:0.8px;
    }}
    QScrollBar:vertical {{ background:{C['bg']}; width:6px; border-radius:3px; }}
    QScrollBar::handle:vertical {{ background:rgba(245,166,35,0.35); border-radius:3px; }}
    QScrollBar::handle:vertical:hover {{ background:{C['amber']}; }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height:0; }}
"""


class InvoiceDetailsDialog(QDialog):
    """Facture au format professionnel — thème Midnight Amber"""

    def __init__(self, sale_data, parent=None):
        super().__init__(parent)
        self.sale = sale_data
        self.setWindowTitle(f"Facture {self.sale['invoice_number']}")
        self.setMinimumSize(820, 780)
        self.setStyleSheet(f"QDialog {{ background:{C['bg']}; }}")
        self._build()

    def _build(self):
        root = QVBoxLayout(self)
        root.setSpacing(0)
        root.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(f"QScrollArea{{ border:none; background:{C['bg']}; }}")

        page = QWidget()
        page.setStyleSheet(f"background:{C['bg']};")
        lay = QVBoxLayout(page)
        lay.setSpacing(0)
        lay.setContentsMargins(36, 32, 36, 32)

        # Bande ambre supérieure
        top_band = QFrame()
        top_band.setFixedHeight(8)
        top_band.setStyleSheet(f"""
            background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                stop:0 {C['amber_d']}, stop:0.5 {C['amber']}, stop:1 {C['amber_d']});
            border:none;
        """)
        lay.addWidget(top_band)
        lay.addSpacing(24)

        # En-tête
        lay.addWidget(self._make_company_row())
        lay.addSpacing(20)

        # Bande décorative
        mid_band = QFrame()
        mid_band.setFixedHeight(2)
        mid_band.setStyleSheet(f"background:rgba(245,166,35,0.25); border:none;")
        lay.addWidget(mid_band)
        lay.addSpacing(20)

        lay.addWidget(self._make_bill_to())
        lay.addSpacing(16)
        lay.addWidget(self._make_items_table())
        lay.addSpacing(16)
        lay.addWidget(self._make_total_row())
        lay.addSpacing(20)
        lay.addWidget(self._make_footer_note())

        # Bande ambre inférieure
        bot_band = QFrame()
        bot_band.setFixedHeight(8)
        bot_band.setStyleSheet(f"""
            background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                stop:0 {C['amber_d']}, stop:0.5 {C['amber']}, stop:1 {C['amber_d']});
            border:none;
        """)
        lay.addWidget(bot_band)

        scroll.setWidget(page)
        root.addWidget(scroll)
        root.addWidget(self._make_actions())

    def _make_company_row(self):
        from db_manager import get_database as _gdb
        db = _gdb()
        company_name = db.get_setting('company_name', 'Ma Société')
        company_addr = db.get_setting('company_address', '')

        frame = QFrame()
        frame.setStyleSheet("background:transparent; border:none;")
        row = QHBoxLayout(frame)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(0)

        # Gauche : badge + nom
        left = QVBoxLayout()
        left.setSpacing(6)

        badge_frame = QFrame()
        badge_frame.setFixedSize(88, 88)
        badge_frame.setStyleSheet(f"""
            background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                stop:0 #2A1E08, stop:1 #1C1408);
            border-radius: 12px;
            border: 2px solid rgba(245,166,35,0.5);
        """)
        bl = QVBoxLayout(badge_frame)
        bl.setContentsMargins(0, 0, 0, 0)
        init = QLabel(company_name[:3].upper() if company_name else "ERP")
        init.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        init.setStyleSheet(f"color:{C['amber']}; background:transparent; border:none;")
        init.setAlignment(Qt.AlignmentFlag.AlignCenter)
        bl.addWidget(init)
        left.addWidget(badge_frame)

        name_lbl = QLabel(company_name.upper())
        name_lbl.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        name_lbl.setStyleSheet(f"color:{C['txt']}; background:transparent; border:none;")
        left.addWidget(name_lbl)

        if company_addr:
            addr_lbl = QLabel(company_addr)
            addr_lbl.setFont(QFont("Segoe UI", 9))
            addr_lbl.setStyleSheet(f"color:{C['txt_sec']}; background:transparent; border:none;")
            addr_lbl.setWordWrap(True)
            left.addWidget(addr_lbl)

        row.addLayout(left)
        row.addStretch()

        # Droite : FACTURE + meta
        right = QVBoxLayout()
        right.setSpacing(4)
        right.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)

        inv_title = QLabel("FACTURE")
        inv_title.setFont(QFont("Segoe UI", 30, QFont.Weight.Bold))
        inv_title.setStyleSheet(f"color:{C['amber']}; background:transparent; border:none;")
        inv_title.setAlignment(Qt.AlignmentFlag.AlignRight)
        right.addWidget(inv_title)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background:rgba(245,166,35,0.30); border:none;")
        right.addWidget(sep)

        try:
            date_str = datetime.fromisoformat(self.sale['sale_date']).strftime('%d/%m/%Y')
        except Exception:
            date_str = str(self.sale.get('sale_date', '—'))

        for label, value in [
            ("Date :", date_str),
            ("N° Facture :", self.sale['invoice_number']),
            ("Paiement :", {'cash': 'Espèces', 'card': 'Carte', 'check': 'Chèque',
                            'transfer': 'Virement', 'mobile': 'Mobile', 'credit': 'À Crédit'
                            }.get(self.sale.get('payment_method', 'cash'), '—'))
        ]:
            w = QWidget()
            w.setStyleSheet("background:transparent;")
            rl = QHBoxLayout(w)
            rl.setContentsMargins(0, 2, 0, 2)
            rl.setSpacing(10)
            lbl = QLabel(label)
            lbl.setFont(QFont("Segoe UI", 10))
            lbl.setStyleSheet(f"color:{C['txt_sec']}; background:transparent; border:none;")
            lbl.setMinimumWidth(100)
            val = QLabel(str(value))
            val.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
            val.setStyleSheet(f"color:{C['txt']}; background:transparent; border:none;")
            val.setAlignment(Qt.AlignmentFlag.AlignRight)
            rl.addWidget(lbl)
            rl.addWidget(val)
            right.addWidget(w)

        row.addLayout(right)
        return frame

    def _make_bill_to(self):
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background: rgba(245,166,35,0.05);
                border-radius: 8px;
                border: 1px solid rgba(245,166,35,0.15);
            }}
        """)
        lay = QVBoxLayout(frame)
        lay.setContentsMargins(14, 12, 14, 12)
        lay.setSpacing(4)

        bill_lbl = QLabel("Facturé à :")
        bill_lbl.setFont(QFont("Segoe UI", 9))
        bill_lbl.setStyleSheet(f"color:{C['txt_sec']}; background:transparent; border:none;")
        lay.addWidget(bill_lbl)

        client_name = self.sale.get('client_name', 'Client Anonyme')
        name_lbl = QLabel(client_name.upper())
        name_lbl.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        name_lbl.setStyleSheet(f"color:{C['amber']}; background:transparent; border:none;")
        lay.addWidget(name_lbl)

        client_addr = self.sale.get('client_address', '')
        if client_addr:
            addr = QLabel(client_addr)
            addr.setFont(QFont("Segoe UI", 10))
            addr.setStyleSheet(f"color:{C['txt_sec']}; background:transparent; border:none;")
            lay.addWidget(addr)
        return frame

    def _make_items_table(self):
        from currency import fmt_da
        items = self.sale.get('items', [])

        table = QTableWidget(len(items), 6)
        table.setHorizontalHeaderLabels(["Qté", "Nom", "Description", "Prix Unit.", "TVA %", "Total"])

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
                background: {C['bg_card']};
                alternate-background-color: {C['bg_row']};
                color: {C['txt']};
                border: 1px solid {C['border']};
                border-radius: 8px;
                gridline-color: rgba(255,255,255,0.05);
                font-size: 12px;
            }}
            QHeaderView::section {{
                background: {C['bg']};
                color: {C['amber']};
                font-size: 11px; font-weight: bold;
                padding: 10px 8px; border: none;
                border-right: 1px solid rgba(245,166,35,0.15);
                border-bottom: 2px solid rgba(245,166,35,0.30);
            }}
            QTableWidget::item {{ padding: 10px 8px; border-bottom:1px solid rgba(255,255,255,0.04); }}
        """)

        def make_cell(text, align=Qt.AlignmentFlag.AlignCenter, bold=False, color=None):
            it = QTableWidgetItem(str(text))
            it.setTextAlignment(align | Qt.AlignmentFlag.AlignVCenter)
            if bold:
                it.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
            if color:
                it.setForeground(QColor(color))
            return it

        tax_rate = float(self.sale.get('tax_rate', 0))
        for r, item in enumerate(items):
            try:
                qty = int(item.get('quantity', 0) or 0)
            except:
                qty = 0
            ref = str(item.get('product_name') or '')
            desc = str(item.get('product_reference') or '')
            try:
                price = float(item.get('unit_price', 0) or 0)
            except:
                price = 0.0
            try:
                total = float(item.get('total', 0) or 0)
            except:
                total = 0.0

            table.setItem(r, 0, make_cell(qty))
            table.setItem(r, 1, make_cell(ref if ref else '—'))
            table.setItem(r, 2, make_cell(desc if desc else '—', Qt.AlignmentFlag.AlignLeft))
            table.setItem(r, 3, make_cell(fmt_da(price), Qt.AlignmentFlag.AlignRight))
            table.setItem(r, 4, make_cell(f"{tax_rate:.0f}%"))
            table.setItem(r, 5, make_cell(
                fmt_da(total), Qt.AlignmentFlag.AlignRight,
                bold=True, color=C['teal']))
            table.setRowHeight(r, 42)

        nb = max(len(items), 1)
        table.setMinimumHeight(min(42 * nb + 50, 420))
        table.setMaximumHeight(min(42 * nb + 50, 420))
        return table

    def _make_total_row(self):
        from currency import fmt_da
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background: {C['bg_card']};
                border-radius: 10px;
                border: 1px solid {C['border']};
            }}
        """)
        lay = QVBoxLayout(frame)
        lay.setContentsMargins(20, 16, 20, 16)
        lay.setSpacing(8)

        subtotal = float(self.sale.get('subtotal', 0))
        tax_amt = float(self.sale.get('tax_amount', 0))
        total = float(self.sale.get('total', 0))

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
            lbl.setStyleSheet(f"color:{C['txt_sec'] if not big else C['txt']}; background:transparent; border:none;")
            rl.addWidget(lbl)
            rl.addStretch()
            val = QLabel(value)
            val.setFont(QFont("Segoe UI", size_val, QFont.Weight.Bold))
            val.setStyleSheet(f"color:{color or C['txt']}; background:transparent; border:none;")
            rl.addWidget(val)
            return w

        lay.addWidget(total_line("Sous-total HT", fmt_da(subtotal)))
        lay.addWidget(total_line(
            f"TVA ({self.sale.get('tax_rate', 0)}%)", fmt_da(tax_amt), C['yellow']))

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background:rgba(245,166,35,0.25); border:none;")
        lay.addWidget(sep)
        lay.addWidget(total_line("TOTAL TTC", fmt_da(total), C['amber'], big=True))
        return frame

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
            lbl.setFont(QFont("Segoe UI", 10))
            lbl.setStyleSheet(f"color:{C['txt_dim']}; background:transparent; border:none;")
            lay.addWidget(lbl)
        return frame

    def _make_actions(self):
        bar = QFrame()
        bar.setStyleSheet(f"""
            QFrame {{ background:{C['bg_card']}; border-top:1px solid {C['border']}; }}
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
                        border:1.5px solid {color}66;border-radius:7px;padding:0 18px;}}
                    QPushButton:hover{{background:{color}18;border-color:{color};}}
                """)
            else:
                b.setStyleSheet(f"""
                    QPushButton{{background:{color};color:#0D0D0F;
                        border:none;border-radius:7px;padding:0 18px;font-weight:bold;}}
                    QPushButton:hover{{opacity:0.85;}}
                """)
            return b

        csv_b = btn("📊  Exporter CSV", C['amber'], outlined=True)
        csv_b.clicked.connect(self.export_csv)
        pdf_b = btn("📄  Exporter PDF", C['teal'], outlined=True)
        pdf_b.clicked.connect(self.export_pdf)
        close_b = btn("✕  Fermer", C['coral'])
        close_b.clicked.connect(self.accept)

        lay.addWidget(csv_b)
        lay.addWidget(pdf_b)
        lay.addStretch()
        lay.addWidget(close_b)
        return bar

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
                    w.writerow([item['quantity'], item.get('product_name', ''),
                                 item['product_name'], item['unit_price'],
                                 self.sale.get('tax_rate', 0), item['total']])
                w.writerow([])
                w.writerow(["Sous-total", self.sale['subtotal']])
                w.writerow(["TVA", self.sale['tax_amount']])
                w.writerow(["Total TTC", self.sale['total']])
            QMessageBox.information(self, "Export Réussi", f"✅ Facture exportée !\n\n{file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur CSV:\n{str(e)}")

    def export_pdf(self):
        try:
            from invoice_pdf import create_invoice_pdf
        except ImportError:
            QMessageBox.warning(self, "Module manquant",
                "ReportLab est requis.\n\npip install reportlab")
            return
        default_name = f"facture_{self.sale['invoice_number']}.pdf"
        filename, _ = QFileDialog.getSaveFileName(
            self, "Sauvegarder la facture PDF", default_name, "PDF Files (*.pdf)")
        if not filename:
            return
        try:
            from db_manager import get_database as _gdb
            db = _gdb()
            items_list = []
            for item in self.sale.get('items', []):
                try:
                    qty = int(item.get('quantity', 0) or 0)
                    price = float(item.get('unit_price', 0) or 0)
                    discount = float(item.get('discount', 0) or 0)
                    total = float(item.get('total', 0) or 0)
                    product = str(item.get('product_name') or 'N/A')
                    ref = str(item.get('product_reference') or '')
                except:
                    qty, price, discount, total = 0, 0.0, 0.0, 0.0
                    product, ref = 'N/A', ''
                items_list.append({
                    'product': product, 'reference': ref,
                    'quantity': qty, 'price': price,
                    'discount': discount, 'total': total
                })
            try:
                sale_date = datetime.fromisoformat(self.sale['sale_date']).strftime('%d/%m/%Y')
            except:
                sale_date = str(self.sale.get('sale_date', ''))
            invoice_data = {
                'invoice_number': self.sale.get('invoice_number', ''),
                'date': sale_date,
                'company': {
                    'name': db.get_setting('company_name', 'Ma Société'),
                    'address': db.get_setting('company_address', ''),
                    'phone': db.get_setting('company_phone', ''),
                    'email': db.get_setting('company_email', ''),
                    'nif': db.get_setting('vat_number', ''),
                },
                'customer': {
                    'name': self.sale.get('client_name', 'Client Anonyme'),
                    'address': self.sale.get('client_address', ''),
                    'phone': self.sale.get('client_phone', ''),
                },
                'items': items_list,
                'subtotal': float(self.sale.get('subtotal', 0) or 0),
                'tax': float(self.sale.get('tax_amount', 0) or 0),
                'tax_rate': float(self.sale.get('tax_rate', 0) or 0),
                'total': float(self.sale.get('total', 0) or 0),
            }
            pdf_file = create_invoice_pdf(invoice_data, filename)
            QMessageBox.information(self, "✅ PDF Créé",
                f"Facture exportée avec succès !\n\n📄 {pdf_file}")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Impossible de générer le PDF :\n\n{str(e)}")


class SalesHistoryPage(QWidget):
    def __init__(self):
        super().__init__()
        self.db = get_database()

        self.setStyleSheet(f"background-color:{C['bg']};")
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(22, 20, 22, 20)

        # ── Titre ──
        hdr = QHBoxLayout()
        accent = QFrame()
        accent.setFixedSize(4, 50)
        accent.setStyleSheet(f"""
            background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
                stop:0 {C['amber']}, stop:1 {C['teal']});
            border-radius: 2px;
        """)
        hdr.addWidget(accent)
        hdr.addSpacing(10)
        titles = QVBoxLayout()
        titles.setSpacing(2)
        t = QLabel("Historique des Ventes")
        t.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        t.setStyleSheet(f"color:{C['txt']}; background:transparent;")
        titles.addWidget(t)
        s = QLabel("Consultez l'historique complet de vos ventes")
        s.setFont(QFont("Segoe UI", 11))
        s.setStyleSheet(f"color:{C['txt_dim']}; background:transparent;")
        titles.addWidget(s)
        hdr.addLayout(titles)
        hdr.addStretch()
        layout.addLayout(hdr)

        # ── Statistiques ──
        self.stats_layout = QHBoxLayout()
        self.stats_layout.setSpacing(12)
        layout.addLayout(self.stats_layout)
        self.update_statistics()
        self.stats_layout.addStretch()

        # ── Filtres ──
        filters_card = QFrame()
        filters_card.setStyleSheet(f"""
            QFrame {{ background:{C['bg_card']}; border-radius:10px; border:1px solid {C['border']}; }}
        """)
        fl = QHBoxLayout(filters_card)
        fl.setContentsMargins(16, 12, 16, 12)
        fl.setSpacing(14)

        period_lbl = QLabel("📅  Période :")
        period_lbl.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        period_lbl.setStyleSheet(f"color:{C['amber']}; border:none;")

        self.period_combo = QComboBox()
        self.period_combo.addItems([
            "Aujourd'hui", "Cette semaine", "Ce mois",
            "3 derniers mois", "Cette année", "Tout"
        ])
        self.period_combo.setStyleSheet(INPUT_STYLE)
        self.period_combo.setMinimumHeight(42)
        self.period_combo.currentIndexChanged.connect(self.apply_filters)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("  Rechercher par facture ou client...")
        self.search_input.setStyleSheet(INPUT_STYLE)
        self.search_input.textChanged.connect(self.apply_filters)
        self.search_input.setMinimumHeight(42)

        fl.addWidget(period_lbl)
        fl.addWidget(self.period_combo)
        fl.addWidget(self.search_input)
        layout.addWidget(filters_card)

        # ── Tableau ──
        tbl_card = QFrame()
        tbl_card.setStyleSheet(f"""
            QFrame {{ background:{C['bg_card']}; border-radius:12px; border:1px solid {C['border']}; }}
        """)
        tcl = QVBoxLayout(tbl_card)
        tcl.setContentsMargins(14, 12, 14, 12)
        tcl.setSpacing(8)

        tbl_title = QLabel("📋  Liste des Ventes")
        tbl_title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        tbl_title.setStyleSheet(f"color:{C['txt']}; border:none;")
        tcl.addWidget(tbl_title)

        self.table = QTableWidget(0, 7)
        self.table.setHorizontalHeaderLabels([
            "N° Facture", "Date", "Client", "Articles",
            "Sous-total", "TVA", "Total TTC"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.setStyleSheet(TABLE_STYLE)
        self.table.doubleClicked.connect(self.view_sale_details)
        self.showEvent = self.load_sales()
        tcl.addWidget(self.table)
        layout.addWidget(tbl_card)

        # ── Boutons d'action ──
        actions = QHBoxLayout()
        actions.setSpacing(10)

        self.view_btn = QPushButton("👁  Voir Détails")
        self.view_btn.setStyleSheet(BTN['primary'])
        self.view_btn.clicked.connect(self.view_sale_details)
        self.view_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.view_btn.setMinimumHeight(40)

        self.return_btn = QPushButton("↩  Créer un Avoir")
        self.return_btn.setStyleSheet(BTN['danger'])
        self.return_btn.clicked.connect(self.create_return)
        self.return_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.return_btn.setMinimumHeight(40)
        self.return_btn.setFixedWidth(165)

        self.import_btn = QPushButton("↓  Importer .DAT")
        self.import_btn.setStyleSheet(BTN['success'])
        self.import_btn.clicked.connect(self.import_dat_file)
        self.import_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.import_btn.setMinimumHeight(40)
        self.import_btn.setFixedWidth(155)

        actions.addStretch()
        actions.addWidget(self.import_btn)
        actions.addWidget(self.return_btn)
        actions.addWidget(self.view_btn)
        layout.addLayout(actions)

        self.load_sales()

    def build_stat_card(self, title, value, color):
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background:{C['bg_card']}; border-radius:10px;
                border:1px solid {C['border']}; border-left:3px solid {color};
            }}
        """)
        card.setFixedHeight(78)
        card.setMinimumWidth(200)
        cl = QVBoxLayout(card)
        cl.setSpacing(3)
        cl.setContentsMargins(14, 10, 14, 10)
        tl = QLabel(title)
        tl.setFont(QFont("Segoe UI", 10))
        tl.setStyleSheet(f"color:{C['txt_dim']}; border:none; background:transparent;")
        cl.addWidget(tl)
        vl = QLabel(str(value))
        vl.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        vl.setStyleSheet(f"color:{color}; border:none; background:transparent;")
        cl.addWidget(vl)
        return card

    def update_statistics(self):
        from currency import fmt_da
        stats_layout = self.layout().itemAt(1)
        while stats_layout.count() > 1:
            child = stats_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        stats = self.db.get_statistics()
        today = datetime.now().strftime("%Y-%m-%d")
        today_sales = self.db.get_sales_by_date_range(today, today)
        today_total = sum(sale['total'] for sale in today_sales)
        week_start = (datetime.now() - timedelta(days=datetime.now().weekday())).strftime("%Y-%m-%d")
        week_end = datetime.now().strftime("%Y-%m-%d")
        week_sales = self.db.get_sales_by_date_range(week_start, week_end)
        week_total = sum(sale['total'] for sale in week_sales)
        stats_layout.insertWidget(0, self.build_stat_card(
            "Ventes Aujourd'hui", fmt_da(today_total), C['amber']))
        stats_layout.insertWidget(1, self.build_stat_card(
            "Ventes Cette Semaine", fmt_da(week_total), C['teal']))
        stats_layout.insertWidget(2, self.build_stat_card(
            "Total Ventes", fmt_da(stats['sales_total']), C['coral']))

    def showEvent(self, event):
        super().showEvent(event)
        self.load_sales()

    def load_sales(self):
        from currency import fmt_da
        self.table.setRowCount(0)
        for sale in self.db.get_all_sales():
            self.add_sale_to_table(sale)
        self.update_statistics()

    def add_sale_to_table(self, sale):
        from currency import fmt_da
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setRowHeight(row, 44)

        invoice_item = QTableWidgetItem(sale['invoice_number'])
        invoice_item.setData(Qt.ItemDataRole.UserRole, sale['id'])
        invoice_item.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        invoice_item.setForeground(QColor(C['amber']))
        self.table.setItem(row, 0, invoice_item)

        sale_date = datetime.fromisoformat(sale['sale_date'])
        date_item = QTableWidgetItem(sale_date.strftime("%d/%m/%Y %H:%M"))
        date_item.setForeground(QColor(C['txt_sec']))
        self.table.setItem(row, 1, date_item)

        client_item = QTableWidgetItem(sale.get('client_name', 'Anonyme'))
        self.table.setItem(row, 2, client_item)

        sale_details = self.db.get_sale_by_id(sale['id'])
        items_count = len(sale_details['items']) if sale_details else 0
        items_item = QTableWidgetItem(f"{items_count} article(s)")
        items_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        items_item.setForeground(QColor(C['txt_sec']))
        self.table.setItem(row, 3, items_item)

        subtotal_item = QTableWidgetItem(fmt_da(sale['subtotal']))
        subtotal_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        subtotal_item.setForeground(QColor(C['txt_sec']))
        self.table.setItem(row, 4, subtotal_item)

        tax_item = QTableWidgetItem(fmt_da(sale['tax_amount']))
        tax_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        tax_item.setForeground(QColor(C['yellow']))
        self.table.setItem(row, 5, tax_item)

        total_item = QTableWidgetItem(fmt_da(sale['total']))
        total_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        total_item.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        total_item.setForeground(QColor(C['teal']))
        self.table.setItem(row, 6, total_item)

    def apply_filters(self):
        period = self.period_combo.currentText()
        search_text = self.search_input.text().lower().strip()
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
        else:
            self.table.setRowCount(0)
            for sale in self.db.get_all_sales():
                if self._matches_search_starts_with(sale, search_text):
                    self.add_sale_to_table(sale)
            return
        self.table.setRowCount(0)
        for sale in self.db.get_sales_by_date_range(start_date, end_date):
            if self._matches_search_starts_with(sale, search_text):
                self.add_sale_to_table(sale)

    def _matches_search_starts_with(self, sale, search_text):
        if not search_text:
            return True
        if sale['invoice_number'].lower().startswith(search_text):
            return True
        if sale.get('client_name', 'anonyme').lower().startswith(search_text):
            return True
        return False

    def view_sale_details(self):
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

    def import_dat_file(self):
        import os
        from urllib.parse import unquote_plus
        file_paths, _ = QFileDialog.getOpenFileNames(
            self, "Importer des factures (.dat)", "",
            "Fichiers DAT (*.dat);;Tous les fichiers (*.*)")
        if not file_paths:
            return
        imported = 0
        errors = []
        for file_path in file_paths:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    raw = f.read().strip()
                params = {}
                for part in raw.split('&'):
                    if '=' in part:
                        k, _, v = part.partition('=')
                        params[k] = unquote_plus(v)
                client_name = params.get('Customer', 'Client Anonyme').strip() or 'Client Anonyme'
                date_str = params.get('Date', '').strip()
                if not date_str:
                    date_str = datetime.now().strftime('%Y-%m-%d')
                if len(date_str) == 10:
                    date_str = date_str + " 00:00:00"
                tax_rate = float(params.get('TaxRate', 0) or 0)
                notes = params.get('Notes', '')
                payment_terms = params.get('PaymentTerms', '1')
                pay_map = {'1': 'cash', '2': 'credit', '3': 'card', '4': 'transfer'}
                payment_method = pay_map.get(str(payment_terms), 'cash')
                clients = self.db.search_clients(client_name)
                client_id = clients[0]['id'] if clients else self.db.add_client(client_name)
                if not client_id:
                    raise ValueError(f"Impossible de créer le client '{client_name}'")
                item_count = int(params.get('ItemCount', 1) or 1)
                items_for_db = []
                for i in range(1, item_count + 1):
                    name = params.get(f'Item{i}Code', '').strip()
                    desc = params.get(f'Item{i}Name', '').strip()
                    code = params.get(f'Item{i}Code', '').strip()
                    qty_raw = params.get(f'Item{i}Qty', '1')
                    price_raw = params.get(f'Item{i}UnitValue', '0')
                    disc_raw = params.get(f'Item{i}Discount', '0')
                    try:
                        qty = float(qty_raw or 1)
                        price = float(price_raw or 0) / 100
                        discount = float(disc_raw or 0)
                    except:
                        qty, price, discount = 1.0, 0.0, 0.0
                    product_id = None
                    if code:
                        results = self.db.search_products(code)
                        if results:
                            product_id = results[0]['id']
                    if not product_id and name:
                        results = self.db.search_products(name)
                        if results:
                            product_id = results[0]['id']
                    if not product_id:
                        product_id = self.db.add_product(
                            name=name or desc or f'Article {i}',
                            description=desc, selling_price=price,
                            purchase_price=price, stock_quantity=0, barcode=code)
                    if not product_id:
                        raise ValueError(f"Impossible de créer le produit '{name or desc}'")
                    items_for_db.append({
                        'product_id': product_id, 'quantity': qty,
                        'unit_price': price, 'discount': discount})
                base_name = os.path.splitext(os.path.basename(file_path))[0]
                invoice_number = f"IMP-{base_name}-{datetime.now().strftime('%H%M%S')}"
                sale_id = self.db.create_sale(
                    invoice_number=invoice_number, client_id=client_id,
                    items=items_for_db, payment_method=payment_method,
                    tax_rate=tax_rate, notes=notes, sale_date=date_str)
                if not sale_id:
                    raise ValueError("La vente n'a pas pu être enregistrée")
                imported += 1
            except Exception as e:
                errors.append(f"• {os.path.basename(file_path)}\n  → {str(e)}")
        self.load_sales()
        if errors:
            msg = f"✅ {imported} facture(s) importée(s)."
            msg += f"\n\n⚠️ Erreurs ({len(errors)}) :\n" + "\n".join(errors)
            QMessageBox.warning(self, "Import terminé avec avertissements", msg)
        else:
            QMessageBox.information(self, "✅ Import réussi",
                f"{imported} facture(s) importée(s) avec succès!")


from currency import fmt_da, fmt, currency_manager