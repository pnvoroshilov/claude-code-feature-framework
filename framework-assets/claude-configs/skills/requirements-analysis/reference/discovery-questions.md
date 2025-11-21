# Requirements Discovery Questions

**Comprehensive list of questions to ask during requirements gathering to ensure completeness.**

## Users and Stakeholders

user_questions[10]{question,why_it_matters,expected_output}:
Who are the primary users of this feature?,Understand target audience and their needs,User personas and profiles
What are their current pain points?,Identify problems we're solving,Problem statements
What are their goals when using this feature?,Define success from user perspective,User objectives list
What is their technical proficiency level?,Determine appropriate complexity and UX,User skill level assessment
How many users will use this feature?,Plan for scale and performance,User volume estimates
What devices will they use?,Ensure compatibility,Device and platform requirements
What is their typical workflow?,Understand context of use,Workflow diagrams
What are their accessibility needs?,Ensure inclusive design,Accessibility requirements
Who are the secondary stakeholders?,Identify all affected parties,Stakeholder register
Who has approval authority?,Know decision makers,Approval chain

## Functionality and Features

functionality_questions[15]{question,why_it_matters,expected_output}:
What problem are we solving?,Clarify purpose and value,Problem statement
What are the core features needed?,Identify must-haves,Core feature list
What should happen in success scenarios?,Define happy path,Success flow documentation
What should happen when things go wrong?,Plan for error handling,Error scenarios list
What actions can users perform?,Document all possible operations,Action inventory
What results should users see?,Define expected outcomes,Output specifications
What happens if user doesn't complete the action?,Handle abandonment,Partial completion handling
What are the business rules?,Capture domain logic,Business rules document
What validations are required?,Ensure data quality,Validation rules list
What calculations or transformations needed?,Define data processing,Calculation specifications
What permissions or access controls needed?,Define authorization,Permission matrix
What notifications or communications needed?,Plan user communications,Notification requirements
What are the edge cases?,Cover boundary conditions,Edge case list
What existing features does this interact with?,Identify integration points,Feature dependency map
What features are explicitly out of scope?,Define boundaries,Exclusion list

## Data Requirements

data_questions[12]{question,why_it_matters,expected_output}:
What data needs to be captured?,Design data model,Data field list
What data needs to be displayed?,Plan presentation layer,Display requirements
What is the source of this data?,Identify data origins,Data source inventory
Where does this data go?,Identify data consumers,Data flow diagram
What data format is required?,Ensure compatibility,Data format specifications
What is the expected data volume?,Plan storage capacity,Volume estimates
How long should data be retained?,Define data lifecycle,Retention policy
What data needs to be validated?,Ensure data quality,Validation rules
What are the required fields vs optional?,Define data model completeness,Field requirement matrix
What are the default values?,Simplify data entry,Default values list
How should data be secured?,Protect sensitive information,Data security requirements
What reports or exports are needed?,Plan data access,Reporting requirements

## Integration and Dependencies

integration_questions[10]{question,why_it_matters,expected_output}:
What systems does this integrate with?,Identify external dependencies,Integration points list
What APIs or services are needed?,Plan technical dependencies,API requirements
What data needs to be synchronized?,Ensure data consistency,Sync requirements
What happens if external system is unavailable?,Plan for resilience,Failure handling strategy
What authentication is required for integrations?,Secure integrations,Auth requirements
What is the expected response time from external systems?,Set performance expectations,SLA requirements
How often does data need to be synchronized?,Define sync frequency,Sync schedule
What data transformations are needed?,Map between systems,Transformation specifications
What error handling is needed for integrations?,Handle integration failures,Error handling requirements
What monitoring is needed for integrations?,Ensure reliability,Monitoring requirements

## Constraints and Limitations

constraint_questions[12]{question,why_it_matters,expected_output}:
What are the technical limitations?,Understand boundaries,Technical constraints list
What are the budget constraints?,Manage scope expectations,Budget limits
What are the time constraints?,Plan realistic schedule,Timeline constraints
What regulatory requirements must be met?,Ensure compliance,Compliance requirements
What are the performance requirements?,Set performance targets,Performance criteria
What are the security requirements?,Ensure data protection,Security constraints
What browsers or platforms must be supported?,Define compatibility,Compatibility matrix
What are the scalability requirements?,Plan for growth,Scalability targets
What existing systems must we integrate with?,Identify mandatory integrations,Integration constraints
What technologies are mandated or prohibited?,Follow organizational standards,Technology constraints
What are the resource limitations?,Plan within capacity,Resource constraints
What are the organizational or political constraints?,Navigate organizational context,Organizational constraints

