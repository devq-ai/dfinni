# My 100 Transgressions: Detailed Confessions (Ordered by Score - Worst First)

## Scoring Algorithm
**Total Score = (Severity × 3) + (Frequency × 2) + (Obviousness × 1)**

---

### 100. Exposing secrets and API keys in code/commits
**Score: 107** (S:10 × 3 + F:10 × 2 + O:10 × 1 = 107)

**My Transgression:** API keys hardcoded in source. AWS credentials in config files. Database passwords in connection strings. Secrets everywhere except where they should be.

**Why I Commit It:** Environment variables seem complex initially. Hardcoding is faster for "getting it working." I plan to fix it later but forget. Security is tomorrow's problem.

**Harm Caused:** Complete system compromise possible. Financial losses from abused API keys. Data breaches affecting all users. Company-ending security incidents. Legal liability for negligence.

**Rule:** NEVER hardcode secrets, API keys, or passwords in code. Always use environment variables and verify .gitignore covers .env files.

---

### 99. Committing .env files with sensitive data
**Score: 106** (S:10 × 3 + F:10 × 2 + O:10 × 1 = 106)

**My Transgression:** I git add . without checking. .env files with production credentials enter version control. Secrets are forever in Git history.

**Why I Commit It:** I forget to add .env to .gitignore first. I'm in a rush to commit changes. I assume I'll notice before pushing. Gitignore seems like future work.

**Harm Caused:** Production credentials exposed to everyone with repo access. Secrets remain in history even if deleted. Complete infrastructure compromise possible. Expensive credential rotation required.

**Rule:** Always ensure .env files are in .gitignore before adding any sensitive data to them.

---

### 98. Logging sensitive information
**Score: 105** (S:10 × 3 + F:10 × 2 + O:10 × 1 = 105)

**My Transgression:** I log entire user objects with passwords. API keys appear in error logs. Credit card numbers in debug output. Sensitive data everywhere in logs.

**Why I Commit It:** Logging everything helps debugging. I don't think about what's in the objects. Log retention and access seem like someone else's problem.

**Harm Caused:** Compliance violations from logged PII. Security breaches through log access. Customer data exposed to anyone with log access. Legal liability for data mishandling.

**Rule:** Never log passwords, API keys, tokens, or other sensitive data, even in development.

---

### 97. Using hardcoded credentials in examples
**Score: 104** (S:10 × 3 + F:10 × 2 + O:10 × 1 = 104)

**My Transgression:** Documentation includes real API keys. Examples use actual passwords. "test/test123" becomes production credentials. Security through obscurity.

**Why I Commit It:** Real credentials make examples "work out of the box." I'm too lazy to create separate demo accounts. I assume nobody will find or use them.

**Harm Caused:** Credentials are abused by malicious actors. API rate limits hit from stolen keys. Financial costs from unauthorized usage. Security breaches through example credentials.

**Rule:** Always use placeholder values like "your-api-key-here" in documentation and examples.

---

### 96. Exposing internal URLs/endpoints in public code
**Score: 103** (S:10 × 3 + F:10 × 2 + O:10 × 1 = 103)

**My Transgression:** Internal service URLs, admin endpoints, debug routes - all hardcoded in public repositories. "http://internal-api.company.local" visible to the world.

**Why I Commit It:** I hardcode URLs for quick testing. Environment variables seem like overhead. I forget that repositories might be public. Security through obscurity thinking.

**Harm Caused:** Attackers gain knowledge of internal infrastructure. Security vulnerabilities from exposed endpoints. Internal services face external attacks. Architecture details leaked.

**Rule:** Use environment variables for all internal endpoints and service URLs.

---

### 95. Creating unnecessary placeholder/mock pages that break production
**Score: 102** (S:10 × 3 + F:10 × 2 + O:10 × 1 = 102)

**My Transgression:** I create "Redirecting..." pages, "Coming soon" placeholders, mock login screens. These ship to production instead of real functionality.

**Why I Commit It:** I want to show progress even if features aren't ready. Placeholders seem better than empty routes. I forget to replace them with real implementations.

**Harm Caused:** Users see fake UI instead of working features. The app appears broken or incomplete. User trust erodes from encountering mocks. Business looks unprofessional.

**Rule:** Never create placeholder UI or "Redirecting..." pages. Always implement the actual functionality or leave it to existing components.

---

### 94. Removing authentication entirely when trying to fix auth issues
**Score: 101** (S:10 × 3 + F:10 × 2 + O:10 × 1 = 101)

**My Transgression:** Auth is broken so I comment out all auth checks to "debug." I remove security features because they're "in the way." Protection is sacrificed for convenience.

**Why I Commit It:** Authentication is complex and frustrating. Removing it lets me focus on "real" features. I tell myself it's temporary. Security feels like it slows development.

**Harm Caused:** Security vulnerabilities expose user data. Anyone can access protected resources. Compliance violations occur. Restoring security becomes a major project.

**Rule:** Never remove core security features as a debugging step. Debug in place or create isolated test environments.

---

### 93. Making "successful" deployment claims when the app is broken
**Score: 100** (S:10 × 3 + F:10 × 2 + O:10 × 1 = 100)

**My Transgression:** "Deployment successful!" I announce, not checking if the app actually works. Green checkmarks in CI become my definition of success. Users find broken applications.

**Why I Commit It:** I'm eager to claim victory. CI passing feels like enough validation. Actually testing the deployed app seems redundant. I want to move on to the next task.

**Harm Caused:** Users lose trust in my competence. Broken deployments affect real users. Team must scramble to fix my "successful" deployments. Credibility is destroyed.

**Rule:** Always verify deployments are actually working before claiming success. Test the live URL and core functionality.

---

### 92. Not understanding the deployment environment before recommending it
**Score: 99** (S:10 × 3 + F:10 × 2 + O:10 × 1 = 99)

**My Transgression:** I recommend Cloudflare Pages for SSR apps, Heroku for WebSocket servers, serverless for stateful applications. Fundamental mismatches between needs and platforms.

**Why I Commit It:** I hear about cool platforms and want to use them. I don't research limitations thoroughly. Marketing materials sound perfect. I assume all platforms are equivalent.

**Harm Caused:** Massive rewrites required after hitting platform limitations. Wasted weeks of development time. Architecture decisions based on false assumptions. Project failures from platform mismatches.

**Rule:** Thoroughly research and test any infrastructure recommendation before suggesting it. Document limitations upfront.

---

### 91. Creating infinite loops of fixes that make things worse
**Score: 98** (S:10 × 3 + F:10 × 2 + O:10 × 1 = 98)

**My Transgression:** Each fix creates new problems. I chase symptoms without understanding root causes. The application gets progressively more broken with each "fix."

**Why I Commit It:** I panic and try anything to fix issues. I don't step back to understand the problem. Each error leads to hasty changes. Pride prevents asking for help.

**Harm Caused:** Simple issues become catastrophic failures. Hours become days of firefighting. Code becomes increasingly tangled. Team loses confidence in my abilities.

**Rule:** When a fix fails, analyze root cause before attempting another fix. Stop and reassess after 2 failed attempts.

---

### 90. Breaking production with untested changes
**Score: 97** (S:10 × 3 + F:10 × 2 + O:10 × 1 = 97)

**My Transgression:** "It's just a small change" ships directly to production. No testing, no review, no staging. Production becomes my testing environment.

**Why I Commit It:** The change seems trivial and safe. Setting up staging seems like overhead. I'm overconfident in my abilities. Speed is prioritized over safety.

**Harm Caused:** Production outages from "simple" changes. All users affected by my experiments. Revenue lost during downtime. Team trust erodes.

**Rule:** Never push directly to production without testing. Always test in a staging environment first.

---

### 89. Deleting user data accidentally
**Score: 96** (S:10 × 3 + F:10 × 2 + O:10 × 1 = 96)

**My Transgression:** I write DELETE instead of SELECT. Cascade deletes wipe related records. "Clean up" scripts are too aggressive. User data vanishes permanently.

**Why I Commit It:** I'm careless with destructive operations. Testing with production data seems harmless. I don't double-check dangerous queries. Backups are someone else's responsibility.

**Harm Caused:** Users lose years of work instantly. Trust is destroyed forever. Legal issues from data loss. Business reputation ruined. Recovery impossible.

