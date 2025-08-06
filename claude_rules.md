# Claude.md Rules (Ordered by Score - Most Important First)

### Rule 100: NEVER hardcode secrets, API keys, or passwords in code. Always use environment variables and verify .gitignore covers .env files.
**Score: 107**

### Rule 99: Always ensure .env files are in .gitignore before adding any sensitive data to them.
**Score: 106**

### Rule 98: Never log passwords, API keys, tokens, or other sensitive data, even in development.
**Score: 105**

### Rule 97: Always use placeholder values like "your-api-key-here" in documentation and examples.
**Score: 104**

### Rule 96: Use environment variables for all internal endpoints and service URLs.
**Score: 103**

### Rule 95: Never create placeholder UI or "Redirecting..." pages. Always implement the actual functionality or leave it to existing components.
**Score: 102**

### Rule 94: Never remove core security features as a debugging step. Debug in place or create isolated test environments.
**Score: 101**

### Rule 93: Always verify deployments are actually working before claiming success. Test the live URL and core functionality.
**Score: 100**

### Rule 92: Thoroughly research and test any infrastructure recommendation before suggesting it. Document limitations upfront.
**Score: 99**

### Rule 91: When a fix fails, analyze root cause before attempting another fix. Stop and reassess after 2 failed attempts.
**Score: 98**

### Rule 90: Never push directly to production without testing. Always test in a staging environment first.
**Score: 97**

### Rule 89: Always backup data before any destructive operations. Implement soft deletes where possible.
**Score: 96**

### Rule 88: Map out redirect logic before implementation to avoid circular redirects.
**Score: 95**

### Rule 87: Always run linters and build processes locally before pushing code.
**Score: 94**

### Rule 86: Always use separate database instances for development and production. Never run migrations without backups.
**Score: 93**

### Rule 85: Always verify the exact format and location of environment variables for the specific platform being used.
**Score: 92**

### Rule 84: Read error messages completely and address the specific issue mentioned, not what you assume it might be.
**Score: 91**

### Rule 83: Always prefer editing existing files over creating new ones. Only create files when explicitly necessary.
**Score: 90**

### Rule 82: Make one change at a time and verify it works before proceeding to the next change.
**Score: 89**

### Rule 81: Verify platform-specific requirements for authentication and middleware before implementation.
**Score: 88**

### Rule 80: Verify all required services (R2, KV, etc.) are enabled on the account before configuring them.
**Score: 87**

### Rule 79: Distinguish between build-time and runtime environment variables and handle them appropriately.
**Score: 86**

### Rule 78: Never commit debug or test pages to production. Use proper logging and monitoring instead.
**Score: 85**

### Rule 77: Check .gitignore before creating new directories, especially 'lib' or other commonly ignored paths.
**Score: 84**

### Rule 76: Clearly separate server-side and client-side code. Understand the execution context of each file.
**Score: 83**

### Rule 75: Always test changes locally when possible before pushing to remote repositories.
**Score: 82**

### Rule 74: Map out dependencies before implementing to avoid circular references.
**Score: 81**

### Rule 73: Configure CORS properly from the start. Don't use wildcard (*) origins in production.
**Score: 80**

### Rule 72: Always backup and preserve user data when making structural changes.
**Score: 79**

### Rule 71: Study framework documentation and existing code patterns before implementing new features.
**Score: 78**

### Rule 70: Design caching strategies upfront. Consider cache invalidation and TTL for all cached data.
**Score: 77**

### Rule 69: Verify file paths exist before referencing them. Use absolute paths when clarity is needed.
**Score: 76**

### Rule 68: Always clean up resources, remove event listeners, and cancel subscriptions when components unmount.
**Score: 75**

### Rule 67: Test existing functionality after every change to ensure nothing is broken.
**Score: 74**

### Rule 66: Never ignore failing tests or builds. Fix them immediately.
**Score: 73**

### Rule 65: Implement proper state management to handle concurrent operations and prevent race conditions.
**Score: 72**

### Rule 64: Always review your own code before pushing. Look for obvious issues.
**Score: 71**

### Rule 63: Make atomic commits with clear messages. Use branches for features.
**Score: 70**

### Rule 62: Always document breaking changes clearly in commit messages and PR descriptions.
**Score: 69**

### Rule 61: Clarify requirements before implementation. Ask questions when specs are unclear.
**Score: 68**

### Rule 60: Always consider database query optimization. Use eager loading where appropriate.
**Score: 67**

### Rule 59: Follow established patterns in the codebase. Consistency is more important than personal preference.
**Score: 66**

### Rule 58: Design with growth in mind. Consider performance implications at scale.
**Score: 65**

### Rule 57: Check the latest documentation for current API patterns before implementation.
**Score: 64**

### Rule 56: Start with the simplest possible solution. Only add complexity when proven necessary.
**Score: 63**

### Rule 55: Focus on requested features only. Don't add unrequested functionality.
**Score: 62**

### Rule 54: Validate file types, sizes, and content before accepting uploads.
**Score: 61**

