from fastapi import FastAPI
from dataclasses import dataclass

__all__ = ['Routes']


@dataclass(frozen=True)
class Routes:

    routers: tuple

    def register_routes(self, app: FastAPI):

        for route in self.routers:
            app.include_router(route)
