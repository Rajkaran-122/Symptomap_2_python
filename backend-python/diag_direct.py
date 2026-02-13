"""Capture exact error to file"""
import asyncio, sys, traceback as tb

async def main():
    from app.core.database import AsyncSessionLocal, engine, Base
    from app.models import User, OTPCode, AuthEvent
    from app.services.otp_service import OTPService
    from app.core.security import get_password_hash
    import uuid

    log = []
    def p(msg):
        log.append(str(msg))
        print(msg)

    try:
        p("Step 1: Creating tables...")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        p("Tables OK")
    except Exception as e:
        p(f"Table creation error: {e}")
        p(tb.format_exc())

    try:
        async with AsyncSessionLocal() as db:
            p("\nStep 2: Creating user...")
            user = User(
                id=uuid.uuid4(),
                email=f"diag{uuid.uuid4().hex[:4]}@test.com",
                phone="+910000000000",
                password_hash=get_password_hash("MyStr0ng@Pass!"),
                full_name="Diag",
                role="user",
                is_active=True,
            )
            db.add(user)
            await db.flush()
            p(f"User flushed: {user.id}")

            p("\nStep 3: Creating OTP...")
            otp_code, otp_id = await OTPService.create_otp(db, user.id, "signup", "127.0.0.1")
            p(f"OTP OK: code={otp_code}")

            p("\nStep 4: Logging event...")
            await OTPService.log_auth_event(db, "test", True, "127.0.0.1", user_id=user.id)
            p("Event OK")

            await db.commit()
            p("\nAll committed!")
    except Exception as e:
        p(f"\nERROR at step: {type(e).__name__}: {e}")
        p(tb.format_exc())

    with open("diag_error.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(log))

asyncio.run(main())
