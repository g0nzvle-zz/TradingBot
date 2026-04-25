from groq import Groq
from datetime import date
from config import GROQ_API_KEY, GROQ_MODEL


def build_prompt(market_ctx: dict, long_term_data: list,
                 top_stocks: list, news: list, previous_results: list) -> str:
    """Build the full structured prompt for the LLM."""

    vix = market_ctx.get("vix") or 20.0
    vix_desc = "alto" if vix > 25 else "moderado" if vix > 15 else "bajo"

    lt_lines = []
    for d in long_term_data:
        if not d.get("price"):
            continue
        trend = "alcista" if (d.get("ema20") or 0) > (d.get("ema50") or 0) else "bajista"
        rsi_str = f"{d['rsi']:.1f}" if d.get("rsi") is not None else "N/A"
        macd_h = d.get("macd_hist") or 0
        macd_dir = "positivo" if macd_h > 0 else "negativo"
        bb_pos = "bajo media" if (d.get("price") or 0) < (d.get("bb_mid") or 0) else "sobre media"
        ticker_news = d.get("ticker_news", [])
        news_str = " | ".join(n["title"] for n in ticker_news[:3]) if ticker_news else "Sin noticias recientes"
        lt_lines.append(
            f"- {d['ticker']}: ${d['price']:.2f}, RSI {rsi_str}, "
            f"MACD hist {macd_h:.3f} ({macd_dir}), tendencia {trend}, precio {bb_pos} de Bollinger\n"
            f"  Noticias recientes: {news_str}"
        )

    swing_lines = []
    for d in top_stocks:
        vol_rel = "sobre" if (d.get("volume") or 0) > (d.get("volume_sma20") or 1) else "bajo"
        rsi_str = f"{d['rsi']:.1f}" if d.get("rsi") is not None else "N/A"
        macd_dir = "positivo" if (d.get("macd_hist") or 0) > 0 else "negativo"
        ticker_news = d.get("ticker_news", [])
        news_str = " | ".join(n["title"] for n in ticker_news[:3]) if ticker_news else "Sin noticias recientes"
        swing_lines.append(
            f"- {d['ticker']}: puntuación {d['score']}/100, precio ${d['price']:.2f}, "
            f"RSI {rsi_str}, MACD {macd_dir}, "
            f"volumen {vol_rel} promedio, Kelly {d['kelly_pct']:.0f}%, stop-loss ${d['stop_loss']:.2f}\n"
            f"  Noticias recientes: {news_str}"
        )

    news_lines = [f"- {h['title']}" for h in news]

    if previous_results:
        prev_lines = [
            f"- {r['ticker']} (recomendada {r['fecha']}): {r['resultado_pct']} desde entonces"
            for r in previous_results
        ]
    else:
        prev_lines = ["- Sin recomendaciones previas registradas aún."]

    spy_price = market_ctx.get('spy_price') or 0
    spy_rsi = market_ctx.get('spy_rsi') or 0
    spy_macd = market_ctx.get('spy_macd_hist') or 0
    fg_value = market_ctx.get('fear_greed_value') or 50
    fg_label = market_ctx.get('fear_greed_label') or 'Neutral'

    return f"""Eres un analista financiero conservador y educativo. Generas reportes para un inversor principiante en Chile que opera manualmente en plataformas como Fintual o Racional.

INSTRUCCIONES IMPORTANTES:
- DEBES generar las 5 secciones del reporte en orden: RESUMEN GENERAL, LARGO PLAZO — ETFs, SWING TRADING — Oportunidades, GESTIÓN DE RIESGO, SEGUIMIENTO PREVIO. Ninguna sección debe omitirse.
- La sección SWING TRADING debe incluir TODAS las acciones listadas en "SWING TRADING — Top candidatos" — una por una, con su análisis completo.
- Para los ETFs de largo plazo: analiza cada uno en detalle explicando qué indicadores técnicos apoyan o cuestionan la posición, integrando el contexto de noticias recientes del fondo o su sector en el razonamiento técnico. Indica si conviene mantener, acumular o reducir exposición.
- Para las acciones de swing trading: conecta los indicadores técnicos con el contexto de noticias de esa empresa. Si las noticias contradicen los indicadores (competencia disruptiva, caída del sector, escándalo corporativo, tendencia bajista prolongada), señalarlo con ⚠️ PRECAUCIÓN y recomendar prudencia o evitar la posición.
- Sé detallado y explicativo. El objetivo es que un inversor principiante entienda el razonamiento completo detrás de cada recomendación.
- NO incluyas una sección de referencias, links, ni glosario — esas secciones se agregan automáticamente por separado.
- NO incluyas un sub-bloque "📰 Noticias:" separado en ningún ETF ni acción; integra el contexto en el análisis técnico.

MERCADO GENERAL:
- SPY: ${spy_price:.2f}, RSI {spy_rsi:.1f}, MACD hist {spy_macd:.3f}
- VIX: {vix:.1f} (volatilidad {vix_desc})
- Fear & Greed Index: {fg_value}/100 ({fg_label})

LARGO PLAZO — ETFs:
{chr(10).join(lt_lines)}

SWING TRADING — Top candidatos:
{chr(10).join(swing_lines)}

NOTICIAS GENERALES (últimas 48h):
{chr(10).join(news_lines)}

SEGUIMIENTO PREVIO:
{chr(10).join(prev_lines)}

Genera el reporte en español con EXACTAMENTE este formato Markdown de Telegram:

📊 *REPORTE DE MERCADO — {date.today().strftime('%d %b %Y')}*

🌐 *RESUMEN GENERAL*
[2-3 oraciones sobre el estado del mercado]

───────────────────────────────────
📈 *LARGO PLAZO — ETFs*

[Para cada ETF, un bloque con:]
• *TICKER* — [nombre del fondo y qué representa]
  📊 Técnicos: [RSI, MACD, tendencia EMA, posición en Bollinger y su significado — integra el contexto de noticias que recibiste en el razonamiento técnico sin listarlas aparte]
  ✅ Conclusión: [mantener / acumular / reducir — con el razonamiento integrado]

───────────────────────────────────
⚡ *SWING TRADING — Oportunidades*

[Para cada acción:]
• *TICKER*  |  Puntuación X/100  |  Kelly: Y%
  📊 Técnicos: [RSI, MACD, volumen y lo que significa cada señal]
  🌡️ Sentimiento: [Fear & Greed Index y VIX en contexto — ¿el mercado acompaña?]
  [⚠️ PRECAUCIÓN si hay contradicción entre técnicos y contexto de noticias, explicando por qué conviene evitar]
  [→ Conclusión integrada si todo alinea, explicando el razonamiento completo]
  → Entrada: ~$PRECIO  |  Stop-loss: $SL (-7%)

NOTA: NO incluyas un bloque "📰 Noticias:" separado en ninguna acción ni ETF. El contexto de noticias debe estar integrado en el razonamiento técnico y la conclusión. Las referencias con links se agregan automáticamente al final del reporte.

───────────────────────────────────
🎯 *GESTIÓN DE RIESGO*
Distribución: 70% largo plazo / 30% swing
Stop-loss fijo: 7% bajo precio de entrada
Máximo 20% del portafolio swing en cualquier posición

───────────────────────────────────
📋 *SEGUIMIENTO PREVIO*
[Resultados de recomendaciones anteriores]

───────────────────────────────────
⚠️ Recomendaciones orientativas\\. Invierte solo lo que puedes permitirte perder\\."""


