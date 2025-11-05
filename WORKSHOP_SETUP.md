# 🎓 Setup do Flow-Forecaster para Workshops

**Guia rápido para rodar o Flow-Forecaster localmente durante workshops**

---

## 🎯 Por que rodar localmente?

Durante workshops com múltiplos participantes e rede instável (4G compartilhado), o deploy cloud pode ter problemas:
- ❌ Latência alta em redes ruins
- ❌ Falhas de conexão
- ❌ Lentidão com múltiplos usuários
- ❌ Dependência de internet estável

**Solução:** Cada participante roda sua própria instância local!

---

## 📋 Pré-requisitos

### Opção A: Docker (Recomendado - Mais Fácil)

1. **Instalar Docker Desktop**
   - Windows/Mac: https://www.docker.com/products/docker-desktop
   - Linux: https://docs.docker.com/engine/install/

2. **Verificar instalação:**
   ```bash
   docker --version
   # Deve mostrar: Docker version 20.x ou superior
   ```

### Opção B: Python Local (Alternativa)

1. **Python 3.10+**
   - Windows: https://www.python.org/downloads/
   - Mac: `brew install python@3.10`
   - Linux: `sudo apt install python3.10`

2. **Git** (para clonar o repositório)

---

## 🚀 Setup Rápido (5 minutos)

### Método 1: Docker Compose (Recomendado)

```bash
# 1. Clonar ou extrair o repositório
cd flow-forecaster

# 2. Iniciar o container
docker-compose -f docker-compose.workshop.yml up

# 3. Aguardar mensagem:
# "Listening at: http://0.0.0.0:8080"

# 4. Abrir navegador em:
http://localhost:8080

# Para parar:
Ctrl+C
```

**Primeira execução:** Pode demorar 2-3 minutos (download da imagem)
**Execuções seguintes:** 10-20 segundos

---

### Método 2: Python Local

```bash
# 1. Clonar repositório
git clone <repo-url>
cd flow-forecaster

# 2. Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Instalar dependências
pip install -r requirements.txt

# 4. Iniciar aplicação
python app.py

# 5. Abrir navegador em:
http://localhost:8080
```

---

## 👥 Setup para Facilitador (Servidor Local)

Se preferir rodar um servidor único para todos os participantes:

### Requisitos do Laptop

- **CPU:** 4+ cores
- **RAM:** 8GB+
- **OS:** Windows/Mac/Linux

### Passos

```bash
# 1. Iniciar com múltiplos workers
docker-compose -f docker-compose.workshop.yml up

# 2. Descobrir IP local
# Windows:
ipconfig
# Mac/Linux:
ifconfig | grep inet

# 3. Compartilhar IP com participantes
# Exemplo: http://192.168.1.100:8080

# 4. Conectar laptop a:
# - WiFi local (melhor)
# - Hotspot 4G (ok para até 6 pessoas)
```

### Configurar WiFi Dedicado

Se possível, criar rede WiFi exclusiva para o workshop:

1. **Roteador portátil** TP-Link ou similar
2. **Configurar:**
   - SSID: "Workshop-FlowForecaster"
   - Senha: "workshop2024"
   - Modo: 5GHz (menos interferência)

---

## 🎨 Modo Workshop (Performance)

O Flow-Forecaster tem um "Modo Workshop" que reduz simulações de 10.000 para 2.000, tornando tudo 5x mais rápido.

### Ativar no Navegador

1. Abrir aplicação
2. No formulário de simulação, marcar:
   ```
   ☑️ Modo Workshop (simulações rápidas)
   ```

3. Resultado:
   - ✅ Simulações: 1-3s (vs 5-10s)
   - ✅ Menos carga de CPU
   - ✅ Experiência mais fluida

---

## 🔧 Troubleshooting

### Problema: "Port 8080 already in use"

**Solução:** Mudar a porta

```bash
# Docker:
docker-compose -f docker-compose.workshop.yml up
# Editar docker-compose.workshop.yml:
ports:
  - "9090:8080"  # Use porta 9090

# Acessar em: http://localhost:9090
```

### Problema: Docker muito lento

**Solução:** Aumentar recursos do Docker Desktop

1. Docker Desktop → Settings → Resources
2. CPUs: 4
3. Memory: 4GB
4. Apply & Restart

### Problema: Erro de banco de dados

**Solução:** Limpar dados antigos

```bash
# Parar container
docker-compose -f docker-compose.workshop.yml down

# Remover volume de dados
docker volume rm flow-forecaster_workshop_data

# Reiniciar
docker-compose -f docker-compose.workshop.yml up
```

