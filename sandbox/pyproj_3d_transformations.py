import marimo

__generated_with = "0.13.11"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    from pyproj import CRS, Transformer
    from pyproj.crs import CompoundCRS
    return CRS, CompoundCRS, Transformer


@app.cell
def _(CRS, Transformer):
    # https://pyproj4.github.io/pyproj/stable/advanced_examples.html#promote-crs-to-3d
    wgs84 = CRS("EPSG:4326")
    swiss_proj = CRS("EPSG:2056")
    transformer = Transformer.from_crs(wgs84, swiss_proj, always_xy=True)
    # 2D Transformation
    print(f"2D transform of point {(8.37909, 47.01987, 1000)} from {wgs84} to {swiss_proj} gives:")
    print(transformer.transform(8.37909, 47.01987, 1000))

    wgs84_3d = wgs84.to_3d()
    swiss_proj_ellipsoidal_3d = swiss_proj.to_3d()
    transformer_ellipsoidal_3d = Transformer.from_crs(
        wgs84_3d,
        swiss_proj_ellipsoidal_3d,
        always_xy=True,
    )
    # 3D Transformation
    print(f"3D transform of point {(8.37909, 47.01987, 1000)} from {wgs84_3d.to_string()} to {swiss_proj_ellipsoidal_3d} gives:")
    print(transformer_ellipsoidal_3d.transform(8.37909, 47.01987, 1000))

    return swiss_proj, transformer_ellipsoidal_3d, wgs84_3d


@app.cell
def _(
    CRS,
    CompoundCRS,
    Transformer,
    swiss_proj,
    transformer_ellipsoidal_3d,
    wgs84_3d,
):
    # https://pyproj4.github.io/pyproj/stable/build_crs.html#compound-crs
    swiss_lhn95_height = CRS("EPSG:5729")
    swiss_compound = CompoundCRS(
        name="CH1903+ / LV95 + LHN95 height",
        components=[swiss_proj, swiss_lhn95_height]
    )
    transformer_wgs84_3d_to_swiss_compound = Transformer.from_crs(
        wgs84_3d,
        swiss_compound,
        always_xy=True,
    )
    print(transformer_ellipsoidal_3d.transform(8.37909, 47.01987, 1000))
    return


if __name__ == "__main__":
    app.run()
