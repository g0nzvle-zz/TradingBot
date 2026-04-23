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
        trend = ">" if (d.get("ema20") or 0) > (d.get("ema50") or 0) else "<"
        rsi_str = f"{d['rsi']:.1f}" if d.get("rsi") is not None else "N/A"
        macd_h = d.get("macd_hist") or 0
        lt_lines.append(
            f"- {d['ticker']}: ${d['price']:.2f}, RSI {rsi_str}, "
            f"MACD hist {macd_h:.3f}, EMA20 {trend} EMA50"
        )

    swing_lines = []
    for d in top_stocks:
        s = d["sentiment"]
        vol_rel = "sobre" if (d.get("volume") or 0) > (d.get("volume_sma20") or 1) else "bajo"
        rsi_str = f"{d['rsi']:.1f}" if d.get("rsi") is not None else "N/A"
        macd_dir = "positivo" if (d.get("macd_hist") or 0) > 0 else "negativo"
        swing_lines.append(
            f"- {d['ticker']}: puntuación {d['score']}/100, precio ${d['price']:.2f}, "
            f"RSI {rsi_str}, MACD {macd_dir}, "
            f"volumen {vol_rel} promedio, Kelly {d['kelly_pct']:.0f}%, stop-loss ${d['stop_loss']:.2f}, "
            f"Reddit: {s['sentiment']} ({s['mentions']} menciones, {s['positive_pct']}% positivo)"
        )

    news_lines = [f"- {h}" for h in news]

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

    return f"""Eres un analista financiero conservador y educativo. Generas reportes para un inversor principiante en Chile que opera manualmente en plataformas como Fintual o Racional.

Para cada recomendación de swing trading DEBES conectar tres elementos: indicadores técnicos, noticias relevantes y sentimiento Reddit. Explica el POR QUÉ, no solo el QUÉ. Sé conciso pero completo.

MERCADO GENERAL:
- SPY: ${spy_price:.2f}, RSI {spy_rsi:.1f}, MACD hist {spy_macd:.3f}
- VIX: {vix:.1f} (volatilidad {vix_desc})

LARGO PLAZO — ETFs:
{chr(10).join(lt_lines)}

SWING TRADING — Top candidatos:
{chr(10).join(swing_lines)}

NOTICIAS (últimas 48h):
{chr(10).join(news_lines)}

SEGUIMIENTO PREVIO:
{chr(10).join(prev_lines)}

Genera el reporte en español con EXACTAMENTE este formato Markdown de Telegram:

📊 *REPORTE DE MERCADO — {date.today().strftime('%d %b %Y')}*

🌐 *RESUMEN GENERAL*
[2-3 oraciones sobre el estado del mercado]

───────────────────────────────────
📈 *LARGO PLAZO — ETFs*
[Estado y recomendación conectando los datos provistos]

───────────────────────────────────
⚡ *SWING TRADING — Oportunidades*

[Para cada acción:]
• *TICKER*  |  Puntuación X/100  |  Kelly: Y%
  [Indicadores técnicos activos y su significado]
  [Noticias relevantes del sector o empresa]
  [Sentimiento Reddit: volumen y tono]
  [Conclusión y razonamiento integrado]
  → Entrada: ~$PRECIO  |  Stop-loss: $SL (-7%)

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


def generate_report(prompt: str) -> str:
    """Call Groq API with the prompt and return the generated report text."""
    client = Groq(api_key=GROQ_API_KEY)
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=2000,
    )
    return response.choices[0].message.content
