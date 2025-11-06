# Instruções de Backup do PostgreSQL

## Status Atual
⚠️ **Backups automáticos NÃO estão habilitados**

## Como Habilitar Backup Automático (RECOMENDADO)

### Passo 1: Habilitar backups no Fly.io
Execute no seu terminal local (não funciona via Claude Code devido a bug no flyctl):

```bash
flyctl postgres backup enable --app flow-forecaster-db
```

Quando perguntado, aceite os termos de serviço do Tigris (digite `y`).

### Passo 2: Verificar se foi habilitado
```bash
flyctl postgres backup list --app flow-forecaster-db
```

### Passo 3: Configurar periodicidade (opcional)
```bash
flyctl postgres backup config --app flow-forecaster-db
```

## Como Funciona o Backup Automático

Uma vez habilitado:
- **Tipo**: WAL-based continuous backup (Write-Ahead Log)
- **Armazenamento**: Tigris (S3-compatible storage)
- **Frequência**: Contínua (PITR - Point-in-Time Recovery)
- **Restore**: Pode restaurar para qualquer momento no tempo
- **Custo**: Apenas pelo armazenamento usado no Tigris

## Backup Manual (Alternativa Temporária)

Enquanto não habilita o backup automático, use o script fornecido:

```bash
./backup_postgres_manual.sh
```

Este script:
1. Cria um túnel para o PostgreSQL
2. Faz dump completo do banco
3. Comprime o arquivo (.sql.gz)
4. Salva em `backups/flow_forecaster_backup_YYYYMMDD_HHMMSS.sql.gz`

### Automação com cron
Para fazer backup diário às 3h da manhã:

```bash
crontab -e
```

Adicione:
```
0 3 * * * cd /caminho/para/flow-forecaster && ./backup_postgres_manual.sh
```

## Restaurar de um Backup

### De backup automático (WAL-based):
```bash
flyctl postgres backup restore <backup-id> --app flow-forecaster-db
```

### De backup manual (.sql.gz):
```bash
# 1. Descompactar
gunzip backups/flow_forecaster_backup_YYYYMMDD_HHMMSS.sql.gz

# 2. Iniciar proxy
flyctl proxy 15432:5432 --app flow-forecaster-db &

# 3. Restaurar
PGPASSWORD="4ZRplUZglrnfO3Y" psql \
    -h localhost \
    -p 15432 \
    -U flow_forecaster \
    -d flow_forecaster \
    < backups/flow_forecaster_backup_YYYYMMDD_HHMMSS.sql
```

## Recomendações

1. ✅ **Habilite o backup automático o quanto antes**
2. ✅ Faça um backup manual hoje mesmo como contingência
3. ✅ Teste a restauração periodicamente
4. ✅ Mantenha backups em múltiplos locais (Tigris + Google Drive)
5. ⚠️ Não commite arquivos de backup no Git (.gitignore já configurado)

## Monitoramento

Verificar backups regularmente:
```bash
flyctl postgres backup list --app flow-forecaster-db
```

Verificar tamanho do banco:
```bash
flyctl ssh console --app flow-forecaster-db -C "du -h /data"
```

## Custos Estimados

- **Tigris Storage**: ~$0.02/GB/mês
- **Backup de 50MB**: ~$0.001/mês (praticamente gratuito)
- **Egress**: Gratuito até 10GB/mês

## Suporte

Em caso de problemas:
- Documentação: https://fly.io/docs/postgres/managing/backup-and-restore/
- Status: https://status.fly.io/
- Forum: https://community.fly.io/