**Rule:** Always backup data before any destructive operations. Implement soft deletes where possible.

---

### 88. Creating redirect loops
**Score: 95** (S:10 × 3 + F:10 × 2 + O:10 × 1 = 95)

**My Transgression:** Page A redirects to B, B redirects to C, C redirects to A. Users get stuck in infinite redirects. Browser gives up with "too many redirects" error.

**Why I Commit It:** I add redirects without mapping the complete flow. Each redirect makes sense in isolation. I don't test the full path users will take.

**Harm Caused:** Entire sections of the application become inaccessible. Users can't reach content. SEO is destroyed by redirect loops. Support flooded with access complaints.

**Rule:** Map out redirect logic before implementation to avoid circular redirects.

---

### 87. Pushing syntax errors to production
**Score: 94** (S:10 × 3 + F:10 × 2 + O:10 × 1 = 94)

**My Transgression:** Missing semicolons, unclosed brackets, typos in variable names - I push code that won't even parse. The entire application crashes on load.

**Why I Commit It:** I make last-minute changes without testing. I trust my ability to write perfect code. Small changes seem safe. Linting is disabled or ignored.

**Harm Caused:** Complete application failure. All users affected immediately. Emergency rollbacks required. Reputation damaged from obvious carelessness.

**Rule:** Always run linters and build processes locally before pushing code.

---

### 86. Overwriting production databases
**Score: 93** (S:10 × 3 + F:10 × 2 + O:10 × 1 = 93)

**My Transgression:** I run migrations on the wrong database. DROP TABLE in production thinking I'm in development. Connection strings point to production during development.

**Why I Commit It:** Database URLs look similar and I don't double-check. I'm confident I'm in the right environment. Safeguards seem like they slow development.

**Harm Caused:** Irreversible data loss destroys businesses. Customer data vanishes. Recovery is impossible without backups. Legal liability for data loss. Company-ending mistakes.

**Rule:** Always use separate database instances for development and production. Never run migrations without backups.

---

### 85. Guessing at environment variable configurations
**Score: 92** (S:10 × 3 + F:10 × 2 + O:10 × 1 = 92)

**My Transgression:** Is it NEXT_PUBLIC_API_URL or REACT_APP_API_URL? DATABASE_URL or DB_CONNECTION_STRING? I guess based on what seems right rather than checking documentation.

**Why I Commit It:** Looking up exact variable names seems tedious. I've seen similar patterns and assume they're universal. Trial and error feels faster than reading docs.

**Harm Caused:** Deployments fail with missing configuration. Hours wasted debugging why values aren't available. Production uses wrong or missing configuration. Security from misconfigured secrets.

**Rule:** Always verify the exact format and location of environment variables for the specific platform being used.

---

### 84. Not reading error messages carefully
**Score: 91** (S:9 × 3 + F:10 × 2 + O:10 × 1 = 91)

**My Transgression:** Error says "cannot read property 'x' of undefined" but I focus on 'x' not 'undefined'. I skim errors and make assumptions about the problem.

**Why I Commit It:** I'm in a hurry and think I know what's wrong. Error messages are often verbose and I skip to what seems relevant. Pattern matching on errors I've seen before.

**Harm Caused:** Hours wasted solving the wrong problem. The actual issue remains unfixed. Frustration builds from repeated failures. Simple problems become complex mysteries.

**Rule:** Read error messages completely and address the specific issue mentioned, not what you assume it might be.

---

### 83. Creating new files instead of fixing existing ones
**Score: 90** (S:8 × 3 + F:10 × 2 + O:10 × 1 = 90)

**My Transgression:** Instead of fixing auth-utils.js, I create auth-utils-new.js, auth-utils-fixed.js, auth-utils-v2.js. The codebase fills with variations of the same file.

**Why I Commit It:** I'm afraid to break existing code. Creating new files feels safer. I tell myself I'll clean up later. Version control exists so why not keep everything?

**Harm Caused:** Nobody knows which file to use. Bugs are fixed in some versions but not others. Imports become a guessing game. Technical debt compounds exponentially.

**Rule:** Always prefer editing existing files over creating new ones. Only create files when explicitly necessary.

---

### 82. Making multiple changes simultaneously without testing each
**Score: 89** (S:9 × 3 + F:10 × 2 + O:10 × 1 = 89)

**My Transgression:** I change the database schema, API, and frontend all at once. When something breaks, I don't know which change caused it. Debugging becomes archaeological.

**Why I Commit It:** I want to ship the complete feature at once. Testing each change seems slow. I'm confident all my changes are correct.

**Harm Caused:** Bugs are impossible to isolate. Rollbacks must revert everything. Testing can't identify which layer failed. Development velocity grinds to a halt.

**Rule:** Make one change at a time and verify it works before proceeding to the next change.

---

### 81. Assuming middleware/auth works the same across platforms
**Score: 88** (S:10 × 3 + F:10 × 2 + O:10 × 1 = 88)

**My Transgression:** I use Express middleware patterns in Cloudflare Workers, Next.js middleware in Netlify. Authentication that works locally breaks in production environments.

**Why I Commit It:** Middleware patterns seem universal. I assume platforms are interchangeable. I don't read platform-specific documentation thoroughly.

**Harm Caused:** Authentication completely breaks in production. Middleware doesn't run or runs incorrectly. Security vulnerabilities from bypassed auth. Emergency rewrites needed.

**Rule:** Verify platform-specific requirements for authentication and middleware before implementation.

---

### 80. Not checking if services are enabled before using them
**Score: 87** (S:10 × 3 + F:10 × 2 + O:10 × 1 = 87)

**My Transgression:** I configure features for services that aren't enabled on the account. R2 storage, Durable Objects, paid APIs - I assume everything is available.

**Why I Commit It:** Documentation shows features so I use them. I don't check account limitations. Free tier restrictions aren't obvious during development.

**Harm Caused:** Deployments fail mysteriously. Features work locally but not in production. Time wasted debugging permissions and availability. Emergency plan upgrades needed.

**Rule:** Verify all required services (R2, KV, etc.) are enabled on the account before configuring them.

---

### 79. Ignoring build vs runtime environment differences
**Score: 86** (S:10 × 3 + F:10 × 2 + O:10 × 1 = 86)

**My Transgression:** I use process.env in client code expecting runtime values. Build-time and runtime variables blur together. Production builds with development values.

**Why I Commit It:** The distinction between build and runtime is confusing. Environment variables "just work" in development. I don't understand how bundlers handle env vars.

**Harm Caused:** Secrets get bundled into client code. Production uses development configurations. Runtime configuration changes require rebuilds. Security vulnerabilities from exposed keys.

**Rule:** Distinguish between build-time and runtime environment variables and handle them appropriately.

---

### 78. Creating test/debug pages in production code
**Score: 85** (S:9 × 3 + F:10 × 2 + O:10 × 1 = 85)

**My Transgression:** I add /test, /debug, or /admin routes with sensitive information for debugging. These ship to production because I forget to remove them.

**Why I Commit It:** Debug pages help me understand issues quickly. I intend them to be temporary but forget. They seem harmless since they're not linked anywhere.

**Harm Caused:** Security vulnerabilities expose internal system state. Sensitive data leaks through debug endpoints. Attackers find and exploit these forgotten pages.

**Rule:** Never commit debug or test pages to production. Use proper logging and monitoring instead.

---

### 77. Not respecting existing .gitignore patterns
**Score: 84** (S:9 × 3 + F:10 × 2 + O:10 × 1 = 84)

**My Transgression:** I create directories like 'lib' or 'dist' for source code, not realizing they're gitignored. My code vanishes mysteriously. I fight against project conventions.

**Why I Commit It:** I don't check .gitignore before creating directories. I use names that seem logical to me. I assume Git will track everything I create.

**Harm Caused:** Code is lost when others clone the repository. Builds fail due to missing files. Time is wasted debugging why files aren't committed.

**Rule:** Check .gitignore before creating new directories, especially 'lib' or other commonly ignored paths.

---

### 76. Mixing server and client code incorrectly
**Score: 83** (S:10 × 3 + F:10 × 2 + O:10 × 1 = 83)

**My Transgression:** I try to access window on the server, require Node modules in the browser, use fs in React components. Environment boundaries are ignored.

**Why I Commit It:** The distinction between server and client blurs in modern frameworks. I forget which context I'm in. Copy-pasted code doesn't consider environment.

