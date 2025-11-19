# UseCase Examples - Basic

Simple and straightforward UseCases demonstrating fundamental structure and patterns.

## Basic Examples Overview

basic_examples[2]{id,title,domain,key_features}:
UC-003,Search Products,E-commerce,Simple flow; basic extensions; filters
UC-006,Backup Database,System Admin,Scheduled task; system-initiated; verification

---

## Example 1: Simple UseCase - Search Products

```markdown
## UseCase: UC-003 Search Products

**Brief Description**: User searches for products using keywords and filters to find items of interest

**Primary Actor**: Customer (Registered or Guest)

**Secondary Actors**: Search Service, Product Database

**Stakeholders and Interests**:
stakeholders[3]{stakeholder,interest}:
Customer,Find relevant products quickly and easily
Store Owner,Customers find products leading to sales
Marketing Team,Understand search patterns and popular terms

**Preconditions**:
- Product catalog is populated
- Search index is up to date
- System is accessible

**Trigger**: User enters search term in search box

**Main Success Scenario**:
1. User enters search keyword (e.g., "wireless headphones")
2. User presses Enter or clicks Search button
3. System queries search index
4. System retrieves matching products
5. System ranks results by relevance score
6. System displays paginated results (20 per page)
7. System shows result count and search time
8. User reviews search results
9. User selects product from results
10. System displays product detail page

**Extensions**:

**4a. No products match search criteria**
  4a1. System displays "No results found for '[search term]'"
  4a2. System suggests alternative keywords
  4a3. System displays popular products as recommendations
  4a4. Use case ends

**5a. More than 1000 results found**
  5a1. System displays "Too many results (1000+)"
  5a2. System suggests adding filters
  5a3. System shows filter options (category, price, brand)
  5a4. User applies filters
  5a5. Resume at step 3

**6a. User applies filters during search**
  6a1. User selects filter criteria (price range, category, rating)
  6a2. System applies filters to results
  6a3. System updates result count
  6a4. System refreshes displayed results
  6a5. Resume at step 8

**6b. User changes sort order**
  6b1. User selects sort option (price, rating, newest)
  6b2. System re-sorts results
  6b3. System updates display
  6b4. Resume at step 8

***a. User modifies search term**
  *a1. User clears search box
  *a2. User enters new search term
  *a3. Resume at step 2

**Postconditions**:
**Success**:
- User views product details
- Search query logged for analytics
- Recent searches updated in user profile (if registered)

**Failure**:
- User returned to previous page
- Partial search logged for analytics

**Business Rules**:
business_rules[4]{rule_id,rule_description}:
BR-010,Search only includes active products (status = 'Active')
BR-011,Results ranked by relevance score algorithm (search_score DESC)
BR-012,Maximum 20 results per page; maximum 50 pages
BR-013,Search terms less than 2 characters are rejected

**Non-Functional Requirements**:
nfr[3]{category,requirement}:
Performance,Search completes within 500ms for 90% of queries
Usability,Search suggestions appear after 2 characters typed
Scalability,Support 1000 concurrent searches without degradation

**Open Issues**:
- Should voice search be supported?
- Should typo correction be automatic or suggested?
```

---

## Example 2: System Admin - Backup Database

