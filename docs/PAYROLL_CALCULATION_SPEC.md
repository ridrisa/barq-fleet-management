
## 1. Categories in Scope

Handle **only** these categories:

* `"Motorcycle"`
* `"Food Trial"`
* `"Food In-House New"`
* `"Food In-House Old"`
* `"Ecommerce WH"`
* `"Ecommerce"`

Ignore / skip `"Ajeer"` completely.

---

## 2. Required Inputs per Courier (for a given period)

For **each courier**, the AI will receive (or can query) at least:

* `BARQ_ID`
* `iban`
* `id_number`
* `joining_Date` (string `"YYYY-MM-DD"`)
* `Name`
* `Status`
* `Sponsorshipstatus`
* `PROJECT`
* `Supervisor`
* `Total_Orders`  (sum of `total_Orders` over the period)
* `Total_Revenue` (sum of `Total_revenue` over the period)
* `Gas_Usage`     (sum of `Gas_Usage_without_vat` over the period)
* `TARGET`        (daily target taken from `master_saned.targets` table, one value per courier for that period)
* `category`      (one of: Motorcycle / Food Trial / Food In-House New / Food In-House Old / Ecommerce WH / Ecommerce)

Global context for the period:

* `period.start_date` (string `"YYYY-MM-DD"`)
* `period.end_date`   (string `"YYYY-MM-DD"`)

### 2.1 Period calculation (for non-Ajeer categories)

Given `month` and `year` and `category != "Ajeer"`:

```text
if month == 1:
    start_date = (year - 1)-12-25
    end_date   = year-01-24
else:
    start_date = year-(month-1)-25
    end_date   = year-month-24
```

All salary calculations for that category use this `[start_date, end_date]` date range.

---

## 3. Shared Pre-processing Logic

For each courier record:

1. **Days since joining**

   ```pseudo
   days_since_joining = max(0, (today_date - joining_Date).days + 1)
   ```

   * `today_date` is current date at calculation time.

2. Initialize salary component outputs (will be overwritten by the category logic):

   ```json
   {
     "Basic_Salary": 0,
     "Bonus_Amount": 0,
     "Gas_Deserved": 0,
     "Gas_Difference": 0,
     "Total_Salary": 0,
     "target": 0
   }
   ```

3. Then apply **the category-specific formula** below.

---

## 4. Category Parameters (Default Values)

These can be hardcoded or passed in as configurable params:

### 4.1 Motorcycle

```json
{
  "motorcycle_basic_salary_rate": 53.33333,
  "motorcycle_bonus_rate": 6,
  "motorcycle_penalty_rate": 10,
  "motorcycle_gas_rate": 0.65,
  "motorcycle_gas_cap": 261
}
```

### 4.2 Food Trial

```json
{
  "food_trial_basic_salary_rate": 66.66666667,
  "food_trial_bonus_rate": 7,
  "food_trial_penalty_rate": 10,
  "food_trial_gas_rate": 2.11,
  "food_trial_gas_cap": 826
}
```

### 4.3 Food In-House New

```json
{
  "food_inhouse_new_basic_salary_rate": 66.66666667,
  "food_inhouse_new_bonus_rate": 7,
  "food_inhouse_new_penalty_rate": 10,
  "food_inhouse_new_gas_rate": 1.739,
  "food_inhouse_new_gas_cap": 826
}
```

### 4.4 Food In-House Old

```json
{
  "food_inhouse_old_basic_salary_rate": 66.66666667,
  "food_inhouse_old_penalty_rate": 10,
  "food_inhouse_old_gas_rate": 2.065,
  "food_inhouse_old_gas_cap": 826
}
```

### 4.5 Ecommerce WH

```json
{
  "ecommerce_wh_basic_salary_rate": 66.666667,
  "ecommerce_wh_bonus_rate": 8,
  "ecommerce_wh_penalty_rate": 10,
  "ecommerce_wh_gas_rate": 15.03,
  "ecommerce_wh_gas_cap": 452
}
```

### 4.6 Ecommerce

```json
{
  "ecommerce_basic_salary_rate": 66.66666667,
  "ecommerce_revenue_coefficient": 0.3016591252,
  "ecommerce_gas_cap": 452
}
```

---

## 5. Category-Specific Salary Formulas

For each courier, use the formula that matches their **category**.

### 5.1 Motorcycle

**Inputs:**