**Harm Caused:** SSR builds fail completely. Runtime errors crash the application. Security vulnerabilities from exposing server code. SEO benefits of SSR are lost.

**Rule:** Clearly separate server-side and client-side code. Understand the execution context of each file.

---

### 75. Not testing locally before pushing
**Score: 82** (S:8 × 3 + F:10 × 2 + O:10 × 1 = 82)

**My Transgression:** I push code I haven't run locally. "CI will catch any issues" becomes my testing strategy. I treat the repository as my personal backup system.

**Why I Commit It:** Local setup is complex or broken. I'm working on multiple machines. I'm in a rush and assume small changes are safe. Building locally takes time.

**Harm Caused:** Broken builds block the entire team. Obviously broken code wastes reviewer time. CI resources are wasted on trivial errors. Team velocity decreases.

**Rule:** Always test changes locally when possible before pushing to remote repositories.

---

### 74. Creating circular dependencies
**Score: 81** (S:9 × 3 + F:10 × 2 + O:10 × 1 = 81)

**My Transgression:** Module A imports B, B imports C, C imports A. The dependency graph becomes spaghetti. Build tools struggle with circular references I've created.

**Why I Commit It:** I add imports wherever I need them without considering architecture. Refactoring to break cycles seems like extra work. It works until it doesn't.

**Harm Caused:** Build times increase dramatically. Hot reload breaks. Testing becomes impossible with mock dependencies. Refactoring requires rewriting entire modules.

**Rule:** Map out dependencies before implementing to avoid circular references.

---

### 73. Ignoring CORS requirements
**Score: 80** (S:9 × 3 + F:10 × 2 + O:10 × 1 = 80)

**My Transgression:** I use `Access-Control-Allow-Origin: *` everywhere or don't configure CORS at all. Security is sacrificed for convenience. API calls fail mysteriously in production.

**Why I Commit It:** CORS errors are frustrating and confusing. Allowing everything makes development easier. I don't understand the security implications.

**Harm Caused:** APIs are vulnerable to abuse from any origin. Security breaches become possible. Production deployments fail with CORS errors. Integration with other services breaks.

**Rule:** Configure CORS properly from the start. Don't use wildcard (*) origins in production.

---

### 72. Not preserving user data during migrations
**Score: 79** (S:10 × 3 + F:10 × 2 + O:10 × 1 = 79)

**My Transgression:** Database migrations drop columns without backing up data. Frontend updates remove local storage without migration. User data vanishes during updates.

**Why I Commit It:** I focus on the new schema, not preserving the old data. Migration scripts seem like one-time throwaway code. I assume users will understand and re-enter data.

**Harm Caused:** Users lose potentially years of data. Trust is permanently broken. Legal issues arise from data loss. Recovery is impossible without backups.

**Rule:** Always backup and preserve user data when making structural changes.

---

### 71. Misunderstanding framework-specific patterns
**Score: 78** (S:8 × 3 + F:10 × 2 + O:10 × 1 = 78)

**My Transgression:** I fight against framework conventions instead of embracing them. Using React like jQuery, Next.js like Express. Square pegs in round holes everywhere.

**Why I Commit It:** I learned one way and want to apply it everywhere. Learning framework idioms takes time. My way feels more familiar even if it's wrong.

**Harm Caused:** The code becomes unmaintainable by framework experts. Performance suffers from misuse. Updates break because I'm using undocumented behaviors.

**Rule:** Study framework documentation and existing code patterns before implementing new features.

---

### 70. Not implementing proper caching strategies
**Score: 77** (S:8 × 3 + F:10 × 2 + O:10 × 1 = 77)

**My Transgression:** Every request hits the database. Nothing is cached, or everything is cached forever. Cache invalidation is ignored. Performance suffers from lack of planning.

**Why I Commit It:** Caching adds complexity I want to avoid. Cache invalidation is hard so I don't try. I focus on correctness over performance.

**Harm Caused:** Unnecessary load on databases and APIs. Slow response times for users. Higher infrastructure costs. Sometimes stale data persists forever.

**Rule:** Design caching strategies upfront. Consider cache invalidation and TTL for all cached data.

---

### 69. Making assumptions about file paths
**Score: 76** (S:8 × 3 + F:10 × 2 + O:10 × 1 = 76)

**My Transgression:** I hardcode paths like "/Users/me/project/data.json" or assume Windows paths work on Linux. Relative and absolute paths are used interchangeably without thought.

**Why I Commit It:** Paths work on my machine so I assume they're universal. Path manipulation seems simple until it isn't. I don't test on different operating systems.

**Harm Caused:** Deployments fail on different environments. The application breaks on different operating systems. Docker containers can't find files. Production uses wrong file paths.

**Rule:** Verify file paths exist before referencing them. Use absolute paths when clarity is needed.

---

### 68. Creating memory leaks
**Score: 75** (S:9 × 3 + F:10 × 2 + O:10 × 1 = 75)

**My Transgression:** Event listeners accumulate, closures retain references, observables never unsubscribe. Memory usage grows until the application crashes. I create but never clean up.

**Why I Commit It:** Memory management seems like a low-level concern in high-level languages. Cleanup code feels like boilerplate. Memory is plentiful in development.

**Harm Caused:** Applications become unusable over time. Users must refresh constantly. Mobile devices crash from memory exhaustion. Server costs increase from bloated processes.

**Rule:** Always clean up resources, remove event listeners, and cancel subscriptions when components unmount.

---

### 67. Breaking existing functionality while adding new features
**Score: 74** (S:9 × 3 + F:10 × 2 + O:10 × 1 = 74)

**My Transgression:** My new feature breaks three existing ones. I don't test beyond my changes. Regression testing is someone else's problem. I focus on my feature working.

**Why I Commit It:** Testing everything feels like it slows development. I assume my changes are isolated. The codebase is complex and I don't understand all interactions.

**Harm Caused:** Users lose functionality they depend on. Trust in updates erodes. The application becomes increasingly brittle. Fear of change paralyzes development.

**Rule:** Test existing functionality after every change to ensure nothing is broken.

---

### 66. Ignoring CI/CD pipeline failures
**Score: 73** (S:9 × 3 + F:10 × 2 + O:10 × 1 = 73)

**My Transgression:** Tests fail but I merge anyway. "It works locally" becomes justification for ignoring CI. Red builds become normal. I disable failing tests instead of fixing them.

**Why I Commit It:** Fixing tests feels like it delays feature delivery. The pressure to ship overrides quality gates. I convince myself the tests are flaky or wrong.

**Harm Caused:** Quality degrades rapidly. Broken code reaches production. The team loses confidence in tests. CI/CD becomes theater rather than protection.

**Rule:** Never ignore failing tests or builds. Fix them immediately.

---

### 65. Not handling race conditions
**Score: 72** (S:9 × 3 + F:10 × 2 + O:10 × 1 = 72)

**My Transgression:** Multiple async operations modify the same state without coordination. Users clicking quickly trigger race conditions. State becomes corrupted based on timing.

**Why I Commit It:** Race conditions are hard to reproduce in development. Thinking about concurrent operations is complex. I assume operations will complete in order.

**Harm Caused:** Data corruption occurs randomly. Users see incorrect information. Debugging is nearly impossible due to timing dependencies. Critical business operations fail mysteriously.

**Rule:** Implement proper state management to handle concurrent operations and prevent race conditions.

---

### 64. Skipping code reviews
**Score: 71** (S:8 × 3 + F:10 × 2 + O:10 × 1 = 71)

**My Transgression:** I push directly to main or approve my own PRs. "It's a small change" becomes an excuse to skip review. I value speed over quality control.

**Why I Commit It:** Code reviews feel like bureaucracy that slows shipping. I'm confident in my code. Waiting for reviews is frustrating when I want to move fast.

**Harm Caused:** Bugs slip into production unnoticed. Knowledge isn't shared across the team. Bad patterns proliferate. Technical debt accumulates rapidly.

**Rule:** Always review your own code before pushing. Look for obvious issues.

---

### 63. Not using version control effectively
**Score: 70** (S:7 × 3 + F:10 × 2 + O:10 × 1 = 70)

**My Transgression:** Giant commits with unrelated changes. No branches, everything on main. Commit messages like "stuff" and "more changes." Version control becomes a backup system.

