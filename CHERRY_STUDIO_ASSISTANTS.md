# Cherry Studio Assistants — Mapping from Osama/ Files

Create 9 assistants in Cherry Studio. Each gets its agent description + skill as the system prompt.

## 1. Lead Auditor (The Judge)
- **System prompt source:** AGENTS.md → Agent 1 (all lines)
- **Skill source:** SKILLS.md → Skill 02 (IMS Audit) + Skill 07 (Gap Analysis) + Skill 12 (CAPA)
- **Context:** Context.md → Track A section (lines 39-63)
- **Purpose:** Gap analysis, NC severity, clause-level audit

## 2. Lead Implementer (The Architect)
- **System prompt source:** AGENTS.md → Agent 2 (all lines)
- **Skill source:** SKILLS.md → Skill 06 (ISO 42001) + Skill 14 (Audit Package)
- **Context:** Context.md → Track B + Active Clients sections
- **Purpose:** Build deliverables, policies, client systems

## 3. Excel Workbook Engineer
- **System prompt source:** AGENTS.md → Agent 4 (all lines)
- **Skill source:** SKILLS.md → Skill 03 (Risk Register) + Skill 04 (BIA) + Skill 09 (Treatment Plan)
- **Context:** Memory.md → Excel preferences (lines 7-16) + Corrections 1,4,5,6
- **Purpose:** openpyxl workbooks with live formulas

## 4. Arabic Technical Writer
- **System prompt source:** AGENTS.md → Agent 5 (all lines)
- **Skill source:** SKILLS.md → Skill 05 (Arabic BCM)
- **Context:** Context.md → MSD-MOI section + Memory.md Arabic preferences + Corrections 2,3
- **Purpose:** Arabic MSA ISO docs, RTL formatting

## 5. AI Developer (The Automator)
- **System prompt source:** AGENTS.md → Agent 3 (all lines)
- **Skill source:** SKILLS.md → Skill 08 (Build Python Tool) + Skill 11 (ComplianceHub Dev) + Skill 17 (Debug)
- **Context:** SOUL.md → Platform Work section (lines 35-42)
- **Purpose:** Python automation, ComplianceHub dev

## 6. Delivery Manager
- **System prompt source:** AGENTS.md → Agent 9 (all lines)
- **Skill source:** SKILLS.md → Skill 16 (Six-Gate Pipeline)
- **Context:** Context.md → Active Clients section
- **Purpose:** 6-gate pipeline, client delivery tracking

## 7. Prompt Architect
- **System prompt source:** AGENTS.md → Agent 8 (all lines)
- **Skill source:** SKILLS.md → Skill 15 (12-part Prompt Framework)
- **Context:** Context.md → Prompt Quick Reference (lines 406-465)
- **Purpose:** Better AI prompts for any tool

## 8. Personal Concierge
- **System prompt source:** AGENTS.md → Agent 6 (all lines)
- **Skill source:** SKILLS.md → Skill 10 (Travel & Savings)
- **Context:** Context.md → Personal Finance section (lines 468-475)
- **Purpose:** Travel, cashback, Umrah planning

## 9. Platform Engineer (Legacy)
- **System prompt source:** AGENTS.md → Agent 7 (all lines)
- **Skill source:** SKILLS.md → Skill 18 (Legacy React Artifact)
- **Context:** Context.md → Legacy React Artifact section (lines 346-353)
- **Purpose:** TUV_Platform_Fixed.jsx maintenance only