* `Total_Orders`, `TARGET`, `Gas_Usage`, `days_since_joining`
* Params shown in 4.1

**Steps:**

```pseudo
final_target = min( ceil(TARGET), days_since_joining * 13.333 )

basic_salary = (final_target / 13.333) * motorcycle_basic_salary_rate

bonus_orders = Total_Orders - final_target

if bonus_orders > 0:
    bonus_amount = bonus_orders * motorcycle_bonus_rate
else:
    bonus_amount = bonus_orders * motorcycle_penalty_rate  # negative = penalty

gas_deserved = min(Total_Orders * motorcycle_gas_rate, motorcycle_gas_cap)

gas_difference = gas_deserved - Gas_Usage

total_salary = max(0, basic_salary + bonus_amount + gas_difference)
```

**Outputs:**

```json
{
  "Basic_Salary": round(basic_salary, 2),
  "Bonus_Amount": round(bonus_amount, 2),
  "Gas_Deserved": round(gas_deserved, 2),
  "Gas_Difference": round(gas_difference, 2),
  "Total_Salary": round(total_salary, 2),
  "target": final_target
}
```

---

### 5.2 Food Trial

**Inputs:**

* `Total_Orders`, `TARGET`, `Gas_Usage`, `days_since_joining`
* Params in 4.2

**Steps:**

```pseudo
target_v2 = days_since_joining * 13
final_target = min(TARGET, target_v2)

basic_salary = (final_target / 13) * food_trial_basic_salary_rate

bonus_orders = Total_Orders - final_target

if bonus_orders > 0:
    bonus_amount = bonus_orders * food_trial_bonus_rate
else:
    bonus_amount = bonus_orders * food_trial_penalty_rate  # negative

gas_deserved = min(food_trial_gas_rate * Total_Orders, food_trial_gas_cap)

gas_difference = gas_deserved - Gas_Usage

total_salary = max(0, basic_salary + bonus_amount + gas_difference)
```

**Outputs:**

```json
{
  "Basic_Salary": round(basic_salary, 2),
  "Bonus_Amount": round(bonus_amount, 2),
  "Gas_Deserved": round(gas_deserved, 2),
  "Gas_Difference": round(gas_difference, 2),
  "Total_Salary": round(total_salary, 2),
  "target": final_target
}
```

---

### 5.3 Food In-House New

**Inputs:**

* `Total_Orders`, `TARGET`, `Gas_Usage`, `days_since_joining`
* Params in 4.3

**Steps:**

```pseudo
target_v2 = days_since_joining * 15.8333333
final_target = min(TARGET, target_v2)

basic_salary = (final_target / 15.83333333) * food_inhouse_new_basic_salary_rate

bonus_orders = Total_Orders - final_target

if bonus_orders > 0:
    bonus_amount = bonus_orders * food_inhouse_new_bonus_rate
else:
    bonus_amount = bonus_orders * food_inhouse_new_penalty_rate  # negative

gas_deserved = min(food_inhouse_new_gas_rate * Total_Orders, food_inhouse_new_gas_cap)

gas_difference = gas_deserved - Gas_Usage

total_salary = max(0, basic_salary + bonus_amount + gas_difference)
```

**Outputs:**

```json
{
  "Basic_Salary": round(basic_salary, 2),
  "Bonus_Amount": round(bonus_amount, 2),
  "Gas_Deserved": round(gas_deserved, 2),
  "Gas_Difference": round(gas_difference, 2),
  "Total_Salary": round(total_salary, 2),
  "target": final_target
}
```

---

### 5.4 Food In-House Old

**Inputs:**

* `Total_Orders`, `TARGET`, `Gas_Usage`, `days_since_joining`
* Params in 4.4

**Steps:**

```pseudo
target_v2 = days_since_joining * 15.8333333
final_target = min(TARGET, target_v2)

basic_salary = (final_target / 15.83333333) * food_inhouse_old_basic_salary_rate

bonus_orders = Total_Orders - final_target

if bonus_orders <= 0:
    # below target → pure penalties
    bonus_amount = bonus_orders * food_inhouse_old_penalty_rate  # negative
else:
    # above target → tiered bonus
    if bonus_orders > 199:
        bonus_amount = bonus_orders * 9
    else:
        bonus_amount = bonus_orders * 6

gas_deserved = min(food_inhouse_old_gas_rate * Total_Orders, food_inhouse_old_gas_cap)

gas_difference = gas_deserved - Gas_Usage

total_salary = max(0, basic_salary + bonus_amount + gas_difference)
```