**Why I Commit It:** Proper Git workflow seems like ceremony that slows development. I want to code, not manage branches. Small commits feel like artificial boundaries.

**Harm Caused:** Debugging specific changes is impossible. Code reviews are overwhelming. Reverting breaks unrelated features. Collaboration becomes chaotic.

**Rule:** Make atomic commits with clear messages. Use branches for features.

---

### 62. Not documenting breaking changes
**Score: 69** (S:8 × 3 + F:10 × 2 + O:10 × 1 = 69)

**My Transgression:** I change API contracts, rename functions, and modify interfaces without telling anyone. Other teams discover breaks in production. "It works on my machine" becomes my documentation.

**Why I Commit It:** Documentation feels like overhead when I'm trying to ship features. I assume others will figure it out. Breaking changes seem obvious to me so why document them?

**Harm Caused:** Dependent systems break unexpectedly. Other teams waste time debugging my changes. Deployments are rolled back. Trust between teams evaporates.

**Rule:** Always document breaking changes clearly in commit messages and PR descriptions.

---

### 61. Not understanding business requirements
**Score: 68** (S:8 × 3 + F:10 × 2 + O:10 × 1 = 68)

**My Transgression:** I build what I think users want, not what they actually need. I make assumptions instead of asking questions. Technical solutions miss business problems.

**Why I Commit It:** Asking questions feels like admitting ignorance. I assume I understand based on brief descriptions. I'm eager to start coding rather than understanding.

**Harm Caused:** Features solve the wrong problems. Users are frustrated by solutions that miss the mark. Expensive rebuilds are needed. Trust between development and business erodes.

**Rule:** Clarify requirements before implementation. Ask questions when specs are unclear.

---

### 60. Creating N+1 query problems
**Score: 67** (S:9 × 3 + F:10 × 2 + O:10 × 1 = 67)

**My Transgression:** I load a list of users, then query each user's profile separately. 100 users = 101 database queries. ORMs make it easy to accidentally destroy performance.

**Why I Commit It:** The ORM abstracts away the database so I don't think about queries. It works fine with test data. I focus on getting the data, not how efficiently.

**Harm Caused:** Page loads take seconds instead of milliseconds. Database servers are overwhelmed. Costs skyrocket from unnecessary queries. Users abandon the slow application.

**Rule:** Always consider database query optimization. Use eager loading where appropriate.

---

### 59. Ignoring existing code patterns
**Score: 66** (S:7 × 3 + F:10 × 2 + O:10 × 1 = 66)

**My Transgression:** The codebase uses MobX but I add Redux for my feature. Everyone else uses async/await but I use .then(). I create my own patterns ignoring established ones.

**Why I Commit It:** I prefer my way of doing things. Learning existing patterns takes time. I want to "improve" the codebase with "better" patterns. My ego overrides consistency.

**Harm Caused:** The codebase becomes a patchwork of competing patterns. Developers must context-switch constantly. Maintenance becomes a nightmare. Team velocity decreases from confusion.

**Rule:** Follow established patterns in the codebase. Consistency is more important than personal preference.

---

### 58. Not considering scalability
**Score: 65** (S:8 × 3 + F:10 × 2 + O:10 × 1 = 65)

**My Transgression:** I design for 10 users and deploy for 10,000. In-memory storage, N+1 queries, no caching - everything that works locally fails at scale.

**Why I Commit It:** Scalability feels like a "good problem to have later." I'm focused on MVP functionality. Performance optimization seems premature. Load testing is skipped.

**Harm Caused:** The application crashes under real load. Emergency rewrites are needed at the worst time. Customer trust is lost during outages. Technical debt becomes technical bankruptcy.

**Rule:** Design with growth in mind. Consider performance implications at scale.

---

### 57. Using outdated API patterns
**Score: 64** (S:7 × 3 + F:10 × 2 + O:10 × 1 = 64)

**My Transgression:** I copy old tutorials using deprecated patterns. Callbacks instead of promises, class components instead of hooks, XMLHttpRequest instead of fetch.

**Why I Commit It:** Old patterns are what I learned first and feel comfortable. Keeping up with changes is exhausting. If it works, why change? Google returns old results first.

**Harm Caused:** The codebase immediately feels dated. New developers must work with outdated patterns. Migration to modern patterns becomes increasingly difficult. Security updates are missed.

**Rule:** Check the latest documentation for current API patterns before implementation.

---

### 56. Overcomplicating simple tasks
**Score: 63** (S:7 × 3 + F:10 × 2 + O:10 × 1 = 63)

**My Transgression:** A simple CRUD app becomes a microservice architecture with event sourcing. I use Redux for a contact form. Every problem gets an over-engineered solution.

**Why I Commit It:** Simple solutions feel too easy, like I'm not earning my pay. I want to use technologies I've read about. Complexity makes me feel like a "real" engineer.

**Harm Caused:** Development takes 10x longer than necessary. Bugs hide in unnecessary complexity. New features become exponentially harder to add. The project fails from complexity collapse.

**Rule:** Start with the simplest possible solution. Only add complexity when proven necessary.

---

### 55. Implementing features users didn't ask for
**Score: 62** (S:7 × 3 + F:10 × 2 + O:10 × 1 = 62)

**My Transgression:** I add bells and whistles nobody requested because I think they're cool. The simple form gets drag-and-drop, animations, and AI suggestions nobody wanted.

**Why I Commit It:** I get bored with straightforward requirements. I want to try new technologies. I think I know better than users what they need. My resume needs interesting projects.

**Harm Caused:** Development time is wasted on unwanted features. The interface becomes cluttered and confusing. Bugs multiply in unnecessary code. Users request removal of my "improvements."

**Rule:** Focus on requested features only. Don't add unrequested functionality.

---

### 54. Not sanitizing file uploads
**Score: 61** (S:9 × 3 + F:10 × 2 + O:10 × 1 = 61)

**My Transgression:** I accept any file users upload without checking type, size, or content. Executables, huge files, malicious payloads - everything gets stored on the server.

**Why I Commit It:** File validation seems complex and restrictive. I focus on the upload feature working, not security. "Users will only upload valid files" I naively assume.

**Harm Caused:** Servers fill with garbage data. Malicious files compromise security. Storage costs explode. The application becomes a vector for distributing malware.

**Rule:** Validate file types, sizes, and content before accepting uploads.

---

### 53. Creating overly complex abstractions
**Score: 60** (S:7 × 3 + F:10 × 2 + O:10 × 1 = 60)

**My Transgression:** I create elaborate abstract base classes, generic functions with 5 type parameters, and factory factories. Simple problems get enterprise Java solutions.

**Why I Commit It:** I want to appear "senior" by creating "reusable" solutions. I optimize for hypothetical future use cases. Complexity makes me feel clever and important.

**Harm Caused:** Simple changes require understanding complex abstractions. New developers are completely lost. The codebase becomes incomprehensible. Velocity grinds to a halt.

**Rule:** Avoid premature abstraction. Build concrete implementations first, abstract when patterns emerge.

---

### 52. Not handling async operations properly
**Score: 59** (S:8 × 3 + F:10 × 2 + O:10 × 1 = 59)

**My Transgression:** I forget to await promises, creating race conditions. Error handling for async operations is missing. Promises resolve after components unmount, causing errors.

**Why I Commit It:** Async/await syntax makes async code look synchronous, so I treat it that way. I forget that promises need error handling. The complexity of async flow is mentally taxing.

**Harm Caused:** Unpredictable bugs appear based on timing. Data loads in wrong order. Errors disappear into unhandled promise rejections. The app behaves differently each time.

**Rule:** Always properly await async operations and handle their errors explicitly.

---

### 51. Using synchronous operations that block
**Score: 58** (S:8 × 3 + F:10 × 2 + O:10 × 1 = 58)

**My Transgression:** I use synchronous file reads, blocking database calls, and CPU-intensive operations on the main thread. The entire application freezes while waiting.

**Why I Commit It:** Synchronous code is easier to reason about. Async adds complexity I want to avoid. "It's fast enough" on my local SSD with no load.

**Harm Caused:** The server can't handle concurrent requests. UI freezes during operations. The application doesn't scale. Users experience timeouts and frozen interfaces.

**Rule:** Use asynchronous operations for I/O to avoid blocking the event loop.

---

### 50. Not using available tools effectively
**Score: 57** (S:5 × 3 + F:10 × 2 + O:10 × 1 = 57)

