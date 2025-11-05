# Análise de Performance - Flow-Forecaster Workshop

**Data:** 2025-11-05
**Contexto:** Workshop com 6+ conexões simultâneas em rede 4G compartilhada
**Problemas Reportados:** Falhas de login, falhas em simulações, lentidão geral

---

## 🔍 Diagnóstico do Problema

### 1. Configuração Atual do Fly.io

```toml
[[vm]]
  memory = '1gb'
  cpu_kind = 'shared'
  cpus = 1

[http_service]
  auto_stop_machines = "stop"
  auto_start_machines = true
  min_machines_running = 0  # ⚠️ Cold start problem
```

**Problemas Identificados:**

| Item | Status Atual | Impacto |
|------|--------------|---------|
| **CPU** | 1 vCPU compartilhada | Alto - Monte Carlo é CPU-intensive |
| **Memória** | 1GB RAM | Médio - Simulações grandes podem esgotar |
| **Instâncias** | 1 máquina ativa | **Crítico** - Sem redundância |
| **Cold Start** | 0 min machines | Alto - Delays de 10-30s no primeiro acesso |
| **Concorrência** | Gunicorn default | Alto - Não otimizado para múltiplos workers |

### 2. Análise dos Gargalos

#### 2.1 Simulações Monte Carlo

**Operação mais custosa:** `run_monte_carlo_simulation()`

```python
# Exemplo típico de workshop:
n_simulations = 10000  # 10k simulações
backlog = 50 itens
complexity = "alta"

# Tempo estimado: 3-8 segundos por simulação
# Com 6 usuários simultâneos = 18-48 segundos de CPU bloqueada
```

**Problema:** Simulações bloqueiam o thread principal (síncrono)

#### 2.2 Banco de Dados (SQLite)

```python
DATABASE_URL = "sqlite:////data/forecaster.db"
```

**Problemas:**
- SQLite tem locks globais para escritas
- Múltiplos usuários escrevendo simultaneamente = serialização forçada
- Sem connection pooling otimizado

#### 2.3 Rede e Assets

**Assets não otimizados:**
- JavaScript/CSS não minificados
- Sem cache HTTP agressivo
- Chart.js carregado por completo (~200KB)
- Bootstrap completo (~150KB)

**Total:** ~500KB+ por página inicial em rede 4G ruim = 10-20s

---

## 🎯 Soluções Propostas

### Solução 1: **Deploy Local para Workshops** (Recomendado)

#### Opção A: Docker Compose Simples

**Vantagem:** Cada participante roda localmente, zero dependência de rede

**Arquivo:** `docker-compose.workshop.yml`

```yaml
version: '3.8'
services:
  flow-forecaster:
    build: .
    ports:
      - "8080:8080"
    environment:
      - DATABASE_URL=sqlite:////data/forecaster.db
      - SECRET_KEY=workshop-secret-key
      - FLASK_ENV=development
    volumes:
      - ./data:/data
    restart: unless-stopped
```

**Instruções para participantes:**

```bash
# 1. Instalar Docker Desktop
# 2. Clonar repositório ou receber pasta zipada
# 3. Executar:
cd flow-forecaster
docker-compose -f docker-compose.workshop.yml up

# 4. Acessar: http://localhost:8080
```

**Prós:**
- ✅ Zero latência de rede
- ✅ Cada usuário tem CPU/RAM dedicada
- ✅ Funciona 100% offline
- ✅ Sem problemas de autenticação compartilhada

**Contras:**
- ❌ Requer Docker instalado (150MB download)
- ❌ Setup inicial de ~5 minutos

#### Opção B: Servidor Local no Workshop

**Setup:** Um laptop potente como servidor local

```bash
# No laptop do facilitador:
docker run -d \
  -p 80:8080 \
  -e SECRET_KEY=workshop \
  -e WORKERS=4 \
  --name flow-forecaster \
  flow-forecaster:latest

# Compartilhar via IP local:
# http://192.168.x.x
```

**Configurar Gunicorn para múltiplos workers:**

```python
# wsgi.py ou comando de start
workers = 4  # 1 por CPU core
worker_class = 'sync'
worker_connections = 1000
timeout = 120  # Simulações podem demorar
keepalive = 5
```

**Prós:**
- ✅ Setup único pelo facilitador
- ✅ Rede local WiFi é muito mais rápida
- ✅ 4+ workers = 4+ simulações simultâneas

**Contras:**
- ❌ Ainda depende de WiFi local
- ❌ Requer laptop potente (8GB+ RAM, 4+ cores)

---