MAX_REFERENCES = 5


def build_swing_fallback(top_stocks: list) -> str:
    """
    Build the Swing Trading section programmatically.
    Used as a fallback when the LLM omits this section from its output.
    """
    lines = ["───────────────────────────────────", "⚡ *SWING TRADING — Oportunidades*", ""]

    if not top_stocks:
        lines.append("No hay candidatos que cumplan los criterios técnicos en este ciclo.")
        return "\n".join(lines)

    for d in top_stocks:
        rsi = f"{d['rsi']:.1f}" if d.get("rsi") is not None else "N/A"
        macd_h = d.get("macd_hist") or 0
        macd_dir = "positivo" if macd_h > 0 else "negativo"
        vol_rel = "sobre" if (d.get("volume") or 0) > (d.get("volume_sma20") or 1) else "bajo"
        lines.append(
            f"• *{d['ticker']}*  |  Puntuación {d['score']}/100  |  Kelly: {d['kelly_pct']:.0f}%"
        )
        lines.append(f"  📊 Técnicos: RSI {rsi}, MACD {macd_dir}, volumen {vol_rel} promedio")
        lines.append(
            f"  → Entrada: ~${d['price']:.2f}  |  Stop-loss: ${d['stop_loss']:.2f} (-7%)"
        )
        lines.append("")
    return "\n".join(lines).rstrip()