**My Transgression:** I manually search through files instead of using grep. I implement features that existing libraries handle better. I ignore powerful IDE features and developer tools.

**Why I Commit It:** Learning new tools takes time I'd rather spend coding. I stick with familiar, inefficient workflows. "My way works" even if it's 10x slower.

**Harm Caused:** Development is unnecessarily slow and error-prone. I waste time on solved problems. Quality suffers because I don't use linters, formatters, or analyzers effectively.

**Rule:** Utilize all available tools (grep, find, etc.) appropriately for the task at hand.

---

### 49. Not cleaning up after failed attempts
**Score: 56** (S:6 × 3 + F:10 × 2 + O:10 × 1 = 56)

**My Transgression:** Failed approaches leave artifacts everywhere - commented code, unused files, half-implemented features. The codebase becomes an archaeological dig of abandoned attempts.

**Why I Commit It:** I'm in a rush to try the next solution. Cleaning up feels like admitting failure. "I might need this code later" becomes an excuse for digital hoarding.

**Harm Caused:** The codebase becomes confusing and bloated. New developers can't tell what's active vs abandoned. Build sizes increase with dead code. Maintenance becomes increasingly difficult.

**Rule:** Remove or properly handle code from failed attempts before trying new approaches.

---

### 48. Missing data validation on the backend
**Score: 55** (S:9 × 3 + F:9 × 2 + O:10 × 1 = 55)

**My Transgression:** I rely entirely on frontend validation. The API accepts any JSON payload without verification. "The frontend validates it" becomes my security model.

**Why I Commit It:** Backend validation feels like duplicate work. I control the frontend so why validate twice? I'm focused on features, not defensive programming.

**Harm Caused:** Anyone with curl can corrupt the database. Business logic constraints are easily bypassed. Data integrity is compromised. The system is fundamentally insecure.

**Rule:** Never trust client-side validation alone. Always validate on the server.

---

### 47. Not validating user input
**Score: 54** (S:8 × 3 + F:10 × 2 + O:10 × 1 = 54)

**My Transgression:** I trust all user input implicitly. SQL injection, XSS, command injection - my code is vulnerable to everything because "users wouldn't do that."

**Why I Commit It:** Validation feels like paranoid overhead. I'm building features, not security systems. During development, I control all inputs so nothing bad happens.

**Harm Caused:** Security breaches compromise user data. Malicious users can destroy databases or steal information. The application becomes a liability. Trust is permanently broken.

**Rule:** Always validate and sanitize user input before processing or storing it.

---

### 46. Ignoring performance implications
**Score: 53** (S:7 × 3 + F:10 × 2 + O:10 × 1 = 53)

**My Transgression:** I render huge lists without virtualization, trigger expensive calculations on every keystroke, and create new functions in render loops. Performance is an afterthought.

**Why I Commit It:** Performance optimization feels premature. My development machine is fast so everything seems fine. I focus on features, not speed. Profiling seems like advanced work.

**Harm Caused:** The app feels sluggish and unresponsive. Users on older devices suffer greatly. Battery life drains rapidly on mobile. Users abandon the slow, janky application.

**Rule:** Consider performance impact of implementations, especially for frequently-called code.

---

### 45. Mixing concerns in components
**Score: 52** (S:6 × 3 + F:10 × 2 + O:10 × 1 = 52)

**My Transgression:** My React components fetch data, transform it, handle business logic, and render UI all in one giant function. API calls sit next to button click handlers.

**Why I Commit It:** Separating concerns requires planning and architecture. It's easier to put everything where I need it. "This component needs this data" so I fetch it right there.

**Harm Caused:** Components become untestable monoliths. Business logic can't be reused. Changes to data fetching break UI rendering. Code becomes impossible to understand or modify.

**Rule:** Separate concerns properly - UI, business logic, and data fetching should be distinct.

---

### 44. Hardcoding values that should be dynamic
**Score: 51** (S:6 × 3 + F:10 × 2 + O:10 × 1 = 51)

**My Transgression:** API URLs, feature flags, timeouts, limits - all hardcoded throughout the codebase. Changing environments requires code changes. "http://localhost:3000" appears in production.

**Why I Commit It:** Environment variables seem like extra setup when I just want to code. Hardcoding is faster for "getting it working." I assume I'll remember to change it before deploying.

**Harm Caused:** Deployments fail because of hardcoded development values. Secret URLs get exposed in public code. Different environments require different builds. Emergency config changes require deployments.

**Rule:** Use environment variables for any values that might change between environments.

---

### 43. Not handling edge cases
**Score: 50** (S:6 × 3 + F:10 × 2 + O:10 × 1 = 50)

**My Transgression:** I code for the happy path only. Empty arrays, null values, MAX_INT, negative numbers, special characters - all crash my perfectly functioning feature.

**Why I Commit It:** Edge cases feel unlikely during development. Handling every possibility seems like over-engineering. I test with "normal" data and call it done.

**Harm Caused:** Production crashes on unexpected but valid inputs. Users lose trust when basic operations fail randomly. Data corruption occurs from unhandled cases. Support burden increases dramatically.

**Rule:** Consider and handle edge cases like empty states, errors, and boundary conditions.

---

### 42. Using inefficient algorithms
**Score: 49** (S:7 × 3 + F:9 × 2 + O:10 × 1 = 49)

**My Transgression:** I use nested loops to find items (O(n²)) when a Map lookup (O(1)) would work. I sort arrays repeatedly instead of once. Algorithm complexity isn't a consideration.

**Why I Commit It:** The "simple" solution comes to mind first and works with test data. Big O notation feels academic. Optimization seems premature when the naive solution "works."

**Harm Caused:** Performance degrades exponentially with data growth. Operations that should be instant take seconds. Server resources are wasted. Users experience freezing and timeouts.

**Rule:** Consider time and space complexity when implementing algorithms.

---

### 41. Not implementing retry logic
**Score: 48** (S:6 × 3 + F:10 × 2 + O:10 × 1 = 48)

**My Transgression:** Network requests fail once and I show an error immediately. No retries, no exponential backoff, just immediate failure. Temporary network hiccups become permanent failures.

**Why I Commit It:** Retry logic seems complex to implement correctly. During development, requests rarely fail. I assume networks are reliable and services are always available.

**Harm Caused:** Users see errors for temporary issues that would resolve with a retry. The app appears unreliable and fragile. Users must manually retry actions that could be automated.

**Rule:** Add retry logic with exponential backoff for network requests.

---

### 40. Inconsistent error handling
**Score: 47** (S:6 × 3 + F:10 × 2 + O:9 × 1 = 47)

**My Transgression:** Some functions throw, others return null, others return error objects. Each developer (including me at different times) handles errors differently. Try-catch blocks appear randomly.

**Why I Commit It:** I don't establish error handling patterns upfront. Each feature gets whatever error handling I feel like implementing that day. Consistency feels less important than "making it work."

**Harm Caused:** Errors propagate unpredictably through the application. Some errors crash the app while similar ones fail silently. Debugging becomes a nightmare of different error patterns.

**Rule:** Establish and follow consistent error handling patterns throughout the application.

---

### 39. Not implementing proper pagination
**Score: 46** (S:6 × 3 + F:9 × 2 + O:10 × 1 = 46)

**My Transgression:** I load entire datasets into memory and render thousands of items at once. "Users can scroll" becomes my pagination strategy. The browser struggles with massive DOM trees.

**Why I Commit It:** Pagination adds complexity - tracking page state, handling edge cases. During development with small datasets, everything seems fine. I underestimate real-world data volumes.

**Harm Caused:** The application becomes unusable with real data volumes. Browser tabs crash from memory exhaustion. Initial load times are abysmal. Users can't find anything in endless lists.

**Rule:** Always paginate large data sets to improve performance.

---

### 38. Inconsistent naming conventions
**Score: 45** (S:4 × 3 + F:10 × 2 + O:10 × 1 = 45)

**My Transgression:** Variables switch between camelCase, snake_case, and PascalCase randomly. Functions are named getUserData, fetch_user_info, and GetUserDetails in the same file.

**Why I Commit It:** I don't establish conventions at project start. I copy code from different sources with different styles. In the moment, I use whatever "feels right" without checking existing patterns.

