"""
Module de gestion des retours et avoirs (Proposition 5)
Permet d'annuler partiellement ou totalement une vente
et de remettre le stock en place automatiquement.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QDialog, QTextEdit, QMessageBox, QLineEdit, QScrollArea,
    QSpinBox, QDoubleSpinBox, QComboBox, QFormLayout
)
from currency import fmt_da, fmt, currency_manager
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtCore import Qt, pyqtSignal
from db_manager import get_database
from styles import COLORS, BUTTON_STYLES, INPUT_STYLE, TABLE_STYLE
from datetime import datetime


# ─────────────────────────────────────────────────────────────────────────────
#  Dialogue de création d'un avoir
# ─────────────────────────────────────────────────────────────────────────────

class ReturnDialog(QDialog):
    """
    Dialogue permettant de créer un avoir pour une vente existante.
    L'utilisateur choisit les articles et les quantités à retourner.
    """
    return_created = pyqtSignal(dict)   # Émet les données de l'avoir créé

    def __init__(self, sale: dict, parent=None):
        super().__init__(parent)
        self.sale = sale
        self.db   = get_database()
        self.setWindowTitle(f"📦 Créer un Avoir — Facture {sale.get('invoice_number','')}")
        self.setMinimumWidth(700)
        self.setMinimumHeight(500)
        self.setStyleSheet(f"QDialog {{ background: {COLORS['bg_medium']}; }}")

        layout = QVBoxLayout(self)
        layout.setSpacing(18)
        layout.setContentsMargins(24, 24, 24, 24)

        # ── En-tête ──────────────────────────────────────────────────
        hdr = QHBoxLayout()
        title_lbl = QLabel(f"📦 Retour / Avoir — Facture {sale['invoice_number']}")
        title_lbl.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        title_lbl.setStyleSheet(f"color: {COLORS['text_primary']};")
        hdr.addWidget(title_lbl)
        hdr.addStretch()

        info = QLabel(
            f"Client : {sale.get('client_name','Anonyme')}  ·  "
            f"Total : {fmt_da(float(sale.get('total',0)), 0)}"
        )
        info.setFont(QFont("Segoe UI", 10))
        info.setStyleSheet(f"color: {COLORS['text_tertiary']};")
        hdr.addWidget(info)
        layout.addLayout(hdr)

        # ── Séparateur ───────────────────────────────────────────────
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(f"background: {COLORS['border']}; border: none;")
        layout.addWidget(sep)

        # ── Tableau des articles ─────────────────────────────────────
        lbl = QLabel("Sélectionnez les articles à retourner et les quantités :")
        lbl.setFont(QFont("Segoe UI", 11))
        lbl.setStyleSheet(f"color: {COLORS['text_secondary']};")
        layout.addWidget(lbl)

        self.items_table = QTableWidget(0, 5)
        self.items_table.setHorizontalHeaderLabels(
            ["Article", "Prix Unit.", "Qté vendue", "Qté à retourner", "Remboursement"]
        )
        self.items_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.items_table.verticalHeader().setVisible(False)
        self.items_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.items_table.setAlternatingRowColors(True)
        self.items_table.setStyleSheet(TABLE_STYLE)
        self.items_table.setMinimumHeight(200)
        layout.addWidget(self.items_table)

        self._spinboxes = []
        self._populate_items()

        # ── Motif du retour ──────────────────────────────────────────
        form = QFormLayout()
        form.setSpacing(10)

        self.motif_combo = QComboBox()
        self.motif_combo.addItems([
            "Produit défectueux",
            "Erreur de commande",
            "Produit non conforme",
            "Client insatisfait",
            "Autre",
        ])
        self.motif_combo.setStyleSheet(INPUT_STYLE)
        self.motif_combo.setMinimumHeight(38)
        form.addRow("Motif :", self.motif_combo)

        self.notes_edit = QTextEdit()
        self.notes_edit.setPlaceholderText("Notes complémentaires (optionnel)...")
        self.notes_edit.setMaximumHeight(70)
        self.notes_edit.setStyleSheet(f"""
            QTextEdit {{
                background: {COLORS['bg_dark']};
                color: {COLORS['text_primary']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                padding: 8px;
                font-size: 12px;
            }}
        """)
        form.addRow("Notes :", self.notes_edit)
        layout.addLayout(form)

        # ── Résumé du montant ────────────────────────────────────────
        self._total_lbl = QLabel("Montant à rembourser : 0 DA")
        self._total_lbl.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        self._total_lbl.setStyleSheet(f"color: #10B981;")
        self._total_lbl.setAlignment(Qt.AlignmentFlag.AlignRight)
        layout.addWidget(self._total_lbl)

        # ── Boutons ──────────────────────────────────────────────────
        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)

        cancel_btn = QPushButton("❌ Annuler")
        cancel_btn.setStyleSheet(BUTTON_STYLES['secondary'])
        cancel_btn.setMinimumHeight(42)
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)

        confirm_btn = QPushButton("✅ Créer l'Avoir")
        confirm_btn.setStyleSheet(BUTTON_STYLES['success'])
        confirm_btn.setMinimumHeight(42)
        confirm_btn.clicked.connect(self._create_return)
        confirm_btn.setCursor(Qt.CursorShape.PointingHandCursor)

        btn_row.addStretch()
        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(confirm_btn)
        layout.addLayout(btn_row)

    def _populate_items(self):
        """Remplit le tableau avec les articles de la vente originale."""
        items = self.sale.get('items', [])
        self.items_table.setRowCount(len(items))

        for row, item in enumerate(items):
            # Priorité : nom du produit, sinon référence/barcode, sinon 'N/A'
            name = (
                item.get('product_name')
                or item.get('product_reference')
                or item.get('reference')
                or 'N/A'
            )
            price = float(item.get('unit_price', 0))
            qty   = int(item.get('quantity', 0))

            self.items_table.setItem(row, 0, QTableWidgetItem(name))
            self.items_table.setItem(row, 1, QTableWidgetItem(f"{price:,.2f} DA"))
            self.items_table.setItem(row, 2, QTableWidgetItem(str(qty)))

            # SpinBox pour la quantité à retourner
            spin = QSpinBox()
            spin.setMinimum(0)
            spin.setMaximum(qty)
            spin.setValue(qty)
            spin.setStyleSheet("""
                QSpinBox {
                    background: #0F1117; color: #E2E8F0;
                    border: 1px solid rgba(255,255,255,0.15);
                    border-radius: 6px; padding: 4px 8px;
                }
            """)
            spin.valueChanged.connect(self._update_total)
            self.items_table.setCellWidget(row, 3, spin)
            self._spinboxes.append((spin, price, item.get('product_id')))

            total_item = QTableWidgetItem(f"{price * qty:,.2f} DA")
            total_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            total_item.setForeground(QColor("#10B981"))
            self.items_table.setItem(row, 4, total_item)

        self._update_total()

    def _update_total(self):
        """Recalcule et affiche le montant total du remboursement."""
        total = sum(spin.value() * price for spin, price, _ in self._spinboxes)
        self._total_lbl.setText(f"Montant à rembourser : {total:,.2f} DA")

        # Mettre à jour la colonne remboursement
        for row, (spin, price, _) in enumerate(self._spinboxes):
            item = self.items_table.item(row, 4)
            if item:
                item.setText(f"{spin.value() * price:,.2f} DA")

    def _create_return(self):
        """Valide et enregistre l'avoir en base de données."""
        return_items = []
        for spin, price, product_id in self._spinboxes:
            if spin.value() > 0:
                return_items.append({
                    'product_id': product_id,
                    'quantity':   spin.value(),
                    'unit_price': price,
                    'total':      spin.value() * price,
                })

        if not return_items:
            QMessageBox.warning(self, "Attention",
                "Veuillez sélectionner au moins un article à retourner.")
            return

        total = sum(i['total'] for i in return_items)
        motif = self.motif_combo.currentText()
        notes = self.notes_edit.toPlainText().strip()

        # Confirmer
        reply = QMessageBox.question(
            self, "Confirmer l'avoir",
            f"Créer un avoir de {total:,.2f} DA ?\n\n"
            f"Motif : {motif}\n"
            f"Le stock sera automatiquement remis en place.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        # Enregistrer en base
        return_data = self.db.create_return(
            original_sale_id=self.sale['id'],
            items=return_items,
            motif=motif,
            notes=notes
        )

        if return_data:
            QMessageBox.information(
                self, "✅ Avoir créé",
                f"L'avoir a été créé avec succès.\n\n"
                f"Avoir N° : {return_data.get('return_number','—')}\n"
                f"Montant remboursé : {total:,.2f} DA\n\n"
                f"Le stock a été remis à jour automatiquement."
            )
            self.return_created.emit(return_data)
            self.accept()
        else:
            QMessageBox.critical(self, "Erreur",
                "Impossible de créer l'avoir. Vérifiez la base de données.")


# ─────────────────────────────────────────────────────────────────────────────
#  Page Historique des Avoirs
# ─────────────────────────────────────────────────────────────────────────────

class ReturnsPage(QWidget):
    """Page listant tous les avoirs créés."""

    def __init__(self):
        super().__init__()
        self.db = get_database()

        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(24, 24, 24, 24)

        # En-tête
        hdr = QHBoxLayout()
        col = QVBoxLayout()
        col.setSpacing(4)
        title = QLabel("📦 Retours & Avoirs")
        title.setFont(QFont("Segoe UI", 26, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {COLORS['text_primary']};")
        col.addWidget(title)
        sub = QLabel("Historique de tous les avoirs et retours produits")
        sub.setFont(QFont("Segoe UI", 12))
        sub.setStyleSheet(f"color: {COLORS['text_tertiary']};")
        col.addWidget(sub)
        hdr.addLayout(col)
        hdr.addStretch()

        refresh_btn = QPushButton("🔄 Actualiser")
        refresh_btn.setStyleSheet(BUTTON_STYLES['secondary'])
        refresh_btn.setMinimumHeight(40)
        refresh_btn.setFixedWidth(140)
        refresh_btn.clicked.connect(self.load_returns)
        refresh_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        hdr.addWidget(refresh_btn)
        layout.addLayout(hdr)

        # Carte résumé
        self._stats_row = QHBoxLayout()
        self._stats_row.setSpacing(14)
        layout.addLayout(self._stats_row)

        # Tableau des avoirs
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background: {COLORS['bg_card']};
                border-radius: 12px;
                border: 1px solid {COLORS['border']};
            }}
        """)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(16, 16, 16, 16)

        tbl_title = QLabel("📋 Liste des Avoirs")
        tbl_title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        tbl_title.setStyleSheet(f"color: {COLORS['text_primary']}; border: none;")
        card_layout.addWidget(tbl_title)

        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels([
            "N° Avoir", "Facture d'origine", "Client",
            "Motif", "Montant remboursé", "Date"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setStyleSheet(TABLE_STYLE)
        self.table.setMinimumHeight(300)
        card_layout.addWidget(self.table)
        layout.addWidget(card)

        self.load_returns()

    def _make_stat_card(self, icon, label, value, color):
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background: {COLORS['bg_card']};
                border-radius: 10px;
                border: 1px solid {COLORS['border']};
            }}
        """)
        card.setFixedHeight(80)
        lay = QVBoxLayout(card)
        lay.setContentsMargins(16, 10, 16, 10)
        lay.setSpacing(2)
        top = QLabel(f"{icon}  {label}")
        top.setFont(QFont("Segoe UI", 10))
        top.setStyleSheet(f"color: {COLORS['text_tertiary']}; border: none;")
        lay.addWidget(top)
        val_lbl = QLabel(value)
        val_lbl.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        val_lbl.setStyleSheet(f"color: {color}; border: none;")
        lay.addWidget(val_lbl)
        return card

    def load_returns(self):
        """Charge et affiche tous les avoirs."""
        # Nettoyer les cartes stats
        while self._stats_row.count():
            item = self._stats_row.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        returns = self.db.get_all_returns() or []

        # Cartes stats
        total_montant = sum(float(r.get('total', 0)) for r in returns)
        self._stats_row.addWidget(self._make_stat_card(
            "📦", "Total Avoirs", str(len(returns)), COLORS['primary']))
        self._stats_row.addWidget(self._make_stat_card(
            "💰", "Montant Total Remboursé",
            fmt_da(total_montant, 0), "#EF4444"))
        self._stats_row.addStretch()

        # Remplir le tableau
        self.table.setRowCount(len(returns))
        for row, ret in enumerate(returns):
            try:
                date_str = datetime.fromisoformat(
                    ret.get('return_date', '')).strftime("%d/%m/%Y %H:%M")
            except Exception:
                date_str = str(ret.get('return_date', '—'))

            cells = [
                (ret.get('return_number', '—'),   "#F1F5F9"),
                (ret.get('invoice_number', '—'),   COLORS['text_secondary']),
                (ret.get('client_name', 'Anonyme'), COLORS['text_secondary']),
                (ret.get('motif', '—'),              COLORS['text_tertiary']),
                (f"{float(ret.get('total',0)):,.2f} DA", "#EF4444"),
                (date_str,                           COLORS['text_tertiary']),
            ]
            for col, (val, color) in enumerate(cells):
                item = QTableWidgetItem(str(val))
                item.setForeground(QColor(color))
                item.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
                self.table.setItem(row, col, item)
            self.table.setRowHeight(row, 40)