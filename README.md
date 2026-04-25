# 📈 TradingBot

Bot automatizado de análisis de mercado que genera reportes diarios con señales técnicas para ETFs y acciones de swing trading, enviados directamente a Telegram.

---

## ¿Qué hace?

Cada dos días, el bot:

1. Obtiene el contexto del mercado (SPY, VIX, Fear & Greed Index)
2. Analiza ETFs de largo plazo con indicadores técnicos y noticias recientes
3. Filtra un universo de ~40 acciones buscando las mejores oportunidades de swing trading
4. Calcula el tamaño óptimo de posición con el **Criterio de Kelly**
5. Genera un reporte en lenguaje natural usando un modelo LLM (Llama 3.3 70B via Groq)
6. Envía el reporte al grupo de Telegram en 3 mensajes organizados

---

## Estructura del reporte

| Mensaje | Contenido |
|---|---|
| 1️⃣ | Resumen general del mercado + análisis de ETFs |
| 2️⃣ | Oportunidades de swing trading con entrada, stop-loss y Kelly % |
| 3️⃣ | Glosario de indicadores + referencias con links |

---

## Stack tecnológico

| Componente | Tecnología |
|---|---|
| Datos de mercado | `yfinance` |
| Noticias | RSS feeds + `yfinance` ticker news |
| Indicadores técnicos | `ta` (RSI, MACD, Bollinger, EMA) |
| Modelo LLM | Groq API — `llama-3.3-70b-versatile` |
| Entrega | Telegram Bot API |
| Automatización | GitHub Actions (cron cada 2 días) |

---

## Indicadores utilizados

- **RSI** — Detecta sobrecompra/sobreventa
- **MACD** — Momentum y cambios de tendencia
- **Bandas de Bollinger** — Rango normal de precio
- **EMA 20 / EMA 50** — Tendencia de corto y mediano plazo
- **Volumen vs SMA 20** — Confirmación de movimientos
- **VIX** — Volatilidad del mercado
- **Fear & Greed Index** — Sentimiento general

---

## Configuración local

### 1. Clonar el repositorio

```bash
git clone https://github.com/g0nzvle-zz/TradingBot.git
cd TradingBot
```

### 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 3. Crear archivo `.env`

```bash
cp .env.example .env
```

Edita `.env` con tus claves:

```
GROQ_API_KEY=tu_clave_de_groq
TELEGRAM_TOKEN=tu_token_del_bot
TELEGRAM_CHAT_ID=id_del_chat_o_grupo
```

### 4. Ejecutar

```bash
python main.py
```

---

## Configuración en GitHub Actions

Agrega los siguientes secrets en **Settings → Secrets and variables → Actions**:

| Secret | Descripción |
|---|---|
| `GROQ_API_KEY` | Clave de la API de Groq |
| `TELEGRAM_TOKEN` | Token del bot de Telegram |
| `TELEGRAM_CHAT_ID` | ID del chat o grupo de Telegram |

El workflow se ejecuta automáticamente cada 2 días a las 11:00 UTC (≈ 8:00 AM Chile). También puede lanzarse manualmente desde la pestaña **Actions**.

---

## Gestión de riesgo

El bot aplica las siguientes reglas por defecto:

- **70%** del portafolio en ETFs de largo plazo
- **30%** en swing trading
- **Stop-loss fijo** del 7% bajo el precio de entrada
- **Máximo 20%** del portafolio en cualquier posición de swing
- Tamaño de posición calculado con **Half Kelly**

---

## Tests

```bash
pytest tests/
```

---

## Advertencia

> Las recomendaciones generadas son **orientativas y educativas**. No constituyen asesoría financiera. Invierte solo lo que puedes permitirte perder.
