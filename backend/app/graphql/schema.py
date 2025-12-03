"""
GraphQL Schema for BARQ Fleet
Main schema definition with Query and Mutation types
"""

import strawberry
from typing import List, Optional
from strawberry.types import Info

from app.graphql.types import (
    LoanType, LeaveTypeGQL, SalaryType,
    VehicleTypeGQL, VehicleAssignmentType, CourierType,
    BuildingType, RoomType, CourierDashboard,
    LeaveRequestInput, LoanRequestInput, MutationResponse,
)
from app.graphql.resolvers import QueryResolvers
from app.core.database import get_db


def get_db_session(info: Info):
    """Get database session from context or create new one"""
    if hasattr(info.context, 'db'):
        return info.context.db
    # Fallback: create new session
    return next(get_db())


@strawberry.type
class Query:
    """GraphQL Query type - Read operations"""

    # ============================================
    # COURIER QUERIES
    # ============================================

    @strawberry.field
    def courier(self, info: Info, courier_id: int) -> Optional[CourierType]:
        """Get courier by ID"""
        db = get_db_session(info)
        return QueryResolvers.get_courier(db, courier_id)

    @strawberry.field
    def courier_by_barq_id(self, info: Info, barq_id: str) -> Optional[CourierType]:
        """Get courier by BARQ ID"""
        db = get_db_session(info)
        return QueryResolvers.get_courier_by_barq_id(db, barq_id)

    @strawberry.field
    def courier_dashboard(self, info: Info, courier_id: int) -> Optional[CourierDashboard]:
        """Get aggregated courier dashboard data"""
        db = get_db_session(info)
        return QueryResolvers.get_courier_dashboard(db, courier_id)

    # ============================================
    # HR QUERIES - LOANS
    # ============================================

    @strawberry.field
    def courier_loans(self, info: Info, courier_id: int) -> List[LoanType]:
        """Get all loans for a courier"""
        db = get_db_session(info)
        return QueryResolvers.get_courier_loans(db, courier_id)

    @strawberry.field
    def courier_active_loans(self, info: Info, courier_id: int) -> List[LoanType]:
        """Get active loans for a courier"""
        db = get_db_session(info)
        return QueryResolvers.get_courier_active_loans(db, courier_id)

    # ============================================
    # HR QUERIES - LEAVES
    # ============================================

    @strawberry.field
    def courier_leaves(self, info: Info, courier_id: int) -> List[LeaveTypeGQL]:
        """Get all leave requests for a courier"""
        db = get_db_session(info)
        return QueryResolvers.get_courier_leaves(db, courier_id)

    @strawberry.field
    def courier_pending_leaves(self, info: Info, courier_id: int) -> List[LeaveTypeGQL]:
        """Get pending leave requests for a courier"""
        db = get_db_session(info)
        return QueryResolvers.get_courier_pending_leaves(db, courier_id)

    # ============================================
    # HR QUERIES - SALARIES
    # ============================================

    @strawberry.field
    def courier_salaries(
        self, info: Info, courier_id: int, limit: int = 12
    ) -> List[SalaryType]:
        """Get salary history for a courier"""
        db = get_db_session(info)
        return QueryResolvers.get_courier_salaries(db, courier_id, limit)

    # ============================================
    # FLEET QUERIES - VEHICLES
    # ============================================

    @strawberry.field
    def courier_vehicle(self, info: Info, courier_id: int) -> Optional[VehicleTypeGQL]:
        """Get currently assigned vehicle for a courier"""
        db = get_db_session(info)
        return QueryResolvers.get_courier_vehicle(db, courier_id)

    @strawberry.field
    def vehicle(self, info: Info, vehicle_id: int) -> Optional[VehicleTypeGQL]:
        """Get vehicle by ID"""
        db = get_db_session(info)
        return QueryResolvers.get_vehicle(db, vehicle_id)

    # ============================================
    # FLEET QUERIES - ASSIGNMENTS
    # ============================================

    @strawberry.field
    def courier_assignments(self, info: Info, courier_id: int) -> List[VehicleAssignmentType]:
        """Get vehicle assignment history for a courier"""
        db = get_db_session(info)
        return QueryResolvers.get_courier_assignments(db, courier_id)

    @strawberry.field
    def courier_active_assignment(
        self, info: Info, courier_id: int
    ) -> Optional[VehicleAssignmentType]:
        """Get active vehicle assignment for a courier"""
        db = get_db_session(info)
        return QueryResolvers.get_courier_active_assignment(db, courier_id)

    # ============================================
    # ACCOMMODATION QUERIES
    # ============================================

    @strawberry.field
    def buildings(self, info: Info) -> List[BuildingType]:
        """Get all accommodation buildings"""
        db = get_db_session(info)
        return QueryResolvers.get_buildings(db)

    @strawberry.field
    def building(self, info: Info, building_id: int) -> Optional[BuildingType]:
        """Get building by ID"""
        db = get_db_session(info)
        return QueryResolvers.get_building(db, building_id)

    @strawberry.field
    def building_rooms(self, info: Info, building_id: int) -> List[RoomType]:
        """Get all rooms in a building"""
        db = get_db_session(info)
        return QueryResolvers.get_building_rooms(db, building_id)

    @strawberry.field
    def room(self, info: Info, room_id: int) -> Optional[RoomType]:
        """Get room by ID"""
        db = get_db_session(info)
        return QueryResolvers.get_room(db, room_id)

    @strawberry.field
    def courier_accommodation(self, info: Info, courier_id: int) -> Optional[RoomType]:
        """Get courier's assigned accommodation"""
        db = get_db_session(info)
        return QueryResolvers.get_courier_accommodation(db, courier_id)


