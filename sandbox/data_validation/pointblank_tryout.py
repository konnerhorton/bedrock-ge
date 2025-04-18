# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo",
#     "pandas==2.2.3",
#     "pointblank==0.8.6",
#     "polars==1.27.1",
# ]
# ///

import marimo

__generated_with = "0.12.10"
app = marimo.App(width="medium")


app._unparsable_cell(
    r"""
    https://posit-dev.github.io/pointblank/blog/intro-pointblank/
    """,
    column=None, disabled=False, hide_code=True, name="_"
)


@app.cell
def _():
    import marimo as mo
    import pointblank as pb
    import polars as pl
    return mo, pb, pl


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        Bit of a funny issue, given that this the pointblank example data?!? Should be easy to resolve, right?

        `ImportError: Passing a plain list of values currently requires the library pandas. You can avoid this error by passing a polars Series.`

        Besides, shouldn't pointblank be BYODF (Bring Your Own Data Frame)?
        """
    )
    return


@app.cell
def _(pb):
    small_table = pb.load_dataset(dataset="small_table", tbl_type="polars")

    validation_1 = (
        pb.Validate(
            data=small_table,
            tbl_name="small_table",
            label="Example Validation"
        )
        .col_vals_lt(columns="a", value=10)
        .col_vals_between(columns="d", left=0, right=5000)
        .col_vals_in_set(columns="f", set=["low", "mid", "high"])
        .col_vals_regex(columns="b", pattern=r"^[0-9]-[a-z]{3}-[0-9]{3}$")
        .interrogate()
    )

    validation_1
    return small_table, validation_1


@app.cell
def _(pb, pl):
    validation_2 = (
        pb.Validate(
            data=pb.load_dataset(dataset="game_revenue", tbl_type="polars"),
            tbl_name="game_revenue",
            label="Data validation with threshold levels set.",
            thresholds=pb.Thresholds(warning=1, error=20, critical=0.10),
        )
        .col_vals_regex(columns="player_id", pattern=r"^[A-Z]{12}[0-9]{3}$")        # STEP 1
        .col_vals_gt(columns="session_duration", value=5)                           # STEP 2
        .col_vals_ge(columns="item_revenue", value=0.02)                            # STEP 3
        .col_vals_in_set(columns="item_type", set=["iap", "ad"])                    # STEP 4
        .col_vals_in_set(                                                           # STEP 5
            columns="acquisition",
            set=["google", "facebook", "organic", "crosspromo", "other_campaign"]
        )
        .col_vals_not_in_set(columns="country", set=["Mongolia", "Germany"])        # STEP 6
        .col_vals_between(                                                          # STEP 7
            columns="session_duration",
            left=10, right=50,
            pre = lambda df: df.select(pl.median("session_duration"))
        )
        .rows_distinct(columns_subset=["player_id", "session_id", "time"])          # STEP 8
        .row_count_match(count=2000)                                                # STEP 9
        .col_exists(columns="start_day")                                            # STEP 10
        .interrogate()
    )

    validation_2
    return (validation_2,)


if __name__ == "__main__":
    app.run()
