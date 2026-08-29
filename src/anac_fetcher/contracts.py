"""DataContracts para grupos-chave da ANAC.

Contratos definidos a partir de amostras reais convertidas (2026-08-29) —
schemas da ANAC são majoritariamente String; o contrato valida a presença do
conjunto de colunas esperado (drift de schema) e aplica cast no `wrangling`
(best-effort: falha loga warning sem abortar a conversão).
"""

import polars as pl
from quantilica.analytics.schema import DataContract, Field

_OCORRENCIAS_COLUMNS = [
    "Numero_da_Ocorrencia",
    "Numero_da_Ficha",
    "Operador_Padronizado",
    "Classificacao_da_Ocorrencia",
    "Data_da_Ocorrencia",
    "Hora_da_Ocorrencia",
    "Municipio",
    "UF",
    "Regiao",
    "Descricao_do_Tipo",
    "ICAO",
    "Latitude",
    "Longitude",
    "Tipo_de_Aerodromo",
    "Historico",
    "Matricula",
    "Categoria_da_Aeronave",
    "Operador",
    "Tipo_de_Ocorrencia",
    "Fase_da_Operacao",
    "Operacao",
    "Danos_a_Aeronave",
    "Aerodromo_de_Destino",
    "Aerodromo_de_Origem",
    "Lesoes_Fatais_Tripulantes",
    "Lesoes_Fatais_Passageiros",
    "Lesoes_Fatais_Terceiros",
    "Lesoes_Graves_Tripulantes",
    "Lesoes_Graves_Passageiros",
    "Lesoes_Graves_Terceiros",
    "Lesoes_Leves_Tripulantes",
    "Lesoes_Leves_Passageiros",
    "Lesoes_Leves_Terceiros",
    "Ilesos_Tripulantes",
    "Ilesos_Passageiros",
    "Lesoes_Desconhecidas_Tripulantes",
    "Lesoes_Desconhecidas_Passageiros",
    "Lesoes_Desconhecidas_Terceiros",
    "Modelo",
    "CLS",
    "Tipo_ICAO",
    "PMD",
    "Numero_de_Assentos",
    "Nome_do_Fabricante",
    "PSSO",
]

_RECOMENDACOES_COLUMNS = [
    "NUMERO_OCORRENCIA",
    "NUMERO_PROCESSO",
    "CATEGORIA_OCORRENCIA",
    "MATRICULA",
    "DATA_OCORRENCIA",
    "NRO_RECOM_SEGURANCA",
    "TXT_RECOM_SEGURANCA",
    "CLASS_RECOM_SEGURANCA",
    "DATA_RECEBIMENTO_RECOM",
    "AREA_COMPETENTE",
    "STATUS_ANAC_RECOMENDACAO",
    "PRAZO_RESPOSTA_RECOM_SEGURANCA",
    "TEXTO_RESPOSTA",
    "DATA_RESPOSTA",
]

_VRA_COLUMNS = [
    "ICAO Empresa Aérea",
    "Número Voo",
    "Código Autorização (DI)",
    "Código Tipo Linha",
    "ICAO Aeródromo Origem",
    "ICAO Aeródromo Destino",
    "Partida Prevista",
    "Partida Real",
    "Chegada Prevista",
    "Chegada Real",
    "Situação Voo",
    "Código Justificativa",
]

_AERO_LISTA_COLUMNS = [
    "Código OACI",
    "CIAD",
    "Nome",
    "Município",
    "UF",
    "Município Servido",
    "UF Servido",
    "Longitude",
    "Latitude",
    "Altitude",
    "Operação Diurna",
    "Operação Noturna",
    "Situação",
    "Validade do Registro",
    "Portaria de Registro",
    "Link Portaria",
    "LATGEOPOINT",
    "LONGEOPOINT",
]


def _string_fields(columns: list[str]) -> list[Field]:
    return [Field(name, pl.Utf8) for name in columns]


CONTRACTS: dict[str, DataContract] = {
    "ocorrencias": DataContract("ocorrencias", _string_fields(_OCORRENCIAS_COLUMNS)),
    "recomendacoes-seguranca": DataContract(
        "recomendacoes-seguranca", _string_fields(_RECOMENDACOES_COLUMNS)
    ),
    "vra": DataContract("vra", _string_fields(_VRA_COLUMNS)),
    "aero-lista-publicos": DataContract(
        "aero-lista-publicos", _string_fields(_AERO_LISTA_COLUMNS)
    ),
}
