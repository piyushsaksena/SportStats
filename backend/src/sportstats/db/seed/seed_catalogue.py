"""Seed script to populate reference tables and the metric catalogue.

Loads sports, disciplines, common countries, official sources, and all 69 metrics.
"""

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from sportstats.db.models import (
    Country,
    Discipline,
    MetricDefinition,
    Source,
    Sport,
)
from sportstats.db.session import SessionLocal, engine
from sportstats.db.views import create_views
from sportstats.metrics.catalog import (
    METRICS_CATALOGUE,
    OLYMPIC_DISCIPLINES,
    SPORTS_REGISTRY,
)

CORE_COUNTRIES = [
    {"iso3": "IND", "name": "India", "continent": "Asia"},
    {"iso3": "USA", "name": "United States", "continent": "North America"},
    {"iso3": "GBR", "name": "Great Britain / United Kingdom", "continent": "Europe"},
    {"iso3": "AUS", "name": "Australia", "continent": "Oceania"},
    {"iso3": "FRA", "name": "France", "continent": "Europe"},
    {"iso3": "GER", "name": "Germany", "continent": "Europe"},
    {"iso3": "JPN", "name": "Japan", "continent": "Asia"},
    {"iso3": "CHN", "name": "China", "continent": "Asia"},
    {"iso3": "BRA", "name": "Brazil", "continent": "South America"},
    {"iso3": "ESP", "name": "Spain", "continent": "Europe"},
    {"iso3": "ARG", "name": "Argentina", "continent": "South America"},
    {"iso3": "QAT", "name": "Qatar", "continent": "Asia"},
    {"iso3": "RUS", "name": "Russia", "continent": "Europe"},
    {"iso3": "DNK", "name": "Denmark", "continent": "Europe"},
    {"iso3": "IRN", "name": "Iran", "continent": "Asia"},
    {"iso3": "KOR", "name": "South Korea", "continent": "Asia"},
    {"iso3": "PAK", "name": "Pakistan", "continent": "Asia"},
    {"iso3": "NZL", "name": "New Zealand", "continent": "Oceania"},
    {"iso3": "SRI", "name": "Sri Lanka", "continent": "Asia"},
    {"iso3": "RSA", "name": "South Africa", "continent": "Africa"},
    {"iso3": "CAN", "name": "Canada", "continent": "North America"},
    {"iso3": "ITA", "name": "Italy", "continent": "Europe"},
    {"iso3": "SRB", "name": "Serbia", "continent": "Europe"},
    {"iso3": "INA", "name": "Indonesia", "continent": "Asia"},
    {"iso3": "MAS", "name": "Malaysia", "continent": "Asia"},
    {"iso3": "THA", "name": "Thailand", "continent": "Asia"},
    {"iso3": "KEN", "name": "Kenya", "continent": "Africa"},
    {"iso3": "JAM", "name": "Jamaica", "continent": "North America"},
]

OFFICIAL_SOURCES = [
    {
        "organisation": "ICC",
        "name": "International Cricket Council Official Archive",
        "url": "https://www.icc-cricket.com",
        "access_method": "manual_csv",
        "tier": "official",
        "terms_note": "Official ICC tournament records and match results compendiums.",
        "is_verified": True,
    },
    {
        "organisation": "FIFA",
        "name": "FIFA Tournament Statistics & Match Center",
        "url": "https://www.fifa.com",
        "access_method": "manual_csv",
        "tier": "official",
        "terms_note": "Official FIFA World Cup technical reports and match archives.",
        "is_verified": True,
    },
    {
        "organisation": "BWF",
        "name": "Badminton World Federation Tournament Software",
        "url": "https://bwfbadminton.com",
        "access_method": "manual_csv",
        "tier": "official",
        "terms_note": "Official BWF tournament draws and world rankings archive.",
        "is_verified": True,
    },
    {
        "organisation": "FIBA",
        "name": "FIBA Basketball World Cup Official Statistics",
        "url": "https://www.fiba.basketball",
        "access_method": "manual_csv",
        "tier": "official",
        "terms_note": "Official FIBA tournament event box scores and player stats.",
        "is_verified": True,
    },
    {
        "organisation": "AELTC / Grand Slam",
        "name": "The Championships, Wimbledon Official Compendium",
        "url": "https://www.wimbledon.com",
        "access_method": "manual_csv",
        "tier": "official",
        "terms_note": "Official Wimbledon draw sheets and match statistics records.",
        "is_verified": True,
    },
    {
        "organisation": "IKF",
        "name": "International Kabaddi Federation Official Archives",
        "url": "https://www.kabaddiikf.com",
        "access_method": "manual_csv",
        "tier": "official",
        "terms_note": "Official Kabaddi World Cup and Asian Games scores.",
        "is_verified": True,
    },
    {
        "organisation": "IOC",
        "name": "International Olympic Committee Official Results",
        "url": "https://olympics.com",
        "access_method": "download",
        "tier": "official",
        "terms_note": "Official Olympic Results Books and Historical Medal Tables.",
        "is_verified": True,
    },
    {
        "organisation": "ATP/WTA",
        "name": "ATP & WTA Official Tour Rankings (Secondary Official)",
        "url": "https://www.atptour.com",
        "access_method": "manual_csv",
        "tier": "secondary",
        "terms_note": "Official tour ranking snapshots noted per master build prompt Section 8.1.",
        "is_verified": True,
    },
]


