from io import BytesIO
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)
from reportlab.lib.units import cm


def create_pdf(data):

    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=25,
        leftMargin=25,
        topMargin=0,
        bottomMargin=0
    )

    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        name='HeaderBlue',
        fontSize=16,
        textColor=colors.HexColor("#0d47a1"),
        alignment=1,
        spaceAfter=4
    ))

    styles.add(ParagraphStyle(
        name='SubHeader',
        fontSize=12,
        textColor=colors.HexColor("#0d47a1"),
        spaceAfter=4,
        fontName='Helvetica-Bold'
    ))

    styles.add(ParagraphStyle(
        name='NormalSmall',
        fontSize=8,
        leading=12
    ))

    elements = []

    def fmt_rp(x):
        return f"Rp {x:,.0f}"

    def pct_of_total(x):
        try:
            if data["total_cost"] > 0:
                return f" ({(x / data['total_cost']) * 100:.1f}%)"
            return " (0%)"
        except:
            return " (0%)"

    # ===== HEADER =====
    title = Paragraph(
        "<b>Freight Calculation Report</b>",
        styles['HeaderBlue']
    )

    elements.append(title)
    elements.append(Spacer(1, 2))

    # ===== VOYAGE =====
    elements.append(Paragraph(
        "Voyage Information",
        styles['SubHeader']
    ))

    voyage_data = [
        ["Port Of Loading", data["port_pol"]],
        ["Port Of Discharge", data["port_pod"]],
        ["Next Port", data["next_port"]],
        ["Cargo Quantity", f"{data['qyt_cargo']:,.0f} {data['type_cargo']}"],
        ["Distance (NM)", f"{data['distance_pol_pod']:,.0f}"],
        ["Total Voyage (Days)", f"{data['total_voyage_days']:.2f}"],
    ]

    t_voyage = Table(voyage_data, colWidths=[9*cm, 9*cm])

    t_voyage.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.3, colors.grey),
        ('BACKGROUND', (0, 0), (-1, -1), colors.whitesmoke),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
    ]))

    elements += [t_voyage, Spacer(1, 4)]

    # ===== COST =====
    elements.append(Paragraph(
        "Operational & Cost Summary",
        styles['SubHeader']
    ))

    calc_data = [
        ["Total Sailing Time (Hour)", f"{data['sailing_time']:.2f}"],
        ["Total Consumption Fuel (Ltr)", f"{data['total_consumption_fuel']:,.0f}"],
        ["Total Consumption FW (Ton)", f"{data['total_consumption_fw']:,.0f}"],

        ["Fuel Cost", f"{fmt_rp(data['cost_fuel'])}{pct_of_total(data['cost_fuel'])}"],

        ["Freshwater Cost", f"{fmt_rp(data['cost_fw'])}{pct_of_total(data['cost_fw'])}"],

        ["General Overhead", f"{fmt_rp(data['total_general_overhead'])}{pct_of_total(data['total_general_overhead'])}"],
    ]

    for k, v in data["owner_data"].items():

        calc_data.append([
            k,
            f"{fmt_rp(v)}{pct_of_total(v)}"
        ])

    if data["additional_breakdown"]:

        calc_data.append(["--- Additional Cost ---", ""])

        for k, v in data["additional_breakdown"].items():

            calc_data.append([
                k,
                f"{fmt_rp(v)}{pct_of_total(v)}"
            ])

    calc_data.append([
        "Total Cost",
        fmt_rp(data["total_cost"])
    ])

    calc_data.append([
        "Freight Cost / MT",
        fmt_rp(data["freight_cost_mt"])
    ])

    t_calc = Table(calc_data, colWidths=[9*cm, 9*cm])

    t_calc.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.3, colors.grey),
        ('BACKGROUND', (0, -2), (-1, -1), colors.lightgrey),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
    ]))

    elements += [t_calc, Spacer(1, 4)]

    # ===== USER FREIGHT =====
    if data["freight_price_input"] > 0:

        elements.append(Paragraph(
            "Freight Price Calculation User",
            styles['SubHeader']
        ))

        fpc_data = [
            ["Freight Price", fmt_rp(data["freight_price_input"])],
            ["Revenue", fmt_rp(data["revenue_user"])],
            ["PPH 1.2%", fmt_rp(data["pph_user"])],
            ["Profit", fmt_rp(data["profit_user"])],
            ["Profit %", f"{data['profit_percent_user']:.2f}%"],
        ]

        t_fpc = Table(fpc_data, colWidths=[9*cm, 9*cm])

        t_fpc.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.3, colors.grey),
            ('BACKGROUND', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
        ]))

        elements += [t_fpc, Spacer(1, 4)]

    # ===== TCE =====
    elements.append(Paragraph(
        "Time Charter Equivalent (TCE)",
        styles['SubHeader']
    ))

    tce_data = [
        ["Base Cost", fmt_rp(data["tce_base_cost"])],
        ["TCE Per Day", fmt_rp(data["tce_per_day"])],
        ["TCE Per Month", fmt_rp(data["tce_per_month"])],
    ]

    t_tce = Table(tce_data, colWidths=[9*cm, 9*cm])

    t_tce.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.3, colors.grey),
        ('BACKGROUND', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
    ]))

    elements += [t_tce, Spacer(1, 4)]

    # ===== PROFIT SCENARIO =====
    elements.append(Paragraph(
        "Profit Scenario 0–75%",
        styles['SubHeader']
    ))

    profit_table = [data["df_profit"].columns.to_list()] + data["df_profit"].values.tolist()

    t_profit = Table(
        profit_table,
        colWidths=[3*cm, 3.8*cm, 3.8*cm, 3.8*cm, 3.8*cm]
    )

    t_profit.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#0d47a1")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.25, colors.grey),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
    ]))

    elements += [t_profit, Spacer(1, 4)]

    # ===== NOTE SECTION =====
    if data.get("note"):
    
        note_text = f"""
    <b>Note :</b><br/>
    • Fuel Price : Rp {data.get('fuel_price', 0):,.0f} / Ltr<br/>
    • Port Stay POL : {data.get('port_stay_pol', 0)} Days<br/>
    • Port Stay POD : {data.get('port_stay_pod', 0)} Days<br/>
    • Speed Laden : {data.get('speed_laden', 0)} Knot<br/>
    • Speed Ballast : {data.get('speed_ballast', 0)} Knot<br/>
    • Weather Factor : {data.get('weather_factor', 0)}% included in sailing time<br/>
    """
    
        elements.append(Paragraph(note_text, styles['NormalSmall']))
        elements.append(Spacer(1, 6))

    # ===== FOOTER =====
    footer = Paragraph(
        f"Generated by {data['username']}"| https://freight-calculator-mobile.streamlit.app",
        styles['NormalSmall']
    )

    elements.append(footer)

    generated_date = Paragraph(
        f"Generated: {datetime.now().strftime('%d %B %Y')}",
        styles['NormalSmall']
    )

    elements.append(generated_date)

    # ===== BUILD =====
    doc.build(elements)

    buffer.seek(0)

    return buffer
