import debugpy
from debugpy import breakpoint as bk
import os

# To debug something call this function and then place a breakpoint with: debugpy.breakpoint()


def start_debug_session():
    port = os.getenv("DEBUGGER_PORT")
    if port is None:
        port = 9013
        print(f"Warning! DEBUG_PORT was not specified defaulting to: {port}")
    if debugpy.is_client_connected():
        return
    debugpy.listen(("0.0.0.0", int(port)))
    debugpy.wait_for_client()
