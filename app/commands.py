import click
from flask import current_app
from flask.cli import with_appcontext
from flask_migrate import upgrade
from sqlalchemy import MetaData, create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.exc import OperationalError

from app.extensions import db
from app.utils.seed import seed_default_admin


def register_commands(app):
    app.cli.add_command(create_db_command)
    app.cli.add_command(init_db_command)
    app.cli.add_command(seed_admin_command)
    app.cli.add_command(reset_db_command)


@click.command("create-db")
@with_appcontext
def create_db_command():
    """Create the configured PostgreSQL database if it does not already exist."""
    database_uri = current_app.config["SQLALCHEMY_DATABASE_URI"]
    url = make_url(database_uri)

    if not url.drivername.startswith("postgresql"):
        raise click.ClickException(
            "The create-db command currently supports PostgreSQL connections only."
        )

    target_database = url.database
    if not target_database:
        raise click.ClickException("No target database name was found in the connection settings.")

    maintenance_database = current_app.config["POSTGRES_MAINTENANCE_DB"]
    maintenance_url = url.set(database=maintenance_database)
    maintenance_engine = create_engine(
        maintenance_url,
        isolation_level="AUTOCOMMIT",
        pool_pre_ping=True,
    )

    try:
        with maintenance_engine.connect() as connection:
            exists = connection.execute(
                text("SELECT 1 FROM pg_database WHERE datname = :db_name"),
                {"db_name": target_database},
            ).scalar()
            if exists:
                click.echo(f"Database '{target_database}' already exists.")
                return

            quoted_database_name = maintenance_engine.dialect.identifier_preparer.quote(
                target_database
            )
            connection.exec_driver_sql(f"CREATE DATABASE {quoted_database_name}")
            click.echo(f"Database '{target_database}' created successfully.")
    except OperationalError as exc:
        raise click.ClickException(
            "Unable to connect to PostgreSQL. Check POSTGRES_HOST, POSTGRES_PORT, "
            "POSTGRES_USER, POSTGRES_PASSWORD, and whether the PostgreSQL service is running."
        ) from exc
    finally:
        maintenance_engine.dispose()


@click.command("init-db")
@with_appcontext
def init_db_command():
    """Apply migrations to the configured database and ensure the default admin exists."""
    try:
        upgrade(directory="migrations")
        seed_default_admin()
        click.echo("Database initialized and default admin account ensured.")
    except OperationalError as exc:
        raise click.ClickException(
            "Unable to initialize the database. If the PostgreSQL database does not exist yet, "
            "run `python -m flask --app run.py create-db` first."
        ) from exc


@click.command("seed-admin")
@with_appcontext
def seed_admin_command():
    """Create the default admin account if it is missing."""
    admin = seed_default_admin()
    click.echo(f"Admin account ready: {admin.username}")


@click.command("reset-db")
@with_appcontext
def reset_db_command():
    """Drop all tables in the configured database, then re-apply migrations and seed admin."""
    click.echo(
        f"Resetting database: {current_app.config['SQLALCHEMY_DATABASE_URI']}"
    )

    db.session.remove()
    db.engine.dispose()

    try:
        metadata = MetaData()
        metadata.reflect(bind=db.engine)
        if metadata.tables:
            metadata.drop_all(bind=db.engine)
            click.echo("Dropped existing tables from the configured database.")
        else:
            click.echo("No existing tables were found. Continuing with migration setup.")

        upgrade(directory="migrations")
        seed_default_admin()
        click.echo("Database rebuilt from migrations and admin account ensured.")
    except OperationalError as exc:
        raise click.ClickException(
            "Unable to reset the database. If the PostgreSQL database does not exist yet, "
            "run `python -m flask --app run.py create-db` first."
        ) from exc
