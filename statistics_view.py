# ─────────────────────────────────────────────────────────────
#  statistics_view.py — Version PRO (Design + Export + Charts)
#  PART 1 / 3
# ─────────────────────────────────────────────────────────────

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QHBoxLayout, QFrame,
    QPushButton, QScrollArea, QSizePolicy, QFileDialog, QMessageBox
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt, QObject, pyqtProperty, QPropertyAnimation, QEasingCurve
import pyqtgraph as pg
import csv
from datetime import datetime
from db_manager import get_database


# ─────────────────────────────────────────────────────────────
#  Palette Colors
# ─────────────────────────────────────────────────────────────

BG_PAGE  = "#0F1117"
BG_CARD  = "#1A1D27"
BG_DEEP  = "#13151F"
BORDER   = "rgba(255,255,255,0.07)"
TXT_PRI  = "#F1F5F9"
TXT_SEC  = "rgba(255,255,255,0.45)"

C_BLUE   = "#3B82F6"
C_GREEN  = "#10B981"
C_AMBER  = "#F59E0B"
C_VIOLET = "#8B5CF6"
C_CYAN   = "#06B6D4"
C_RED    = "#EF4444"

CHART_COLORS = [C_BLUE, C_GREEN, C_AMBER, C_VIOLET, C_CYAN]

CARD_STYLE = f"""
    QFrame {{
        background: {BG_CARD};
        border-radius: 16px;
        border: 1px solid {BORDER};
    }}
"""

MONTHS_FR = ['Jan','Fév','Mar','Avr','Mai','Jun','Jul','Aoû','Sep','Oct','Nov','Déc']


# ─────────────────────────────────────────────────────────────
#  Counter Animation
# ─────────────────────────────────────────────────────────────

class _KpiAnim(QObject):
    def __init__(self, label, suffix=""):
        super().__init__()
        self._v = 0
        self.label = label
        self.suffix = suffix

    def _get(self):
        return self._v

    def _set(self, v):
        self._v = v
        self.label.setText(f"{v:,.0f}{self.suffix}")

    value = pyqtProperty(float, fget=_get, fset=_set)


def count_up(label, target, suffix="", ms=700):
    obj = _KpiAnim(label, suffix)
    anim = QPropertyAnimation(obj, b"value")
    anim.setDuration(ms)
    anim.setStartValue(0.0)
    anim.setEndValue(float(target))
    anim.setEasingCurve(QEasingCurve.Type.OutCubic)
    anim.start()
    label._anim = anim
    label._obj = obj


# ─────────────────────────────────────────────────────────────
#  Helpers UI
# ─────────────────────────────────────────────────────────────

def _sep():
    f = QFrame()
    f.setFrameShape(QFrame.Shape.HLine)
    f.setFixedHeight(1)
    f.setStyleSheet(f"background:{BORDER}; border:none;")
    return f

def _card():
    f = QFrame()
    f.setStyleSheet(CARD_STYLE)
    return f

def _lbl(text, size, bold=False, color=TXT_PRI):
    l = QLabel(text)
    l.setFont(QFont("Segoe UI", size, QFont.Weight.Bold if bold else QFont.Weight.Normal))
    l.setStyleSheet(f"color:{color}; background:transparent;")
    return l

def _styled_plot(bg=BG_DEEP, height=220):
    plot = pg.PlotWidget()
    plot.setBackground(bg)
    plot.setMinimumHeight(height)
    plot.showGrid(x=True, y=True, alpha=0.08)
    plot.setMouseEnabled(x=False, y=False)
    plot.hideButtons()

    axis_pen  = pg.mkPen(color="#ffffff22", width=1)
    label_pen = pg.mkPen(color="#ffffff55")

    for axis in ("bottom", "left"):
        plot.getAxis(axis).setPen(axis_pen)
        plot.getAxis(axis).setTextPen(label_pen)
        plot.getAxis(axis).setStyle(tickFont=QFont("Segoe UI", 8))

    return plot


# ─────────────────────────────────────────────────────────────
#  Main Page Layout
# ─────────────────────────────────────────────────────────────

