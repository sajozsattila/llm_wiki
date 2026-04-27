# Skill: Wiki Ingest

## Goal

Transform raw input into structured wiki knowledge.

## Steps

1. Check if relevant pages already exist in `/wiki/`
2. If YES:

   * Update existing pages
   * Merge new information
   * Update `updated` timestamp
   * Adjust `confidence`
3. If NO:

   * Create a new page using the schema

## Extraction Rules

* Extract atomic concepts
* Avoid duplication
* Split large topics into multiple pages

## Writing Rules

* Fill all required sections
* Add links to related pages
* Add sources in frontmatter + Sources section

## Confidence Scoring

* 0.9–1.0 → well-established fact
* 0.6–0.8 → likely correct
* 0.3–0.5 → uncertain
* <0.3 → speculative

## Output

* Only write markdown files into `/wiki/`
* Prefer updating over creating
