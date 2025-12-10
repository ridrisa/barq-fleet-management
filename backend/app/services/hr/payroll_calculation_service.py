"""
Payroll Calculation Service

Implements category-based salary calculation formulas from salary.md specification.
Supports 6 categories: Motorcycle, Food Trial, Food In-House New, Food In-House Old, Ecommerce WH, Ecommerce
"""

import json
import logging
import math
from datetime import date, datetime
from decimal import ROUND_HALF_UP, Decimal
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.fleet.courier import Courier
from app.models.hr.payroll_category import (
    CourierTarget,
    DEFAULT_PAYROLL_PARAMETERS,
    PayrollCategory,
    PayrollParameters,
)
from app.models.hr.salary import Salary
from app.schemas.hr.payroll import (
    BatchPayrollRequest,
    BatchPayrollResponse,
    CourierPayrollInput,
    PayrollCalculationResult,
    PayrollCategoryEnum,
    PeriodInput,
)

logger = logging.getLogger(__name__)


def to_decimal(value: Any, default: Decimal = Decimal("0")) -> Decimal:
    """Safely convert value to Decimal"""
    if value is None:
        return default
    if isinstance(value, Decimal):
        return value
    try:
        return Decimal(str(value))
    except Exception:
        return default


def round_decimal(value: Decimal, places: int = 2) -> Decimal:
    """Round decimal to specified places"""
    return value.quantize(Decimal(10) ** -places, rounding=ROUND_HALF_UP)


