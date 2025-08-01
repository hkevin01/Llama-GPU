
function ProjectPlans() {
  return (
    <div className="project-plans animate-fadeIn">
      <div className="page-header">
        <h1>Project Plans</h1>
        <p>Overview of all project planning documents and milestones</p>
      </div>

      <div className="plans-grid">
        <div className="plan-card">
          <h3>Core Development Plan</h3>
          <p>Main development roadmap and technical implementation</p>
          <div className="plan-meta">
            <span>📄 plan.md</span>
            <span>✅ Active</span>
          </div>
        </div>

        <div className="plan-card">
          <h3>GUI Implementation</h3>
          <p>User interface and dashboard development plan</p>
          <div className="plan-meta">
            <span>📄 plan_part1.md</span>
            <span>✅ Complete</span>
          </div>
        </div>

        <div className="plan-card">
          <h3>Security & Deployment</h3>
          <p>Security implementation and production deployment</p>
          <div className="plan-meta">
            <span>📄 plan_part2.md</span>
            <span>🟡 In Progress</span>
          </div>
        </div>
      </div>
    </div>
  );
}

export default ProjectPlans;
