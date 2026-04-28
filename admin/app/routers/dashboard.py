from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Header, HTTPException, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import text

from admin.app.config import get_settings
from admin.app.db.session import SessionLocal
from admin.app.schemas.tariff import TariffCreateRequest, TariffToggleRequest

router = APIRouter()
templates = Jinja2Templates(directory="admin/app/templates")


def require_admin_token(x_admin_token: str = Header(default="", alias="X-Admin-Token")) -> None:
    if x_admin_token != get_settings().admin_api_token:
        raise HTTPException(status_code=401, detail="unauthorized")


@router.get("/", response_class=HTMLResponse, dependencies=[Depends(require_admin_token)])
async def dashboard(request: Request) -> HTMLResponse:
    data = {
        "users": 0,
        "active_subscriptions": 0,
        "nodes": 3,
        "monthly_revenue": "0.00",
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    return templates.TemplateResponse("dashboard.html", {"request": request, "data": data})


@router.get("/api/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/api/users", dependencies=[Depends(require_admin_token)])
async def users() -> list[dict[str, object]]:
    async with SessionLocal() as session:
        rows = await session.execute(
            text("SELECT id, telegram_id, username, referral_code, trial_used FROM users ORDER BY id DESC LIMIT 200")
        )
    return [dict(row._mapping) for row in rows]


@router.get("/api/payments", dependencies=[Depends(require_admin_token)])
async def payments() -> list[dict[str, object]]:
    async with SessionLocal() as session:
        rows = await session.execute(
            text("SELECT id, user_id, provider, amount_usd, currency, status, created_at FROM payments ORDER BY id DESC LIMIT 200")
        )
    return [dict(row._mapping) for row in rows]


@router.get("/api/tariffs", dependencies=[Depends(require_admin_token)])
async def tariffs() -> list[dict[str, object]]:
    async with SessionLocal() as session:
        rows = await session.execute(
            text("SELECT id, name, months, price_usd, traffic_limit_gb, device_limit, is_active FROM tariffs ORDER BY months")
        )
    return [dict(row._mapping) for row in rows]


@router.post("/api/tariffs", dependencies=[Depends(require_admin_token)])
async def create_tariff(payload: TariffCreateRequest) -> dict[str, str]:
    async with SessionLocal() as session:
        await session.execute(
            text(
                "INSERT INTO tariffs (name, months, price_usd, traffic_limit_gb, device_limit, is_active) "
                "VALUES (:name, :months, :price_usd, :traffic_limit_gb, :device_limit, true)"
            ),
            payload.model_dump(mode="json"),
        )
        await session.commit()
    return {"status": "created"}


@router.patch("/api/tariffs/{tariff_id}", dependencies=[Depends(require_admin_token)])
async def toggle_tariff(tariff_id: int, payload: TariffToggleRequest) -> dict[str, str]:
    async with SessionLocal() as session:
        result = await session.execute(
            text("UPDATE tariffs SET is_active=:is_active WHERE id=:id"),
            {"is_active": payload.is_active, "id": tariff_id},
        )
        await session.commit()
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="tariff not found")
    return {"status": "updated"}


@router.post("/api/subscriptions/expire", dependencies=[Depends(require_admin_token)])
async def expire_subscriptions() -> dict[str, int]:
    async with SessionLocal() as session:
        result = await session.execute(
            text(
                "UPDATE subscriptions SET status='expired' "
                "WHERE status='active' AND expires_at IS NOT NULL AND expires_at < now()"
            )
        )
        await session.commit()
    return {"updated": int(result.rowcount or 0)}


@router.get("/api/stats", dependencies=[Depends(require_admin_token)])
async def stats() -> dict[str, int]:
    async with SessionLocal() as session:
        users_count = await session.execute(text("SELECT COUNT(*) AS c FROM users"))
        subscriptions_count = await session.execute(text("SELECT COUNT(*) AS c FROM subscriptions WHERE status='active'"))
        payments_count = await session.execute(text("SELECT COUNT(*) AS c FROM payments"))
    return {
        "users": int(users_count.scalar_one()),
        "active_subscriptions": int(subscriptions_count.scalar_one()),
        "payments": int(payments_count.scalar_one()),
    }


@router.get("/api/export/payments.csv", dependencies=[Depends(require_admin_token)])
async def export_payments_csv() -> StreamingResponse:
    async with SessionLocal() as session:
        rows = await session.execute(
            text(
                "SELECT id, user_id, provider, amount_usd, currency, status, created_at "
                "FROM payments ORDER BY id DESC LIMIT 5000"
            )
        )
    header = "id,user_id,provider,amount_usd,currency,status,created_at\n"
    csv_rows = [header]
    for row in rows:
        m = row._mapping
        csv_rows.append(
            f"{m['id']},{m['user_id']},{m['provider']},{m['amount_usd']},{m['currency']},{m['status']},{m['created_at']}\n"
        )

    content = "".join(csv_rows).encode("utf-8")
    return StreamingResponse(iter([content]), media_type="text/csv")
