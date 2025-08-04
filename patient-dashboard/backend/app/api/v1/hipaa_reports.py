"""
HIPAA compliance reporting endpoints.
"""
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from app.core.dependencies import get_current_user, require_role
from app.models.user import User, UserRole
from app.services.hipaa_audit_report import hipaa_audit_report
import logfire

router = APIRouter()


@router.get("/access-report")
async def get_access_report(
    start_date: Optional[datetime] = Query(None, description="Start date for report"),
    end_date: Optional[datetime] = Query(None, description="End date for report"),
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    patient_id: Optional[str] = Query(None, description="Filter by patient ID"),
    current_user: User = Depends(get_current_user)
):
    """
    Generate PHI access report for HIPAA compliance.
    
    Requires ADMIN role.
    """
    # Only admins can generate audit reports
    require_role(current_user, [UserRole.ADMIN])
    
    # Default to last 30 days if no dates provided
    if not end_date:
        end_date = datetime.utcnow()
    if not start_date:
        start_date = end_date - timedelta(days=30)
    
    # Validate date range
    if start_date > end_date:
        raise HTTPException(status_code=400, detail="Start date must be before end date")
    
    if (end_date - start_date).days > 365:
        raise HTTPException(status_code=400, detail="Date range cannot exceed 365 days")
    
    with logfire.span("generate_access_report"):
        report = await hipaa_audit_report.generate_access_report(
            start_date=start_date,
            end_date=end_date,
            user_id=user_id,
            patient_id=patient_id
        )
    
    logfire.info(
        "HIPAA access report generated",
        user_id=current_user.id,
        report_period_days=(end_date - start_date).days
    )
    
    return report


@router.get("/user-activity/{user_id}")
async def get_user_activity_report(
    user_id: str,
    days: int = Query(30, ge=1, le=365, description="Number of days to include"),
    current_user: User = Depends(get_current_user)
):
    """
    Generate activity report for a specific user.
    
    Requires ADMIN role.
    """
    require_role(current_user, [UserRole.ADMIN])
    
    with logfire.span("generate_user_activity_report"):
        report = await hipaa_audit_report.generate_user_activity_report(
            user_id=user_id,
            days=days
        )
    
    logfire.info(
        "User activity report generated",
        admin_id=current_user.id,
        target_user_id=user_id,
        days=days
    )
    
    return report


@router.get("/security-status")
async def get_security_report(
    current_user: User = Depends(get_current_user)
):
    """
    Generate security and compliance status report.
    
    Requires ADMIN role.
    """
    require_role(current_user, [UserRole.ADMIN])
    
    with logfire.span("generate_security_report"):
        report = await hipaa_audit_report.generate_security_report()
    
    logfire.info(
        "Security status report generated",
        user_id=current_user.id
    )
    
    return report


@router.get("/compliance-summary")
async def get_compliance_summary(
    current_user: User = Depends(get_current_user)
):
    """
    Generate overall HIPAA compliance summary.
    
    Requires ADMIN role.
    """
    require_role(current_user, [UserRole.ADMIN])
    
    with logfire.span("generate_compliance_summary"):
        report = await hipaa_audit_report.generate_compliance_summary()
    
    logfire.info(
        "HIPAA compliance summary generated",
        user_id=current_user.id,
        compliance_score=report.get("overall_compliance_score")
    )
    
    return report


@router.post("/export-audit-logs")
async def export_audit_logs(
    start_date: datetime,
    end_date: datetime,
    format: str = Query("json", enum=["json", "csv"], description="Export format"),
    current_user: User = Depends(get_current_user)
):
    """
    Export audit logs for external analysis or archival.
    
    Requires ADMIN role.
    """
    require_role(current_user, [UserRole.ADMIN])
    
    # Validate date range
    if start_date > end_date:
        raise HTTPException(status_code=400, detail="Start date must be before end date")
    
    if (end_date - start_date).days > 90:
        raise HTTPException(status_code=400, detail="Export range cannot exceed 90 days")
    
    # Generate access report
    report = await hipaa_audit_report.generate_access_report(
        start_date=start_date,
        end_date=end_date
    )
    
    logfire.info(
        "Audit logs exported",
        user_id=current_user.id,
        format=format,
        records=len(report.get("access_logs", []))
    )
    
    if format == "csv":
        # Convert to CSV format
        import csv
        import io
        
        output = io.StringIO()
        if report["access_logs"]:
            writer = csv.DictWriter(output, fieldnames=report["access_logs"][0].keys())
            writer.writeheader()
            writer.writerows(report["access_logs"])
        
        return {
            "content_type": "text/csv",
            "filename": f"audit_logs_{start_date.date()}_{end_date.date()}.csv",
            "data": output.getvalue()
        }
    
    return {
        "content_type": "application/json",
        "filename": f"audit_logs_{start_date.date()}_{end_date.date()}.json",
        "data": report
    }