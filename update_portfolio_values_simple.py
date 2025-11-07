#!/usr/bin/env python3
"""
Script para atualizar business_value e risk_level dos projetos.
Usa a mesma sessão do database que o app Flask.
"""

import os

# Forçar uso do PostgreSQL em produção
os.environ['DATABASE_URL'] = 'postgres://postgres:SSkOEIw5f3eTiFF@flow-forecaster-db.internal:5432/flow_forecaster_db?sslmode=disable'

from database import get_session
from models import Project

def main():
    db_session = get_session()

    try:
        # Buscar todos os projetos
        projects = db_session.query(Project).order_by(Project.id).all()

        print(f"\n{'='*70}")
        print(f"Encontrados {len(projects)} projetos")
        print(f"{'='*70}\n")

        # Mapeamento de atualizações
        updates = {
            'prj-01': (75, 'low', 'Quick Wins'),
            'prj03': (80, 'medium', 'Quick Wins'),
            'projeto-performance': (50, 'medium', 'Fill-ins'),
        }

        # Buscar projetos por nome e atualizar
        for name_pattern, (biz_val, risk, quadrant) in updates.items():
            project = db_session.query(Project).filter(Project.name == name_pattern).first()
            if project:
                project.business_value = biz_val
                project.risk_level = risk
                print(f"✓ {project.name:40} → Valor: {biz_val:3}, Risco: {risk:10} [{quadrant}]")

        # Tratar projetos com nomes parciais ou duplicados
        # DESENVOLVIMENTO DE APP MOBILE (pode haver mais de um)
        dev_mobile = db_session.query(Project).filter(
            Project.name.like('DESENVOLVIMENTO DE APP MOBILE%')
        ).first()
        if dev_mobile:
            dev_mobile.business_value = 70
            dev_mobile.risk_level = 'high'
            print(f"✓ {dev_mobile.name:40} → Valor:  70, Risco: high       [Strategic Bets]")

        # TRANSFORMAÇÃO DIGITAL
        transf = db_session.query(Project).filter(
            Project.name.like('TRANSFORMAÇÃO DIGITAL%')
        ).first()
        if transf:
            transf.business_value = 85
            transf.risk_level = 'critical'
            print(f"✓ {transf.name:40} → Valor:  85, Risco: critical   [Strategic Bets]")

        # Default Projects - pegar o primeiro para Fill-ins com low risk
        default_low = db_session.query(Project).filter(
            Project.name == 'Default Project'
        ).first()
        if default_low:
            default_low.business_value = 40
            default_low.risk_level = 'low'
            print(f"✓ {default_low.name:40} → Valor:  40, Risco: low        [Fill-ins]")

        # Demais Default Projects como Fill-ins com medium risk
        other_defaults = db_session.query(Project).filter(
            Project.name == 'Default Project',
            Project.business_value == 50
        ).all()
        for proj in other_defaults:
            proj.business_value = 45
            proj.risk_level = 'medium'
            print(f"✓ {proj.name:40} → Valor:  45, Risco: medium     [Fill-ins]")

        # Commit
        db_session.commit()

        print(f"\n{'='*70}")
        print("✅ Projetos atualizados com sucesso!")
        print(f"{'='*70}\n")

        # Mostrar distribuição final
        print("Distribuição nos quadrantes:\n")
        all_projects = db_session.query(Project).all()

        for proj in sorted(all_projects, key=lambda p: (-p.business_value, p.name)):
            if proj.business_value >= 60 and proj.risk_level in ['low', 'medium']:
                quadrant = 'Quick Wins'
            elif proj.business_value >= 60 and proj.risk_level in ['high', 'critical']:
                quadrant = 'Strategic Bets'
            elif proj.business_value < 60 and proj.risk_level in ['low', 'medium']:
                quadrant = 'Fill-ins'
            else:
                quadrant = 'Avoid'

            print(f"  {proj.name:45} | Valor: {proj.business_value:3} | Risco: {proj.risk_level:10} | [{quadrant}]")

        print("\nAcesse https://flow-forecaster.fly.dev → aba 'Portfólio' para ver a matriz atualizada!\n")

    except Exception as e:
        print(f"❌ Erro: {e}")
        db_session.rollback()
        raise
    finally:
        db_session.close()

if __name__ == '__main__':
    main()
