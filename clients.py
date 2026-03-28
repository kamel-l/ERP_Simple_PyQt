from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QHeaderView, QPushButton, QHBoxLayout, QLineEdit, QDialog, QFormLayout,
    QFrame, QMessageBox, QTabWidget, QScrollArea, QGridLayout, QSizePolicy,
    QSpacerItem, QProgressBar, QTextEdit, QComboBox, QApplication
)
from PyQt6.QtGui import QFont, QColor, QPainter, QPainterPath
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from auth import session
from styles import COLORS, BUTTON_STYLES, INPUT_STYLE, TABLE_STYLE
from db_manager import get_database
from currency import fmt_da, fmt, currency_manager  # IMPORT DE LA FONCTION DE FORMATAGE

# ------------------ DIALOG POUR AJOUTER / MODIFIER CLIENT ------------------
class ClientDialog(QDialog):
    def __init__(self, name="", phone="", email="", address="", client_id=None):
        super().__init__()

        self.client_id = client_id
        self.setWindowTitle("📝 Détails du Client") 
        self.setMinimumWidth(500)
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {COLORS['BG_CARD']};
            }}
            QLabel {{
                color: {COLORS['text_primary']};
                font-size: 13px;
            }}
            {INPUT_STYLE}
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(25, 25, 25, 25)

        # Titre
        title_text = "Modifier le Client" if client_id else "Nouveau Client"
        title = QLabel(title_text)
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {COLORS['text_primary']}; margin-bottom: 10px;")
        main_layout.addWidget(title)

        # Formulaire
        form = QFormLayout()
        form.setSpacing(15)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self.name_edit = QLineEdit(name)
        self.name_edit.setPlaceholderText("Entrez le nom du client")
        
        self.phone_edit = QLineEdit(phone)
        self.phone_edit.setPlaceholderText("Ex: 0555123456")
        
        self.email_edit = QLineEdit(email)
        self.email_edit.setPlaceholderText("email@exemple.com")
        
        self.address_edit = QLineEdit(address)
        self.address_edit.setPlaceholderText("Adresse du client")

        form.addRow("Nom:", self.name_edit)
        form.addRow("Téléphone:", self.phone_edit)
        form.addRow("Email:", self.email_edit)
        form.addRow("Adresse:", self.address_edit)

        main_layout.addLayout(form)

        # Boutons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        
        save_btn = QPushButton("💾 Enregistrer")
        save_btn.setStyleSheet(BUTTON_STYLES['success'])
        save_btn.clicked.connect(self.accept)
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        
        cancel_btn = QPushButton("❌ Annuler")
        cancel_btn.setStyleSheet(BUTTON_STYLES['secondary'])
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)

        btn_layout.addStretch()
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)
        
        main_layout.addLayout(btn_layout)


