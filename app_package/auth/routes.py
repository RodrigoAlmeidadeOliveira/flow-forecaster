"""
Authentication routes blueprint.

This module contains routes for user registration, login, and logout.
"""

import re
from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import current_user, login_user, logout_user, login_required
from sqlalchemy.exc import IntegrityError

from database import get_session
from models import User
from app_package.utils import is_safe_redirect_url
from logger import get_logger

logger = get_logger('auth')

# Create blueprint
auth_bp = Blueprint('auth', __name__)

# Email validation regex
EMAIL_REGEX = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Allow students/instructors to create an account."""
    if current_user.is_authenticated:
        return redirect(url_for('web.index'))

    errors = []
    form_data = {
        'name': '',
        'email': ''
    }

    if request.method == 'POST':
        name = (request.form.get('name') or '').strip()
        email_raw = (request.form.get('email') or '').strip()
        email = email_raw.lower()
        password = request.form.get('password') or ''
        confirm_password = request.form.get('confirm_password') or ''

        form_data['name'] = name
        form_data['email'] = email_raw

        if not name:
            errors.append('Informe seu nome completo.')

        if not email or not EMAIL_REGEX.match(email):
            errors.append('Informe um e-mail válido.')

        if len(password) < 8:
            errors.append('A senha deve ter pelo menos 8 caracteres.')

        if password != confirm_password:
            errors.append('As senhas informadas não coincidem.')

        session = None
        new_user = None

        if not errors:
            session = get_session()
            try:
                is_first_user = session.query(User.id).first() is None
                role = 'admin' if is_first_user else 'student'

                registration_date = datetime.utcnow()
                new_user = User(
                    email=email,
                    name=name,
                    role=role,
                    registration_date=registration_date,
                    access_expires_at=registration_date + timedelta(days=365),
                )
                new_user.set_password(password)

                session.add(new_user)
                session.commit()
                session.refresh(new_user)
                session.expunge(new_user)

                login_user(new_user)
                flash('Conta criada com sucesso! Bem-vindo ao Flow Forecaster.', 'success')
                logger.info(f"New user registered: {email}")
                return redirect(url_for('web.index'))
            except IntegrityError:
                if session:
                    session.rollback()
                errors.append('Este e-mail já está cadastrado. Faça login ou escolha outro e-mail.')
                logger.warning(f"Registration failed - email already exists: {email}")
            finally:
                if session:
                    session.close()

    return render_template('auth/register.html', errors=errors, form_data=form_data)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Authenticate an existing user."""
    if current_user.is_authenticated:
        return redirect(url_for('web.index'))

    errors = []
    form_data = {
        'email': ''
    }

    next_url = request.args.get('next') if request.method == 'GET' else request.form.get('next')

    if request.method == 'POST':
        email_raw = (request.form.get('email') or '').strip()
        email = email_raw.lower()
        password = request.form.get('password') or ''
        remember = bool(request.form.get('remember'))

        form_data['email'] = email_raw

        session = get_session()
        try:
            user = session.query(User).filter(User.email == email).first()
            if not user or not user.check_password(password):
                errors.append('E-mail ou senha inválidos. Verifique e tente novamente.')
                logger.warning(f"Failed login attempt for email: {email}")
            elif not user.is_active:
                errors.append('Sua conta está desativada. Entre em contato com o instrutor.')
                logger.warning(f"Login attempt for inactive account: {email}")
            elif user.access_expires_at and datetime.utcnow() > user.access_expires_at:
                errors.append('Seu acesso expirou. Entre em contato com o instrutor para renovação.')
                logger.warning(f"Login attempt for expired account: {email}")
            else:
                user.last_login = datetime.utcnow()
                session.commit()
                session.refresh(user)
                session.expunge(user)

                login_user(user, remember=remember)
                flash(f'Bem-vindo de volta, {user.name}!', 'success')
                logger.info(f"User logged in: {email}")

                if next_url and is_safe_redirect_url(next_url):
                    return redirect(next_url)
                return redirect(url_for('web.index'))
        finally:
            session.close()

    return render_template('auth/login.html', errors=errors, form_data=form_data, next=next_url)


@auth_bp.route('/logout')
@login_required
def logout():
    """Terminate the current user session."""
    email = getattr(current_user, 'email', 'unknown')
    logout_user()
    flash('Você saiu da aplicação com segurança.', 'info')
    logger.info(f"User logged out: {email}")
    return redirect(url_for('auth.login'))