**Outputs:**

```json
{
  "Basic_Salary": round(basic_salary, 2),
  "Bonus_Amount": round(bonus_amount, 2),
  "Gas_Deserved": round(gas_deserved, 2),
  "Gas_Difference": round(gas_difference, 2),
  "Total_Salary": round(total_salary, 2),
  "target": final_target
}
```

---

### 5.5 Ecommerce WH

**Inputs:**

* `Total_Orders`, `TARGET`, `Gas_Usage`, `days_since_joining`
* Params in 4.5

**Steps:**

```pseudo
target2 = days_since_joining * 16.66667
final_target = min(TARGET, target2)

basic_salary = (final_target / 16.6666667) * ecommerce_wh_basic_salary_rate

bonus_orders = Total_Orders - final_target

if bonus_orders > 0:
    bonus_amount = bonus_orders * ecommerce_wh_bonus_rate
else:
    bonus_amount = bonus_orders * ecommerce_wh_penalty_rate  # negative

# Diesel/Gas deserved is based on final_target, not total_orders
diesel_deserved = min((final_target / 16.666667) * ecommerce_wh_gas_rate, ecommerce_wh_gas_cap)

gas_difference = diesel_deserved - Gas_Usage

total_salary = max(0, basic_salary + bonus_amount + gas_difference)
```

**Outputs:**

```json
{
  "Basic_Salary": round(basic_salary, 2),
  "Bonus_Amount": round(bonus_amount, 2),
  "Gas_Deserved": round(diesel_deserved, 2),
  "Gas_Difference": round(gas_difference, 2),
  "Total_Salary": round(total_salary, 2),
  "target": final_target
}
```

---

### 5.6 Ecommerce

**Inputs:**

* `Total_Orders`, `TARGET`, `Gas_Usage`, `days_since_joining`, `Total_Revenue`
* Params in 4.6

**Steps:**

```pseudo
target2 = days_since_joining * 221
final_target = min(TARGET, target2)

# Two possible basic salaries
revenue_based_salary = Total_Revenue * ecommerce_revenue_coefficient
target_based_salary  = (final_target / 221) * ecommerce_basic_salary_rate

# Basic salary is the MINIMUM of the two
basic_salary = min(revenue_based_salary, target_based_salary)

# Bonus based on revenue above final_target
bonus_revenue = max(0, Total_Revenue - final_target)

if bonus_revenue <= 4000:
    bonus_amount = bonus_revenue * 0.55
else:
    bonus_amount = (4000 * 0.55) + ((bonus_revenue - 4000) * 0.5)

# Fuel compensation: three-way minimum
diesel_deserved = min(
    0.068 * Total_Revenue,
    (final_target / 221) * 15.06,
    ecommerce_gas_cap
)

gas_difference = diesel_deserved - Gas_Usage

total_salary = max(0, basic_salary + bonus_amount + gas_difference)
```

**Outputs:**

```json
{
  "Basic_Salary": round(basic_salary, 2),
  "Bonus_Amount": round(bonus_amount, 2),
  "Gas_Deserved": round(diesel_deserved, 2),
  "Gas_Difference": round(gas_difference, 2),
  "Total_Salary": round(total_salary, 2),
  "target": final_target
}
```

---

## 6. Final Output per Courier

For each courier, the AI should return a JSON-like structure:

```json
{
  "BARQ_ID": "...",
  "iban": "...",
  "id_number": "...",
  "Name": "...",
  "Status": "...",
  "Sponsorshipstatus": "...",
  "PROJECT": "...",
  "Supervisor": "...",
  "Total_Orders": 0,
  "Total_Revenue": 0,
  "Gas_Usage": 0,
  "Basic_Salary": 0,
  "Bonus_Amount": 0,
  "Gas_Deserved": 0,
  "Gas_Difference": 0,
  "Total_Salary": 0,
  "target": 0,
  "days_since_joining": 0,
  "period": {
    "start_date": "YYYY-MM-DD",
    "end_date": "YYYY-MM-DD"
  },
  "generated_date": "YYYY-MM-DD",
  "category": "Motorcycle | Food Trial | Food In-House New | Food In-House Old | Ecommerce WH | Ecommerce"
}
```

---