import marimo

__generated_with = "0.12.5"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    return (mo,)


@app.cell
def _(mo):
    mo.md(
        """
        Below this I'm going to define a function
        """
    )
    return


@app.cell
def _(mo):
    mo.md(
        """
        Below this I'm going to define a function
        """
    )

    def add_two_numbers(a, b):
        return a + b
    return (add_two_numbers,)


if __name__ == "__main__":
    app.run()
