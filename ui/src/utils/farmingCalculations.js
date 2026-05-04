/**
 * Centralized Farming Calculation Engine
 * Handles all agricultural financial formulas with standardized logic.
 */

export const calculateFarmFinances = (inputs, effectiveYield, targetProfit = 0) => {
  const {
    landSize,
    seedCost,
    fertilizerUrea,
    fertilizerDAP,
    fertilizerPotash,
    pesticideCost,
    laborDays,
    laborRate,
    irrigationCost,
    machineryCost,
    landPrepCost,
    transportCost,
    miscCost,
    marketPrice
  } = inputs;

  const totalLabor = laborDays * laborRate;
  const totalFertilizer = fertilizerUrea + fertilizerDAP + fertilizerPotash;
  
  const baseExpensePerAcre = (
    seedCost + 
    totalFertilizer + 
    pesticideCost + 
    totalLabor + 
    irrigationCost + 
    machineryCost + 
    landPrepCost + 
    transportCost + 
    miscCost
  );

  const totalExpense = baseExpensePerAcre * landSize;
  const totalYield = effectiveYield * landSize;
  const totalRevenue = totalYield * marketPrice;
  
  const netProfit = totalRevenue - totalExpense;
  const profitMargin = totalRevenue > 0 ? (netProfit / totalRevenue) * 100 : 0;
  const costPerAcre = totalExpense / landSize;

  // No Loss Price: total cost / total yield
  const noLossPrice = totalYield > 0 ? totalExpense / totalYield : 0;
  
  // Required Yield: total cost / market price
  const requiredYield = marketPrice > 0 ? totalExpense / marketPrice : 0;
  const requiredYieldPerAcre = requiredYield / landSize;

  // Max Budget: (Target Profit = Revenue - Budget) => Budget = Revenue - Target Profit
  const maxBudgetTotal = totalRevenue - targetProfit;
  const maxBudgetPerAcre = maxBudgetTotal / landSize;

  return {
    totalExpense,
    totalRevenue,
    netProfit,
    profitMargin,
    costPerAcre,
    noLossPrice,
    requiredYield,
    requiredYieldPerAcre,
    maxBudgetTotal,
    maxBudgetPerAcre,
    totalLabor: totalLabor * landSize,
    totalFertilizer: totalFertilizer * landSize,
    totalYield
  };
};

/**
 * Validates agricultural inputs to prevent division by zero or unrealistic results.
 */
export const validateInputs = (inputs) => {
  const errors = {};
  if (inputs.landSize <= 0) errors.landSize = "Land size must be positive";
  if (inputs.marketPrice < 0) errors.marketPrice = "Price cannot be negative";
  return {
    isValid: Object.keys(errors).length === 0,
    errors
  };
};