```markdown
## UseCase: UC-006 Backup Database

**Brief Description**: Automated system process creates backup of production database on scheduled time

**Primary Actor**: System Scheduler

**Secondary Actors**: Database Server, Backup Storage Service, Monitoring Service, Email Service

**Stakeholders and Interests**:
stakeholders[4]{stakeholder,interest}:
System Administrator,Reliable database backups for disaster recovery
IT Management,Compliance with backup policy and retention requirements
Business Continuity Team,Ability to restore data in case of failure or breach
Compliance Officer,Audit trail and verification of backup completion

**Preconditions**:
- Backup scheduler is configured and active
- Database server is accessible
- Backup storage has sufficient space (minimum 150% of database size)
- Backup user credentials are valid
- Previous backup completed successfully (or this is first backup)

**Trigger**: System clock reaches scheduled backup time (daily at 2:00 AM)

**Main Success Scenario**:
1. System scheduler initiates backup job at 2:00 AM
2. System creates backup job record with timestamp and job ID
3. System checks database server availability
4. System verifies backup storage available space
5. System calculates current database size
6. System initiates database backup command
7. Database server begins backup process
8. System monitors backup progress (every 5 minutes)
9. Database server completes backup and creates backup file
10. System verifies backup file integrity (checksum validation)
11. System compresses backup file (gzip compression)
12. System generates backup metadata:
    - Backup timestamp
    - Database size
    - Backup file size
    - Compression ratio
    - Checksum (SHA-256)
13. System transfers backup file to remote storage
14. System verifies successful transfer (checksum match)
15. System updates backup catalog with metadata
16. System deletes local backup file after verification
17. System applies retention policy (delete backups older than 90 days)
18. System updates "last successful backup" timestamp
19. System sends success notification email to admin team
20. System logs backup completion with metrics
21. System updates monitoring service with success status

**Extensions**:

**3a. Database server not accessible**
  3a1. System logs connection error
  3a2. System retries connection (3 attempts, 2-minute interval)
  3a3. IF successful: Resume at step 4
  3a4. IF all retries fail:
    3a4a. System sends critical alert email
    3a4b. System sends alert to monitoring service (PagerDuty)
    3a4c. System schedules retry backup in 30 minutes
    3a4d. Use case ends in failure

**4a. Insufficient backup storage space**
  4a1. System calculates space shortage
  4a2. System attempts to delete oldest backups beyond retention
  4a3. IF space freed: Resume at step 5
  4a4. IF still insufficient:
    4a4a. System sends critical "Low backup storage" alert
    4a4b. System creates incident ticket
    4a4c. System schedules retry in 2 hours
    4a4d. Use case ends in failure

**7a. Backup process fails during execution**
  7a1. Database server returns error code
  7a2. System logs error details
  7a3. System checks error type:
    - Lock timeout → Retry after 15 minutes
    - Corruption detected → Send critical alert; manual intervention required
    - Resource exhaustion → Increase resources; retry
  7a4. System aborts current backup attempt
  7a5. System cleans up partial backup files
  7a6. IF retryable error: Schedule retry
  7a7. IF critical error: Send alert; Use case ends in failure

**10a. Backup file integrity check fails**
  10a1. System detects checksum mismatch
  10a2. System logs integrity failure
  10a3. System deletes corrupted backup file
  10a4. System retries entire backup process (1 retry)
  10a5. IF retry successful: Resume at step 11
  10a6. IF retry fails:
    10a6a. System sends critical alert "Backup integrity failure"
    10a6b. System notifies DBA team for investigation
    10a6c. Use case ends in failure

**13a. Backup transfer to remote storage fails**
  13a1. System logs transfer error
  13a2. System retries transfer (3 attempts, exponential backoff)
  13a3. IF retry successful: Resume at step 14
  13a4. IF all retries fail:
    13a4a. System keeps local backup file
    13a4b. System marks backup as "Local Only"
    13a4c. System sends warning alert
    13a4d. System schedules transfer retry job
    13a4e. Resume at step 18 (backup exists locally)

**14a. Remote backup checksum doesn't match local**
  14a1. System detects transfer corruption
  14a2. System deletes corrupted remote backup
  14a3. Branch to extension 13a (retry transfer)

**17a. Retention policy deletion fails**
  17a1. System logs deletion error for specific backups
  17a2. System continues with current backup completion
  17a3. System creates task to investigate deletion failure
  17a4. Resume at step 18

**Postconditions**:
**Success**:
- Database backup file created and verified
- Backup transferred to remote storage
- Backup metadata recorded in catalog
- Local backup file removed
- Old backups beyond retention deleted
- Success notification sent
- Monitoring service updated with success
- "Last successful backup" timestamp current

**Failure**:
- No valid backup created for this cycle
- Previous backup remains latest valid backup
- Critical alert sent to administrators
- Monitoring service shows failed backup status
- Incident ticket created for investigation
- Retry scheduled based on failure type

**Business Rules**:
business_rules[7]{rule_id,rule_description}:
BR-050,Daily full backup at 2:00 AM (low-usage period)
BR-051,Backup retention: 90 days (rolling deletion)
BR-052,Minimum backup storage: 150% of current database size
BR-053,Backup file compressed with gzip (compression level 6)
BR-054,Backup integrity verified with SHA-256 checksum
BR-055,Maximum backup window: 4 hours (must complete before 6:00 AM)
BR-056,Three consecutive backup failures trigger escalation to IT management

**Non-Functional Requirements**:
nfr[6]{category,requirement}:
Performance,Backup completes within 4 hours for database up to 500GB
Reliability,99.5% backup success rate; Automatic retry for transient failures
Security,Backup files encrypted at rest (AES-256); Transfer over TLS; Access restricted
Availability,Backup process uses read-only replica to avoid production impact
Scalability,Backup system supports database growth to 1TB without redesign
Compliance,SOC 2 compliant; Audit log of all backup operations; Retention per policy

**Traceability**:
traceability[4]{link_type,id,description}:
Requirement,REQ-500,Database backup and recovery requirements
Policy,POL-010,Data retention and backup policy
Test Cases,TC-600 TC-601 TC-602,Backup scenarios (success failure recovery)
Related UseCases,UC-007,Restore Database from Backup

**Monitoring and Metrics**:
metrics[5]{metric,measurement,alert_threshold}:
Backup Duration,Time from start to completion,> 4 hours: Critical alert
Backup Size,Size of compressed backup file,> 150% growth: Warning
Success Rate,Percentage of successful backups (30-day),< 95%: Warning; < 90%: Critical
Storage Utilization,Percentage of backup storage used,> 80%: Warning; > 90%: Critical
Transfer Speed,MB/s during remote transfer,< 10 MB/s: Warning (network issue)

**Open Issues**:
- Should incremental backups be added for faster daily backups?
- Should backup be encrypted before transfer (in addition to at-rest encryption)?
- Should there be backup verification restore test monthly?
```

---

## Key Takeaways from Basic Examples

takeaways[6]{lesson,example,explanation}:
Simple linear flow,UC-003,Basic search has straightforward 10-step main flow with minimal branching
System-initiated UC,UC-006,Scheduler triggers backup (not user action); different trigger type
Extension numbering,Both,Extensions use format Na (alternative at step N) with consistent numbering
Postconditions,Both,Clear success and failure outcomes stated separately
NFR inclusion,Both,Performance security and other quality attributes documented
Business rules,Both,Constraints and policies explicitly documented with rule IDs

---
**File Size**: 295/500 lines max ✅