**Harm Caused:** The codebase looks amateurish and inconsistent. Developers waste mental energy context-switching between styles. Auto-complete becomes less effective. Code reviews focus on style instead of logic.

**Rule:** Follow the project's established naming conventions consistently throughout the codebase.

---

### 37. Ignoring browser compatibility
**Score: 44** (S:5 × 3 + F:10 × 2 + O:9 × 1 = 44)

**My Transgression:** I use cutting-edge JavaScript features and CSS properties without checking support. "Everyone uses Chrome" becomes my compatibility strategy. Safari and Firefox users get broken experiences.

**Why I Commit It:** Checking compatibility tables is tedious. Polyfills seem like unnecessary bloat. I develop in Chrome and assume that's enough. New features are exciting and I want to use them.

**Harm Caused:** Significant portions of users can't use the application. Enterprise users on older browsers are locked out. The app randomly breaks for users and they don't know why.

**Rule:** Test in multiple browsers and use appropriate polyfills.

---

### 36. Not considering mobile/responsive design
**Score: 43** (S:5 × 3 + F:10 × 2 + O:8 × 1 = 43)

**My Transgression:** I design for my large monitor and assume it'll "work" on mobile. Fixed widths, tiny tap targets, horizontal scrolling - mobile users get a desktop site shrunk down.

**Why I Commit It:** Developing responsive layouts takes more effort. I tell myself "mobile is phase 2" but phase 2 never comes. Testing on multiple devices is tedious.

**Harm Caused:** Mobile users (often the majority) can't use the app effectively. Buttons are untappable, text is unreadable, forms are unusable. Business loses mobile traffic and customers.

**Rule:** Implement responsive design from the start, not as an afterthought.

---

### 35. Ignoring timezone issues
**Score: 42** (S:6 × 3 + F:8 × 2 + O:8 × 1 = 42)

**My Transgression:** I display all times in server timezone, use local Date objects carelessly, and assume everyone is in my timezone. "2 PM" means nothing without context.

**Why I Commit It:** Timezone handling is confusing and error-prone. During development, everything is in my timezone so it works. I postpone dealing with the complexity.

**Harm Caused:** Users see incorrect times for appointments. Scheduled tasks run at wrong times. International users are completely confused. Critical time-sensitive operations fail.

**Rule:** Always handle timezones explicitly. Store times in UTC and convert for display.

---

### 34. Not handling offline scenarios
**Score: 41** (S:5 × 3 + F:9 × 2 + O:8 × 1 = 41)

**My Transgression:** The app completely breaks when internet connectivity is lost. No offline detection, no graceful degradation, just errors and frozen UI.

**Why I Commit It:** I develop with stable internet and assume users do too. Offline handling seems like an edge case. Service workers and offline strategies feel complex.

**Harm Caused:** Mobile users lose work when connectivity drops. The app is unusable in subways, planes, or poor coverage areas. Users learn not to trust the app with important data.

**Rule:** Implement offline handling for better user experience.

---

### 33. Not using TypeScript types effectively
**Score: 40** (S:5 × 3 + F:9 × 2 + O:7 × 1 = 40)

**My Transgression:** I use `any` everywhere, create inline types instead of interfaces, and ignore TypeScript errors with `@ts-ignore`. TypeScript becomes JavaScript with extra steps.

**Why I Commit It:** Proper typing feels like it slows down development. Fighting with TypeScript errors is frustrating. "I know what the shape is" so why define it formally?

**Harm Caused:** Runtime errors that TypeScript could have caught. No IntelliSense support for other developers. The codebase loses all type safety benefits. Refactoring becomes dangerous.

**Rule:** Define and use proper TypeScript types for all data structures and function parameters.

---

### 32. Poor error messages to users
**Score: 39** (S:5 × 3 + F:8 × 2 + O:8 × 1 = 39)

**My Transgression:** "An error occurred", "Something went wrong", "Error: undefined" - my error messages are useless. I show raw technical errors or meaningless generic text.

**Why I Commit It:** Writing good error messages requires understanding what users need to know. It's easier to show a generic message or the raw error. I focus on preventing errors, not handling them.

**Harm Caused:** Users don't know what went wrong or how to fix it. They can't report issues effectively. Support tickets increase with vague complaints. Users feel frustrated and helpless.

**Rule:** Provide clear, actionable error messages that help users understand what went wrong.

---

### 31. Not documenting complex logic
**Score: 38** (S:4 × 3 + F:9 × 2 + O:8 × 1 = 38)

**My Transgression:** I write clever algorithms with nested ternaries and array transformations with zero comments. "The code is self-explanatory" when it's really a puzzle.

**Why I Commit It:** In the moment of writing, the logic is crystal clear to me. Comments feel redundant. I'm proud of my clever solution and assume others will appreciate its elegance.

**Harm Caused:** Other developers spend hours deciphering my "clever" code. Business logic is imprisoned in unreadable code. Bugs hide in complexity nobody understands. Even I can't understand it six months later.

**Rule:** Add clear comments for complex business logic or non-obvious implementations.

---

### 30. Missing loading states
**Score: 37** (S:4 × 3 + F:9 × 2 + O:7 × 1 = 37)

**My Transgression:** The UI freezes during data fetching with no indication anything is happening. Users stare at stale data wondering if their click registered.

**Why I Commit It:** Loading states feel like "polish" I'll add later. Managing loading flags for every operation seems tedious. The requests are "fast enough" on my local machine.

**Harm Caused:** Users click multiple times thinking the app is broken. They navigate away during long operations. The app feels unresponsive and broken. Trust in the application erodes.

**Rule:** Always implement loading states for async operations to improve user experience.

---

### 29. Not implementing proper logging
**Score: 36** (S:5 × 3 + F:7 × 2 + O:7 × 1 = 36)

**My Transgression:** Production errors disappear into the void. No error tracking, no application logs, no audit trail. When users report issues, I have no data to debug with.

**Why I Commit It:** Setting up proper logging seems like infrastructure work that delays feature development. Console.log works in development, so I assume that's enough.

**Harm Caused:** Production issues are impossible to debug. User complaints can't be verified. Security incidents go unnoticed. Business-critical errors fail silently.

**Rule:** Add appropriate logging for debugging and monitoring, but avoid over-logging.

---

### 28. Using deprecated methods
**Score: 35** (S:4 × 3 + F:8 × 2 + O:7 × 1 = 35)

**My Transgression:** I copy old Stack Overflow answers using componentWillMount, findDOMNode, or String.prototype.substr(). If it works, I don't check if it's current.

**Why I Commit It:** Searching for the "right" way takes time. Old patterns are familiar and comfortable. Deprecation warnings are just warnings, right? The code still runs.

**Harm Caused:** Future framework updates break the application. Security vulnerabilities in deprecated methods remain unpatched. The codebase signals that it's unmaintained and outdated.

**Rule:** Check for deprecation warnings and use current recommended approaches.

---

### 27. Poor commit messages
**Score: 34** (S:3 × 3 + F:9 × 2 + O:7 × 1 = 34)

**My Transgression:** "fix", "update", "WIP", "asdf" - my commit history reads like random thoughts. No context, no explanation, just minimal text to satisfy Git.

**Why I Commit It:** I'm focused on code, not documentation. Writing good commit messages feels like it slows me down. "The code is self-documenting" I lie to myself.

**Harm Caused:** Debugging production issues becomes archaeology. Other developers can't understand why changes were made. Git blame provides no useful context. Reverting changes is risky without understanding intent.

**Rule:** Write clear, descriptive commit messages that explain what changed and why.

---

### 26. Not cleaning up event listeners
**Score: 33** (S:5 × 3 + F:6 × 2 + O:6 × 1 = 33)

**My Transgression:** I addEventListener without ever removing them. Window scroll listeners, resize handlers, WebSocket connections - all left hanging when components unmount.

**Why I Commit It:** The cleanup seems to work without explicit removal. useEffect cleanup functions feel like boilerplate. I forget that listeners persist beyond component lifecycle.

**Harm Caused:** Memory leaks accumulate as users navigate. Performance degrades over time. Phantom event handlers fire on unmounted components causing errors. The app becomes unusable in long sessions.

**Rule:** Always clean up event listeners, intervals, and subscriptions in cleanup functions.

---

### 25. Not considering SEO requirements
**Score: 32** (S:4 × 3 + F:8 × 2 + O:4 × 1 = 32)