def seed_database(db: Session) -> None:
    """Seed all reference data into the active database session."""
    # 1. Seed Sports
    sport_map = {}
    for sport_data in SPORTS_REGISTRY:
        existing = db.query(Sport).filter(Sport.code == sport_data["code"]).first()
        if not existing:
            sport = Sport(
                code=sport_data["code"],
                name=sport_data["name"],
                is_team_sport=sport_data["is_team_sport"],
                is_individual_sport=sport_data["is_individual_sport"],
                notes=sport_data.get("notes"),
            )
            db.add(sport)
            db.flush()
            sport_map[sport.code] = sport.id
        else:
            sport_map[existing.code] = existing.id

    # 2. Seed Disciplines (Olympic)
    olympic_sport_id = sport_map.get("olympic")
    if olympic_sport_id:
        for disc_data in OLYMPIC_DISCIPLINES:
            existing_disc = (
                db.query(Discipline)
                .filter(
                    Discipline.sport_id == olympic_sport_id, Discipline.code == disc_data["code"]
                )
                .first()
            )
            if not existing_disc:
                disc = Discipline(
                    sport_id=olympic_sport_id,
                    code=disc_data["code"],
                    name=disc_data["name"],
                )
                db.add(disc)

    # 3. Seed Countries
    for c_data in CORE_COUNTRIES:
        existing_country = db.query(Country).filter(Country.iso3 == c_data["iso3"]).first()
        if not existing_country:
            country = Country(
                iso3=c_data["iso3"],
                name=c_data["name"],
                continent=c_data.get("continent"),
            )
            db.add(country)

    # 4. Seed Sources
    for src_data in OFFICIAL_SOURCES:
        existing_src = (
            db.query(Source).filter(Source.organisation == src_data["organisation"]).first()
        )
        if not existing_src:
            src = Source(
                organisation=src_data["organisation"],
                name=src_data["name"],
                url=src_data["url"],
                access_method=src_data["access_method"],
                tier=src_data["tier"],
                terms_note=src_data.get("terms_note"),
                retrieved_at=datetime.now(timezone.utc),
                is_verified=src_data["is_verified"],
            )
            db.add(src)

    # 5. Seed Metric Catalogue
    db.flush()
    for m in METRICS_CATALOGUE:
        sport_id = sport_map.get(m.sport_code)
        if not sport_id:
            continue
        existing_metric = (
            db.query(MetricDefinition)
            .filter(MetricDefinition.sport_id == sport_id, MetricDefinition.code == m.code)
            .first()
        )
        if not existing_metric:
            metric = MetricDefinition(
                sport_id=sport_id,
                code=m.code,
                name=m.name,
                unit=m.unit,
                category=m.category,
                aggregation=m.aggregation,
                formula=m.formula,
                higher_is_better=m.higher_is_better,
                description=m.description,
            )
            db.add(metric)

    db.commit()


def main():
    """CLI entrypoint for database seeding."""
    print("Creating tables and views...")
    from sportstats.db.session import Base

    Base.metadata.create_all(bind=engine)
    create_views(engine)

    print("Seeding reference catalogue...")
    db = SessionLocal()
    try:
        seed_database(db)
        print("Database successfully seeded with 7 sports and 69 metrics!")
    finally:
        db.close()


if __name__ == "__main__":
    main()