# ------------------ PAGE CLIENTS ------------------
class ClientsPage(QWidget):
    """Page clients — grille de cartes avec avatar, tri alphabétique."""

    client_added = pyqtSignal()

    # Palette d'avatars — une couleur par lettre initiale
    _AVATAR_COLORS = [
        "#6366F1","#A855F7","#EC4899","#F59E0B","#10B981",
        "#3B82F6","#EF4444","#14B8A6","#F97316","#8B5CF6",
    ]

    def __init__(self):
        super().__init__()
        self.db = get_database()
        self._all_clients = []   # cache complet pour filtre/tri

        # ── Layout racine ──────────────────────────────────────
        root = QVBoxLayout(self)
        root.setSpacing(0)
        root.setContentsMargins(0, 0, 0, 0)

        # ── En-tête ────────────────────────────────────────────
        hdr_frame = QFrame()
        hdr_frame.setStyleSheet(f"""
            QFrame {{
                background: {COLORS.get('BG_PAGE','#1E1E2E')};
                border-bottom: 1px solid {COLORS.get('BORDER','rgba(0,180,255,0.2)')};
            }}
        """)
        hdr_lay = QVBoxLayout(hdr_frame)
        hdr_lay.setContentsMargins(28, 20, 28, 16)
        hdr_lay.setSpacing(12)

        # Titre + bouton
        top_row = QHBoxLayout()
        col = QVBoxLayout()
        col.setSpacing(3)
        title = QLabel("👥 Gestion des Clients")
        title.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {COLORS.get('TXT_PRI','#F0F4FF')}; background:transparent;")
        col.addWidget(title)
        sub = QLabel("Gérez vos clients, leurs factures et notes")
        sub.setFont(QFont("Segoe UI", 11))
        sub.setStyleSheet(f"color: {COLORS.get('TXT_SEC','#A0AACC')}; background:transparent;")
        col.addWidget(sub)
        top_row.addLayout(col)
        top_row.addStretch()

        self.add_btn = QPushButton("➕  Nouveau Client")
        self.add_btn.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        self.add_btn.setFixedHeight(42)
        self.add_btn.setFixedWidth(175)
        self.add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.add_btn.setStyleSheet(f"""
            QPushButton {{
                background: {COLORS.get('primary','#3B82F6')};
                color: white; border: none; border-radius: 10px;
            }}
            QPushButton:hover {{ background: {COLORS.get('primary_dark','#2563EB')}; }}
        """)
        self.add_btn.clicked.connect(self.add_client)
        top_row.addWidget(self.add_btn)
        hdr_lay.addLayout(top_row)

        # Statistiques
        self.stats_layout = QHBoxLayout()
        self.stats_layout.setSpacing(12)
        hdr_lay.addLayout(self.stats_layout)

        # Barre recherche + tri
        ctrl_row = QHBoxLayout()
        ctrl_row.setSpacing(10)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Rechercher un client...")
        self.search_input.setMinimumHeight(40)
        self.search_input.setStyleSheet(INPUT_STYLE)
        self.search_input.textChanged.connect(self._apply_filter)
        ctrl_row.addWidget(self.search_input, 1)

        self.sort_combo = QComboBox()
        self.sort_combo.addItems(["A → Z", "Z → A", "Plus récent", "Plus de ventes"])
        self.sort_combo.setMinimumHeight(40)
        self.sort_combo.setFixedWidth(160)
        self.sort_combo.setStyleSheet(INPUT_STYLE)
        self.sort_combo.currentIndexChanged.connect(self._apply_filter)
        ctrl_row.addWidget(self.sort_combo)

        hdr_lay.addLayout(ctrl_row)
        root.addWidget(hdr_frame)

        # ── Zone scrollable pour la grille ─────────────────────
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setStyleSheet("QScrollArea { border:none; background:transparent; }")

        self._grid_container = QWidget()
        self._grid_container.setStyleSheet(f"background: {COLORS.get('BG_PAGE','#1E1E2E')};")
        self._grid_layout = QGridLayout(self._grid_container)
        self._grid_layout.setSpacing(16)
        self._grid_layout.setContentsMargins(28, 20, 28, 20)
        self._grid_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self._scroll.setWidget(self._grid_container)
        root.addWidget(self._scroll, 1)

        # ── Boutons d'action en bas ─────────────────────────────
        action_bar = QFrame()
        action_bar.setFixedHeight(60)
        action_bar.setStyleSheet(f"""
            QFrame {{
                background: {COLORS.get('BG_PAGE','#1E1E2E')};
                border-top: 1px solid {COLORS.get('BORDER','rgba(0,180,255,0.2)')};
            }}
        """)
        ab_lay = QHBoxLayout(action_bar)
        ab_lay.setContentsMargins(28, 8, 28, 8)
        ab_lay.setSpacing(10)
        ab_lay.addStretch()

        self.edit_btn = QPushButton("✏️  Modifier")
        self.edit_btn.setFixedHeight(38)
        self.edit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.edit_btn.setStyleSheet(BUTTON_STYLES['secondary'])
        self.edit_btn.clicked.connect(self.edit_client)
        ab_lay.addWidget(self.edit_btn)

        self.delete_btn = QPushButton("🗑️  Supprimer")
        self.delete_btn.setFixedHeight(38)
        self.delete_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.delete_btn.setStyleSheet(BUTTON_STYLES['danger'])
        self.delete_btn.clicked.connect(self.delete_client)
        ab_lay.addWidget(self.delete_btn)

        root.addWidget(action_bar)

        # ── Chargement initial ──────────────────────────────────
        self.load_statistics()
        self.load_clients()

    # ── Carte client ───────────────────────────────────────────
    def _make_card(self, client: dict) -> QFrame:
        """Crée une carte visuelle pour un client."""
        cid   = client["id"]
        name  = client.get("name", "?")
        phone = client.get("phone") or "—"
        email = client.get("email") or ""
        init  = name[0].upper() if name else "?"
        color = self._AVATAR_COLORS[ord(init) % len(self._AVATAR_COLORS)]

        # Compter les ventes
        try:
            self.db.cursor.execute(
                "SELECT COUNT(*), COALESCE(SUM(total),0) FROM sales WHERE client_id=?", (cid,))
            nb_v, ca = self.db.cursor.fetchone()
            nb_v = int(nb_v or 0)
            ca   = float(ca or 0)
        except Exception:
            nb_v, ca = 0, 0.0

        card = QFrame()
        card.setObjectName(f"card_{cid}")
        card.setFixedHeight(190)
        card.setCursor(Qt.CursorShape.PointingHandCursor)
        card.setStyleSheet(f"""
            QFrame#card_{cid} {{
                background: {COLORS.get('BG_CARD','#252535')};
                border-radius: 14px;
                border: 1px solid {COLORS.get('BORDER','rgba(0,180,255,0.2)')};
            }}
            QFrame#card_{cid}:hover {{
                border: 1px solid {color};
                background: {color}0A;
            }}
        """)

        lay = QVBoxLayout(card)
        lay.setContentsMargins(16, 16, 16, 14)
        lay.setSpacing(10)

        # ── Ligne haut : avatar + nom + actions ────────────────
        top = QHBoxLayout()
        top.setSpacing(12)

        # Avatar
        av = QLabel(init)
        av.setFixedSize(48, 48)
        av.setAlignment(Qt.AlignmentFlag.AlignCenter)
        av.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        av.setStyleSheet(f"""
            background: {color};
            color: white;
            border-radius: 24px;
            border: none;
        """)
        top.addWidget(av)

        # Nom + téléphone
        info_col = QVBoxLayout()
        info_col.setSpacing(2)
        name_lbl = QLabel(name)
        name_lbl.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        name_lbl.setStyleSheet(f"color:{COLORS.get('TXT_PRI','#F0F4FF')}; background:transparent;")
        name_lbl.setWordWrap(False)
        info_col.addWidget(name_lbl)

        ph_lbl = QLabel(f"📞 {phone}")
        ph_lbl.setFont(QFont("Segoe UI", 10))
        ph_lbl.setStyleSheet(f"color:{COLORS.get('TXT_SEC','#A0AACC')}; background:transparent;")
        info_col.addWidget(ph_lbl)

        if email:
            em_lbl = QLabel(f"✉ {email[:26]}{'…' if len(email)>26 else ''}")
            em_lbl.setFont(QFont("Segoe UI", 9))
            em_lbl.setStyleSheet(f"color:{COLORS.get('TXT_SEC','#A0AACC')}; background:transparent;")
            info_col.addWidget(em_lbl)

        top.addLayout(info_col, 1)
        lay.addLayout(top)

        # ── Séparateur ──────────────────────────────────────────
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background:{COLORS.get('BORDER','rgba(0,180,255,0.2)')}; border:none;")
        lay.addWidget(sep)

        # ── Stats ventes ────────────────────────────────────────
        stat_row = QHBoxLayout()
        stat_row.setSpacing(0)

        for label, val, col in [
            ("Ventes", str(nb_v), color),
            ("CA Total", fmt_da(ca, 0), "#10B981"),
        ]:
            s_frame = QFrame()
            s_frame.setStyleSheet("background:transparent; border:none;")
            sl = QVBoxLayout(s_frame)
            sl.setContentsMargins(0, 0, 0, 0)
            sl.setSpacing(1)
            vl = QLabel(val)
            vl.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
            vl.setStyleSheet(f"color:{col}; background:transparent;")
            tl = QLabel(label)
            tl.setFont(QFont("Segoe UI", 8))
            tl.setStyleSheet(f"color:{COLORS.get('TXT_SEC','#A0AACC')}; background:transparent;")
            sl.addWidget(vl)
            sl.addWidget(tl)
            stat_row.addWidget(s_frame, 1)

        lay.addLayout(stat_row)

        # ── Bouton Fiche ────────────────────────────────────────
        fiche_btn = QPushButton("📋  Voir Fiche")
        fiche_btn.setFixedHeight(30)
        fiche_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        fiche_btn.setStyleSheet(f"""
            QPushButton {{
                background: {color}18; color: {color};
                border: 1px solid {color}55;
                border-radius: 8px; font-size: 11px; font-weight: bold;
            }}
            QPushButton:hover {{ background: {color}35; }}
        """)
        fiche_btn.clicked.connect(lambda _, i=cid: self.open_fiche(i))
        lay.addWidget(fiche_btn)

        # Stocker l'ID pour edit/delete
        card.setProperty("client_id", cid)
        card.mousePressEvent = lambda e, i=cid: self._select_card(i)

        return card

    # ── Sélection de carte ─────────────────────────────────────
    def _select_card(self, client_id: int):
        self._selected_id = client_id

    # ── Affichage grille ───────────────────────────────────────
    def _display_grid(self, clients: list):
        """Remplit la grille avec la liste de clients."""
        # Vider la grille
        while self._grid_layout.count():
            item = self._grid_layout.takeAt(0)
            w = item.widget()
            if w: w.deleteLater()

        if not clients:
            empty = QLabel("Aucun client trouvé")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty.setFont(QFont("Segoe UI", 14))
            empty.setStyleSheet(f"color:{COLORS.get('TXT_SEC','#A0AACC')}; padding:60px;")
            self._grid_layout.addWidget(empty, 0, 0, 1, 3)
            return

        cols = 3
        for i, client in enumerate(clients):
            card = self._make_card(client)
            self._grid_layout.addWidget(card, i // cols, i % cols)

    # ── Filtre + tri ───────────────────────────────────────────
    def _apply_filter(self):
        text  = self.search_input.text().lower().strip()
        order = self.sort_combo.currentIndex()

        clients = [c for c in self._all_clients
                   if not text or text in c.get("name","").lower()
                   or text in (c.get("phone") or "").lower()
                   or text in (c.get("email") or "").lower()]

        if order == 0:   # A → Z
            clients.sort(key=lambda c: c.get("name","").lower())
        elif order == 1: # Z → A
            clients.sort(key=lambda c: c.get("name","").lower(), reverse=True)
        elif order == 2: # Plus récent
            clients.sort(key=lambda c: c.get("created_at",""), reverse=True)
        elif order == 3: # Plus de ventes
            def get_ca(client):
                try:
                    self.db.cursor.execute(
                        "SELECT COALESCE(SUM(total),0) FROM sales WHERE client_id=?",
                        (client["id"],))
                    return float(self.db.cursor.fetchone()[0] or 0)
                except Exception:
                    return 0.0
            clients.sort(key=get_ca, reverse=True)

        self._display_grid(clients)

    # ── Statistiques ───────────────────────────────────────────
    def build_stat_card(self, title, value, color):
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background: {color}15;
                border-radius: 10px;
                border: 1px solid {color}44;
            }}
        """)
        card.setFixedHeight(72)
        card.setMinimumWidth(160)
        cl = QVBoxLayout(card)
        cl.setContentsMargins(16, 10, 16, 10)
        cl.setSpacing(2)
        vl = QLabel(str(value))
        vl.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        vl.setStyleSheet(f"color:{color}; border:none; background:transparent;")
        tl = QLabel(title)
        tl.setFont(QFont("Segoe UI", 10))
        tl.setStyleSheet(f"color:{COLORS.get('TXT_SEC','#A0AACC')}; border:none; background:transparent;")
        cl.addWidget(vl)
        cl.addWidget(tl)
        return card

    def load_statistics(self):
        while self.stats_layout.count():
            item = self.stats_layout.takeAt(0)
            w = item.widget()
            if w: w.deleteLater()
        stats = self.db.get_statistics()
        self.stats_layout.addWidget(
            self.build_stat_card("Total Clients",  stats['total_clients'], COLORS.get('primary','#3B82F6')))
        self.stats_layout.addWidget(
            self.build_stat_card("Clients actifs", stats['total_clients'], COLORS.get('success','#22C55E')))
        self.stats_layout.addStretch()

    # ── Chargement ─────────────────────────────────────────────
    def load_clients(self):
        self._selected_id = None
        try:
            clients = self.db.get_all_clients() or []
        except Exception:
            clients = []
        # Tri par défaut A→Z
        clients.sort(key=lambda c: c.get("name","").lower())
        self._all_clients = clients
        self._apply_filter()

    def showEvent(self, event):
        super().showEvent(event)
        self.load_clients()
        self.load_statistics()

    def filter_clients(self, text):
        self._apply_filter()

    # ── Fiche ──────────────────────────────────────────────────
    def open_fiche(self, client_id: int):
        client = self.db.get_client_by_id(client_id)
        if not client:
            QMessageBox.warning(self, "Erreur", "Client introuvable.")
            return
        dlg = ClientFicheDialog(client, self.db, parent=self)
        dlg.exec()
        self.load_clients()

    # ── CRUD ───────────────────────────────────────────────────
    def add_client(self):
        if not session.can('add_client'):
            QMessageBox.warning(self, "Accès refusé", "Votre rôle ne permet pas d'ajouter des clients.")
            return
        dialog = ClientDialog()
        if dialog.exec():
            name    = dialog.name_edit.text().strip()
            phone   = dialog.phone_edit.text().strip()
            email   = dialog.email_edit.text().strip()
            address = dialog.address_edit.text().strip()
            if not name:
                QMessageBox.warning(self, "Erreur", "Le nom du client est obligatoire!")
                return
            client_id = self.db.add_client(name, phone, email, address)
            if client_id:
                QMessageBox.information(self, "Succès", f"Client '{name}' ajouté avec succès!")
                self.load_clients()
                self.load_statistics()
                self.client_added.emit()
            else:
                QMessageBox.critical(self, "Erreur", "Impossible d'ajouter le client!")

    def edit_client(self):
        if not session.can('edit_client'):
            QMessageBox.warning(self, "Accès refusé", "Votre rôle ne permet pas de modifier des clients.")
            return
        cid = getattr(self, '_selected_id', None)
        if not cid:
            QMessageBox.warning(self, "Attention", "Cliquez d'abord sur une carte client pour la sélectionner.")
            return
        client = self.db.get_client_by_id(cid)
        if not client:
            QMessageBox.critical(self, "Erreur", "Client introuvable!")
            return
        dialog = ClientDialog(
            name=client["name"], phone=client["phone"] or "",
            email=client["email"] or "", address=client["address"] or "",
            client_id=cid)
        if dialog.exec():
            name    = dialog.name_edit.text().strip()
            phone   = dialog.phone_edit.text().strip()
            email   = dialog.email_edit.text().strip()
            address = dialog.address_edit.text().strip()
            if not name:
                QMessageBox.warning(self, "Erreur", "Le nom est obligatoire!")
                return
            if self.db.update_client(cid, name, phone, email, address):
                QMessageBox.information(self, "Succès", f"Client '{name}' modifié!")
                self.load_clients()
                self.client_added.emit()
            else:
                QMessageBox.critical(self, "Erreur", "Impossible de modifier le client!")

    def delete_client(self):
        if not session.can('delete_client'):
            QMessageBox.warning(self, "Accès refusé", "Seul un administrateur peut supprimer des clients.")
            return
        cid = getattr(self, '_selected_id', None)
        if not cid:
            QMessageBox.warning(self, "Attention", "Cliquez d'abord sur une carte client.")
            return
        client = self.db.get_client_by_id(cid)
        client_name = client["name"] if client else "ce client"
        reply = QMessageBox.question(
            self, "Confirmation",
            f"Supprimer '{client_name}' ? Cette action est irréversible.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            if self.db.delete_client(cid):
                QMessageBox.information(self, "Succès", "Client supprimé!")
                self._selected_id = None
                self.load_clients()
                self.load_statistics()
                self.client_added.emit()
            else:
                QMessageBox.critical(self, "Erreur", "Impossible de supprimer!")


class ClientFicheDialog(QDialog):
    """Fiche détaillée d'un client : infos, factures, paiements, statistiques."""

    _CARD_STYLE = """
        QFrame {{
            background: {bg};
            border-radius: 10px;
            border: 1px solid {border};
        }}
    """

    def __init__(self, client: dict, db, parent=None):
        super().__init__(parent)
        self.client = client
        self.db     = db
        self.setWindowTitle(f"📋 Fiche Client — {client.get('name','')}")
        self.setMinimumSize(820, 620)
        self.setStyleSheet(f"""
            QDialog {{
                background: {COLORS.get('bg_page', '#1E1E2E')};
            }}
            QTabWidget::pane {{
                border: 1px solid rgba(255,255,255,0.08);
                border-radius: 10px;
                background: {COLORS.get('bg_card', '#252535')};
            }}
            QTabBar::tab {{
                background: {COLORS.get('bg_deep', '#16161F')};
                color: {COLORS.get('text_secondary', '#A0AACC')};
                padding: 10px 22px;
                font-size: 12px;
                font-weight: bold;
                border: none;
                border-radius: 8px 8px 0 0;
                margin-right: 3px;
            }}
            QTabBar::tab:selected {{
                background: {COLORS.get('primary', '#00B4FF')};
                color: white;
            }}
            QTabBar::tab:hover:!selected {{
                background: rgba(0,180,255,0.15);
                color: white;
            }}
            QLabel {{ color: {COLORS.get('text_primary', '#F0F4FF')}; background: transparent; }}
            QTableWidget {{
                background: {COLORS.get('bg_deep', '#16161F')};
                color: {COLORS.get('text_primary', '#F0F4FF')};
                border: none;
                gridline-color: rgba(255,255,255,0.05);
                font-size: 11px;
            }}
            QHeaderView::section {{
                background: rgba(0,180,255,0.12);
                color: #00B4FF;
                font-size: 11px;
                font-weight: bold;
                padding: 8px;
                border: none;
                border-bottom: 2px solid #00B4FF;
            }}
            QTableWidget::item {{ padding: 6px 8px; }}
            QTableWidget::item:selected {{
                background: rgba(0,180,255,0.18);
                color: white;
            }}
        """)

        main = QVBoxLayout(self)
        main.setContentsMargins(20, 20, 20, 20)
        main.setSpacing(16)

        # ── En-tête ────────────────────────────────────────────
        hdr = self._build_header()
        main.addWidget(hdr)

        # ── Onglets ────────────────────────────────────────────
        tabs = QTabWidget()
        tabs.addTab(self._tab_infos(),        "👤  Informations")
        tabs.addTab(self._tab_factures(),     "🧾  Factures")
        tabs.addTab(self._tab_paiements(),    "💳  Paiements")
        tabs.addTab(self._tab_statistiques(), "📊  Statistiques")
        tabs.addTab(self._tab_email(),        "📧  Email")
        tabs.addTab(self._tab_notes(),        "📝  Notes & Appels")
        main.addWidget(tabs)

        # ── Bouton fermer ──────────────────────────────────────
        close_btn = QPushButton("✖  Fermer")
        close_btn.setFixedHeight(38)
        close_btn.setFixedWidth(130)
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255,255,255,0.07); color: #A0AACC;
                border: 1px solid rgba(255,255,255,0.12);
                border-radius: 8px; font-size: 12px;
            }
            QPushButton:hover { background: rgba(255,80,80,0.18); color: #FF6060; }
        """)
        close_btn.clicked.connect(self.accept)
        row_close = QHBoxLayout()
        row_close.addStretch()
        row_close.addWidget(close_btn)
        main.addLayout(row_close)

    # ── En-tête coloré ─────────────────────────────────────────
    def _build_header(self) -> QFrame:
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(0,180,255,0.18), stop:1 rgba(0,229,255,0.08));
                border-radius: 12px;
                border: 1px solid rgba(0,180,255,0.25);
            }}
        """)
        frame.setFixedHeight(90)
        lay = QHBoxLayout(frame)
        lay.setContentsMargins(20, 12, 20, 12)
        lay.setSpacing(18)

        avatar = QLabel(self.client.get('name','?')[0].upper())
        avatar.setFixedSize(56, 56)
        avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        avatar.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        avatar.setStyleSheet("""
            background: #00B4FF; color: white;
            border-radius: 28px; border: none;
        """)
        lay.addWidget(avatar)

        col = QVBoxLayout()
        col.setSpacing(2)
        name_lbl = QLabel(self.client.get('name', '—'))
        name_lbl.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        name_lbl.setStyleSheet("color: #F0F4FF;")
        col.addWidget(name_lbl)

        sub_parts = []
        if self.client.get('phone'): sub_parts.append(f"📞 {self.client['phone']}")
        if self.client.get('email'): sub_parts.append(f"✉ {self.client['email']}")
        sub_lbl = QLabel("   ·   ".join(sub_parts) if sub_parts else "Aucune coordonnée")
        sub_lbl.setFont(QFont("Segoe UI", 10))
        sub_lbl.setStyleSheet("color: rgba(160,170,204,0.85);")
        col.addWidget(sub_lbl)
        lay.addLayout(col, 1)

        # Badge ID
        id_lbl = QLabel(f"#{self.client.get('id','')}")
        id_lbl.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        id_lbl.setStyleSheet("""
            color: #00B4FF; background: rgba(0,180,255,0.12);
            border-radius: 8px; padding: 4px 12px; border: 1px solid rgba(0,180,255,0.3);
        """)
        lay.addWidget(id_lbl)
        return frame

    # ── Onglet 1 : Informations ────────────────────────────────
    def _tab_infos(self) -> QWidget:
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(16, 16, 16, 16)
        lay.setSpacing(12)

        def info_row(icon, label, value):
            row = QFrame()
            row.setStyleSheet(f"""
                QFrame {{
                    background: {COLORS.get('bg_deep','#16161F')};
                    border-radius: 8px; border: 1px solid rgba(255,255,255,0.06);
                }}
            """)
            rl = QHBoxLayout(row)
            rl.setContentsMargins(14, 10, 14, 10)
            rl.setSpacing(12)

            ico = QLabel(icon)
            ico.setFixedWidth(24)
            ico.setFont(QFont("Segoe UI", 14))
            ico.setStyleSheet("border:none; background:transparent;")
            rl.addWidget(ico)

            lbl = QLabel(label)
            lbl.setFixedWidth(130)
            lbl.setFont(QFont("Segoe UI", 10))
            lbl.setStyleSheet("color: rgba(160,170,204,0.8); border:none; background:transparent;")
            rl.addWidget(lbl)

            val = QLabel(str(value) if value else "—")
            val.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
            val.setStyleSheet("color: #F0F4FF; border:none; background:transparent;")
            val.setWordWrap(True)
            rl.addWidget(val, 1)
            return row

        lay.addWidget(info_row("👤", "Nom complet",  self.client.get('name')))
        lay.addWidget(info_row("📞", "Téléphone",    self.client.get('phone')))
        lay.addWidget(info_row("✉️",  "Email",        self.client.get('email')))
        lay.addWidget(info_row("📍", "Adresse",      self.client.get('address')))
        lay.addWidget(info_row("🗓️", "Créé le",      str(self.client.get('created_at','—')).split(' ')[0]))
        lay.addStretch()
        return w

    # ── Onglet 2 : Factures ────────────────────────────────────
    def _tab_factures(self) -> QWidget:
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(12, 12, 12, 12)
        lay.setSpacing(8)

        # Récupérer les factures du client
        try:
            self.db.cursor.execute("""
                SELECT id, invoice_number, sale_date, total,
                       payment_method, payment_status
                FROM sales
                WHERE client_id = ?
                ORDER BY sale_date DESC
            """, (self.client['id'],))
            rows = [dict(r) for r in self.db.cursor.fetchall()]
        except Exception:
            rows = []

        # Résumé
        total_ca = sum(float(r.get('total',0)) for r in rows)
        summary = QHBoxLayout()
        for txt, val, col in [
            ("Nombre de factures", str(len(rows)), "#00B4FF"),
            ("Chiffre d'affaires total", fmt_da(total_ca), "#10B981"),  # 🔴 FORMATAGE ICI
        ]:
            card = QFrame()
            card.setStyleSheet(f"""
                QFrame {{ background: rgba(0,0,0,0.2); border-radius:8px;
                          border: 1px solid {col}33; }}
            """)
            cl = QVBoxLayout(card)
            cl.setContentsMargins(14, 10, 14, 10)
            vl = QLabel(val)
            vl.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
            vl.setStyleSheet(f"color:{col};border:none;")
            tl = QLabel(txt)
            tl.setFont(QFont("Segoe UI", 9))
            tl.setStyleSheet("color:rgba(160,170,204,0.8);border:none;")
            cl.addWidget(vl)
            cl.addWidget(tl)
            summary.addWidget(card)
        summary.addStretch()
        lay.addLayout(summary)

        # Tableau
        tbl = QTableWidget(len(rows), 5)
        tbl.setHorizontalHeaderLabels(["N° Facture","Date","Total","Paiement","Statut"])
        tbl.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        tbl.verticalHeader().setVisible(False)
        tbl.setAlternatingRowColors(True)

        STATUS_COLOR = {
            'paid': ('#10B981', '✅ Payée'),
            'pending': ('#F59E0B', '⏳ En attente'),
            'cancelled': ('#EF4444', '❌ Annulée'),
        }

        for i, r in enumerate(rows):
            date = str(r.get('sale_date','—')).split(' ')[0]
            total = float(r.get('total') or 0)
            status = r.get('payment_status','paid')
            col_s, lbl_s = STATUS_COLOR.get(status, ('#A0AACC', status))

            cells = [
                (r.get('invoice_number','—'), '#F0F4FF'),
                (date,                        '#A0AACC'),
                (fmt_da(total),                '#10B981'),  # 🔴 FORMATAGE ICI
                (r.get('payment_method','—'), '#A0AACC'),
                (lbl_s,                       col_s),
            ]
            for j, (val, color) in enumerate(cells):
                item = QTableWidgetItem(str(val))
                item.setForeground(QColor(color))
                item.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                tbl.setItem(i, j, item)
            tbl.setRowHeight(i, 38)

        if not rows:
            tbl.setRowCount(1)
            msg = QTableWidgetItem("Aucune facture pour ce client")
            msg.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            msg.setForeground(QColor('#A0AACC'))
            msg.setFlags(msg.flags() & ~Qt.ItemFlag.ItemIsEditable)
            tbl.setItem(0, 0, msg)
            tbl.setSpan(0, 0, 1, 5)

        lay.addWidget(tbl)
        return w

    # ── Onglet 3 : Paiements ───────────────────────────────────
    def _tab_paiements(self) -> QWidget:
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(12, 12, 12, 12)
        lay.setSpacing(8)

        try:
            self.db.cursor.execute("""
                SELECT invoice_number, sale_date, total,
                       payment_method, payment_status
                FROM sales
                WHERE client_id = ?
                ORDER BY sale_date DESC
            """, (self.client['id'],))
            rows = [dict(r) for r in self.db.cursor.fetchall()]
        except Exception:
            rows = []

        # Regrouper par mode de paiement
        from collections import defaultdict
        by_method = defaultdict(lambda: {'count': 0, 'total': 0.0})
        for r in rows:
            m = r.get('payment_method') or 'Autre'
            by_method[m]['count'] += 1
            by_method[m]['total'] += float(r.get('total') or 0)

        METHOD_ICON = {'cash': '💵', 'credit': '💳', 'cheque': '🏦',
                       'virement': '🔄', 'Autre': '❓'}
        METHOD_COLOR = {'cash': '#10B981', 'credit': '#6366F1',
                        'cheque': '#F59E0B', 'virement': '#00B4FF', 'Autre': '#A0AACC'}

        # Cartes par méthode
        cards_row = QHBoxLayout()
        for method, data in by_method.items():
            icon  = METHOD_ICON.get(method, '💰')
            color = METHOD_COLOR.get(method, '#A0AACC')
            card  = QFrame()
            card.setStyleSheet(f"""
                QFrame {{ background: rgba(0,0,0,0.2);
                          border-radius: 10px; border: 1px solid {color}44; }}
            """)
            cl = QVBoxLayout(card)
            cl.setContentsMargins(16, 12, 16, 12)
            cl.setSpacing(4)
            
            lbl_m = QLabel(f"{icon} {method.capitalize()}")
            lbl_m.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
            lbl_m.setStyleSheet(f"color:{color};border:none;")
            cl.addWidget(lbl_m)
            
            # 🔴 UTILISATION DE fmt_da POUR LE MONTANT
            lbl_v = QLabel(fmt_da(data['total']))
            lbl_v.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
            lbl_v.setStyleSheet(f"color:#F0F4FF;border:none;")
            cl.addWidget(lbl_v)
            
            lbl_c = QLabel(f"{data['count']} transaction{'s' if data['count']>1 else ''}")
            lbl_c.setFont(QFont("Segoe UI", 9))
            lbl_c.setStyleSheet("color:rgba(160,170,204,0.8);border:none;")
            cl.addWidget(lbl_c)
            cards_row.addWidget(card)

        if not by_method:
            no_lbl = QLabel("Aucun paiement enregistré")
            no_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            no_lbl.setStyleSheet("color:#A0AACC;font-size:12px;")
            cards_row.addWidget(no_lbl)

        cards_row.addStretch()
        lay.addLayout(cards_row)

        # Tableau historique paiements
        tbl = QTableWidget(len(rows), 4)
        tbl.setHorizontalHeaderLabels(["N° Facture","Date","Mode de Paiement","Montant"])
        tbl.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        tbl.verticalHeader().setVisible(False)
        tbl.setAlternatingRowColors(True)

        for i, r in enumerate(rows):
            date   = str(r.get('sale_date','—')).split(' ')[0]
            method = r.get('payment_method') or '—'
            total  = float(r.get('total') or 0)
            icon   = METHOD_ICON.get(method, '💰')
            color  = METHOD_COLOR.get(method, '#A0AACC')

            for j, (val, col) in enumerate([
                (r.get('invoice_number','—'), '#F0F4FF'),
                (date,                        '#A0AACC'),
                (f"{icon} {method}",          color),
                (fmt_da(total),                '#10B981'),  # 🔴 FORMATAGE ICI
            ]):
                it = QTableWidgetItem(val)
                it.setForeground(QColor(col))
                it.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
                it.setFlags(it.flags() & ~Qt.ItemFlag.ItemIsEditable)
                tbl.setItem(i, j, it)
            tbl.setRowHeight(i, 38)

        lay.addWidget(tbl)
        return w

    # ── Onglet 4 : Statistiques ────────────────────────────────
    def _tab_statistiques(self) -> QWidget:
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(16, 16, 16, 16)
        lay.setSpacing(14)

        try:
            self.db.cursor.execute("""
                SELECT COUNT(*) as nb_ventes,
                       COALESCE(SUM(total),0) as ca_total,
                       COALESCE(AVG(total),0) as panier_moyen,
                       COALESCE(MAX(total),0) as plus_grosse,
                       COALESCE(MIN(total),0) as plus_petite,
                       MIN(sale_date) as premiere_vente,
                       MAX(sale_date) as derniere_vente
                FROM sales WHERE client_id = ?
            """, (self.client['id'],))
            st = dict(self.db.cursor.fetchone() or {})
        except Exception:
            st = {}

        # Meilleure catégorie de produits achetés
        try:
            self.db.cursor.execute("""
                SELECT p.name, SUM(si.quantity) as qty
                FROM sale_items si
                JOIN sales s ON si.sale_id = s.id
                LEFT JOIN products p ON si.product_id = p.id
                WHERE s.client_id = ?
                GROUP BY si.product_id
                ORDER BY qty DESC LIMIT 5
            """, (self.client['id'],))
            top_products = self.db.cursor.fetchall()
        except Exception:
            top_products = []

        def stat_card(icon, label, value, color='#00B4FF'):
            card = QFrame()
            card.setStyleSheet(f"""
                QFrame {{ background: rgba(0,0,0,0.25);
                          border-radius: 10px; border: 1px solid {color}33; }}
            """)
            cl = QVBoxLayout(card)
            cl.setContentsMargins(16, 12, 16, 12)
            cl.setSpacing(3)
            il = QLabel(f"{icon}")
            il.setFont(QFont("Segoe UI", 20))
            il.setStyleSheet("border:none;")
            cl.addWidget(il)
            vl = QLabel(str(value))
            vl.setFont(QFont("Segoe UI", 15, QFont.Weight.Bold))
            vl.setStyleSheet(f"color:{color};border:none;")
            cl.addWidget(vl)
            tl = QLabel(label)
            tl.setFont(QFont("Segoe UI", 9))
            tl.setStyleSheet("color:rgba(160,170,204,0.8);border:none;")
            cl.addWidget(tl)
            return card

        grid = QGridLayout()
        grid.setSpacing(10)

        nb   = int(st.get('nb_ventes', 0))
        ca   = float(st.get('ca_total', 0))
        avg  = float(st.get('panier_moyen', 0))
        big  = float(st.get('plus_grosse', 0))
        prem = str(st.get('premiere_vente','—')).split(' ')[0]
        last = str(st.get('derniere_vente','—')).split(' ')[0]

        grid.addWidget(stat_card("🧾", "Nb de ventes",        str(nb),                 '#00B4FF'), 0, 0)
        # 🔴 UTILISATION DE fmt_da POUR TOUS LES MONTANTS
        grid.addWidget(stat_card("💰", "Chiffre d'affaires",  fmt_da(ca),              '#10B981'), 0, 1)
        grid.addWidget(stat_card("🛒", "Panier moyen",        fmt_da(avg),             '#6366F1'), 0, 2)
        grid.addWidget(stat_card("🏆", "Plus grosse facture", fmt_da(big),             '#F59E0B'), 1, 0)
        grid.addWidget(stat_card("📅", "Première visite",     prem,                    '#A0AACC'), 1, 1)
        grid.addWidget(stat_card("🕐", "Dernière visite",     last,                    '#A0AACC'), 1, 2)
        lay.addLayout(grid)

        # Top produits achetés
        if top_products:
            top_lbl = QLabel("🛍️  Produits les plus achetés")
            top_lbl.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
            top_lbl.setStyleSheet("color:#F0F4FF;")
            lay.addWidget(top_lbl)

            max_qty = max(int(r[1] if not hasattr(r,'keys') else r['qty']) for r in top_products) or 1
            for r in top_products:
                name = str(r[0] if not hasattr(r,'keys') else r['name']) or 'Produit supprimé'
                qty  = int(r[1] if not hasattr(r,'keys') else r['qty'])
                rw = QFrame()
                rw.setStyleSheet("QFrame{background:rgba(0,0,0,0.18);border-radius:8px;border:1px solid rgba(255,255,255,0.05);}")
                rl = QHBoxLayout(rw)
                rl.setContentsMargins(12, 8, 12, 8)
                rl.setSpacing(10)
                nl = QLabel(name[:32])
                nl.setFont(QFont("Segoe UI", 10))
                nl.setStyleSheet("color:#F0F4FF;border:none;")
                rl.addWidget(nl, 1)
                bar = QProgressBar()
                bar.setRange(0, max_qty)
                bar.setValue(qty)
                bar.setTextVisible(False)
                bar.setFixedHeight(8)
                bar.setFixedWidth(160)
                bar.setStyleSheet("""
                    QProgressBar{background:rgba(0,180,255,0.1);border-radius:4px;border:none;}
                    QProgressBar::chunk{background:#00B4FF;border-radius:4px;}
                """)
                rl.addWidget(bar)
                ql = QLabel(f"{qty} u.")
                ql.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
                ql.setStyleSheet("color:#00B4FF;border:none;")
                ql.setFixedWidth(45)
                rl.addWidget(ql)
                lay.addWidget(rw)

        lay.addStretch()
        return w

    # ── Onglet Email ───────────────────────────────────────────
    def _tab_email(self) -> QWidget:
        """Onglet pour envoyer un email au client."""
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(16, 16, 16, 16)
        lay.setSpacing(12)

        # Vérifier si le client a un email
        client_email = self.client.get('email', '')

        if not client_email:
            # Pas d'email enregistré
            no_email = QFrame()
            no_email.setStyleSheet("""
                QFrame { background: rgba(245,158,11,0.08);
                         border-radius: 10px; border: 1px solid rgba(245,158,11,0.3); }
            """)
            nel = QVBoxLayout(no_email)
            nel.setContentsMargins(20, 20, 20, 20)
            nel.setSpacing(8)
            ico = QLabel("⚠️")
            ico.setFont(QFont("Segoe UI", 28))
            ico.setAlignment(Qt.AlignmentFlag.AlignCenter)
            ico.setStyleSheet("border:none;")
            nel.addWidget(ico)
            msg = QLabel("Aucun email enregistré pour ce client.")
            msg.setFont(QFont("Segoe UI", 12))
            msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
            msg.setStyleSheet("color:#F59E0B; border:none;")
            nel.addWidget(msg)
            hint = QLabel("Modifiez la fiche client pour ajouter une adresse email.")
            hint.setFont(QFont("Segoe UI", 10))
            hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
            hint.setStyleSheet("color:rgba(160,170,204,0.7); border:none;")
            nel.addWidget(hint)
            lay.addWidget(no_email)
            lay.addStretch()
            return w

        # ── Formulaire d'email ────────────────────────────────
        # Destinataire
        dest_frame = QFrame()
        dest_frame.setStyleSheet("""
            QFrame { background: rgba(0,0,0,0.2); border-radius: 8px;
                     border: 1px solid rgba(255,255,255,0.06); }
        """)
        dl = QHBoxLayout(dest_frame)
        dl.setContentsMargins(14, 10, 14, 10)
        dest_lbl = QLabel("À :")
        dest_lbl.setFixedWidth(50)
        dest_lbl.setFont(QFont("Segoe UI", 10))
        dest_lbl.setStyleSheet("color:rgba(160,170,204,0.8); border:none;")
        dl.addWidget(dest_lbl)
        dest_val = QLabel(client_email)
        dest_val.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        dest_val.setStyleSheet("color:#00B4FF; border:none;")
        dl.addWidget(dest_val, 1)
        lay.addWidget(dest_frame)

        # Sujet
        subj_frame = QFrame()
        subj_frame.setStyleSheet("""
            QFrame { background: rgba(0,0,0,0.2); border-radius: 8px;
                     border: 1px solid rgba(255,255,255,0.06); }
        """)
        sl = QHBoxLayout(subj_frame)
        sl.setContentsMargins(14, 6, 14, 6)
        subj_lbl = QLabel("Sujet :")
        subj_lbl.setFixedWidth(50)
        subj_lbl.setFont(QFont("Segoe UI", 10))
        subj_lbl.setStyleSheet("color:rgba(160,170,204,0.8); border:none;")
        sl.addWidget(subj_lbl)
        self._email_subject = QLineEdit()
        self._email_subject.setPlaceholderText("Objet de l'email...")
        self._email_subject.setText(f"Message de votre partenaire")
        self._email_subject.setStyleSheet("""
            QLineEdit { background:transparent; color:#F0F4FF;
                        border:none; font-size:12px; }
        """)
        sl.addWidget(self._email_subject, 1)
        lay.addWidget(subj_frame)

        # Corps du message
        body_lbl = QLabel("Message :")
        body_lbl.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        body_lbl.setStyleSheet("color:#F0F4FF;")
        lay.addWidget(body_lbl)

        self._email_body = QTextEdit()
        self._email_body.setPlaceholderText(
            f"Bonjour {self.client.get('name','')},\n\n"
            "Écrivez votre message ici...\n\n"
            "Cordialement,")
        self._email_body.setFont(QFont("Segoe UI", 11))
        self._email_body.setStyleSheet(f"""
            QTextEdit {{
                background: rgba(0,0,0,0.25);
                color: #F0F4FF;
                border: 1px solid rgba(0,180,255,0.2);
                border-radius: 8px;
                padding: 10px;
            }}
            QTextEdit:focus {{ border: 1px solid #00B4FF; }}
        """)
        lay.addWidget(self._email_body, 1)

        # Boutons
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        copy_btn = QPushButton("📋  Copier l'email")
        copy_btn.setFixedHeight(38)
        copy_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        copy_btn.setStyleSheet("""
            QPushButton { background:rgba(0,180,255,0.12); color:#00B4FF;
                border:1px solid rgba(0,180,255,0.3); border-radius:8px;
                font-size:11px; font-weight:bold; padding:0 14px; }
            QPushButton:hover { background:rgba(0,180,255,0.25); }
        """)
        copy_btn.clicked.connect(lambda: (
            QApplication.clipboard().setText(client_email),
            QMessageBox.information(self, "✅ Copié", f"Email copié : {client_email}")
        ))
        btn_row.addWidget(copy_btn)

        open_btn = QPushButton("📧  Ouvrir dans la messagerie")
        open_btn.setFixedHeight(38)
        open_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        open_btn.setStyleSheet("""
            QPushButton { background:#00B4FF; color:white;
                border:none; border-radius:8px;
                font-size:11px; font-weight:bold; padding:0 14px; }
            QPushButton:hover { background:#0090DD; }
        """)
        def open_mail():
            import urllib.parse
            subject = urllib.parse.quote(self._email_subject.text())
            body    = urllib.parse.quote(self._email_body.toPlainText())
            import subprocess
            import sys
            url = f"mailto:{client_email}?subject={subject}&body={body}"
            if sys.platform == "win32":
                import os
                os.startfile(url)
        open_btn.clicked.connect(open_mail)
        btn_row.addWidget(open_btn)
        btn_row.addStretch()
        lay.addLayout(btn_row)
        return w

    # ── Onglet Notes & Appels ──────────────────────────────────
    def _tab_notes(self) -> QWidget:
        """Onglet pour gérer les notes et l'historique des appels."""
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(16, 16, 16, 16)
        lay.setSpacing(12)

        # ── Ajouter une note ──────────────────────────────────
        add_frame = QFrame()
        add_frame.setStyleSheet("""
            QFrame { background: rgba(0,0,0,0.2); border-radius: 10px;
                     border: 1px solid rgba(0,180,255,0.15); }
        """)
        af = QVBoxLayout(add_frame)
        af.setContentsMargins(14, 12, 14, 12)
        af.setSpacing(8)

        add_hdr = QHBoxLayout()
        add_title = QLabel("➕  Ajouter une note / un appel")
        add_title.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        add_title.setStyleSheet("color:#F0F4FF; border:none;")
        add_hdr.addWidget(add_title)
        add_hdr.addStretch()

        # Type : note ou appel
        self._note_type = QComboBox()
        self._note_type.addItems(["📝 Note", "📞 Appel entrant", "📞 Appel sortant", "📅 Rendez-vous"])
        self._note_type.setFixedWidth(180)
        self._note_type.setFixedHeight(32)
        self._note_type.setStyleSheet("""
            QComboBox { background:rgba(0,180,255,0.1); color:#00B4FF;
                border:1px solid rgba(0,180,255,0.3); border-radius:6px;
                padding:0 8px; font-size:11px; }
            QComboBox::drop-down { border:none; }
            QComboBox QAbstractItemView { background:#252535; color:#F0F4FF;
                border:1px solid rgba(0,180,255,0.2); }
        """)
        add_hdr.addWidget(self._note_type)
        af.addLayout(add_hdr)

        self._note_edit = QTextEdit()
        self._note_edit.setPlaceholderText("Écrivez votre note ou le résumé de l'appel...")
        self._note_edit.setFixedHeight(80)
        self._note_edit.setFont(QFont("Segoe UI", 11))
        self._note_edit.setStyleSheet("""
            QTextEdit { background:rgba(0,0,0,0.2); color:#F0F4FF;
                border:1px solid rgba(0,180,255,0.15);
                border-radius:8px; padding:8px; }
            QTextEdit:focus { border:1px solid #00B4FF; }
        """)
        af.addWidget(self._note_edit)

        save_note_btn = QPushButton("💾  Enregistrer")
        save_note_btn.setFixedHeight(34)
        save_note_btn.setFixedWidth(140)
        save_note_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        save_note_btn.setStyleSheet("""
            QPushButton { background:#00B4FF; color:white; border:none;
                border-radius:7px; font-size:11px; font-weight:bold; }
            QPushButton:hover { background:#0090DD; }
        """)
        af.addWidget(save_note_btn, alignment=Qt.AlignmentFlag.AlignRight)
        lay.addWidget(add_frame)

        # ── Historique des notes ───────────────────────────────
        hist_lbl = QLabel("📋  Historique")
        hist_lbl.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        hist_lbl.setStyleSheet("color:#F0F4FF;")
        lay.addWidget(hist_lbl)

        # Zone scrollable pour les notes
        self._notes_scroll = QScrollArea()
        self._notes_scroll.setWidgetResizable(True)
        self._notes_scroll.setStyleSheet("QScrollArea { border:none; background:transparent; }")

        self._notes_container = QWidget()
        self._notes_container.setStyleSheet("background:transparent;")
        self._notes_list_layout = QVBoxLayout(self._notes_container)
        self._notes_list_layout.setSpacing(8)
        self._notes_list_layout.setContentsMargins(0, 0, 0, 0)
        self._notes_list_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self._notes_scroll.setWidget(self._notes_container)
        lay.addWidget(self._notes_scroll, 1)

        # Charger les notes existantes
        self._load_notes()

        # Connecter le bouton sauvegarder
        save_note_btn.clicked.connect(self._save_note)

        return w

    def _load_notes(self):
        """Charge les notes depuis la BDD."""
        # Vider la liste
        while self._notes_list_layout.count():
            item = self._notes_list_layout.takeAt(0)
            w = item.widget()
            if w: w.deleteLater()

        try:
            self.db.cursor.execute("""
                SELECT id, note_type, content, created_at
                FROM client_notes
                WHERE client_id = ?
                ORDER BY created_at DESC
            """, (self.client['id'],))
            notes = self.db.cursor.fetchall()
        except Exception:
            notes = []

        if not notes:
            empty = QLabel("Aucune note pour ce client.\nAjoutez la première note ci-dessus.")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty.setFont(QFont("Segoe UI", 11))
            empty.setStyleSheet("color:rgba(160,170,204,0.5); padding:20px;")
            self._notes_list_layout.addWidget(empty)
            return

        TYPE_COLOR = {
            "📝 Note":           "#6366F1",
            "📞 Appel entrant":  "#10B981",
            "📞 Appel sortant":  "#3B82F6",
            "📅 Rendez-vous":    "#F59E0B",
        }

        for note in notes:
            nid      = note[0] if not hasattr(note, 'keys') else note['id']
            ntype    = note[1] if not hasattr(note, 'keys') else note['note_type']
            content  = note[2] if not hasattr(note, 'keys') else note['content']
            created  = str(note[3] if not hasattr(note, 'keys') else note['created_at']).split('.')[0]
            color    = TYPE_COLOR.get(ntype, "#A0AACC")

            row = QFrame()
            row.setStyleSheet(f"""
                QFrame {{ background: rgba(0,0,0,0.2);
                          border-radius: 10px;
                          border-left: 3px solid {color};
                          border-top: 1px solid rgba(255,255,255,0.05);
                          border-right: 1px solid rgba(255,255,255,0.05);
                          border-bottom: 1px solid rgba(255,255,255,0.05); }}
            """)
            rl = QVBoxLayout(row)
            rl.setContentsMargins(14, 10, 14, 10)
            rl.setSpacing(4)

            # En-tête : type + date + supprimer
            rh = QHBoxLayout()
            type_lbl = QLabel(ntype)
            type_lbl.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
            type_lbl.setStyleSheet(f"color:{color}; border:none; background:transparent;")
            rh.addWidget(type_lbl)
            rh.addStretch()
            date_lbl = QLabel(created)
            date_lbl.setFont(QFont("Segoe UI", 9))
            date_lbl.setStyleSheet("color:rgba(160,170,204,0.6); border:none; background:transparent;")
            rh.addWidget(date_lbl)

            del_btn = QPushButton("✕")
            del_btn.setFixedSize(22, 22)
            del_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            del_btn.setStyleSheet("""
                QPushButton { background:transparent; color:rgba(160,170,204,0.4);
                    border:none; font-size:10px; }
                QPushButton:hover { color:#EF4444; }
            """)
            del_btn.clicked.connect(lambda _, i=nid: self._delete_note(i))
            rh.addWidget(del_btn)
            rl.addLayout(rh)

            # Contenu
            content_lbl = QLabel(content)
            content_lbl.setFont(QFont("Segoe UI", 10))
            content_lbl.setStyleSheet("color:#F0F4FF; border:none; background:transparent;")
            content_lbl.setWordWrap(True)
            rl.addWidget(content_lbl)

            self._notes_list_layout.addWidget(row)

    def _save_note(self):
        """Enregistre une note en BDD."""
        content = self._note_edit.toPlainText().strip()
        if not content:
            QMessageBox.warning(self, "Attention", "Écrivez une note avant d'enregistrer.")
            return
        note_type = self._note_type.currentText()
        try:
            # Créer la table si elle n'existe pas
            self.db.cursor.execute("""
                CREATE TABLE IF NOT EXISTS client_notes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    client_id INTEGER NOT NULL,
                    note_type TEXT,
                    content TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (client_id) REFERENCES clients(id)
                )
            """)
            self.db.conn.commit()
            self.db.cursor.execute("""
                INSERT INTO client_notes (client_id, note_type, content)
                VALUES (?, ?, ?)
            """, (self.client['id'], note_type, content))
            self.db.conn.commit()
            self._note_edit.clear()
            self._load_notes()
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Impossible d'enregistrer la note :\n{e}")

    def _delete_note(self, note_id: int):
        """Supprime une note."""
        reply = QMessageBox.question(
            self, "Supprimer", "Supprimer cette note ?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.db.cursor.execute("DELETE FROM client_notes WHERE id=?", (note_id,))
                self.db.conn.commit()
                self._load_notes()
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Impossible de supprimer :\n{e}")