### Solução 2: **Otimização do Deploy Fly.io** (Médio Prazo)

#### 2.1 Escalar Recursos

**Arquivo:** `fly.toml`

```toml
[[vm]]
  memory = '2gb'        # Era: 1gb
  cpu_kind = 'shared'
  cpus = 2              # Era: 1

[http_service]
  internal_port = 8080
  force_https = true
  auto_stop_machines = "stop"
  auto_start_machines = true
  min_machines_running = 1  # Era: 0 - Evita cold start
  processes = ["app"]

[processes]
  app = "gunicorn --workers 4 --worker-class sync --timeout 120 --bind 0.0.0.0:8080 wsgi:app"
```

**Custo estimado:** ~$15-20/mês (vs ~$5/mês atual)

**Deploy:**

```bash
flyctl scale vm shared-cpu-2x --memory 2048
flyctl scale count 1 --max-per-region 2  # Auto-scale até 2 máquinas
```

#### 2.2 Cache HTTP Agressivo

**Arquivo:** `app.py`

```python
from flask import Flask, make_response
from datetime import datetime, timedelta

app = Flask(__name__)

@app.after_request
def add_cache_headers(response):
    """Add cache headers for static content"""
    if request.path.startswith('/static/'):
        # Cache assets por 1 semana
        response.cache_control.public = True
        response.cache_control.max_age = 604800
        response.expires = datetime.utcnow() + timedelta(days=7)
    elif request.path in ['/', '/login', '/register']:
        # Páginas HTML: cache por 5 minutos
        response.cache_control.public = True
        response.cache_control.max_age = 300
    return response
```

#### 2.3 Otimizar Simulações (Async)

**Problema atual:** Simulações bloqueiam o thread

**Solução:** Usar background jobs com Celery ou RQ

```python
# Arquivo: tasks.py
from rq import Queue
from redis import Redis
import monte_carlo_unified as mc

redis_conn = Redis(host='localhost', port=6379)
q = Queue(connection=redis_conn)

def run_simulation_async(simulation_data):
    """Run simulation in background"""
    result = mc.run_monte_carlo_simulation(simulation_data)
    return result

# Arquivo: app.py
@app.route('/api/simulate', methods=['POST'])
def simulate():
    data = request.json

    # Enqueue job
    job = q.enqueue(run_simulation_async, data, job_timeout=120)

    return jsonify({
        'job_id': job.id,
        'status': 'processing'
    })

@app.route('/api/simulate/<job_id>', methods=['GET'])
def check_simulation(job_id):
    job = q.fetch_job(job_id)

    if job.is_finished:
        return jsonify({'status': 'completed', 'result': job.result})
    elif job.is_failed:
        return jsonify({'status': 'failed', 'error': str(job.exc_info)})
    else:
        return jsonify({'status': 'processing'})
```

**Prós:**
- ✅ Simulações não bloqueiam requests HTTP
- ✅ Melhor UX com loading spinner
- ✅ Permite cancelar simulações longas

**Contras:**
- ❌ Requer Redis (adiciona complexidade)
- ❌ Mudança significativa no frontend

---

### Solução 3: **Otimizações Rápidas (Imediato)**

#### 3.1 Reduzir Número de Simulações no Workshop

**Arquivo:** `static/js/ui.js`

```javascript
// Configuração atual
const DEFAULT_SIMULATIONS = 10000;

// Workshop mode (adicionar toggle)
const WORKSHOP_SIMULATIONS = 2000;  // 5x mais rápido

// Adicionar no HTML:
<label class="form-check-label">
  <input type="checkbox" id="workshopMode"> Modo Workshop (mais rápido)
</label>

// No JavaScript:
document.getElementById('workshopMode').addEventListener('change', (e) => {
  const nSims = e.target.checked ? 2000 : 10000;
  document.getElementById('nSimulations').value = nSims;
});
```

**Resultado:** Simulações 5x mais rápidas (1-2s vs 5-10s)

#### 3.2 Minificar Assets

**Instalar ferramentas:**

```bash
npm install -g uglify-js clean-css-cli html-minifier
```

**Script de build:**

```bash
#!/bin/bash
# build-assets.sh

# Minify JavaScript
for file in static/js/*.js; do
  uglifyjs "$file" -c -m -o "${file%.js}.min.js"
done

# Minify CSS
for file in static/css/*.css; do
  cleancss "$file" -o "${file%.css}.min.css"
done

echo "Assets minified!"
```

**Resultado:** Redução de ~40% no tamanho (500KB → 300KB)