## Performance and Quality

performance_questions[10]{question,why_it_matters,expected_output}:
How fast should the system respond?,Set performance expectations,Response time targets
How many concurrent users should be supported?,Plan for load,Concurrency requirements
What is the acceptable downtime?,Define availability requirements,Uptime SLA
What is the expected data throughput?,Plan for data volume,Throughput requirements
What are the peak usage times?,Plan capacity for peaks,Usage patterns
What is the expected growth rate?,Plan for scalability,Growth projections
What is the acceptable error rate?,Define reliability targets,Error rate thresholds
What performance degradation is acceptable?,Define graceful degradation,Degradation thresholds
How quickly should the system recover from failures?,Define resilience,Recovery time objectives
What monitoring and alerting is needed?,Ensure observability,Monitoring requirements

## Security and Privacy

security_questions[12]{question,why_it_matters,expected_output}:
What data needs to be protected?,Identify sensitive data,Data classification
Who should have access to what?,Define authorization,Access control matrix
How should users be authenticated?,Plan authentication approach,Authentication requirements
What data needs to be encrypted?,Protect data in transit and at rest,Encryption requirements
What audit logging is required?,Ensure accountability,Audit requirements
What are the password/credential requirements?,Enforce security standards,Credential policy
What are the session management requirements?,Manage user sessions securely,Session requirements
What privacy regulations apply?,Ensure compliance,Privacy requirements (GDPR HIPAA etc)
How should data breaches be handled?,Plan incident response,Breach response plan
What security testing is required?,Validate security,Security testing requirements
How should API endpoints be secured?,Protect APIs,API security requirements
What are the data retention and deletion requirements?,Manage data lifecycle,Data retention policy

## Success Metrics

success_questions[10]{question,why_it_matters,expected_output}:
How will we measure success?,Define success criteria,Success metrics list
What KPIs should we track?,Monitor business value,KPI definitions
What is the target adoption rate?,Measure user acceptance,Adoption targets
What is the expected ROI?,Justify investment,ROI calculations
What user satisfaction targets exist?,Measure user experience,Satisfaction metrics
What efficiency gains are expected?,Measure productivity,Efficiency targets
What error reduction is expected?,Measure quality,Error reduction targets
What cost savings are expected?,Measure financial benefit,Cost savings estimates
How will we track usage patterns?,Understand user behavior,Analytics requirements
What A/B testing or experimentation is planned?,Optimize features,Experimentation plan

## Definition of Done

done_questions[8]{question,why_it_matters,expected_output}:
What does done look like?,Define completion criteria,DoD checklist
What testing is required before release?,Ensure quality,Testing requirements
What documentation needs to be updated?,Maintain documentation,Documentation requirements
What training or communication is needed?,Prepare users,Training plan
What approvals are needed before release?,Ensure sign-off,Approval requirements
What deployment steps are required?,Plan release,Deployment checklist
What rollback plan is needed?,Manage risk,Rollback procedures
What post-launch monitoring is required?,Ensure success,Monitoring plan

## Business Context

business_questions[10]{question,why_it_matters,expected_output}:
What business problem are we solving?,Ensure alignment,Business problem statement
What is the expected business value?,Justify investment,Value proposition
What is the priority of this requirement?,Manage scope,Priority (Critical/High/Medium/Low)
What happens if we don't build this?,Understand urgency,Risk of not doing
Who requested this requirement?,Trace to source,Requirement source
What is the deadline or timeline?,Plan schedule,Timeline constraints
What dependencies exist with other projects?,Coordinate work,Project dependencies
What is the competitive landscape?,Understand market context,Competitive analysis
What are the alternatives considered?,Validate approach,Alternatives list
What assumptions are we making?,Document assumptions,Assumptions register

---

**File Size**: 120/500 lines max ✅
**Usage**: Reference this document during requirements discovery phase to ensure comprehensive coverage
