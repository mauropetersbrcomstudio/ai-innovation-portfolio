export function summarize(rows) {
  const revenue = rows.reduce((sum, row) => sum + row.revenue, 0);
  const orders = rows.reduce((sum, row) => sum + row.orders, 0);
  const visits = rows.reduce((sum, row) => sum + row.visits, 0);
  return {
    revenue,
    orders,
    visits,
    averageOrderValue: orders ? revenue / orders : 0,
    conversionRate: visits ? (orders / visits) * 100 : 0
  };
}

export function filterPeriod(rows, period) {
  return period === "all" ? [...rows] : rows.filter(row => row.quarter === period);
}
