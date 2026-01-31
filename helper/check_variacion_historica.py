import os

import pandas as pd

from core.database import csv_historical, csv_near_real_time


def check_historical_variation():
    """
    Replicates the DAX measure logic to compare the sum of AFFECTED_CUSTOMERS
    between the latest and the second-to-last TIMESTAMP, ensuring they are different snapshots.
    """
    if not os.path.exists(csv_historical):
        print("Historical file does not exist, cannot check variation.")
        return

    df_hist = pd.read_csv(csv_historical, encoding="utf-8-sig")
    if len(df_hist) < 2:
        print("Not enough data in history to calculate variation.")
        return

    # Get the list of unique TIMESTAMPS and sort them
    unique_timestamps = (
        df_hist["TIMESTAMP"].drop_duplicates().sort_values(ascending=True)
    )
    if len(unique_timestamps) < 2:
        print("Only one unique snapshot exists, no second-to-last one to compare.")
        return

    # The latest timestamp (most recent execution)
    latest_time = unique_timestamps.iloc[-1]
    # The second-to-last timestamp (previous execution)
    previous_time = unique_timestamps.iloc[-2]

    # Sum AFFECTED_CUSTOMERS in each snapshot
    affected_latest = df_hist.loc[
        df_hist["TIMESTAMP"] == latest_time, "CLIENTES_AFECTADOS"
    ].sum()
    affected_previous = df_hist.loc[
        df_hist["TIMESTAMP"] == previous_time, "CLIENTES_AFECTADOS"
    ].sum()

    variation = affected_latest - affected_previous

    print(f"🔎 Health Check:")
    print(f"    Latest snapshot: {latest_time} → {affected_latest} affected")
    print(f"    Previous snapshot: {previous_time} → {affected_previous} affected")
    print(f"    Variation (DAX-like): {variation}\n")
    print(
        f"✅ Data saved to:\n📌 {csv_historical} (Historical)\n📌 {csv_near_real_time} (Near-Real-Time)"
    )
