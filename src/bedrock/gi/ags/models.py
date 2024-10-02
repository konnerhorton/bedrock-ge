from pydantic import BaseModel


class Ags3Hole(BaseModel):
    hole_id: str
    hole_type: str
    hole_nate: float
    hole_natn: float
    hole_gl: float
    hole_fdep: float