class StatisticsPage(QWidget):
    def __init__(self):
        super().__init__()

        self.db = get_database()
        self.setStyleSheet(f"background:{BG_PAGE};")

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background:transparent; border:none;")

        container = QWidget()
        container.setStyleSheet("background:transparent;")

        self._lay = QVBoxLayout(container)
        self._lay.setSpacing(22)
        self._lay.setContentsMargins(32, 28, 32, 28)

        # Build Sections
        self._build_header()
        self._build_kpi_row()
        self._build_charts_row()
        self._build_bottom_row()

        self._lay.addStretch()
        scroll.setWidget(container)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.addWidget(scroll)

        # Load Data
        self.refresh()


    # ─────────────────────────────────────────────────────────
    #  Header
    # ─────────────────────────────────────────────────────────

    def _build_header(self):
        row = QHBoxLayout()
        row.setSpacing(14)

        col = QVBoxLayout()
        col.addWidget(_lbl("Statistiques & Analytique", 24, bold=True))
        col.addWidget(_lbl("Vue générale de votre commerce", 11, color=TXT_SEC))
        row.addLayout(col)
        row.addStretch()

        # Année badge
        year_badge = QLabel(str(datetime.now().year))
        year_badge.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        year_badge.setStyleSheet(f"""
            background: rgba(59,130,246,0.15);
            color: {C_BLUE};
            padding: 4px 14px;
            border-radius: 8px;
            border: 1px solid rgba(59,130,246,0.35);
        """)
        row.addWidget(year_badge)

        # Refresh Button
        btn = QPushButton("↻   Actualiser")
        btn.setFixedHeight(36)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setStyleSheet(f"""
            QPushButton {{
                background:{C_BLUE}; color:white; border:none;
                border-radius:8px; padding:0 18px;
            }}
            QPushButton:hover {{ background:#2563EB; }}
        """)
        btn.clicked.connect(self.refresh)
        row.addWidget(btn)

        # Export CSV
        csv_btn = QPushButton("📥 Export CSV")
        csv_btn.setFixedHeight(36)
        csv_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        csv_btn.setStyleSheet(f"""
            QPushButton {{
                background:transparent; color:{C_GREEN};
                border:1.3px solid {C_GREEN};
                border-radius:8px;
                padding:0 14px;
            }}
        """)
        csv_btn.clicked.connect(self._export_csv)
        row.addWidget(csv_btn)

        # Export Excel Ultimate
        xls_btn = QPushButton("📊 Export Excel PRO+")
        xls_btn.setFixedHeight(36)
        xls_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        xls_btn.setStyleSheet(f"""
            QPushButton {{
                background:transparent; color:{C_AMBER};
                border:1.3px solid {C_AMBER};
                border-radius:8px;
                padding:0 14px;
            }}
        """)
        xls_btn.clicked.connect(self._export_excel_pro_plus)
        row.addWidget(xls_btn)

        # Export PDF
        pdf_btn = QPushButton("📄 Export PDF PRO")
        pdf_btn.setFixedHeight(36)
        pdf_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        pdf_btn.setStyleSheet(f"""
            QPushButton {{
                background:transparent; color:{C_VIOLET};
                border:1.3px solid {C_VIOLET};
                border-radius:8px;
                padding:0 14px;
            }}
        """)
        pdf_btn.clicked.connect(self._export_pdf_pro)
        row.addWidget(pdf_btn)

        self._lay.addLayout(row)


    # ─────────────────────────────────────────────────────────
    # KPI Row
    # ─────────────────────────────────────────────────────────

    def _build_kpi_row(self):
        row = QHBoxLayout()
        row.setSpacing(16)

        specs = [
            ("Chiffre d'Affaires", C_BLUE,   "💳", " DA"),
            ("Profit Net",         C_GREEN,  "📈", " DA"),
            ("Commandes",          C_AMBER,  "🛒", ""),
            ("Clients Actifs",     C_VIOLET, "👥", ""),
        ]

        self._kpi_cards = []

        for title, color, icon, suffix in specs:
            card = self._make_kpi(icon, title, color, suffix)
            row.addWidget(card)
            self._kpi_cards.append(card)

        self._lay.addLayout(row)


    def _make_kpi(self, icon, title, color, suffix):
        card = _card()
        card.setFixedHeight(120)

        lay = QVBoxLayout(card)
        lay.setContentsMargins(18, 14, 18, 14)
        lay.setSpacing(8)

        top = QHBoxLayout()
        badge = QLabel(icon)
        badge.setFont(QFont("Segoe UI", 14))
        badge.setFixedSize(32, 32)
        badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        badge.setStyleSheet(f"background:{color}22; border-radius:8px;")
        top.addWidget(badge)
        top.addSpacing(8)
        top.addWidget(_lbl(title, 10, color=TXT_SEC))
        top.addStretch()
        lay.addLayout(top)

        val_lbl = _lbl("0", 26, bold=True, color=color)
        lay.addWidget(val_lbl)

        card.value_label = val_lbl
        card._suffix = suffix

        return card