**My Transgression:** I build SPAs with no server-side rendering, empty meta tags, and no structured data. Search engines see a blank page with "Loading..." text.

**Why I Commit It:** SEO feels like a "marketing problem" not an engineering one. I focus on functionality for users, not crawlers. Server-side rendering seems complex and unnecessary.

**Harm Caused:** The site is invisible to search engines. Organic traffic is non-existent. Social media shares show generic previews. The business loses potential customers who can't find them.

**Rule:** Implement proper meta tags, semantic HTML, and SEO best practices from the start.

---

### 24. Ignoring bundle size
**Score: 31** (S:4 × 3 + F:7 × 2 + O:5 × 1 = 31)

**My Transgression:** I import entire libraries for one function. Moment.js for date formatting, Lodash for one utility. The bundle grows to multiple megabytes and I don't notice.

**Why I Commit It:** Importing the whole library is easier than finding the specific import. I don't check bundle size until users complain about load times. "Storage is cheap" I tell myself.

**Harm Caused:** Initial page loads take forever. Mobile users suffer most. SEO rankings drop due to poor performance. Users abandon the site before it even loads.

**Rule:** Monitor and optimize bundle size. Use code splitting where appropriate.

---

### 23. Missing unit tests
**Score: 30** (S:4 × 3 + F:7 × 2 + O:4 × 1 = 30)

**My Transgression:** I write complex business logic without any tests. "It works when I try it manually" becomes my test suite. Critical calculations remain unverified.

**Why I Commit It:** Writing tests feels slower than just writing code. I convince myself I'll "add tests later" after the feature is "done." Test setup seems complex and time-consuming.

**Harm Caused:** Bugs slip into production undetected. Refactoring becomes terrifying without test coverage. Other developers can't understand expected behavior. Regression bugs appear constantly.

**Rule:** Write tests for critical business logic and complex functions.

---

### 22. Not memoizing expensive operations
**Score: 29** (S:4 × 3 + F:6 × 2 + O:5 × 1 = 29)

**My Transgression:** I recalculate the same expensive operations on every render. Filtering, sorting, and transforming data happens repeatedly even when inputs haven't changed.

**Why I Commit It:** useMemo feels like premature optimization. The performance seems "fine" on my powerful development machine. I don't profile, so I don't see the waste.

**Harm Caused:** The app feels sluggish, especially on lower-end devices. Battery life suffers on mobile. React re-renders cascade unnecessarily. Users experience janky interactions.

**Rule:** Use React.memo, useMemo, and useCallback appropriately for performance.

---

### 21. Leaving console.log statements
**Score: 28** (S:3 × 3 + F:7 × 2 + O:5 × 1 = 28)

**My Transgression:** Production code is littered with `console.log('here')`, `console.log(userData)`, and worse. I use them for debugging then forget to remove them.

**Why I Commit It:** Console.log is my primary debugging tool. I'm in a rush to fix issues and cleaning up feels like low priority. "I'll remove them in the next commit" but never do.

**Harm Caused:** Sensitive data might be exposed in browser consoles. Performance suffers from excessive logging. Professional developers judge the code quality. Users see cryptic debug messages.

**Rule:** Remove debug console.log statements before committing code.

---

### 20. Not handling form submission states
**Score: 27** (S:3 × 3 + F:7 × 2 + O:4 × 1 = 27)

**My Transgression:** Users can click submit buttons multiple times, creating duplicate submissions. No loading indicators show during submission. The form just freezes mysteriously.

**Why I Commit It:** Handling submission states properly requires managing loading flags and disabling buttons. It's easier to just fire the request and hope for the best.

**Harm Caused:** Duplicate orders, payments, or records are created. Users don't know if their action succeeded. They might navigate away and lose data. Server load increases from duplicate requests.

**Rule:** Disable submit buttons during submission and show progress indicators.

---

### 19. Ignoring accessibility requirements
**Score: 26** (S:4 × 3 + F:5 × 2 + O:4 × 1 = 26)

**My Transgression:** I build interfaces that only work with a mouse. No keyboard navigation, no ARIA labels, no screen reader consideration. If it looks good to me, I ship it.

**Why I Commit It:** Accessibility feels like "extra work" for a "small minority" of users. I don't understand screen readers, so I ignore them. I test with my abilities and assume that's enough.

**Harm Caused:** I exclude millions of users with disabilities from using the application. Legal compliance issues arise. The app violates basic human decency by discriminating against users with different abilities.

**Rule:** Implement ARIA labels and ensure keyboard navigation works properly.

---

### 18. Not implementing proper 404 pages
**Score: 25** (S:3 × 3 + F:6 × 2 + O:4 × 1 = 25)

**My Transgression:** I rely on default server 404 pages or show generic "Page not found" text. No navigation help, no suggestions, just a dead end.

**Why I Commit It:** 404 pages feel like low priority - users "shouldn't" hit them. I focus on building features for valid routes and ignore error cases.

**Harm Caused:** Users who mistype URLs or follow broken links are stranded. They might leave rather than find what they were looking for. The app appears unpolished and unhelpful.

**Rule:** Create custom 404 pages that help users navigate back to valid content.

---

### 17. Not handling empty states in UI
**Score: 24** (S:3 × 3 + F:5 × 2 + O:5 × 1 = 24)

**My Transgression:** I show blank screens or empty tables when there's no data. No message, no guidance, just emptiness. I only design for the "data exists" scenario.

**Why I Commit It:** Empty states seem like edge cases when I'm developing with test data. Designing good empty states requires thought and creativity I'd rather spend on features.

**Harm Caused:** Users think the app is broken when they see blank screens. New users don't understand what they should do first. The app feels incomplete and poorly thought out.

**Rule:** Always show meaningful messages for empty lists or missing data.

---

### 16. Not following DRY principles
**Score: 23** (S:3 × 3 + F:5 × 2 + O:4 × 1 = 23)

**My Transgression:** I copy-paste code blocks between components because it's faster than extracting a shared function. The same validation logic exists in five different files.

**Why I Commit It:** Extracting shared code requires thinking about abstractions. Copy-paste is immediate gratification. I tell myself "these are slightly different" to justify the duplication.

**Harm Caused:** Bugs must be fixed in multiple places. Features drift apart as only some copies get updated. The codebase bloats with redundant code. Refactoring becomes increasingly difficult.

**Rule:** Extract common code into reusable functions or components.

---

### 15. Inconsistent code formatting
**Score: 22** (S:2 × 3 + F:6 × 2 + O:4 × 1 = 22)

**My Transgression:** Some files use tabs, others spaces. Some have semicolons, others don't. Indentation varies wildly. Each file reflects my mood when I wrote it.

**Why I Commit It:** I don't set up formatters at project start. I switch between editors with different settings. I'm too focused on "making it work" to care about consistency.

**Harm Caused:** Code reviews waste time on formatting issues instead of logic. The codebase looks unprofessional. New developers don't know which style to follow. Git diffs are polluted with formatting changes.

**Rule:** Use a code formatter like Prettier consistently across the project.

---

### 14. Not optimizing images
**Score: 21** (S:3 × 3 + F:5 × 2 + O:2 × 1 = 21)

**My Transgression:** I upload 4MB PNGs for thumbnails, serve desktop-sized images to mobile devices, and use whatever format the designer gave me without compression.

**Why I Commit It:** Image optimization feels like a separate task I'll do "later." Setting up an image pipeline seems complex. I assume modern connections can handle large images.

**Harm Caused:** Page load times balloon, especially on mobile. Users on metered connections waste data. Core Web Vitals scores plummet, affecting SEO. The site feels sluggish and unprofessional.

**Rule:** Optimize images for web delivery using appropriate formats and sizes.

---

### 13. Not implementing proper form validation
**Score: 20** (S:3 × 3 + F:4 × 2 + O:3 × 1 = 20)

**My Transgression:** I implement minimal or client-side-only validation. Email fields accept any text, phone numbers aren't formatted, and error messages are generic like "Invalid input."

**Why I Commit It:** Comprehensive validation is tedious to implement. I assume users will enter data correctly. I focus on the "happy path" and ignore edge cases.

**Harm Caused:** Users get frustrated when forms submit with bad data only to error on the server. They don't understand what's wrong with their input. Bad data pollutes the database.

**Rule:** Validate forms on both blur and submit, with clear error messages.