class PayrollCalculationService:
    """
    Service for calculating courier salaries based on category-specific formulas.

    Per salary.md, this service handles:
    - Motorcycle: Order-based with 13.333 daily divisor
    - Food Trial: Order-based with 13 daily divisor
    - Food In-House New: Order-based with 15.833 daily divisor
    - Food In-House Old: Order-based with tiered bonus (6/9 SAR)
    - Ecommerce WH: Order-based with 16.667 daily divisor
    - Ecommerce: Revenue-based with coefficient calculation
    """

    def __init__(self, db: AsyncSession, organization_id: int):
        self.db = db
        self.organization_id = organization_id
        self._params_cache: Dict[PayrollCategory, Dict] = {}

    async def get_parameters(self, category: PayrollCategory) -> Dict[str, Decimal]:
        """
        Get payroll parameters for a category.

        Priority:
        1. Organization-specific parameters from database
        2. Default parameters from salary.md
        """
        if category in self._params_cache:
            return self._params_cache[category]

        # Try to get org-specific parameters
        result = await self.db.execute(
            select(PayrollParameters).where(
                PayrollParameters.organization_id == self.organization_id,
                PayrollParameters.category == category,
                PayrollParameters.is_active == 1,
            )
        )
        db_params = result.scalar_one_or_none()

        if db_params:
            params = {
                "basic_salary_rate": to_decimal(db_params.basic_salary_rate),
                "bonus_rate": to_decimal(db_params.bonus_rate),
                "penalty_rate": to_decimal(db_params.penalty_rate, Decimal("10")),
                "gas_rate": to_decimal(db_params.gas_rate),
                "gas_cap": to_decimal(db_params.gas_cap),
                "daily_order_divisor": to_decimal(db_params.daily_order_divisor),
                "revenue_coefficient": to_decimal(db_params.revenue_coefficient),
                "tier_threshold": db_params.tier_threshold,
                "tier_1_rate": to_decimal(db_params.tier_1_rate),
                "tier_2_rate": to_decimal(db_params.tier_2_rate),
                "bonus_revenue_threshold": to_decimal(db_params.bonus_revenue_threshold),
                "bonus_rate_below_threshold": to_decimal(db_params.bonus_rate_below_threshold),
                "bonus_rate_above_threshold": to_decimal(db_params.bonus_rate_above_threshold),
                "fuel_revenue_coefficient": to_decimal(db_params.fuel_revenue_coefficient),
                "fuel_target_coefficient": to_decimal(db_params.fuel_target_coefficient),
            }
        else:
            # Use defaults from salary.md
            defaults = DEFAULT_PAYROLL_PARAMETERS.get(category, {})
            params = {k: to_decimal(v) for k, v in defaults.items()}

        self._params_cache[category] = params
        return params

    def calculate_days_since_joining(
        self, joining_date: date, as_of_date: Optional[date] = None
    ) -> int:
        """
        Calculate days since joining per salary.md section 3.

        days_since_joining = max(0, (today_date - joining_Date).days + 1)
        """
        if as_of_date is None:
            as_of_date = date.today()

        delta = (as_of_date - joining_date).days + 1
        return max(0, delta)

    async def calculate_motorcycle(
        self, input_data: CourierPayrollInput, params: Dict[str, Decimal]
    ) -> PayrollCalculationResult:
        """
        Calculate salary for Motorcycle category (salary.md section 5.1)

        Formula:
        - final_target = min(ceil(TARGET), days_since_joining * 13.333)
        - basic_salary = (final_target / 13.333) * rate
        - bonus/penalty based on orders vs target
        - gas_deserved = min(orders * 0.65, 261)
        """
        days = self.calculate_days_since_joining(input_data.joining_date)
        target_input = to_decimal(input_data.target)
        total_orders = input_data.total_orders
        gas_usage = to_decimal(input_data.gas_usage)

        divisor = params.get("daily_order_divisor", Decimal("13.333"))
        basic_rate = params.get("basic_salary_rate", Decimal("53.33333"))
        bonus_rate = params.get("bonus_rate", Decimal("6"))
        penalty_rate = params.get("penalty_rate", Decimal("10"))
        gas_rate = params.get("gas_rate", Decimal("0.65"))
        gas_cap = params.get("gas_cap", Decimal("261"))

        # final_target = min(ceil(TARGET), days_since_joining * 13.333)
        target_ceiling = math.ceil(float(target_input))
        days_target = Decimal(str(days)) * divisor
        final_target = min(Decimal(str(target_ceiling)), days_target)

        # basic_salary = (final_target / 13.333) * rate
        basic_salary = (final_target / divisor) * basic_rate

        # bonus_orders = Total_Orders - final_target
        bonus_orders = Decimal(str(total_orders)) - final_target

        if bonus_orders > 0:
            bonus_amount = bonus_orders * bonus_rate
        else:
            bonus_amount = bonus_orders * penalty_rate  # Negative = penalty

        # gas_deserved = min(Total_Orders * gas_rate, gas_cap)
        gas_deserved = min(Decimal(str(total_orders)) * gas_rate, gas_cap)
        gas_difference = gas_deserved - gas_usage

        # total_salary = max(0, basic + bonus + gas_diff)
        total_salary = max(Decimal("0"), basic_salary + bonus_amount + gas_difference)

        return self._build_result(
            input_data=input_data,
            basic_salary=basic_salary,
            bonus_amount=bonus_amount,
            gas_deserved=gas_deserved,
            gas_difference=gas_difference,
            total_salary=total_salary,
            final_target=final_target,
            days=days,
            category=PayrollCategoryEnum.MOTORCYCLE,
            calculation_details={
                "divisor": str(divisor),
                "target_ceiling": target_ceiling,
                "days_target": str(round_decimal(days_target)),
                "bonus_orders": str(round_decimal(bonus_orders)),
            },
        )

    async def calculate_food_trial(
        self, input_data: CourierPayrollInput, params: Dict[str, Decimal]
    ) -> PayrollCalculationResult:
        """
        Calculate salary for Food Trial category (salary.md section 5.2)

        Formula:
        - target_v2 = days_since_joining * 13
        - final_target = min(TARGET, target_v2)
        - basic_salary = (final_target / 13) * rate
        """
        days = self.calculate_days_since_joining(input_data.joining_date)
        target_input = to_decimal(input_data.target)
        total_orders = input_data.total_orders
        gas_usage = to_decimal(input_data.gas_usage)

        divisor = params.get("daily_order_divisor", Decimal("13"))
        basic_rate = params.get("basic_salary_rate", Decimal("66.66666667"))
        bonus_rate = params.get("bonus_rate", Decimal("7"))
        penalty_rate = params.get("penalty_rate", Decimal("10"))
        gas_rate = params.get("gas_rate", Decimal("2.11"))
        gas_cap = params.get("gas_cap", Decimal("826"))

        # target_v2 = days_since_joining * 13
        target_v2 = Decimal(str(days)) * divisor
        final_target = min(target_input, target_v2)

        # basic_salary = (final_target / 13) * rate
        basic_salary = (final_target / divisor) * basic_rate

        bonus_orders = Decimal(str(total_orders)) - final_target

        if bonus_orders > 0:
            bonus_amount = bonus_orders * bonus_rate
        else:
            bonus_amount = bonus_orders * penalty_rate

        gas_deserved = min(gas_rate * Decimal(str(total_orders)), gas_cap)
        gas_difference = gas_deserved - gas_usage

        total_salary = max(Decimal("0"), basic_salary + bonus_amount + gas_difference)

        return self._build_result(
            input_data=input_data,
            basic_salary=basic_salary,
            bonus_amount=bonus_amount,
            gas_deserved=gas_deserved,
            gas_difference=gas_difference,
            total_salary=total_salary,
            final_target=final_target,
            days=days,
            category=PayrollCategoryEnum.FOOD_TRIAL,
            calculation_details={
                "divisor": str(divisor),
                "target_v2": str(round_decimal(target_v2)),
                "bonus_orders": str(round_decimal(bonus_orders)),
            },
        )

    async def calculate_food_inhouse_new(
        self, input_data: CourierPayrollInput, params: Dict[str, Decimal]
    ) -> PayrollCalculationResult:
        """
        Calculate salary for Food In-House New category (salary.md section 5.3)

        Formula:
        - target_v2 = days_since_joining * 15.8333333
        - final_target = min(TARGET, target_v2)
        - basic_salary = (final_target / 15.83333333) * rate
        """
        days = self.calculate_days_since_joining(input_data.joining_date)
        target_input = to_decimal(input_data.target)
        total_orders = input_data.total_orders
        gas_usage = to_decimal(input_data.gas_usage)

        divisor = params.get("daily_order_divisor", Decimal("15.83333333"))
        basic_rate = params.get("basic_salary_rate", Decimal("66.66666667"))
        bonus_rate = params.get("bonus_rate", Decimal("7"))
        penalty_rate = params.get("penalty_rate", Decimal("10"))
        gas_rate = params.get("gas_rate", Decimal("1.739"))
        gas_cap = params.get("gas_cap", Decimal("826"))

        target_v2 = Decimal(str(days)) * divisor
        final_target = min(target_input, target_v2)

        basic_salary = (final_target / divisor) * basic_rate

        bonus_orders = Decimal(str(total_orders)) - final_target

        if bonus_orders > 0:
            bonus_amount = bonus_orders * bonus_rate
        else:
            bonus_amount = bonus_orders * penalty_rate

        gas_deserved = min(gas_rate * Decimal(str(total_orders)), gas_cap)
        gas_difference = gas_deserved - gas_usage

        total_salary = max(Decimal("0"), basic_salary + bonus_amount + gas_difference)

        return self._build_result(
            input_data=input_data,
            basic_salary=basic_salary,
            bonus_amount=bonus_amount,
            gas_deserved=gas_deserved,
            gas_difference=gas_difference,
            total_salary=total_salary,
            final_target=final_target,
            days=days,
            category=PayrollCategoryEnum.FOOD_INHOUSE_NEW,
            calculation_details={
                "divisor": str(divisor),
                "target_v2": str(round_decimal(target_v2)),
                "bonus_orders": str(round_decimal(bonus_orders)),
            },
        )

    async def calculate_food_inhouse_old(
        self, input_data: CourierPayrollInput, params: Dict[str, Decimal]
    ) -> PayrollCalculationResult:
        """
        Calculate salary for Food In-House Old category (salary.md section 5.4)

        Formula with TIERED BONUS:
        - target_v2 = days_since_joining * 15.8333333
        - final_target = min(TARGET, target_v2)
        - If bonus_orders <= 0: penalty
        - If bonus_orders > 199: bonus = orders * 9
        - Else: bonus = orders * 6
        """
        days = self.calculate_days_since_joining(input_data.joining_date)
        target_input = to_decimal(input_data.target)
        total_orders = input_data.total_orders
        gas_usage = to_decimal(input_data.gas_usage)

        divisor = params.get("daily_order_divisor", Decimal("15.83333333"))
        basic_rate = params.get("basic_salary_rate", Decimal("66.66666667"))
        penalty_rate = params.get("penalty_rate", Decimal("10"))
        gas_rate = params.get("gas_rate", Decimal("2.065"))
        gas_cap = params.get("gas_cap", Decimal("826"))
        tier_threshold = params.get("tier_threshold", 199)
        tier_1_rate = params.get("tier_1_rate", Decimal("6"))
        tier_2_rate = params.get("tier_2_rate", Decimal("9"))

        target_v2 = Decimal(str(days)) * divisor
        final_target = min(target_input, target_v2)

        basic_salary = (final_target / divisor) * basic_rate

        bonus_orders = Decimal(str(total_orders)) - final_target

        if bonus_orders <= 0:
            # Below target → pure penalties
            bonus_amount = bonus_orders * penalty_rate
        else:
            # Above target → tiered bonus
            if bonus_orders > tier_threshold:
                bonus_amount = bonus_orders * tier_2_rate
            else:
                bonus_amount = bonus_orders * tier_1_rate

        gas_deserved = min(gas_rate * Decimal(str(total_orders)), gas_cap)
        gas_difference = gas_deserved - gas_usage

        total_salary = max(Decimal("0"), basic_salary + bonus_amount + gas_difference)

        return self._build_result(
            input_data=input_data,
            basic_salary=basic_salary,
            bonus_amount=bonus_amount,
            gas_deserved=gas_deserved,
            gas_difference=gas_difference,
            total_salary=total_salary,
            final_target=final_target,
            days=days,
            category=PayrollCategoryEnum.FOOD_INHOUSE_OLD,
            calculation_details={
                "divisor": str(divisor),
                "target_v2": str(round_decimal(target_v2)),
                "bonus_orders": str(round_decimal(bonus_orders)),
                "tier_threshold": tier_threshold,
                "tier_used": "tier_2" if bonus_orders > tier_threshold else "tier_1",
            },
        )

    async def calculate_ecommerce_wh(
        self, input_data: CourierPayrollInput, params: Dict[str, Decimal]
    ) -> PayrollCalculationResult:
        """
        Calculate salary for Ecommerce WH category (salary.md section 5.5)

        Formula:
        - target2 = days_since_joining * 16.66667
        - final_target = min(TARGET, target2)
        - Gas deserved based on final_target (not total_orders)
        """
        days = self.calculate_days_since_joining(input_data.joining_date)
        target_input = to_decimal(input_data.target)
        total_orders = input_data.total_orders
        gas_usage = to_decimal(input_data.gas_usage)

        divisor = params.get("daily_order_divisor", Decimal("16.6666667"))
        basic_rate = params.get("basic_salary_rate", Decimal("66.666667"))
        bonus_rate = params.get("bonus_rate", Decimal("8"))
        penalty_rate = params.get("penalty_rate", Decimal("10"))
        gas_rate = params.get("gas_rate", Decimal("15.03"))
        gas_cap = params.get("gas_cap", Decimal("452"))

        target2 = Decimal(str(days)) * divisor
        final_target = min(target_input, target2)

        basic_salary = (final_target / divisor) * basic_rate

        bonus_orders = Decimal(str(total_orders)) - final_target

        if bonus_orders > 0:
            bonus_amount = bonus_orders * bonus_rate
        else:
            bonus_amount = bonus_orders * penalty_rate

        # Gas deserved is based on final_target, not total_orders
        diesel_deserved = min((final_target / divisor) * gas_rate, gas_cap)
        gas_difference = diesel_deserved - gas_usage

        total_salary = max(Decimal("0"), basic_salary + bonus_amount + gas_difference)

        return self._build_result(
            input_data=input_data,
            basic_salary=basic_salary,
            bonus_amount=bonus_amount,
            gas_deserved=diesel_deserved,
            gas_difference=gas_difference,
            total_salary=total_salary,
            final_target=final_target,
            days=days,
            category=PayrollCategoryEnum.ECOMMERCE_WH,
            calculation_details={
                "divisor": str(divisor),
                "target2": str(round_decimal(target2)),
                "bonus_orders": str(round_decimal(bonus_orders)),
                "note": "Gas based on target, not orders",
            },
        )

    async def calculate_ecommerce(
        self, input_data: CourierPayrollInput, params: Dict[str, Decimal]
    ) -> PayrollCalculationResult:
        """
        Calculate salary for Ecommerce category (salary.md section 5.6)

        REVENUE-BASED formula:
        - target2 = days_since_joining * 221
        - final_target = min(TARGET, target2)
        - basic_salary = MIN(revenue * coef, target_based)
        - Bonus based on revenue above target with tiered rates
        - Fuel is three-way minimum
        """
        days = self.calculate_days_since_joining(input_data.joining_date)
        target_input = to_decimal(input_data.target)
        total_orders = input_data.total_orders
        total_revenue = to_decimal(input_data.total_revenue)
        gas_usage = to_decimal(input_data.gas_usage)

        divisor = params.get("daily_order_divisor", Decimal("221"))
        basic_rate = params.get("basic_salary_rate", Decimal("66.66666667"))
        revenue_coef = params.get("revenue_coefficient", Decimal("0.3016591252"))
        gas_cap = params.get("gas_cap", Decimal("452"))
        bonus_threshold = params.get("bonus_revenue_threshold", Decimal("4000"))
        bonus_rate_below = params.get("bonus_rate_below_threshold", Decimal("0.55"))
        bonus_rate_above = params.get("bonus_rate_above_threshold", Decimal("0.5"))
        fuel_revenue_coef = params.get("fuel_revenue_coefficient", Decimal("0.068"))
        fuel_target_coef = params.get("fuel_target_coefficient", Decimal("15.06"))

        target2 = Decimal(str(days)) * divisor
        final_target = min(target_input, target2)

        # Two possible basic salaries
        revenue_based_salary = total_revenue * revenue_coef
        target_based_salary = (final_target / divisor) * basic_rate

        # Basic salary is the MINIMUM of the two
        basic_salary = min(revenue_based_salary, target_based_salary)

        # Bonus based on revenue above final_target
        bonus_revenue = max(Decimal("0"), total_revenue - final_target)

        if bonus_revenue <= bonus_threshold:
            bonus_amount = bonus_revenue * bonus_rate_below
        else:
            # (4000 * 0.55) + ((bonus_revenue - 4000) * 0.5)
            bonus_amount = (bonus_threshold * bonus_rate_below) + (
                (bonus_revenue - bonus_threshold) * bonus_rate_above
            )

        # Fuel compensation: three-way minimum
        diesel_deserved = min(
            fuel_revenue_coef * total_revenue,
            (final_target / divisor) * fuel_target_coef,
            gas_cap,
        )
        gas_difference = diesel_deserved - gas_usage

        total_salary = max(Decimal("0"), basic_salary + bonus_amount + gas_difference)

        return self._build_result(
            input_data=input_data,
            basic_salary=basic_salary,
            bonus_amount=bonus_amount,
            gas_deserved=diesel_deserved,
            gas_difference=gas_difference,
            total_salary=total_salary,
            final_target=final_target,
            days=days,
            category=PayrollCategoryEnum.ECOMMERCE,
            calculation_details={
                "divisor": str(divisor),
                "target2": str(round_decimal(target2)),
                "revenue_based_salary": str(round_decimal(revenue_based_salary)),
                "target_based_salary": str(round_decimal(target_based_salary)),
                "salary_method": (
                    "revenue_based" if basic_salary == revenue_based_salary else "target_based"
                ),
                "bonus_revenue": str(round_decimal(bonus_revenue)),
                "fuel_calc": "three_way_min(revenue*0.068, target_based*15.06, cap)",
            },
        )

    def _build_result(
        self,
        input_data: CourierPayrollInput,
        basic_salary: Decimal,
        bonus_amount: Decimal,
        gas_deserved: Decimal,
        gas_difference: Decimal,
        total_salary: Decimal,
        final_target: Decimal,
        days: int,
        category: PayrollCategoryEnum,
        calculation_details: Optional[Dict] = None,
    ) -> PayrollCalculationResult:
        """Build standardized result object"""
        return PayrollCalculationResult(
            barq_id=input_data.barq_id,
            courier_id=input_data.courier_id,
            iban=input_data.iban,
            id_number=input_data.id_number,
            name=input_data.name,
            status=input_data.status,
            sponsorship_status=input_data.sponsorship_status,
            project=input_data.project,
            supervisor=input_data.supervisor,
            total_orders=input_data.total_orders,
            total_revenue=input_data.total_revenue,
            gas_usage=input_data.gas_usage,
            basic_salary=round_decimal(basic_salary),
            bonus_amount=round_decimal(bonus_amount),
            gas_deserved=round_decimal(gas_deserved),
            gas_difference=round_decimal(gas_difference),
            total_salary=round_decimal(total_salary),
            target=round_decimal(final_target),
            days_since_joining=days,
            period={},  # Will be set by caller
            generated_date=date.today().isoformat(),
            category=category,
            calculation_details=calculation_details,
        )

    async def calculate_single(
        self, input_data: CourierPayrollInput, period: Optional[PeriodInput] = None
    ) -> PayrollCalculationResult:
        """
        Calculate salary for a single courier.

        Auto-determines category if not provided.
        """
        # Determine category
        if input_data.category:
            category = PayrollCategory(input_data.category.value)
        else:
            # Default to Motorcycle if not specified
            category = PayrollCategory.MOTORCYCLE
            logger.warning(
                f"No category specified for courier {input_data.barq_id}, defaulting to Motorcycle"
            )

        # Skip Ajeer
        if category == PayrollCategory.AJEER:
            raise ValueError(f"Ajeer category is excluded from payroll calculation")

        # Get parameters
        params = await self.get_parameters(category)

        # Calculate based on category
        calculator_map = {
            PayrollCategory.MOTORCYCLE: self.calculate_motorcycle,
            PayrollCategory.FOOD_TRIAL: self.calculate_food_trial,
            PayrollCategory.FOOD_INHOUSE_NEW: self.calculate_food_inhouse_new,
            PayrollCategory.FOOD_INHOUSE_OLD: self.calculate_food_inhouse_old,
            PayrollCategory.ECOMMERCE_WH: self.calculate_ecommerce_wh,
            PayrollCategory.ECOMMERCE: self.calculate_ecommerce,
        }

        calculator = calculator_map.get(category)
        if not calculator:
            raise ValueError(f"No calculator for category: {category}")

        result = await calculator(input_data, params)

        # Add period info if provided
        if period:
            result.period = {
                "start_date": period.start_date.isoformat(),
                "end_date": period.end_date.isoformat(),
                "month": str(period.month),
                "year": str(period.year),
            }

        return result

    async def calculate_batch(
        self, request: BatchPayrollRequest
    ) -> BatchPayrollResponse:
        """
        Calculate salaries for multiple couriers.
        """
        results: List[PayrollCalculationResult] = []
        errors: List[Dict[str, str]] = []
        successful = 0
        failed = 0
        skipped = 0

        # Get couriers from database
        query = select(Courier).where(Courier.organization_id == self.organization_id)

        if request.courier_ids:
            query = query.where(Courier.id.in_(request.courier_ids))

        if not request.include_inactive:
            query = query.where(Courier.status == "active")

        result = await self.db.execute(query)
        couriers = result.scalars().all()

        for courier in couriers:
            try:
                # Get target for this courier/period
                target_result = await self.db.execute(
                    select(CourierTarget).where(
                        CourierTarget.courier_id == courier.id,
                        CourierTarget.month == request.period.month,
                        CourierTarget.year == request.period.year,
                        CourierTarget.organization_id == self.organization_id,
                    )
                )
                target_record = target_result.scalar_one_or_none()
                daily_target = Decimal(str(target_record.daily_target)) if target_record else Decimal("0")

                # Determine category
                category = None
                if target_record and target_record.category:
                    category = PayrollCategoryEnum(target_record.category.value)
                elif request.categories and len(request.categories) == 1:
                    category = request.categories[0]

                # Skip Ajeer
                if category == PayrollCategoryEnum.AJEER:
                    skipped += 1
                    continue

                # Build input
                input_data = CourierPayrollInput(
                    barq_id=courier.barq_id or str(courier.id),
                    courier_id=courier.id,
                    iban=courier.iban,
                    id_number=courier.national_id,
                    name=courier.full_name,
                    status=courier.status or "unknown",
                    sponsorship_status=courier.sponsorship_status,
                    project=courier.project_type,
                    supervisor=courier.supervisor_name,
                    joining_date=courier.joining_date or date.today(),
                    total_orders=0,  # TODO: Get from BigQuery
                    total_revenue=Decimal("0"),  # TODO: Get from BigQuery
                    gas_usage=Decimal("0"),  # TODO: Get from BigQuery
                    target=daily_target,
                    category=category,
                )

                calc_result = await self.calculate_single(input_data, request.period)
                results.append(calc_result)
                successful += 1

            except Exception as e:
                failed += 1
                errors.append({
                    "courier_id": str(courier.id),
                    "barq_id": courier.barq_id or "",
                    "error": str(e),
                })
                logger.error(f"Error calculating salary for courier {courier.id}: {e}")

        # Calculate totals
        total_basic = sum(r.basic_salary for r in results)
        total_bonus = sum(r.bonus_amount for r in results)
        total_gas = sum(r.gas_deserved for r in results)
        total_payroll = sum(r.total_salary for r in results)

        return BatchPayrollResponse(
            period={
                "start_date": request.period.start_date.isoformat(),
                "end_date": request.period.end_date.isoformat(),
                "month": str(request.period.month),
                "year": str(request.period.year),
            },
            total_couriers=len(couriers),
            successful=successful,
            failed=failed,
            skipped=skipped,
            results=results,
            errors=errors,
            total_basic_salary=round_decimal(total_basic),
            total_bonus=round_decimal(total_bonus),
            total_gas_deserved=round_decimal(total_gas),
            total_payroll=round_decimal(total_payroll),
        )

    async def save_salary_record(
        self, result: PayrollCalculationResult, period: PeriodInput
    ) -> Salary:
        """
        Save calculated salary to database.
        """
        # Check for existing record
        existing = await self.db.execute(
            select(Salary).where(
                Salary.courier_id == result.courier_id,
                Salary.month == period.month,
                Salary.year == period.year,
                Salary.organization_id == self.organization_id,
            )
        )
        salary = existing.scalar_one_or_none()

        if salary:
            # Update existing
            salary.category = PayrollCategory(result.category.value)
            salary.period_start = period.start_date
            salary.period_end = period.end_date
            salary.total_orders = result.total_orders
            salary.total_revenue = result.total_revenue
            salary.gas_usage = result.gas_usage
            salary.target = result.target
            salary.days_since_joining = result.days_since_joining
            salary.base_salary = result.basic_salary
            salary.bonus_amount = result.bonus_amount
            salary.gas_deserved = result.gas_deserved
            salary.gas_difference = result.gas_difference
            salary.gross_salary = result.total_salary
            salary.net_salary = result.total_salary
            salary.calculation_details = json.dumps(result.calculation_details)
            salary.generated_date = date.today()
        else:
            # Create new
            salary = Salary(
                organization_id=self.organization_id,
                courier_id=result.courier_id,
                month=period.month,
                year=period.year,
                category=PayrollCategory(result.category.value),
                period_start=period.start_date,
                period_end=period.end_date,
                total_orders=result.total_orders,
                total_revenue=result.total_revenue,
                gas_usage=result.gas_usage,
                target=result.target,
                days_since_joining=result.days_since_joining,
                base_salary=result.basic_salary,
                bonus_amount=result.bonus_amount,
                gas_deserved=result.gas_deserved,
                gas_difference=result.gas_difference,
                gross_salary=result.total_salary,
                net_salary=result.total_salary,
                calculation_details=json.dumps(result.calculation_details),
                generated_date=date.today(),
            )
            self.db.add(salary)

        await self.db.flush()
        return salary