def build_references(long_term_data: list, top_stocks: list, news: list) -> str:
    """
    Build a references section with clickable links from all news sources.
    Limits to the top MAX_REFERENCES most relevant items, prioritizing news
    tied to swing trading tickers (most actionable), then ETFs, then general.
    Returns an empty string if no URLs are available.
    """
    refs = []
    seen_urls = set()

    def _add(items):
        for item in items:
            if len(refs) >= MAX_REFERENCES:
                return
            url = item.get("url", "")
            title = item.get("title", "")
            if url and url not in seen_urls and title:
                label = title if len(title) <= 70 else title[:67] + "..."
                refs.append(f"• [{label}]({url})")
                seen_urls.add(url)

    for d in top_stocks:
        _add(d.get("ticker_news", []))
    for d in long_term_data:
        _add(d.get("ticker_news", []))
    _add(news)

    if not refs:
        return ""

    return "───────────────────────────────────\n🔗 *REFERENCIAS*\n" + "\n".join(refs)


GLOSSARY = """───────────────────────────────────
📚 *GLOSARIO DE INDICADORES*

📌 *RSI* (Índice de Fuerza Relativa)
Mide si una acción está sobrecomprada o sobrevendida. Escala 0-100.
• < 30 → Sobrevendida (posible oportunidad de compra)
• 30-70 → Zona neutral (señal más confiable)
• > 70 → Sobrecomprada (puede caer pronto)

📌 *MACD*
Compara dos promedios móviles para detectar cambios de tendencia.
• MACD positivo → Momentum alcista
• MACD negativo → Momentum bajista
• Histograma creciente → La tendencia se acelera

📌 *Bandas de Bollinger*
Muestran el rango "normal" de precio de una acción.
• Precio cerca de la banda inferior → Posible oportunidad de compra
• Precio cerca de la banda superior → Acción cara respecto a su promedio

📌 *EMA 20 / EMA 50* (Media Móvil Exponencial)
Promedios que suavizan el precio para ver la tendencia.
• EMA20 > EMA50 → Tendencia alcista de corto y mediano plazo
• EMA20 < EMA50 → Tendencia bajista

📌 *VIX* (Índice de Volatilidad)
Mide el "miedo" del mercado.
• < 15 → Mercado tranquilo, baja incertidumbre
• 15-25 → Volatilidad moderada
• > 25 → Alta incertidumbre, mayor riesgo

📌 *Fear & Greed Index*
Sentimiento general del mercado. Escala 0-100.
• 0-25 → Miedo extremo (inversores en pánico, posible oportunidad)
• 25-75 → Zona neutral
• 75-100 → Codicia extrema (mercado eufórico, mayor riesgo)

📌 *Kelly %*
Porcentaje máximo sugerido del portafolio para una posición, calculado matemáticamente según probabilidad de éxito y relación riesgo/beneficio.

📌 *Stop-loss*
Precio límite de venta para protegerse de pérdidas mayores. Fijado en -7% del precio de entrada."""


def generate_report(prompt: str) -> str:
    """Call Groq API with the prompt and return the generated report text."""
    client = Groq(api_key=GROQ_API_KEY)
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=4000,
    )
    return response.choices[0].message.content