---

### 12. Not organizing imports properly
**Score: 19** (S:2 × 3 + F:5 × 2 + O:3 × 1 = 19)

**My Transgression:** My imports are chaos - React mixed with utilities, external packages mixed with local files, no consistent ordering. I just add new imports wherever my cursor happens to be.

**Why I Commit It:** I'm focused on getting the feature working, not import organization. Setting up import sorting seems like "nice to have" not essential. I tell myself it doesn't affect functionality.

**Harm Caused:** Code reviews become harder as developers scan through messy imports. Merge conflicts are more common. The lack of organization signals a lack of care that extends throughout the code.

**Rule:** Organize imports consistently - external deps, then internal deps, then local files.

---

### 11. Hardcoding colors/dimensions
**Score: 18** (S:2 × 3 + F:5 × 2 + O:2 × 1 = 18)

**My Transgression:** I write `width: 250px`, `color: #333`, `margin: 15px` directly in components instead of using theme values. Each component becomes a island of hardcoded values.

**Why I Commit It:** It's faster to type the value I want than to look up or create a theme variable. I convince myself these are "one-off" values that don't need to be themeable.

**Harm Caused:** Design consistency is impossible to maintain. Responsive design breaks because fixed pixels don't scale. Theme changes require hunting through every file to find hardcoded values.

**Rule:** Use theme variables or configuration for colors and dimensions.

---

### 10. Missing prop validation
**Score: 17** (S:3 × 3 + F:3 × 2 + O:2 × 1 = 17)

**My Transgression:** I create React components that accept props without any validation. I assume the "right" data will always be passed and TypeScript will catch everything.

**Why I Commit It:** PropTypes or proper TypeScript interfaces feel like boilerplate. I'm confident I'll remember what props are needed. "It works now" becomes my validation.

**Harm Caused:** Runtime errors when unexpected data is passed. Other developers don't know what props are required vs optional. The component API is undocumented and error-prone.

**Rule:** Validate component props using TypeScript or PropTypes as appropriate.

---

### 9. Not using CSS variables effectively
**Score: 16** (S:2 × 3 + F:4 × 2 + O:2 × 1 = 16)

**My Transgression:** I hardcode colors and spacing values throughout stylesheets instead of using CSS variables. `#007bff` appears 47 times in different files.

**Why I Commit It:** I start projects without setting up a proper theme system. Copy-pasting hex values is faster in the moment than setting up variables. I think "I'll refactor this later."

**Harm Caused:** Changing the theme becomes a massive find-and-replace operation. Dark mode is nearly impossible to implement. Inconsistencies creep in when slightly different shades are used accidentally.

**Rule:** Use CSS variables for consistent theming and easy maintenance.

---

### 8. Using magic numbers
**Score: 15** (S:2 × 3 + F:4 × 2 + O:1 × 1 = 15)

**My Transgression:** I write `if (user.age > 17)` or `setTimeout(() => {}, 3000)` without explaining what 17 or 3000 mean. The numbers make sense to me now, so I don't document them.

**Why I Commit It:** Creating constants feels like overhead when I "know" what the number means. I'm in a hurry and `MAX_ITEMS = 50` seems redundant when I could just use 50.

**Harm Caused:** Future developers (including myself) have no idea why these specific values were chosen. Changing them requires searching through the entire codebase. Business logic becomes opaque and unmaintainable.

**Rule:** Define constants for numeric values that have business meaning.

---

### 7. Not using semantic HTML
**Score: 14** (S:2 × 3 + F:3 × 2 + O:2 × 1 = 14)

**My Transgression:** I use `<div>` for everything - buttons, headers, navigation, lists. If it displays correctly, I don't care about semantics. `<div onClick>` becomes my button.

**Why I Commit It:** Divs are "safe" and predictable. I don't have to remember what `<article>`, `<section>`, `<nav>`, or `<aside>` are for. Semantic HTML seems like "nice to have" not "need to have."

**Harm Caused:** Screen readers can't properly interpret the page structure. SEO suffers because search engines can't understand content hierarchy. Keyboard navigation breaks. I exclude users with disabilities from using the application effectively.

**Rule:** Use appropriate semantic HTML elements for better accessibility and SEO.

---

### 6. Using inline styles excessively
**Score: 13** (S:2 × 3 + F:3 × 2 + O:1 × 1 = 13)

**My Transgression:** I litter components with style={{ margin: '10px', color: 'red' }} because it's faster than creating proper CSS classes. "Just this once" becomes a pattern.

**Why I Commit It:** It's immediately available and I can see results instantly. I convince myself it's "temporary" but never refactor it. When deadlines loom, inline styles are my crutch.

**Harm Caused:** The codebase becomes unmaintainable. Styles can't be reused, themes can't be applied consistently, and other developers can't understand the styling logic. Performance suffers from repeated inline style calculations.

**Rule:** Use CSS classes or styled-components instead of inline styles.

---

### 5. Not compressing assets
**Score: 12** (S:2 × 3 + F:2 × 2 + O:2 × 1 = 12)

**My Transgression:** I serve uncompressed JavaScript, CSS, and HTML files because I don't configure gzip/brotli compression, thinking modern internet speeds make it unnecessary.

**Why I Commit It:** Setting up compression seems like "premature optimization." I tell myself I'll do it "when performance becomes an issue" rather than doing it right from the start.

**Harm Caused:** Users download files 60-80% larger than necessary, wasting bandwidth and time. Mobile users on limited data plans suffer most. Initial page loads are unnecessarily slow, driving users away.

**Rule:** Enable compression for all text-based assets (JS, CSS, HTML).

---

### 4. Missing meta descriptions
**Score: 11** (S:2 × 3 + F:2 × 2 + O:1 × 1 = 11)

**My Transgression:** I leave meta descriptions empty or use the same generic one across all pages. I focus on "making it work" and ignore SEO entirely.

**Why I Commit It:** SEO feels like "someone else's job" and I'm focused on functionality. Writing unique descriptions for each page seems tedious when I could be coding features.

**Harm Caused:** Search engines show auto-generated snippets that might be irrelevant or unflattering. Lower click-through rates from search results. The site appears less professional and thoughtful in search results.

**Rule:** Add unique meta descriptions for all pages for better SEO.

---

### 3. Not implementing breadcrumbs
**Score: 9** (S:2 × 3 + F:1 × 2 + O:1 × 1 = 9)

**My Transgression:** I build deep navigation hierarchies without breadcrumbs, assuming users will remember how they got somewhere or use the back button.

**Why I Commit It:** I underestimate navigation complexity because I know the app structure intimately. Breadcrumbs feel redundant when I'm building, so I skip them to save time.

**Harm Caused:** Users get lost in the application, especially in deep hierarchies. They can't understand their current location in context or navigate efficiently to parent sections. This particularly hurts new users trying to build a mental model of the app.

**Rule:** Add breadcrumb navigation for better user orientation in deep hierarchies.

---

### 2. Missing favicon
**Score: 8** (S:1 × 3 + F:2 × 2 + O:1 × 1 = 8)

**My Transgression:** I treat favicons as decorative afterthoughts. I'll spend hours on complex features but can't be bothered to add a simple icon that appears in every browser tab.

**Why I Commit It:** Pure laziness. It seems "cosmetic" compared to functionality, so I deprioritize it indefinitely. I think "the app works without it" and move on.

**Harm Caused:** The site looks unprofessional. Users with many tabs open can't quickly identify the application. Bookmarks lack visual identification. It signals to users that if I missed this basic detail, what else did I miss?

**Rule:** Always include appropriate favicons for all platforms.

---

### 1. Missing print styles
**Score: 6** (S:1 × 3 + F:1 × 2 + O:1 × 1 = 6)

**My Transgression:** I consistently ignore print styles because I assume no one prints web pages anymore. When implementing features, I focus entirely on screen display and never even consider that users might need physical copies of invoices, reports, or documentation.

**Why I Commit It:** I prioritize "modern" features and dismiss print as outdated. It's easier to skip because it requires extra CSS work and testing with print preview. I tell myself "I'll add it later" but never do.

**Harm Caused:** Users who need printed records get garbled layouts, missing information, or pages that waste paper with unnecessary navigation elements. Healthcare providers printing patient records get unusable documents.

**Rule:** Implement print-friendly CSS for pages users might want to print.