
def calcular_custo_diario(consumo_g, preco_kg):
    try:
        return float((consumo_g / 1000) * preco_kg)
    except:
        return 0.0

def calcular_diferenca_investimento(custo_inbeef_diario, custo_padrao_diario):
    try:
        return float(custo_inbeef_diario - custo_padrao_diario)
    except:
        return 0.0

def calcular_ponto_equilibrio(diferenca_investimento, valor_kg_recria):
    try:
        if valor_kg_recria == 0:
            return 0.0
        return float((diferenca_investimento / valor_kg_recria) * 1000)
    except:
        return 0.0

def calcular_ganho_liquido_por_animal(gmd_adicional, ponto_equilibrio, valor_kg_recria, dias):
    try:
        ganho_diario = (gmd_adicional - ponto_equilibrio) / 1000
        if ganho_diario < 0:
            return 0.0
        return float(ganho_diario * valor_kg_recria * dias)
    except:
        return 0.0

def calcular_ganho_total_lote(ganho_liquido_por_animal, num_animais):
    try:
        return float(ganho_liquido_por_animal * num_animais)
    except:
        return 0.0

def calcular_custo_total_padrao(num_animais, custo_padrao_diario, dias):
    try:
        return float(num_animais * custo_padrao_diario * dias)
    except:
        return 0.0

def calcular_investimento_total(num_animais, custo_inbeef_diario, dias):
    try:
        return float(num_animais * custo_inbeef_diario * dias)
    except:
        return 0.0

def calcular_retorno_inbeef(gmd_adicional, valor_kg_recria, diferenca_investimento, dias):
    try:
        if diferenca_investimento * dias == 0:
            return 0.0
        return float(((gmd_adicional / 1000) * dias * valor_kg_recria) / (diferenca_investimento * dias))
    except:
        return 0.0
