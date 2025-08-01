
function PlanComparison() {
  return (
    <div className="plan-comparison animate-fadeIn">
      <div className="page-header">
        <h1>Plan Comparison</h1>
        <p>Compare planned vs actual progress across all project phases</p>
      </div>

      <div className="comparison-table">
        <table className="table">
          <thead>
            <tr>
              <th>Task</th>
              <th>Planned Date</th>
              <th>Actual Date</th>
              <th>Variance</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>Core Inference Engine</td>
              <td>2025-07-15</td>
              <td>2025-07-14</td>
              <td className="variance positive">-1 day</td>
              <td><span className="status-badge status-complete">Complete</span></td>
            </tr>
            <tr>
              <td>Web Dashboard</td>
              <td>2025-08-05</td>
              <td>2025-08-01</td>
              <td className="variance positive">-4 days</td>
              <td><span className="status-badge status-complete">Complete</span></td>
            </tr>
            <tr>
              <td>API Development</td>
              <td>2025-08-12</td>
              <td>In Progress</td>
              <td className="variance neutral">On track</td>
              <td><span className="status-badge status-progress">85% Complete</span></td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default PlanComparison;
