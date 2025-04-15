from handlers.ping import router as ping_router
from handlers.university import router as university_router

routers = [
    university_router,
    ping_router,
]
