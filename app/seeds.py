import os
import click
from flask.cli import with_appcontext
from app import db
from app.models import Item


@click.command("seed")
@with_appcontext
def seed_command():
    """Wipe and re-seed the database with example items for all profiles."""
    profiles_env = os.environ.get("PROFILES", "Player 1")
    profiles = [p.strip() for p in profiles_env.split(",") if p.strip()]

    click.echo("Clearing existing data...")
    Item.query.delete()
    db.session.commit()

    click.echo(f"Seeding example items for {len(profiles)} profile(s): {profiles}...")
    example_names = ["First Item", "Second Item", "Third Item"]
    for profile in profiles:
        for name in example_names:
            db.session.add(Item(profile_id=profile, name=name))
    db.session.commit()

    click.echo(f"Done. {len(example_names)} items seeded per profile.")
