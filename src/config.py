# ================================
# Experiment Configuration File
# Cashback Targeting Experiment
# ================================

# ----------------
# Reproducibility
# ----------------
RANDOM_SEED = 42

# ----------------
# Population
# ----------------
N_CUSTOMERS = 20_000

# ----------------
# Time Structure
# ----------------
WEEKS_PRE = 8
WEEKS_POST = 4


# ----------------
# Spend Distribution (Log-Normal)
# These parameters control right-skew
# Adjust carefully if distributions look unrealistic
# ----------------
LOGNORMAL_MEAN = 4.9     # controls center of distribution
LOGNORMAL_SIGMA = 0.75   # controls skew / dispersion

# ----------------
# Targeting Rule
# Monthly threshold = $500
# Convert to weekly (~125)
# ----------------
MONTHLY_THRESHOLD = 500
WEEKLY_THRESHOLD = MONTHLY_THRESHOLD / 4

# ----------------
# Behavioral Dynamics
# ----------------
WEEKLY_VOLATILITY = 0.20       # percent noise around baseline
MACRO_TREND_WEEKLY = 0.002     # 0.2% weekly upward macro trend
REGRESSION_TO_MEAN = 0.01      # small upward drift for low spenders

# ----------------
# Treatment Effect
# ----------------
TREATMENT_LIFT = 0.12          # 12% lift during promo
COMPLIANCE_RATE = 0.65         # 65% of treated respond

# Persistence
PERSISTENCE_WEEKS = 20
PERSISTENCE_DECAY = (
    [0.06]*4 +
    [0.04]*4 +
    [0.03]*4 +
    [0.02]*4 +
    [0.01]*4
)
TOTAL_WEEKS = WEEKS_PRE + WEEKS_POST + PERSISTENCE_WEEKS

# ----------------
# Financial Assumptions
# ----------------
ISSUER_REVENUE_RATE = 0.06   # blended interchange + network economics
CASHBACK_RATE = 0.03         # partially merchant-funded

