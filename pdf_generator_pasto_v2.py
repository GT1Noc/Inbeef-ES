from fpdf import FPDF
import io
from datetime import datetime
from config_pasto_v2 import LOGO_PATH

class PDFReport(FPDF):
    def header(self):
        # Logo
        if LOGO_PATH.exists():
            self.image(str(LOGO_PATH), x=10, y=8, w=25)
        # Título principal
        self.set_font("Arial", "B", 16)
        self.cell(0, 10, "Informe Comparativo Inbra", ln=1, align="C")
        # Subtítulo
        self.set_font("Arial", "B", 14)
        self.cell(0, 8, "Inbeef", ln=1, align="C")
        # Data y proyección
        self.set_font("Arial", "", 10)
        subtitle = f"Proyección para {self.dias} días | Fecha del análisis: {datetime.now().strftime('%d/%m/%Y')}"
        self.cell(0, 6, subtitle, ln=1, align="C")
        self.ln(4)


def formatar_reais(valor, casas_decimais=2):
    try:
        v = float(valor)
        if casas_decimais == 0:
            valor_int = int(round(v))
            s = f"{valor_int:,}".replace(",", "X").replace(".", ",").replace("X", ".")
            return s
        else:
            s = f"{v:,.{casas_decimais}f}".replace(",", "X").replace(".", ",").replace("X", ".")
            return s
    except:
        return "0" if casas_decimais == 0 else "0,00"


def render_pdf(dados):
    pdf = PDFReport()
    pdf.dias = dados.get('dias', 0)
    pdf.add_page()

    # Parámetros de Entrada
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, "Parámetros de Entrada", ln=1)
    y0 = pdf.get_y()
    pdf.set_draw_color(200, 200, 200)
    pdf.rect(10, y0, 190, 60)
    pdf.ln(2)

    input_labels = [
        "Número de días",
        "Valor del kg de peso vivo (US$)",
        "Número de animales",
        "Costo diario estándar (US$)/animal",
        "Costo diario con Inbeef (US$)/animal",
        "GMD Estándar (g/día)",
        "Expectativa GMD adicional (g/día)"
    ]
    input_vals = [
        str(dados.get('dias', 0)),
        f"US$ {formatar_reais(dados.get('valor_kg_recria', 0))}",
        str(dados.get('num_animais', 0)),
        f"US$ {formatar_reais(dados.get('custo_padrao_diario', 0))}",
        f"US$ {formatar_reais(dados.get('custo_inbeef_diario', 0))}",
        f"{dados.get('gmd_padrao', 0):.2f} g/día",
        f"{dados.get('expectativa_gmd', 0):.2f} g/día"
    ]
    pdf.set_font("Courier", "", 10)
    line_h = 6
    col_width = pdf.w - pdf.l_margin - pdf.r_margin
    val_width = 50
    y_start = y0 + 2
    for i, (lab, val) in enumerate(zip(input_labels, input_vals)):
        pdf.set_xy(pdf.l_margin, y_start + i * line_h)
        pdf.set_font("Courier", "B", 10)
        pdf.cell(col_width - val_width, line_h, f"{lab}:", border=0, ln=0)
        pdf.set_font("Courier", "", 10)
        pdf.set_x(pdf.l_margin + col_width - val_width)
        pdf.cell(val_width, line_h, val, border=0, align="R")
    pdf.ln(30)

    # Resultados
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, "Resultados", ln=1)
    y_frame = pdf.get_y()
    pdf.set_draw_color(200, 200, 200)
    frame_height = 4 * 6 + 4
    pdf.rect(10, y_frame, 190, frame_height)
    pdf.ln(2)

    col1_labels = [
        "Costo diario estándar (US$)",
        "Costo total suplemento estándar (US$)",
        "Diferencia de inversión animal/día (US$)",
        "Ganancia neta por animal (US$)"
    ]
    col1_vals = [
        f"US$ {formatar_reais(dados.get('costo_padrao_diario', 0))}",
        f"US$ {formatar_reais(dados.get('custo_total_padrao', 0), 0)}",
        f"US$ {formatar_reais(dados.get('diferenca_investimento', 0))}",
        f"US$ {formatar_reais(dados.get('ganho_liq_por_animal', 0))}"
    ]

    col2_labels = [
        "Costo diario con Inbeef (US$)",
        "Costo total suplemento Inbeef (US$)",
        "Punto de equilibrio (g/día)",
        "Retorno sobre la inversión (x)"
    ]
    col2_vals = [
        f"US$ {formatar_reais(dados.get('costo_inbeef_diario', 0))}",
        f"US$ {formatar_reais(dados.get('custo_total_inbeef', 0), 0)}",
        f"{dados.get('punto_equilibrio', 0):.2f} g/día",
        f"{dados.get('retorno_inbeef', 0):.2f} x"
    ]

    # Columna 1
    pdf.set_font("Courier", "", 10)
    for i, (lab, val) in enumerate(zip(col1_labels, col1_vals)):
        pdf.set_xy(pdf.l_margin, y_frame + 2 + i * line_h)
        pdf.set_font("Courier", "B", 10)
        pdf.cell((pdf.w - pdf.l_margin - pdf.r_margin) / 2 - val_width, line_h, f"{lab}:", border=0, ln=0)
        pdf.set_font("Courier", "", 10)
        pdf.set_x(pdf.l_margin + (pdf.w - pdf.l_margin - pdf.r_margin) / 2 - val_width)
        pdf.cell(val_width, line_h, val, border=0, align="R")

    # Columna 2
    for i, (lab, val) in enumerate(zip(col2_labels, col2_vals)):
        pdf.set_xy(pdf.l_margin + (pdf.w - pdf.l_margin - pdf.r_margin) / 2, y_frame + 2 + i * line_h)
        pdf.set_font("Courier", "B", 10)
        pdf.cell((pdf.w - pdf.l_margin - pdf.r_margin) / 2 - val_width, line_h, f"{lab}:", border=0, ln=0)
        pdf.set_font("Courier", "", 10)
        pdf.set_x(pdf.l_margin + (pdf.w - pdf.l_margin - pdf.r_margin) - val_width)
        pdf.cell(val_width, line_h, val, border=0, align="R")

    pdf.ln(frame_height + 10)

    # Interpretación
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, "Interpretación:", ln=1)
    pdf.set_font("Arial", "", 10)
    texto = (
        f"En {dados.get('dias', 0)} días, la inversión adicional en Inbeef de US$ {formatar_reais(dados.get('diferenca_investimento', 0))} "
        f"puede generar {dados.get('retorno_inbeef', 0):.2f} veces el valor adicional invertido, "
        f"equivalente a una ganancia neta de US$ {formatar_reais(dados.get('ganho_liq_por_animal', 0))} por animal."
    )
    pdf.multi_cell(0, 6, texto)
    pdf.ln(4)
    pdf.set_font("Arial", "I", 8)
    disclaimer = (
        "Este informe presenta solo una proyección basada en los parámetros informados. "
        "Los resultados reales pueden variar debido a factores externos no controlables ("  
        "condiciones climáticas, calidad del pasto, salud de los animales, etc.)."
    )
    pdf.multi_cell(0, 5, disclaimer)

    # Generar PDF
    buffer = io.BytesIO()
    output = pdf.output(dest='S')
    if isinstance(output, str):
        buffer.write(output.encode('latin-1', 'replace'))
    else:
        buffer.write(output)
    return buffer.getvalue()