# =============================================================
#  END OF PART 1 / 3
# =============================================================

# ─────────────────────────────────────────────────────────────
#  statistics_view.py — PART 2 / 3
# ─────────────────────────────────────────────────────────────


    # ─────────────────────────────────────────────────────────
    # Charts Row
    # ─────────────────────────────────────────────────────────

    def _build_charts_row(self):
        row = QHBoxLayout()
        row.setSpacing(16)

        # Graphique des ventes
        sales_card, self.sales_chart = self._make_chart_card(
            "Évolution des Ventes", C_BLUE, 240
        )
        row.addWidget(sales_card, 3)

        # Graphique des profits
        profit_card, self.profit_chart = self._make_chart_card(
            "Profit Mensuel", C_GREEN, 240
        )
        row.addWidget(profit_card, 2)

        self._lay.addLayout(row)


    def _make_chart_card(self, title, accent, height):
        card = _card()
        lay = QVBoxLayout(card)
        lay.setContentsMargins(18, 14, 18, 14)
        lay.setSpacing(12)

        hdr = QHBoxLayout()
        dot = QFrame()
        dot.setFixedSize(8, 8)
        dot.setStyleSheet(f"background:{accent}; border-radius:4px;")
        hdr.addWidget(dot)
        hdr.addSpacing(8)
        hdr.addWidget(_lbl(title, 12, bold=True))
        hdr.addStretch()
        lay.addLayout(hdr)

        lay.addWidget(_sep())

        plot = _styled_plot(height=height)
        lay.addWidget(plot)

        return card, plot


    # ─────────────────────────────────────────────────────────
    # Bottom Row (Top Produits + Top Clients + Info Cards)
    # ─────────────────────────────────────────────────────────

    def _build_bottom_row(self):
        row = QHBoxLayout()
        row.setSpacing(16)

        # Top produits
        prod_card, self.products_chart = self._make_chart_card(
            "Top 5 Produits", C_AMBER, 200
        )
        row.addWidget(prod_card, 2)

        # Top clients
        cli_card, self.clients_chart = self._make_chart_card(
            "Top 5 Clients", C_VIOLET, 200
        )
        row.addWidget(cli_card, 2)

        # Infos rapides
        col = QVBoxLayout()
        col.setSpacing(14)

        infos = [
            ("Stock Faible", "0 produit", C_RED, "⚠️"),
            ("Panier Moyen", "0 DA", C_CYAN, "💳"),
            ("Meilleur Jour", "—", C_GREEN, "📅"),
        ]

        self._info_cards = []

        for title, val, color, icon in infos:
            c = self._make_info_card(icon, title, val, color)
            col.addWidget(c)
            self._info_cards.append(c)

        row.addLayout(col, 1)

        self._lay.addLayout(row)


    def _make_info_card(self, icon, title, value, color):
        card = _card()
        card.setFixedHeight(90)

        lay = QHBoxLayout(card)
        lay.setContentsMargins(14, 10, 14, 10)
        lay.setSpacing(12)

        badge = QLabel(icon)
        badge.setFont(QFont("Segoe UI", 18))
        badge.setFixedSize(40, 40)
        badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        badge.setStyleSheet(f"background:{color}22; border-radius:10px;")
        lay.addWidget(badge)

        txt = QVBoxLayout()
        txt.addWidget(_lbl(title, 10, color=TXT_SEC))
        val_lbl = _lbl(value, 14, bold=True, color=color)
        txt.addWidget(val_lbl)
        lay.addLayout(txt)

        lay.addStretch()
        card.value_label = val_lbl
        return card


    # ─────────────────────────────────────────────────────────
    # Refresh Data
    # ─────────────────────────────────────────────────────────

    def refresh(self):
        self._load_kpis()
        self._load_sales_chart()
        self._load_profit_chart()
        self._load_top_products()
        self._load_top_clients()
        self._load_quick_info()


    # ─────────────────────────────────────────────────────────
    # KPI Loader
    # ─────────────────────────────────────────────────────────

    def _load_kpis(self):
        stats = self.db.get_statistics() or {}

        sales_total = float(stats.get("sales_total", 0))
        purchases_total = float(stats.get("purchases_total", 0))
        profit = sales_total - purchases_total

        clients = int(stats.get("total_clients", 0))
        orders = int(stats.get("total_purchases", 0))

        values = [
            (sales_total, " DA"),
            (profit, " DA"),
            (orders, ""),
            (clients, "")
        ]

        for card, (val, suf) in zip(self._kpi_cards, values):
            count_up(card.value_label, val, suf)


    # ─────────────────────────────────────────────────────────
    # Graph: Ventes Mensuelles
    # ─────────────────────────────────────────────────────────

    def _load_sales_chart(self):
        self.sales_chart.clear()
        year = datetime.now().year
        data = self.db.get_sales_by_month(year) or []

        months = list(range(1,13))
        values = [0]*12

        for row in data:
            idx = int(row.get("month",0))-1
            if 0 <= idx < 12:
                values[idx] = float(row.get("total",0))

        pen = pg.mkPen(color=C_BLUE, width=2.5)
        brush = pg.mkBrush(color=(59,130,246,40))

        self.sales_chart.plot(
            months, values,
            pen=pen,
            fillLevel=0,
            brush=brush,
            symbol='o',
            symbolSize=6,
            symbolBrush=C_BLUE,
            symbolPen=pg.mkPen(color=BG_CARD, width=2)
        )
        self.sales_chart.getAxis('bottom').setTicks(
            [list(zip(months, MONTHS_FR))]
        )


    # ─────────────────────────────────────────────────────────
    # Graph: Profit Mensuel
    # ─────────────────────────────────────────────────────────

    def _load_profit_chart(self):
        self.profit_chart.clear()
        year = datetime.now().year
        data = self.db.get_profit_by_month(year) or []

        months = list(range(1,13))
        values = [0]*12

        for row in data:
            idx = int(row.get("month",0))-1
            if 0 <= idx < 12:
                values[idx] = float(row.get("profit",0))

        for i, v in enumerate(values):
            color = C_GREEN if v >= 0 else C_RED
            bar = pg.BarGraphItem(
                x=[i+1], height=[v], width=0.55,
                brush=pg.mkBrush(color+"AA"),
                pen=pg.mkPen(color, width=0)
            )
            self.profit_chart.addItem(bar)

        self.profit_chart.getAxis('bottom').setTicks(
            [list(zip(months, MONTHS_FR))]
        )


    # ─────────────────────────────────────────────────────────
    # Graph: Top Products
    # ─────────────────────────────────────────────────────────

    def _load_top_products(self):
        self.products_chart.clear()
        data = self.db.get_top_products(limit=5) or []

        if not data:
            return

        names  = [p["name"][:12] for p in data]
        values = [float(p["total_quantity"]) for p in data]

        for i, (v, c) in enumerate(zip(values, CHART_COLORS)):
            bar = pg.BarGraphItem(
                x=[i], height=[v], width=0.6,
                brush=pg.mkBrush(c+"CC"),
                pen=pg.mkPen(c, width=0)
            )
            self.products_chart.addItem(bar)

        self.products_chart.getAxis("bottom").setTicks(
            [list(zip(range(len(names)), names))]
        )
        self.products_chart.setXRange(-0.5, len(values)-0.5)


    # ─────────────────────────────────────────────────────────
    # Graph: Top Clients
    # ─────────────────────────────────────────────────────────

    def _load_top_clients(self):
        self.clients_chart.clear()
        data = self.db.get_top_clients(limit=5) or []

        if not data:
            return

        names  = [c["name"][:12] for c in data]
        values = [float(c["total_amount"]) for c in data]
        colors = [C_VIOLET, C_BLUE, C_CYAN, C_GREEN, C_AMBER]

        for i, (v, c) in enumerate(zip(values, colors)):
            bar = pg.BarGraphItem(
                x=[i], height=[v], width=0.6,
                brush=pg.mkBrush(c+"CC"),
                pen=pg.mkPen(c, width=0)
            )
            self.clients_chart.addItem(bar)

        self.clients_chart.getAxis("bottom").setTicks(
            [list(zip(range(len(names)), names))]
        )
        self.clients_chart.setXRange(-0.5, len(values)-0.5)


    # ─────────────────────────────────────────────────────────
    # Info rapide
    # ─────────────────────────────────────────────────────────

    def _load_quick_info(self):
        stats = self.db.get_statistics() or {}

        # Stock faible
        low = self.db.get_low_stock_products() or []
        n = len(low)
        self._info_cards[0].value_label.setText(
            f"{n} produit{'s' if n != 1 else ''}"
        )

        # Panier moyen
        sales_total = float(stats.get("sales_total", 0))
        num_sales = int(stats.get("total_sales", 1)) or 1
        avg = sales_total / num_sales
        self._info_cards[1].value_label.setText(f"{avg:,.0f} DA")

        # Meilleur jour
        best_day = self.db.get_best_day()
        self._info_cards[2].value_label.setText(best_day)


    # ─────────────────────────────────────────────────────────
    # Export CSV
    # ─────────────────────────────────────────────────────────

    def _export_csv(self):
        from datetime import datetime as dt

        path, _ = QFileDialog.getSaveFileName(
            self,
            "Exporter CSV",
            f"statistiques_{dt.now().strftime('%Y%m%d')}.csv",
            "Fichiers CSV (*.csv)"
        )
        if not path:
            return
        if not path.endswith(".csv"):
            path += ".csv"

        stats = self.db.get_statistics() or {}
        year  = dt.now().year

        MOIS = [
            "Janvier","Février","Mars","Avril","Mai","Juin",
            "Juillet","Août","Septembre","Octobre","Novembre","Décembre"
        ]

        try:
            with open(path, "w", newline="", encoding="utf-8-sig") as f:
                w = csv.writer(f, delimiter=';')

                w.writerow(["=== KPI GLOBAUX ==="])
                w.writerow(["Indicateur", "Valeur"])
                w.writerow(["CA Total", stats.get("sales_total", 0)])
                w.writerow(["Achats Totaux", stats.get("purchases_total", 0)])
                w.writerow(["Profit Net", stats.get("profit", 0)])
                w.writerow(["Clients", stats.get("total_clients", 0)])
                w.writerow(["Produits", stats.get("total_products", 0)])
                w.writerow([])

                w.writerow([f"=== VENTES MENSUELLES {year} ==="])
                w.writerow(["Mois", "Nombre", "Montant"])

                monthly = {
                    int(r["month"]): r
                    for r in (self.db.get_sales_by_month(year) or [])
                }

                for m in range(1,13):
                    r = monthly.get(m, {"count":0, "total":0})
                    w.writerow([
                        MOIS[m-1],
                        r.get("count",0),
                        r.get("total",0)
                    ])

            QMessageBox.information(self,"Export OK",f"Export réussi :\n{path}")

        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Impossible d'exporter :\n{e}")



