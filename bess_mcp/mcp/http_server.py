from fastapi import FastAPI
from mcp.server.fastmcp import FastMCP
from .server import prices_get_spotcurve, prices_get_awattar, bess_read_soc, bess_set_mode, sim_run_dispatch, read_pv_load, db_project

app = FastAPI(title="BESS MCP HTTP")
mcp = FastMCP("bess-sim-http")
mcp.bind_fastapi(app)