@strawberry.type
class Mutation:
    """GraphQL Mutation type - Write operations"""

    @strawberry.mutation
    def request_leave(
        self, info: Info, courier_id: int, input: LeaveRequestInput
    ) -> MutationResponse:
        """Submit a leave request"""
        db = get_db_session(info)
        try:
            from app.models.hr.leave import Leave, LeaveType as DBLeaveType, LeaveStatus as DBLeaveStatus

            leave = Leave(
                courier_id=courier_id,
                leave_type=DBLeaveType(input.leave_type.value),
                start_date=input.start_date,
                end_date=input.end_date,
                days=input.days,
                reason=input.reason,
                status=DBLeaveStatus.PENDING,
            )
            db.add(leave)
            db.commit()
            db.refresh(leave)

            return MutationResponse(
                success=True,
                message="Leave request submitted successfully",
                id=leave.id,
            )
        except Exception as e:
            db.rollback()
            return MutationResponse(
                success=False,
                message=f"Failed to submit leave request: {str(e)}",
            )

    @strawberry.mutation
    def cancel_leave(self, info: Info, leave_id: int) -> MutationResponse:
        """Cancel a pending leave request"""
        db = get_db_session(info)
        try:
            from app.models.hr.leave import Leave, LeaveStatus as DBLeaveStatus

            leave = db.query(Leave).filter(Leave.id == leave_id).first()
            if not leave:
                return MutationResponse(success=False, message="Leave request not found")

            if leave.status != DBLeaveStatus.PENDING:
                return MutationResponse(
                    success=False,
                    message="Only pending leave requests can be cancelled",
                )

            leave.status = DBLeaveStatus.CANCELLED
            db.commit()

            return MutationResponse(
                success=True,
                message="Leave request cancelled successfully",
                id=leave_id,
            )
        except Exception as e:
            db.rollback()
            return MutationResponse(
                success=False,
                message=f"Failed to cancel leave request: {str(e)}",
            )

    @strawberry.mutation
    def request_loan(
        self, info: Info, courier_id: int, input: LoanRequestInput
    ) -> MutationResponse:
        """Submit a loan request"""
        db = get_db_session(info)
        try:
            from app.models.hr.loan import Loan, LoanStatus as DBLoanStatus

            loan = Loan(
                courier_id=courier_id,
                amount=input.amount,
                outstanding_balance=input.amount,  # Initially full amount
                monthly_deduction=input.monthly_deduction,
                start_date=input.start_date,
                status=DBLoanStatus.ACTIVE,
                notes=input.reason,
            )
            db.add(loan)
            db.commit()
            db.refresh(loan)

            return MutationResponse(
                success=True,
                message="Loan request submitted successfully",
                id=loan.id,
            )
        except Exception as e:
            db.rollback()
            return MutationResponse(
                success=False,
                message=f"Failed to submit loan request: {str(e)}",
            )


# Create the schema
schema = strawberry.Schema(query=Query, mutation=Mutation)