# =============================================================
#  END OF PART 2 / 3
# =============================================================

# ─────────────────────────────────────────────────────────────
#  statistics_view.py — PART 3 / 3
# ─────────────────────────────────────────────────────────────

    # ======================================================================
    # EXPORT EXCEL PRO+ (Feuilles séparées + Pivot Table + Dégradé + Images)
    # ======================================================================

    def _export_excel_pro_plus(self):
        import tempfile, os
        import xlsxwriter
        from PyQt6.QtWidgets import QMessageBox
        import pyqtgraph.exporters as exporters

        # Choisir chemin sortie
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Exporter Excel PRO+",
            "rapport_erp.xlsx",
            "Excel Files (*.xlsx)"
        )
        if not path:
            return

        # Dossier temporaire
        temp_dir = tempfile.mkdtemp()

        # Fonction sauvegarde graphique
        def save_chart(widget, filename):
            exporter = exporters.ImageExporter(widget.plotItem)
            exporter.export(filename)

        # Sauvegarde images
        img_sales   = os.path.join(temp_dir, "sales.png")
        img_profit  = os.path.join(temp_dir, "profit.png")
        img_prod    = os.path.join(temp_dir, "products.png")
        img_clients = os.path.join(temp_dir, "clients.png")

        save_chart(self.sales_chart, img_sales)
        save_chart(self.profit_chart, img_profit)
        save_chart(self.products_chart, img_prod)
        save_chart(self.clients_chart, img_clients)

        # Créer Excel
        workbook = xlsxwriter.Workbook(path)

        # Styles
        title_fmt = workbook.add_format({
            "bold": True, "font_size": 18,
            "align": "center", "valign": "vcenter"
        })
        header_fmt = workbook.add_format({
            "bold": True, "bg_color": "#3B82F6",
            "font_color": "white", "border": 1,
            "align": "center"
        })
        normal_fmt = workbook.add_format({"border": 1})

        # ==================================================================
        # FEUILLE PRINCIPALE (DASHBOARD)
        # ==================================================================

        dash = workbook.add_worksheet("Dashboard")

        dash.merge_range("A1:E1", "Rapport Statistique – ERP", title_fmt)

        # KPI
        dash.write_row("A3", ["KPI", "Valeur"], header_fmt)

        kpi_names = ["CA Total", "Profit Net", "Commandes", "Clients Actifs"]

        for i, card in enumerate(self._kpi_cards):
            dash.write(i+3, 0, kpi_names[i], normal_fmt)
            dash.write(i+3, 1, card.value_label.text(), normal_fmt)

        # Dégradé automatique
        dash.conditional_format("B4:B7", {
            "type": "2_color_scale",
            "min_color": "#DBEAFE",
            "max_color": "#3B82F6"
        })

        # ==================================================================
        # FEUILLES DES GRAPHIQUES (1 feuille = 1 graphique)
        # ==================================================================

        charts = [
            ("Ventes", img_sales),
            ("Profit", img_profit),
            ("Top Produits", img_prod),
            ("Top Clients", img_clients)
        ]

        for sheet_name, img in charts:
            ws = workbook.add_worksheet(sheet_name)
            ws.set_column("A:A", 55)
            ws.insert_image("A1", img, {"x_scale": 0.8, "y_scale": 0.8})

        # ==================================================================
        # FEUILLE TABLEAU CROISÉ DYNAMIQUE (PIVOT TABLE)
        # ==================================================================

        pivot_raw = workbook.add_worksheet("Données Brut")
        pivot_tab = workbook.add_worksheet("Pivot")

        # Charger données mensuelles
        year = datetime.now().year
        rows = self.db.get_sales_by_month(year) or []

        # Écrire données brutes
        pivot_raw.write_row(0,0,["Mois","Total"])

        r = 1
        for row in rows:
            pivot_raw.write(r,0, row.get("month",0))
            pivot_raw.write(r,1, row.get("total",0))
            r += 1

        data_range = f"'Données Brut'!A1:B{r}"

        # Créer un tableau (base pivot)
        pivot_tab.add_table(0,0, r, 3, {
            "data": data_range,
            "columns": [
                {"header":"Mois"},
                {"header":"Total"}
            ]
        })

        # ==================================================================
        # FIN — sauvegarder
        # ==================================================================

        workbook.close()
        QMessageBox.information(self, "Export OK", f"Excel PRO+ généré :\n{path}")



    # ======================================================================
    # EXPORT PDF PROFESSIONNEL (avec images HD)
    # ======================================================================

    def _export_pdf_pro(self):
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.units import cm
        import tempfile, os
        import pyqtgraph.exporters as exporters

        path, _ = QFileDialog.getSaveFileName(
            self,
            "Exporter PDF",
            "rapport_erp.pdf",
            "PDF Files (*.pdf)"
        )
        if not path:
            return

        temp_dir = tempfile.mkdtemp()

        # Export charts
        def save_chart(widget, filename):
            exporter = exporters.ImageExporter(widget.plotItem)
            exporter.export(filename)

        img_sales   = os.path.join(temp_dir, "sales.png")
        img_profit  = os.path.join(temp_dir, "profit.png")
        img_prod    = os.path.join(temp_dir, "prod.png")
        img_clients = os.path.join(temp_dir, "clients.png")

        save_chart(self.sales_chart, img_sales)
        save_chart(self.profit_chart, img_profit)
        save_chart(self.products_chart, img_prod)
        save_chart(self.clients_chart, img_clients)

        # Build PDF
        doc = SimpleDocTemplate(path, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []

        story.append(Paragraph("<b>Rapport ERP — Analyse Professionnelle</b>", styles["Title"]))
        story.append(Spacer(1, 12))

        graphs = [
            ("Évolution des Ventes", img_sales),
            ("Profit Mensuel", img_profit),
            ("Top Produits", img_prod),
            ("Top Clients", img_clients)
        ]

        for title, img in graphs:
            story.append(Paragraph(f"<b>{title}</b>", styles["Heading2"]))
            story.append(Image(img, width=16*cm, height=8*cm))
            story.append(Spacer(1, 12))

        doc.build(story)

        QMessageBox.information(self,"PDF OK",f"PDF professionnel généré :\n{path}")



# =============================================================
#  END OF PART 3 / 3 — FULL FILE COMPLETED
# =============================================================