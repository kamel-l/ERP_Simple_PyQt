"""
Module de gestion des paiements
Gère les différents modes de paiement et le suivi des encaissements
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QRadioButton, QButtonGroup, QLineEdit, QFrame, QTextEdit,
    QSpinBox, QDoubleSpinBox, QMessageBox, QGridLayout
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt, pyqtSignal
from datetime import datetime
from styles import COLORS, BUTTON_STYLES, INPUT_STYLE, DIALOG_STYLE, RADIO_STYLE


class PaymentDialog(QDialog):
    """Dialogue pour enregistrer un paiement"""
    
    payment_completed = pyqtSignal(dict)  # Signal émis quand le paiement est validé
    
    def __init__(self, total_amount, invoice_number=""):
        super().__init__()
        
        self.total_amount = total_amount
        self.invoice_number = invoice_number
        
        # Initialiser les attributs avant de les utiliser
        self.details_layout = None
        self.cash_received = None
        self.change_label = None
        self.card_transaction = None
        self.card_type = None
        self.check_number = None
        self.check_bank = None
        self.transfer_ref = None
        self.mobile_operator = None
        self.mobile_transaction = None
        self.credit_due_date = None
        self.notes = None
        self.payment_group = None
        
        self.setWindowTitle("💳 Encaissement")
        self.setMinimumWidth(650)
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {COLORS['bg_medium']};
            }}
            {DIALOG_STYLE}
        """)
        
        self.setup_ui()
    
    def setup_ui(self):
        """Configure l'interface"""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(25, 25, 25, 25)
        
        # En-tête
        header = self.create_header()
        layout.addWidget(header)
        
        # Montant à payer
        amount_display = self.create_amount_display()
        layout.addWidget(amount_display)
        
        # Sélection du mode de paiement
        payment_methods = self.create_payment_methods()
        layout.addWidget(payment_methods)
        
        # Zone de détails de paiement
        self.details_frame = QFrame()
        self.details_frame.setObjectName("detailsFrame")
        self.details_frame.setStyleSheet(f"""
            QFrame#detailsFrame {{
                background: {COLORS['bg_card']};
                border-radius: 8px;
                padding: 15px;
            }}
        """)
        self.details_layout = QVBoxLayout(self.details_frame)
        self.details_layout.setContentsMargins(10, 10, 10, 10)
        layout.addWidget(self.details_frame)
        
        # Note/Commentaire
        notes_section = self.create_notes_section()
        layout.addWidget(notes_section)
        
        # Boutons d'action
        buttons = self.create_action_buttons()
        layout.addLayout(buttons)
        
        # Initialiser avec le mode de paiement par défaut (Espèces)
        if self.payment_group and self.payment_group.buttons():
            self.payment_group.buttons()[0].setChecked(True)
            self.on_payment_method_changed(self.payment_group.buttons()[0], True)
    
    def create_header(self):
        """Crée l'en-tête"""
        header = QFrame()
        header.setObjectName("header")
        header.setStyleSheet(f"""
            QFrame#header {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {COLORS['success']}, stop:1 {COLORS['primary']});
                border-radius: 10px;
                padding: 20px;
            }}
        """)
        header_layout = QVBoxLayout(header)
        
        title = QLabel("💳 Encaissement de la Facture")
        title.setObjectName("title")
        title.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        title.setStyleSheet("color: white; border: none;")
        header_layout.addWidget(title)
        
        if self.invoice_number:
            invoice_label = QLabel(f"Facture N° {self.invoice_number}")
            invoice_label.setObjectName("subtitle")
            invoice_label.setFont(QFont("Segoe UI", 12))
            invoice_label.setStyleSheet("color: rgba(255, 255, 255, 0.9); border: none;")
            header_layout.addWidget(invoice_label)
        
        return header
    
    def create_amount_display(self):
        """Affiche le montant total"""
        frame = QFrame()
        frame.setObjectName("amountFrame")
        frame.setStyleSheet(f"""
            QFrame#amountFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {COLORS['bg_card']}, stop:1 #242424);
                border-radius: 12px;
                border: 3px solid {COLORS['success']};
                padding: 20px;
            }}
        """)
        
        frame_layout = QVBoxLayout(frame)
        
        label = QLabel("MONTANT À ENCAISSER")
        label.setFont(QFont("Segoe UI", 12))
        label.setStyleSheet(f"color: {COLORS['text_tertiary']}; border: none;")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        frame_layout.addWidget(label)
        
        amount = QLabel(f"{self.total_amount:,.2f} DA")
        amount.setFont(QFont("Segoe UI", 36, QFont.Weight.Bold))
        amount.setStyleSheet(f"color: {COLORS['success']}; border: none;")
        amount.setAlignment(Qt.AlignmentFlag.AlignCenter)
        frame_layout.addWidget(amount)
        
        return frame
    
    def create_payment_methods(self):
        """Crée les options de paiement"""
        frame = QFrame()
        frame.setObjectName("paymentFrame")
        frame.setStyleSheet(f"""
            QFrame#paymentFrame {{
                background: {COLORS['bg_card']};
                border-radius: 10px;
                padding: 20px;
            }}
        """)
        
        frame_layout = QVBoxLayout(frame)
        
        title = QLabel("💰 Mode de Paiement")
        title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {COLORS['text_primary']}; border: none;")
        frame_layout.addWidget(title)
        
        # Groupe de boutons radio
        self.payment_group = QButtonGroup()
        methods_layout = QGridLayout()
        
        # Définir les méthodes de paiement
        payment_methods = [
            ("💵 Espèces", "cash", 0, 0),
            ("💳 Carte Bancaire", "card", 0, 1),
            ("📝 Chèque", "check", 1, 0),
            ("🏦 Virement", "transfer", 1, 1),
            ("📱 Mobile Money", "mobile", 2, 0),
            ("🔄 Crédit", "credit", 2, 1),
        ]
        
        for label, value, row, col in payment_methods:
            radio = QRadioButton(label)
            radio.setStyleSheet(RADIO_STYLE)
            radio.setProperty("method", value)
            radio.toggled.connect(lambda checked, r=radio: self.on_payment_method_changed(r, checked))
            self.payment_group.addButton(radio)
            methods_layout.addWidget(radio, row, col)
        
        frame_layout.addLayout(methods_layout)
        
        return frame
    
    def on_payment_method_changed(self, radio, checked):
        """Appelé quand le mode de paiement change"""
        if not checked:
            return
        
        method = radio.property("method")
        
        # Effacer les détails précédents
        if self.details_layout:
            while self.details_layout.count():
                child = self.details_layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
        
        # Ajouter les détails selon la méthode
        if method == "cash":
            self.add_cash_details()
        elif method == "card":
            self.add_card_details()
        elif method == "check":
            self.add_check_details()
        elif method == "transfer":
            self.add_transfer_details()
        elif method == "mobile":
            self.add_mobile_details()
        elif method == "credit":
            self.add_credit_details()
    
    def add_cash_details(self):
        """Détails pour paiement en espèces"""
        container = QFrame()
        container.setStyleSheet(f"""
            QFrame {{
                background: {COLORS['bg_light']};
                border-radius: 8px;
                padding: 15px;
            }}
        """)
        layout = QVBoxLayout(container)
        
        # Montant reçu
        received_layout = QHBoxLayout()
        received_label = QLabel("💵 Montant reçu:")
        received_label.setStyleSheet(f"color: {COLORS['text_primary']}; border: none;")
        
        self.cash_received = QDoubleSpinBox()
        self.cash_received.setMinimum(0)
        self.cash_received.setMaximum(999999999)
        self.cash_received.setDecimals(2)
        self.cash_received.setValue(self.total_amount)
        self.cash_received.setStyleSheet(INPUT_STYLE)
        self.cash_received.setMinimumHeight(45)
        self.cash_received.setSuffix(" DA")
        self.cash_received.valueChanged.connect(self.calculate_change)
        
        received_layout.addWidget(received_label)
        received_layout.addWidget(self.cash_received)
        layout.addLayout(received_layout)
        
        # Monnaie à rendre
        self.change_label = QLabel("💸 Monnaie à rendre: 0.00 DA")
        self.change_label.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        self.change_label.setStyleSheet(f"color: {COLORS['warning']}; border: none; padding: 10px;")
        layout.addWidget(self.change_label)
        
        if self.details_layout:
            self.details_layout.addWidget(container)
        self.calculate_change()
    
    def calculate_change(self):
        """Calcule la monnaie à rendre"""
        if hasattr(self, 'cash_received') and hasattr(self, 'change_label') and self.cash_received:
            received = self.cash_received.value()
            change = received - self.total_amount
            
            if change >= 0:
                self.change_label.setText(f"💸 Monnaie à rendre: {change:,.2f} DA")
                self.change_label.setStyleSheet(f"color: {COLORS['success']}; border: none; padding: 10px; font-size: 14px; font-weight: bold;")
            else:
                self.change_label.setText(f"⚠️ Montant insuffisant: {abs(change):,.2f} DA manquants")
                self.change_label.setStyleSheet(f"color: {COLORS['danger']}; border: none; padding: 10px; font-size: 14px; font-weight: bold;")
    
    def add_card_details(self):
        """Détails pour paiement par carte"""
        container = QFrame()
        container.setStyleSheet(f"""
            QFrame {{
                background: {COLORS['bg_light']};
                border-radius: 8px;
                padding: 15px;
            }}
        """)
        layout = QVBoxLayout(container)
        
        # Numéro de transaction
        trans_layout = QHBoxLayout()
        trans_label = QLabel("🔢 N° Transaction:")
        trans_label.setStyleSheet(f"color: {COLORS['text_primary']}; border: none;")
        self.card_transaction = QLineEdit()
        self.card_transaction.setPlaceholderText("Ex: 123456789")
        self.card_transaction.setStyleSheet(INPUT_STYLE)
        trans_layout.addWidget(trans_label)
        trans_layout.addWidget(self.card_transaction)
        layout.addLayout(trans_layout)
        
        # Type de carte
        type_layout = QHBoxLayout()
        type_label = QLabel("💳 Type de carte:")
        type_label.setStyleSheet(f"color: {COLORS['text_primary']}; border: none;")
        self.card_type = QLineEdit()
        self.card_type.setPlaceholderText("Ex: Visa, MasterCard, CIB")
        self.card_type.setStyleSheet(INPUT_STYLE)
        type_layout.addWidget(type_label)
        type_layout.addWidget(self.card_type)
        layout.addLayout(type_layout)
        
        if self.details_layout:
            self.details_layout.addWidget(container)
    
    def add_check_details(self):
        """Détails pour paiement par chèque"""
        container = QFrame()
        container.setStyleSheet(f"""
            QFrame {{
                background: {COLORS['bg_light']};
                border-radius: 8px;
                padding: 15px;
            }}
        """)
        layout = QVBoxLayout(container)
        
        # Numéro de chèque
        check_layout = QHBoxLayout()
        check_label = QLabel("📝 N° Chèque:")
        check_label.setStyleSheet(f"color: {COLORS['text_primary']}; border: none;")
        self.check_number = QLineEdit()
        self.check_number.setPlaceholderText("Numéro du chèque")
        self.check_number.setStyleSheet(INPUT_STYLE)
        check_layout.addWidget(check_label)
        check_layout.addWidget(self.check_number)
        layout.addLayout(check_layout)
        
        # Banque
        bank_layout = QHBoxLayout()
        bank_label = QLabel("🏦 Banque:")
        bank_label.setStyleSheet(f"color: {COLORS['text_primary']}; border: none;")
        self.check_bank = QLineEdit()
        self.check_bank.setPlaceholderText("Nom de la banque")
        self.check_bank.setStyleSheet(INPUT_STYLE)
        bank_layout.addWidget(bank_label)
        bank_layout.addWidget(self.check_bank)
        layout.addLayout(bank_layout)
        
        if self.details_layout:
            self.details_layout.addWidget(container)
    
    def add_transfer_details(self):
        """Détails pour virement bancaire"""
        container = QFrame()
        container.setStyleSheet(f"""
            QFrame {{
                background: {COLORS['bg_light']};
                border-radius: 8px;
                padding: 15px;
            }}
        """)
        layout = QVBoxLayout(container)
        
        # Référence
        ref_layout = QHBoxLayout()
        ref_label = QLabel("🔢 Référence:")
        ref_label.setStyleSheet(f"color: {COLORS['text_primary']}; border: none;")
        self.transfer_ref = QLineEdit()
        self.transfer_ref.setPlaceholderText("Référence du virement")
        self.transfer_ref.setStyleSheet(INPUT_STYLE)
        ref_layout.addWidget(ref_label)
        ref_layout.addWidget(self.transfer_ref)
        layout.addLayout(ref_layout)
        
        if self.details_layout:
            self.details_layout.addWidget(container)
    
    def add_mobile_details(self):
        """Détails pour paiement mobile"""
        container = QFrame()
        container.setStyleSheet(f"""
            QFrame {{
                background: {COLORS['bg_light']};
                border-radius: 8px;
                padding: 15px;
            }}
        """)
        layout = QVBoxLayout(container)
        
        # Opérateur
        op_layout = QHBoxLayout()
        op_label = QLabel("📱 Opérateur:")
        op_label.setStyleSheet(f"color: {COLORS['text_primary']}; border: none;")
        self.mobile_operator = QLineEdit()
        self.mobile_operator.setPlaceholderText("Ex: BaridiMob, CCP, Poste")
        self.mobile_operator.setStyleSheet(INPUT_STYLE)
        op_layout.addWidget(op_label)
        op_layout.addWidget(self.mobile_operator)
        layout.addLayout(op_layout)
        
        # Numéro de transaction
        trans_layout = QHBoxLayout()
        trans_label = QLabel("🔢 N° Transaction:")
        trans_label.setStyleSheet(f"color: {COLORS['text_primary']}; border: none;")
        self.mobile_transaction = QLineEdit()
        self.mobile_transaction.setPlaceholderText("Numéro de transaction")
        self.mobile_transaction.setStyleSheet(INPUT_STYLE)
        trans_layout.addWidget(trans_label)
        trans_layout.addWidget(self.mobile_transaction)
        layout.addLayout(trans_layout)
        
        if self.details_layout:
            self.details_layout.addWidget(container)
    
    def add_credit_details(self):
        """Détails pour paiement à crédit"""
        container = QFrame()
        container.setStyleSheet(f"""
            QFrame {{
                background: {COLORS['bg_light']};
                border-radius: 8px;
                padding: 15px;
            }}
        """)
        layout = QVBoxLayout(container)
        
        warning = QLabel("⚠️ Paiement à crédit - Montant à recouvrer ultérieurement")
        warning.setStyleSheet(f"color: {COLORS['warning']}; border: none; padding: 10px; font-weight: bold;")
        layout.addWidget(warning)
        
        # Date d'échéance
        due_layout = QHBoxLayout()
        due_label = QLabel("📅 Date d'échéance:")
        due_label.setStyleSheet(f"color: {COLORS['text_primary']}; border: none;")
        self.credit_due_date = QLineEdit()
        self.credit_due_date.setPlaceholderText("JJ/MM/AAAA")
        self.credit_due_date.setStyleSheet(INPUT_STYLE)
        due_layout.addWidget(due_label)
        due_layout.addWidget(self.credit_due_date)
        layout.addLayout(due_layout)
        
        if self.details_layout:
            self.details_layout.addWidget(container)
    
    def create_notes_section(self):
        """Crée la section notes"""
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background: {COLORS['bg_card']};
                border-radius: 10px;
                padding: 15px;
            }}
        """)
        
        layout = QVBoxLayout(frame)
        
        label = QLabel("📝 Notes / Commentaires (optionnel)")
        label.setStyleSheet(f"color: {COLORS['text_primary']}; border: none; font-weight: bold;")
        layout.addWidget(label)
        
        self.notes = QTextEdit()
        self.notes.setPlaceholderText("Ajoutez des notes sur ce paiement...")
        self.notes.setMaximumHeight(80)
        self.notes.setStyleSheet(INPUT_STYLE)
        layout.addWidget(self.notes)
        
        return frame
    
    def create_action_buttons(self):
        """Crée les boutons d'action"""
        layout = QHBoxLayout()
        layout.setSpacing(10)
        
        cancel_btn = QPushButton("❌ Annuler")
        cancel_btn.setStyleSheet(BUTTON_STYLES['secondary'])
        cancel_btn.setMinimumHeight(50)
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        
        validate_btn = QPushButton("✅ Valider l'Encaissement")
        validate_btn.setStyleSheet(BUTTON_STYLES['success'])
        validate_btn.setMinimumHeight(50)
        validate_btn.setFixedWidth(250)
        validate_btn.clicked.connect(self.validate_payment)
        validate_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        
        layout.addWidget(cancel_btn)
        layout.addStretch()
        layout.addWidget(validate_btn)
        
        return layout
    
    def validate_payment(self):
        """Valide et enregistre le paiement"""
        # Récupérer la méthode sélectionnée
        method_button = self.payment_group.checkedButton()
        if not method_button:
            QMessageBox.warning(self, "Mode de paiement", 
                              "Veuillez sélectionner un mode de paiement !")
            return
        
        payment_method = method_button.property("method")
        
        # Validation spécifique selon la méthode
        if payment_method == "cash" and self.cash_received:
            if self.cash_received.value() < self.total_amount:
                QMessageBox.warning(self, "Montant insuffisant",
                                  "Le montant reçu est inférieur au total !")
                return
        
        # Créer le dictionnaire de paiement
        payment_data = {
            'method': payment_method,
            'amount': self.total_amount,
            'date': datetime.now().strftime('%d/%m/%Y %H:%M'),
            'invoice_number': self.invoice_number,
            'notes': self.notes.toPlainText() if self.notes else "",
            'details': {}
        }
        
        # Ajouter les détails spécifiques
        if payment_method == "cash" and self.cash_received:
            payment_data['details']['received'] = self.cash_received.value()
            payment_data['details']['change'] = self.cash_received.value() - self.total_amount
        elif payment_method == "card":
            if self.card_transaction:
                payment_data['details']['transaction'] = self.card_transaction.text()
            if self.card_type:
                payment_data['details']['card_type'] = self.card_type.text()
        elif payment_method == "check":
            if self.check_number:
                payment_data['details']['check_number'] = self.check_number.text()
            if self.check_bank:
                payment_data['details']['bank'] = self.check_bank.text()
        elif payment_method == "transfer":
            if self.transfer_ref:
                payment_data['details']['reference'] = self.transfer_ref.text()
        elif payment_method == "mobile":
            if self.mobile_operator:
                payment_data['details']['operator'] = self.mobile_operator.text()
            if self.mobile_transaction:
                payment_data['details']['transaction'] = self.mobile_transaction.text()
        elif payment_method == "credit":
            if self.credit_due_date:
                payment_data['details']['due_date'] = self.credit_due_date.text()
        
        # Émettre le signal
        self.payment_completed.emit(payment_data)
        
        # Message de confirmation
        QMessageBox.information(self, "Paiement enregistré",
                              f"✅ Paiement de {self.total_amount:,.2f} DA enregistré avec succès !")
        
        self.accept()


# Fonction utilitaire
def show_payment_dialog(total_amount, invoice_number="", parent=None):
    """
    Affiche le dialogue de paiement
    
    Returns:
        payment_data si validé, None si annulé
    """
    dialog = PaymentDialog(total_amount, invoice_number)
    if parent:
        dialog.setParent(parent)
    
    payment_data = None
    
    def on_payment(data):
        nonlocal payment_data
        payment_data = data
    
    dialog.payment_completed.connect(on_payment)
    
    if dialog.exec():
        return payment_data
    return None