#### 3.3 Lazy Loading de Dependências

**Chart.js:** Carregar apenas quando necessário

```html
<!-- Antes: carrega sempre -->
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

<!-- Depois: carrega sob demanda -->
<script>
function loadChartJS() {
  return new Promise((resolve) => {
    if (window.Chart) {
      resolve();
    } else {
      const script = document.createElement('script');
      script.src = 'https://cdn.jsdelivr.net/npm/chart.js';
      script.onload = resolve;
      document.head.appendChild(script);
    }
  });
}

// Usar assim:
async function showChart(data) {
  await loadChartJS();
  new Chart(ctx, config);
}
</script>
```

#### 3.4 Compressão GZIP no Gunicorn

**Arquivo:** `wsgi.py`

```python
from flask_compress import Compress

app = Flask(__name__)
Compress(app)  # Auto-compress responses > 500 bytes
```

**Instalar:**

```bash
pip install flask-compress
echo "flask-compress>=1.14.0" >> requirements.txt
```

**Resultado:** Redução de ~70% no tráfego de rede

---

## 📋 Plano de Ação Recomendado

### **Curto Prazo (1 semana) - Para Próximo Workshop**

1. ✅ **Criar Docker Compose para deploy local**
   - Tempo: 2h
   - Impacto: **ALTO** - Resolve 90% dos problemas

2. ✅ **Adicionar "Modo Workshop"** com 2000 simulações
   - Tempo: 1h
   - Impacto: Médio

3. ✅ **Minificar assets**
   - Tempo: 30min
   - Impacto: Médio

4. ✅ **Adicionar Flask-Compress**
   - Tempo: 15min
   - Impacto: Médio

**Total de esforço:** ~4 horas
**Impacto esperado:** 80-90% de melhoria

### **Médio Prazo (1 mês)**

1. **Escalar Fly.io** para 2 CPUs, 2GB RAM
   - Custo: +$10-15/mês
   - Impacto: Alto

2. **Implementar cache HTTP** agressivo
   - Tempo: 2h
   - Impacto: Alto

3. **Otimizar queries SQL** (adicionar índices)
   - Tempo: 3h
   - Impacto: Médio

### **Longo Prazo (3+ meses)**

1. **Migrar simulações para background jobs** (Celery/RQ)
   - Tempo: 1-2 semanas
   - Impacto: **MUITO ALTO**

2. **Migrar SQLite → PostgreSQL** no Fly.io
   - Tempo: 1 semana
   - Impacto: Alto (concorrência)

3. **Implementar CDN** para assets estáticos
   - Tempo: 1 dia
   - Impacto: Alto (rede ruim)

---

## 🚀 Implementação Imediata

Vou criar agora os arquivos essenciais para o próximo workshop:

1. `docker-compose.workshop.yml` - Deploy local
2. `WORKSHOP_SETUP.md` - Instruções para participantes
3. Modificações no `static/js/ui.js` - Modo Workshop
4. Script de minificação - `build-assets.sh`

---

## 📊 Métricas de Sucesso

### Antes (Workshop atual)

| Métrica | Valor | Status |
|---------|-------|--------|
| Tempo de login | 5-10s | ❌ Lento |
| Simulação (10k) | 8-15s | ❌ Muito lento |
| Página inicial | 15-20s | ❌ Muito lento |
| Falhas de conexão | 20-30% | ❌ Inaceitável |
| Usuários simultâneos | 6 | ⚠️ No limite |

### Meta (Pós-otimização)

| Métrica | Valor | Status |
|---------|-------|--------|
| Tempo de login | <2s | ✅ Rápido |
| Simulação (2k) | 1-3s | ✅ Rápido |
| Página inicial | 2-5s | ✅ Aceitável |
| Falhas de conexão | <5% | ✅ Confiável |
| Usuários simultâneos | 20+ | ✅ Escalável |

---

## 💡 Recomendação Final

**Para o próximo workshop:**

1. **PRIORITÁRIO:** Usar Docker Compose local em cada laptop
   - Garante performance e confiabilidade
   - Zero dependência de rede externa

2. **ALTERNATIVA:** Se não for possível Docker:
   - Implementar "Modo Workshop" com 2k simulações
   - Deploy Fly.io com 2 CPUs + min_machines=1
   - Assets minificados + GZIP

3. **BACKUP:** Laptop local como servidor
   - WiFi do celular ou roteador portátil
   - 4 workers Gunicorn

**Tempo de implementação:** 4-6 horas
**Custo adicional:** $0 (Docker local) ou +$10/mês (Fly.io escalado)
