from pathlib import Path
import sys

# Allow imports from the CONFLUX project root
sys.path.append(
    str(Path(__file__).resolve().parents[2])
)

from sqlalchemy import inspect

from backend.database.database import engine
from backend.database.models import (
    Mission,
    Observation,
    AnomalyEvent,
    FusionEvent,
)


def main():

    print("CONFLUX database tables:")

    # --------------------------------------------------
    # Check tables
    # --------------------------------------------------

    inspector = inspect(engine)
    tables = inspector.get_table_names()

    for table in tables:
        print(f"- {table}")

    print(f"\nTotal tables: {len(tables)}")

    # --------------------------------------------------
    # Read stored records
    # --------------------------------------------------

    with engine.connect() as connection:

        missions = connection.execute(
            Mission.__table__.select()
        ).fetchall()

        observations = connection.execute(
            Observation.__table__.select()
        ).fetchall()

        anomalies = connection.execute(
            AnomalyEvent.__table__.select()
        ).fetchall()

        fusion_events = connection.execute(
            FusionEvent.__table__.select()
        ).fetchall()

    # --------------------------------------------------
    # Display missions
    # --------------------------------------------------

    print("\nMissions:")

    for row in missions:
        print(row)

    print(
        f"\nTotal missions: {len(missions)}"
    )

    # --------------------------------------------------
    # Display observations
    # --------------------------------------------------

    print("\nObservations:")

    for row in observations:
        print(row)

    print(
        f"\nTotal observations: {len(observations)}"
    )

    # --------------------------------------------------
    # Display anomaly events
    # --------------------------------------------------

    print("\nAnomaly Events:")

    for row in anomalies:
        print(row)

    print(
        f"\nTotal anomaly events: {len(anomalies)}"
    )

    # --------------------------------------------------
    # Display fusion events
    # --------------------------------------------------

    print("\nFusion Events:")

    for row in fusion_events:
        print(row)

    print(
        f"\nTotal fusion events: {len(fusion_events)}"
    )


if __name__ == "__main__":
    main()