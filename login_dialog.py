"""
login_dialog.py — Écran de connexion et gestion des utilisateurs
================================================================
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFrame, QMessageBox, QWidget, QScrollArea,
    QComboBox, QCheckBox, QTableWidget, QTableWidgetItem,
    QHeaderView, QApplication
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QColor, QKeyEvent

from styles import COLORS
from db_manager import get_database
from auth import session, hash_password, verify_password, ROLE_LABELS, ROLE_COLORS, ROLE_ICONS


# ──────────────────────────────────────────────────────────────────
# Helpers de style
# ──────────────────────────────────────────────────────────────────

def _field(placeholder: str, password: bool = False) -> QLineEdit:
    """Crée un champ de saisie stylisé."""
    f = QLineEdit()
    f.setPlaceholderText(placeholder)
    f.setFixedHeight(44)
    if password:
        f.setEchoMode(QLineEdit.EchoMode.Password)
    f.setStyleSheet(f"""
        QLineEdit {{
            background: {COLORS['BG_DEEP']};
            border: 1.5px solid {COLORS['BORDER']};
            border-radius: 8px;
            color: {COLORS['TXT_PRI']};
            padding: 0 14px;
            font-size: 13px;
        }}
        QLineEdit:focus {{
            border: 1.5px solid {COLORS['primary']};
        }}
    """)
    return f


def _btn(text: str, color: str, height: int = 44) -> QPushButton:
    """Crée un bouton stylisé."""
    b = QPushButton(text)
    b.setFixedHeight(height)
    b.setCursor(Qt.CursorShape.PointingHandCursor)
    b.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
    b.setStyleSheet(f"""
        QPushButton {{
            background: {color};
            color: #FFFFFF;
            border-radius: 8px;
            border: none;
        }}
        QPushButton:hover  {{ background: {color}CC; }}
        QPushButton:pressed {{ background: {color}99; }}
        QPushButton:disabled {{
            background: {COLORS['BG_DEEP']};
            color: {COLORS['TXT_SEC']};
        }}
    """)
    return b


# ──────────────────────────────────────────────────────────────────
# Écran de connexion
# ──────────────────────────────────────────────────────────────────

class LoginDialog(QDialog):
    """Fenêtre de connexion affichée au démarrage de l'application.

    Signals:
        login_success: Émis quand l'authentification réussit.
    """

    login_success = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = get_database()
        self._ensure_admin_exists()

        self.setWindowTitle("Connexion — ERP DAR ELSSALEM")
        self.setFixedSize(420, 520)
        self.setWindowFlags(
            Qt.WindowType.Dialog |
            Qt.WindowType.WindowCloseButtonHint
        )
        self.setStyleSheet(f"background: {COLORS['BG_PAGE']};")
        self._build_ui()

    def _ensure_admin_exists(self) -> None:
        """Crée le compte admin par défaut s'il n'en existe aucun."""
        try:
            self.db.cursor.execute("SELECT COUNT(*) FROM users")
            count = self.db.cursor.fetchone()[0]
            if count == 0:
                default_hash = hash_password("admin123")
                self.db.cursor.execute("""
                    INSERT INTO users (username, password_hash, role, is_active)
                    VALUES (?, ?, 'admin', 1)
                """, ("admin", default_hash))
                self.db.conn.commit()
                print("[OK] Compte admin par défaut créé (admin / admin123)")
        except Exception as e:
            print(f"[ERROR] _ensure_admin_exists: {e}")

    def _build_ui(self) -> None:
        """Construit l'interface de la fenêtre de connexion."""
        lay = QVBoxLayout(self)
        lay.setContentsMargins(40, 40, 40, 40)
        lay.setSpacing(0)

        # ── En-tête ───────────────────────────────────────────
        icon_lbl = QLabel("🏢")
        icon_lbl.setFont(QFont("Segoe UI", 42))
        icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(icon_lbl)

        lay.addSpacing(8)

        title = QLabel("DAR ELSSALEM")
        title.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(f"color: {COLORS['primary']};")
        lay.addWidget(title)

        sub = QLabel("Système de Gestion ERP")
        sub.setFont(QFont("Segoe UI", 11))
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sub.setStyleSheet(f"color: {COLORS['TXT_SEC']};")
        lay.addWidget(sub)

        lay.addSpacing(32)

        # ── Formulaire ────────────────────────────────────────
        self._user_field = _field("Nom d'utilisateur")
        self._pass_field = _field("Mot de passe", password=True)
        self._pass_field.returnPressed.connect(self._do_login)

        lay.addWidget(QLabel("Identifiant", styleSheet=f"color:{COLORS['TXT_SEC']}; font-size:12px;"))
        lay.addSpacing(4)
        lay.addWidget(self._user_field)
        lay.addSpacing(14)
        lay.addWidget(QLabel("Mot de passe", styleSheet=f"color:{COLORS['TXT_SEC']}; font-size:12px;"))
        lay.addSpacing(4)
        lay.addWidget(self._pass_field)

        # Afficher/masquer le mdp
        show_pw = QCheckBox("Afficher le mot de passe")
        show_pw.setStyleSheet(f"color: {COLORS['TXT_SEC']}; font-size: 11px;")
        show_pw.toggled.connect(
            lambda checked: self._pass_field.setEchoMode(
                QLineEdit.EchoMode.Normal if checked
                else QLineEdit.EchoMode.Password))
        lay.addSpacing(8)
        lay.addWidget(show_pw)

        lay.addSpacing(24)

        # ── Bouton connexion ──────────────────────────────────
        self._login_btn = _btn("🔐  Se connecter", COLORS['primary'])
        self._login_btn.clicked.connect(self._do_login)
        lay.addWidget(self._login_btn)

        lay.addSpacing(16)

        # ── Message d'erreur ──────────────────────────────────
        self._error_lbl = QLabel("")
        self._error_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._error_lbl.setWordWrap(True)
        self._error_lbl.setStyleSheet(f"""
            color: {COLORS['danger']};
            font-size: 12px;
            background: {COLORS['danger']}18;
            border-radius: 6px;
            padding: 6px 12px;
        """)
        self._error_lbl.hide()
        lay.addWidget(self._error_lbl)

        lay.addStretch()

        # ── Pied de page ──────────────────────────────────────
        hint = QLabel("Première connexion : admin / admin123")
        hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hint.setStyleSheet(f"color: {COLORS['TXT_SEC']}44; font-size: 10px;")
        lay.addWidget(hint)

    def _do_login(self) -> None:
        """Vérifie les identifiants et ouvre la session si valides."""
        username = self._user_field.text().strip()
        password = self._pass_field.text()

        if not username or not password:
            self._show_error("Veuillez remplir tous les champs.")
            return

        self._login_btn.setEnabled(False)
        self._login_btn.setText("Vérification…")
        QApplication.processEvents()

        try:
            self.db.cursor.execute("""
                SELECT id, username, password_hash, role, is_active
                FROM users WHERE username = ?
            """, (username,))
            row = self.db.cursor.fetchone()

            if row is None:
                self._show_error("Identifiant ou mot de passe incorrect.")
                return

            user_id, uname, stored_hash, role, is_active = (
                row['id'], row['username'], row['password_hash'],
                row['role'], row['is_active']
            ) if hasattr(row, 'keys') else row

            if not is_active:
                self._show_error("Ce compte est désactivé.\nContactez l'administrateur.")
                return

            if not verify_password(password, stored_hash):
                self._show_error("Identifiant ou mot de passe incorrect.")
                return

            # Mettre à jour last_login
            self.db.cursor.execute(
                "UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?",
                (user_id,))
            self.db.conn.commit()

            # Ouvrir la session
            session.login(user_id, uname, role)
            self.login_success.emit()
            self.accept()

        except Exception as e:
            self._show_error(f"Erreur de connexion : {e}")
        finally:
            self._login_btn.setEnabled(True)
            self._login_btn.setText("🔐  Se connecter")

    def _show_error(self, msg: str) -> None:
        """Affiche un message d'erreur sous le formulaire."""
        self._error_lbl.setText(msg)
        self._error_lbl.show()
        # Secouer le champ mot de passe
        self._pass_field.setStyleSheet(self._pass_field.styleSheet().replace(
            COLORS['BORDER'], COLORS['danger']))
        QTimer.singleShot(1500, lambda: self._pass_field.setStyleSheet(
            self._pass_field.styleSheet().replace(COLORS['danger'], COLORS['BORDER'])))