### Problema: Não consigo acessar de outro dispositivo

**Solução:** Verificar firewall

```bash
# Windows:
# Firewall → Permitir aplicativo → Docker Desktop

# Mac:
# System Preferences → Security → Firewall → Allow Docker

# Linux:
sudo ufw allow 8080/tcp
```

---

## 📊 Benchmark de Performance

### Setup Cloud (Fly.io)

| Métrica | Valor |
|---------|-------|
| Login | 5-10s |
| Simulação (10k) | 8-15s |
| Usuários simultâneos | ~6 |
| Falhas de conexão | 20-30% em rede ruim |

### Setup Local (Docker)

| Métrica | Valor |
|---------|-------|
| Login | <1s ✅ |
| Simulação (2k workshop) | 1-3s ✅ |
| Simulação (10k completa) | 3-5s ✅ |
| Usuários simultâneos | Ilimitado ✅ |
| Falhas de conexão | 0% ✅ |

**Ganho:** 5-10x mais rápido, 100% confiável

---

## 🎯 Checklist do Facilitador

### 1 Semana Antes do Workshop

- [ ] Enviar instruções de setup para participantes
- [ ] Solicitar instalação do Docker Desktop
- [ ] Preparar pasta zipada com aplicação (backup)
- [ ] Testar setup em 2-3 laptops diferentes

### 1 Dia Antes

- [ ] Verificar internet do local
- [ ] Testar hotspot 4G como backup
- [ ] Preparar pen drive com instaladores:
  - Docker Desktop (Windows/Mac)
  - Pasta zipada da aplicação

### No Dia do Workshop

- [ ] Chegar 30min antes
- [ ] Iniciar servidor local de backup
- [ ] Testar acesso de 2-3 dispositivos
- [ ] Ter slides offline (PDF) como backup

### Durante o Workshop

- [ ] Manter servidor local rodando
- [ ] Monitorar uso de CPU/memória
- [ ] Ter terminal aberto para logs
- [ ] Reiniciar se necessário (2min downtime)

---

## 📚 Recursos Adicionais

### Para Participantes

- **Documentação Online:** https://flow-forecaster.fly.dev/docs
- **Vídeo Tutorial:** [Link se disponível]
- **FAQ:** Ver seção abaixo

### Para Facilitadores

- **Performance Analysis:** Ver `PERFORMANCE_ANALYSIS.md`
- **Logs:** `docker-compose logs -f`
- **Restart rápido:** `docker-compose restart`

---

## ❓ FAQ

**P: Preciso de internet para usar localmente?**
R: Não! Após o download inicial, tudo funciona 100% offline.

**P: Os dados são salvos?**
R: Sim, em um volume Docker persistente. Mesmo reiniciando, seus projetos são mantidos.

**P: Posso usar o celular para acessar?**
R: Sim! Conecte o celular no mesmo WiFi e acesse `http://[IP-DO-LAPTOP]:8080`

**P: Quanto de espaço em disco usa?**
R: ~2GB (Docker images + dados)

**P: Funciona no Windows 10 Home?**
R: Sim, mas precisa de WSL2. Instruções: https://docs.docker.com/desktop/windows/install/

**P: E se meu laptop não suportar Docker?**
R: Use o Método 2 (Python local) ou acesse o servidor do facilitador.

---

## 🆘 Suporte Durante Workshop

**Se algo der errado:**

1. **Reset rápido** (2min):
   ```bash
   docker-compose down
   docker-compose -f docker-compose.workshop.yml up
   ```

2. **Usar servidor do facilitador** como backup

3. **Acesso cloud** em último caso:
   - https://flow-forecaster.fly.dev
   - Pode estar lento mas funciona

---

## ✅ Validação de Setup

Antes de iniciar o workshop, validar:

```bash
# 1. Container rodando
docker ps | grep flow-forecaster

# 2. Acesso HTTP
curl http://localhost:8080/health

# 3. Simulação rápida (deve retornar em <5s)
curl -X POST http://localhost:8080/api/simulate \
  -H "Content-Type: application/json" \
  -d '{"samples":[1,2,3], "backlog":10, "nSimulations":1000}'
```

**Resposta esperada:** Status 200, JSON com resultados

---

## 📞 Contato

**Problemas durante setup?**
- Email: [seu-email]
- WhatsApp: [seu-número]
- Telegram: [seu-user]

**Boa sorte no workshop! 🚀**