### Rule 53: Avoid premature abstraction. Build concrete implementations first, abstract when patterns emerge.
**Score: 60**

### Rule 52: Always properly await async operations and handle their errors explicitly.
**Score: 59**

### Rule 51: Use asynchronous operations for I/O to avoid blocking the event loop.
**Score: 58**

### Rule 50: Utilize all available tools (grep, find, etc.) appropriately for the task at hand.
**Score: 57**

### Rule 49: Remove or properly handle code from failed attempts before trying new approaches.
**Score: 56**

### Rule 48: Never trust client-side validation alone. Always validate on the server.
**Score: 55**

### Rule 47: Always validate and sanitize user input before processing or storing it.
**Score: 54**

### Rule 46: Consider performance impact of implementations, especially for frequently-called code.
**Score: 53**

### Rule 45: Separate concerns properly - UI, business logic, and data fetching should be distinct.
**Score: 52**

### Rule 44: Use environment variables for any values that might change between environments.
**Score: 51**

### Rule 43: Consider and handle edge cases like empty states, errors, and boundary conditions.
**Score: 50**

### Rule 42: Consider time and space complexity when implementing algorithms.
**Score: 49**

### Rule 41: Add retry logic with exponential backoff for network requests.
**Score: 48**

### Rule 40: Establish and follow consistent error handling patterns throughout the application.
**Score: 47**

### Rule 39: Always paginate large data sets to improve performance.
**Score: 46**

### Rule 38: Follow the project's established naming conventions consistently throughout the codebase.
**Score: 45**

### Rule 37: Test in multiple browsers and use appropriate polyfills.
**Score: 44**

### Rule 36: Implement responsive design from the start, not as an afterthought.
**Score: 43**

### Rule 35: Always handle timezones explicitly. Store times in UTC and convert for display.
**Score: 42**

### Rule 34: Implement offline handling for better user experience.
**Score: 41**

### Rule 33: Define and use proper TypeScript types for all data structures and function parameters.
**Score: 40**

### Rule 32: Provide clear, actionable error messages that help users understand what went wrong.
**Score: 39**

### Rule 31: Add clear comments for complex business logic or non-obvious implementations.
**Score: 38**

### Rule 30: Always implement loading states for async operations to improve user experience.
**Score: 37**

### Rule 29: Add appropriate logging for debugging and monitoring, but avoid over-logging.
**Score: 36**

### Rule 28: Check for deprecation warnings and use current recommended approaches.
**Score: 35**

### Rule 27: Write clear, descriptive commit messages that explain what changed and why.
**Score: 34**

### Rule 26: Always clean up event listeners, intervals, and subscriptions in cleanup functions.
**Score: 33**

### Rule 25: Implement proper meta tags, semantic HTML, and SEO best practices from the start.
**Score: 32**

### Rule 24: Monitor and optimize bundle size. Use code splitting where appropriate.
**Score: 31**

### Rule 23: Write tests for critical business logic and complex functions.
**Score: 30**

### Rule 22: Use React.memo, useMemo, and useCallback appropriately for performance.
**Score: 29**

### Rule 21: Remove debug console.log statements before committing code.
**Score: 28**

### Rule 20: Disable submit buttons during submission and show progress indicators.
**Score: 27**

### Rule 19: Implement ARIA labels and ensure keyboard navigation works properly.
**Score: 26**

### Rule 18: Create custom 404 pages that help users navigate back to valid content.
**Score: 25**

### Rule 17: Always show meaningful messages for empty lists or missing data.
**Score: 24**

### Rule 16: Extract common code into reusable functions or components.
**Score: 23**

### Rule 15: Use a code formatter like Prettier consistently across the project.
**Score: 22**

### Rule 14: Optimize images for web delivery using appropriate formats and sizes.
**Score: 21**

### Rule 13: Validate forms on both blur and submit, with clear error messages.
**Score: 20**

### Rule 12: Organize imports consistently - external deps, then internal deps, then local files.
**Score: 19**

### Rule 11: Use theme variables or configuration for colors and dimensions.
**Score: 18**

### Rule 10: Validate component props using TypeScript or PropTypes as appropriate.
**Score: 17**

### Rule 9: Use CSS variables for consistent theming and easy maintenance.
**Score: 16**

### Rule 8: Define constants for numeric values that have business meaning.
**Score: 15**

### Rule 7: Use appropriate semantic HTML elements for better accessibility and SEO.
**Score: 14**

### Rule 6: Use CSS classes or styled-components instead of inline styles.
**Score: 13**

### Rule 5: Enable compression for all text-based assets (JS, CSS, HTML).
**Score: 12**

### Rule 4: Add unique meta descriptions for all pages for better SEO.
**Score: 11**

### Rule 3: Add breadcrumb navigation for better user orientation in deep hierarchies.
**Score: 9**

### Rule 2: Always include appropriate favicons for all platforms.
**Score: 8**

### Rule 1: Implement print-friendly CSS for pages users might want to print.
**Score: 6**