# ──────────────────────────────────────────────────────────────────
# Page de gestion des utilisateurs (admin seulement)
# ──────────────────────────────────────────────────────────────────

class UsersPage(QWidget):
    """Page d'administration des utilisateurs.

    Accessible uniquement au rôle 'admin'. Permet de créer,
    modifier, désactiver et supprimer des comptes utilisateurs.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = get_database()
        self._build_ui()

    def showEvent(self, event):
        """Recharge la liste à chaque affichage."""
        super().showEvent(event)
        self._load_users()

    def _build_ui(self) -> None:
        """Construit l'interface de gestion des utilisateurs."""
        lay = QVBoxLayout(self)
        lay.setContentsMargins(24, 20, 24, 20)
        lay.setSpacing(16)

        # ── En-tête ───────────────────────────────────────────
        hdr = QHBoxLayout()
        title = QLabel("👥 Gestion des Utilisateurs")
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {COLORS['TXT_PRI']};")
        hdr.addWidget(title)
        hdr.addStretch()

        add_btn = _btn("➕  Ajouter", COLORS['success'], 38)
        add_btn.setFixedWidth(130)
        add_btn.clicked.connect(self._add_user)
        hdr.addWidget(add_btn)
        lay.addLayout(hdr)

        # ── Tableau ───────────────────────────────────────────
        self._table = QTableWidget(0, 6)
        self._table.setHorizontalHeaderLabels([
            "Utilisateur", "Rôle", "Statut", "Dernière connexion", "", ""
        ])
        hh = self._table.horizontalHeader()
        hh.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        hh.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        hh.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        hh.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        hh.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        hh.setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)
        self._table.setColumnWidth(1, 130)
        self._table.setColumnWidth(2, 90)
        self._table.setColumnWidth(4, 80)
        self._table.setColumnWidth(5, 80)
        self._table.verticalHeader().setVisible(False)
        self._table.setAlternatingRowColors(True)
        self._table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows)
        self._table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers)
        self._table.setStyleSheet(f"""
            QTableWidget {{
                background: {COLORS['BG_CARD']};
                alternate-background-color: {COLORS['BG_DEEP']};
                color: {COLORS['TXT_PRI']};
                border: 1px solid {COLORS['BORDER']};
                border-radius: 8px;
                font-size: 12px;
                gridline-color: {COLORS['BORDER']};
            }}
            QHeaderView::section {{
                background: {COLORS['BG_DEEP']};
                color: {COLORS['primary']};
                font-weight: bold;
                font-size: 11px;
                padding: 8px;
                border: none;
                border-bottom: 2px solid {COLORS['primary']};
            }}
            QTableWidget::item:selected {{
                background: {COLORS['primary']}33;
            }}
        """)
        lay.addWidget(self._table)

        # ── Info mdp par défaut ───────────────────────────────
        info = QLabel("💡  Mot de passe par défaut des nouveaux comptes : Erp@2024")
        info.setStyleSheet(f"""
            color: {COLORS['TXT_SEC']};
            font-size: 11px;
            background: {COLORS['info']}18;
            border-radius: 6px;
            padding: 8px 14px;
        """)
        lay.addWidget(info)

    def _load_users(self) -> None:
        """Charge et affiche tous les utilisateurs depuis la base."""
        try:
            self.db.cursor.execute("""
                SELECT id, username, role, is_active,
                       COALESCE(last_login, '—') as last_login
                FROM users ORDER BY role, username
            """)
            rows = self.db.cursor.fetchall()
        except Exception as e:
            print(f"❌ _load_users: {e}")
            return

        self._table.setRowCount(0)
        for row in rows:
            try:
                uid      = row['id']          if hasattr(row, 'keys') else row[0]
                uname    = row['username']     if hasattr(row, 'keys') else row[1]
                role     = row['role']         if hasattr(row, 'keys') else row[2]
                active   = bool(row['is_active'] if hasattr(row, 'keys') else row[3])
                last_log = row['last_login']   if hasattr(row, 'keys') else row[4]
            except Exception:
                continue

            r = self._table.rowCount()
            self._table.insertRow(r)
            self._table.setRowHeight(r, 44)

            # Nom
            name_item = QTableWidgetItem(f"  {uname}")
            name_item.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
            name_item.setData(Qt.ItemDataRole.UserRole, uid)
            self._table.setItem(r, 0, name_item)

            # Badge rôle
            role_color = ROLE_COLORS.get(role, "#AAAAAA")
            role_icon  = ROLE_ICONS.get(role, "👤")
            role_label = ROLE_LABELS.get(role, role)
            role_item  = QTableWidgetItem(f"  {role_icon}  {role_label}")
            role_item.setForeground(QColor(role_color))
            role_item.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
            self._table.setItem(r, 1, role_item)

            # Statut
            status_item = QTableWidgetItem("✅ Actif" if active else "🔒 Inactif")
            status_item.setForeground(
                QColor(COLORS['success']) if active else QColor(COLORS['danger']))
            status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self._table.setItem(r, 2, status_item)

            # Dernière connexion
            conn_item = QTableWidgetItem(str(last_log)[:16])
            conn_item.setForeground(QColor(COLORS['TXT_SEC']))
            self._table.setItem(r, 3, conn_item)

            # Bouton Modifier
            edit_btn = _btn("✏️ Modifier", COLORS['info'], 32)
            edit_btn.setFixedWidth(78)
            edit_btn.clicked.connect(
                lambda _, i=uid, n=uname, ro=role, a=active: self._edit_user(i, n, ro, a))
            self._table.setCellWidget(r, 4, self._wrap(edit_btn))

            # Bouton Supprimer (grisé pour l'admin lui-même)
            del_btn = _btn("🗑", COLORS['danger'], 32)
            del_btn.setFixedWidth(40)
            if uname == session.username:
                del_btn.setEnabled(False)
                del_btn.setToolTip("Impossible de supprimer votre propre compte")
            else:
                del_btn.clicked.connect(
                    lambda _, i=uid, n=uname: self._delete_user(i, n))
            self._table.setCellWidget(r, 5, self._wrap(del_btn))

    def _wrap(self, widget: QWidget) -> QWidget:
        """Centre un widget dans une cellule de tableau."""
        w = QWidget()
        h = QHBoxLayout(w)
        h.setContentsMargins(4, 4, 4, 4)
        h.addStretch()
        h.addWidget(widget)
        h.addStretch()
        w.setStyleSheet("background: transparent;")
        return w

    def _add_user(self) -> None:
        """Ouvre le dialogue de création d'un nouvel utilisateur."""
        dlg = UserFormDialog(parent=self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            data = dlg.get_data()
            try:
                pw_hash = hash_password(data['password'])
                self.db.cursor.execute("""
                    INSERT INTO users (username, password_hash, role, is_active)
                    VALUES (?, ?, ?, 1)
                """, (data['username'], pw_hash, data['role']))
                self.db.conn.commit()
                QMessageBox.information(self, "Succès",
                    f"✅ Utilisateur « {data['username']} » créé.")
                self._load_users()
            except Exception as e:
                if "UNIQUE" in str(e):
                    QMessageBox.critical(self, "Erreur",
                        "Ce nom d'utilisateur est déjà utilisé.")
                else:
                    QMessageBox.critical(self, "Erreur", str(e))

    def _edit_user(self, uid: int, username: str,
                   role: str, is_active: bool) -> None:
        """Ouvre le dialogue de modification d'un utilisateur."""
        dlg = UserFormDialog(uid, username, role, is_active, parent=self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            data = dlg.get_data()
            try:
                if data.get('password'):
                    pw_hash = hash_password(data['password'])
                    self.db.cursor.execute("""
                        UPDATE users
                        SET username=?, password_hash=?, role=?, is_active=?
                        WHERE id=?
                    """, (data['username'], pw_hash,
                          data['role'], int(data['is_active']), uid))
                else:
                    self.db.cursor.execute("""
                        UPDATE users SET username=?, role=?, is_active=? WHERE id=?
                    """, (data['username'], data['role'],
                          int(data['is_active']), uid))
                self.db.conn.commit()
                QMessageBox.information(self, "Succès",
                    f"✅ Utilisateur « {data['username']} » mis à jour.")
                self._load_users()
            except Exception as e:
                QMessageBox.critical(self, "Erreur", str(e))

    def _delete_user(self, uid: int, username: str) -> None:
        """Supprime un utilisateur après confirmation."""
        reply = QMessageBox.question(
            self, "Confirmer la suppression",
            f"Supprimer définitivement le compte « {username} » ?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.db.cursor.execute("DELETE FROM users WHERE id=?", (uid,))
                self.db.conn.commit()
                self._load_users()
            except Exception as e:
                QMessageBox.critical(self, "Erreur", str(e))


# ──────────────────────────────────────────────────────────────────
# Formulaire de création / modification d'utilisateur
# ──────────────────────────────────────────────────────────────────

class UserFormDialog(QDialog):
    """Formulaire de création ou modification d'un compte utilisateur.

    Args:
        uid (int | None): ID de l'utilisateur à modifier, None pour création.
        username (str): Nom d'utilisateur pré-rempli en modification.
        role (str): Rôle pré-sélectionné.
        is_active (bool): Statut pré-rempli.
    """

    def __init__(self, uid=None, username="", role="vendeur",
                 is_active=True, parent=None):
        super().__init__(parent)
        self._uid       = uid
        self._is_edit   = uid is not None
        self.setWindowTitle("Modifier l'utilisateur" if self._is_edit
                            else "Créer un utilisateur")
        self.setFixedSize(400, 420 if self._is_edit else 460)
        self.setStyleSheet(f"background: {COLORS['BG_PAGE']};")
        self._build_ui(username, role, is_active)

    def _build_ui(self, username: str, role: str, is_active: bool) -> None:
        """Construit le formulaire."""
        lay = QVBoxLayout(self)
        lay.setContentsMargins(30, 28, 30, 28)
        lay.setSpacing(14)

        title = QLabel("Modifier l'utilisateur" if self._is_edit
                       else "Nouvel utilisateur")
        title.setFont(QFont("Segoe UI", 15, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {COLORS['TXT_PRI']};")
        lay.addWidget(title)

        # Nom d'utilisateur
        lay.addWidget(QLabel("Nom d'utilisateur *",
                             styleSheet=f"color:{COLORS['TXT_SEC']};font-size:12px;"))
        self._uname = _field("ex: jean.dupont")
        self._uname.setText(username)
        lay.addWidget(self._uname)

        # Rôle
        lay.addWidget(QLabel("Rôle *",
                             styleSheet=f"color:{COLORS['TXT_SEC']};font-size:12px;"))
        self._role_cb = QComboBox()
        self._role_cb.setFixedHeight(44)
        self._role_cb.setStyleSheet(f"""
            QComboBox {{
                background: {COLORS['BG_DEEP']};
                border: 1.5px solid {COLORS['BORDER']};
                border-radius: 8px;
                color: {COLORS['TXT_PRI']};
                padding: 0 14px;
                font-size: 13px;
            }}
            QComboBox::drop-down {{ border: none; }}
            QComboBox QAbstractItemView {{
                background: {COLORS['BG_CARD']};
                color: {COLORS['TXT_PRI']};
                selection-background-color: {COLORS['primary']}44;
            }}
        """)
        from auth import ROLE_LABELS, ROLE_ICONS
        for r_key, r_label in ROLE_LABELS.items():
            self._role_cb.addItem(f"{ROLE_ICONS[r_key]}  {r_label}", userData=r_key)
        # Sélectionner le rôle courant
        for i in range(self._role_cb.count()):
            if self._role_cb.itemData(i) == role:
                self._role_cb.setCurrentIndex(i)
                break
        lay.addWidget(self._role_cb)

        # Mot de passe
        pw_label = ("Nouveau mot de passe (laisser vide = inchangé)"
                    if self._is_edit else "Mot de passe *")
        lay.addWidget(QLabel(pw_label,
                             styleSheet=f"color:{COLORS['TXT_SEC']};font-size:12px;"))
        self._pw1 = _field("••••••••", password=True)
        self._pw2 = _field("Confirmer le mot de passe", password=True)
        if not self._is_edit:
            self._pw1.setText("Erp@2024")
            self._pw2.setText("Erp@2024")
        lay.addWidget(self._pw1)
        lay.addWidget(self._pw2)

        # Statut (modification seulement)
        if self._is_edit:
            self._active_cb = QCheckBox("Compte actif")
            self._active_cb.setChecked(is_active)
            self._active_cb.setStyleSheet(f"color: {COLORS['TXT_PRI']}; font-size: 12px;")
            lay.addWidget(self._active_cb)
        else:
            self._active_cb = None

        lay.addStretch()

        # Boutons
        btn_row = QHBoxLayout()
        cancel  = _btn("Annuler", COLORS['TXT_SEC'], 40)
        cancel.clicked.connect(self.reject)
        save    = _btn("💾  Enregistrer", COLORS['primary'], 40)
        save.clicked.connect(self._validate)
        btn_row.addWidget(cancel)
        btn_row.addWidget(save)
        lay.addLayout(btn_row)

    def _validate(self) -> None:
        """Valide le formulaire avant acceptation."""
        uname = self._uname.text().strip()
        pw1   = self._pw1.text()
        pw2   = self._pw2.text()

        if not uname:
            QMessageBox.warning(self, "Champ manquant",
                                "Le nom d'utilisateur est obligatoire.")
            return
        if len(uname) < 3:
            QMessageBox.warning(self, "Trop court",
                                "Le nom d'utilisateur doit faire au moins 3 caractères.")
            return
        if not self._is_edit and not pw1:
            QMessageBox.warning(self, "Champ manquant",
                                "Le mot de passe est obligatoire.")
            return
        if pw1 and pw1 != pw2:
            QMessageBox.warning(self, "Mots de passe",
                                "Les deux mots de passe ne correspondent pas.")
            return
        if pw1 and len(pw1) < 6:
            QMessageBox.warning(self, "Mot de passe trop court",
                                "Le mot de passe doit faire au moins 6 caractères.")
            return
        self.accept()

    def get_data(self) -> dict:
        """Retourne les données saisies dans le formulaire.

        Returns:
            dict: Clés 'username', 'role', 'password', 'is_active'.
        """
        return {
            'username':  self._uname.text().strip(),
            'role':      self._role_cb.currentData(),
            'password':  self._pw1.text(),
            'is_active': self._active_cb.isChecked() if self._active_cb else True,
        }


# ──────────────────────────────────────────────────────────────────
# Widget badge utilisateur pour la sidebar
# ──────────────────────────────────────────────────────────────────

class UserBadge(QFrame):
    """Badge compact affiché en bas de la sidebar.

    Affiche le nom, le rôle de l'utilisateur connecté
    et un bouton de déconnexion.

    Signals:
        logout_requested: Émis quand l'utilisateur clique sur Déconnexion.
    """

    logout_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            QFrame {{
                background: {COLORS['BG_DEEP']};
                border-radius: 10px;
                border: 1px solid {COLORS['BORDER']};
            }}
        """)
        self._build_ui()

    def _build_ui(self) -> None:
        """Construit le badge."""
        lay = QVBoxLayout(self)
        lay.setContentsMargins(12, 10, 12, 10)
        lay.setSpacing(6)

        # Ligne nom + rôle
        info_row = QHBoxLayout()

        self._icon_lbl = QLabel(session.role_icon)
        self._icon_lbl.setFont(QFont("Segoe UI", 16))
        self._icon_lbl.setFixedWidth(28)
        info_row.addWidget(self._icon_lbl)

        text_col = QVBoxLayout()
        text_col.setSpacing(1)
        self._name_lbl = QLabel(session.display_name)
        self._name_lbl.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        self._name_lbl.setStyleSheet(f"color: {COLORS['TXT_PRI']}; border: none;")
        text_col.addWidget(self._name_lbl)

        self._role_lbl = QLabel(session.role_label)
        self._role_lbl.setFont(QFont("Segoe UI", 9))
        self._role_lbl.setStyleSheet(
            f"color: {session.role_color}; border: none; font-weight: bold;")
        text_col.addWidget(self._role_lbl)
        info_row.addLayout(text_col)
        info_row.addStretch()
        lay.addLayout(info_row)

        # Bouton déconnexion
        logout_btn = QPushButton("🚪  Déconnexion")
        logout_btn.setFixedHeight(28)
        logout_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        logout_btn.setStyleSheet(f"""
            QPushButton {{
                background: {COLORS['danger']}18;
                color: {COLORS['danger']};
                border: 1px solid {COLORS['danger']}44;
                border-radius: 6px;
                font-size: 10px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background: {COLORS['danger']}33;
            }}
        """)
        logout_btn.clicked.connect(self.logout_requested.emit)
        lay.addWidget(logout_btn)